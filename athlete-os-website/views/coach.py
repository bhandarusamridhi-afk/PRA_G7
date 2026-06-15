"""AthleteOS - Coach dashboard (US-06, US-07, US-08, US-09).

The coach only ever sees athletes from their OWN sport.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import data, theme
from core.recommendations import (
    athlete_recommendations,
    coach_alerts,
    readiness_status,
    squad_coaching_tip,
)


def render(account: data.Account) -> None:
    sport = account.sport
    squad = data.squad_summary(sport)  # same-sport athletes only

    # ---- Header ----
    theme.brand_header("Coach Dashboard")
    st.markdown(
        f"### {account.name} &nbsp;|&nbsp; "
        f"<span style='color:{theme.PRIMARY}'>{sport}</span> squad",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='color:{theme.TEXT_MUTED}'>"
        f"{len(squad)} athletes, all {sport} - readiness across the squad at a glance.</span>",
        unsafe_allow_html=True,
    )

    # ---- Squad KPIs ----
    st.markdown("####  ")
    k = st.columns(4)
    with k[0]:
        st.metric("Squad size", len(squad))
    with k[1]:
        st.metric("Avg readiness", f"{squad['readiness'].mean():.0f}/100")
    with k[2]:
        flagged = int((squad["readiness"] < 60).sum() + (squad["acwr"] >= 1.5).sum())
        st.metric("Athletes flagged", flagged)
    with k[3]:
        st.metric("Avg sleep", f"{squad['sleep_hours'].mean():.1f} h")

    st.divider()

    # ---- AthleteOS Recommendations: squad alerts (pop-out) ----
    alerts = coach_alerts(squad)
    tip = squad_coaching_tip(squad)
    theme.render_recommendations(
        [tip] + alerts,
        header="AthleteOS Recommendations",
        subtitle=f"Squad-level alerts and programming guidance for your {sport} group",
    )

    st.divider()

    # ---- Squad comparison chart ----
    st.markdown("### Squad readiness comparison")
    sorted_sq = squad.sort_values("readiness")
    colors = []
    for v in sorted_sq["readiness"]:
        _, sev = readiness_status(v)
        colors.append(theme.SEVERITY_COLORS[sev])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_sq["name"], x=sorted_sq["readiness"], orientation="h",
        marker=dict(color=colors), text=[f"{v:.0f}" for v in sorted_sq["readiness"]],
        textposition="outside", textfont=dict(color=theme.TEXT),
        hovertemplate="%{y}<br>Readiness: %{x:.0f}/100<extra></extra>",
    ))
    fig.add_vline(x=60, line=dict(color=theme.WARN, width=1, dash="dash"))
    theme.style_fig(fig, height=90 + 52 * len(squad), title="Readiness by athlete")
    fig.update_xaxes(range=[0, 105], title="Readiness")
    st.plotly_chart(fig, use_container_width=True)

    # ---- Squad table ----
    st.markdown("### Squad overview")
    view = squad.copy()
    view["status"] = view["readiness"].apply(lambda v: readiness_status(v)[0])
    view = view[["name", "event", "status", "readiness", "recovery", "stress",
                 "sleep_hours", "acwr", "hrv"]]
    view.columns = ["Athlete", "Position/Event", "Status", "Readiness",
                    "Recovery", "Stress", "Sleep (h)", "ACWR", "HRV"]
    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Readiness": st.column_config.ProgressColumn(
                "Readiness", min_value=0, max_value=100, format="%d"),
            "Recovery": st.column_config.ProgressColumn(
                "Recovery", min_value=0, max_value=100, format="%d"),
        },
    )

    st.divider()

    # ---- Correlation analytics (US-08) ----
    st.markdown("### Correlation analytics: mental vs physical")
    metric_x = st.selectbox(
        "Compare physical output against a mental metric",
        ["stress", "focus", "confidence", "motivation"],
        format_func=str.capitalize,
    )

    # Build a combined frame across the whole squad.
    frames = []
    for a in data.athletes_for_sport(sport):
        d = data.generate_athlete_history(a["id"]).copy()
        d["athlete"] = a["name"]
        frames.append(d)
    combined = pd.concat(frames, ignore_index=True)

    corr = combined[metric_x].corr(combined["readiness"])
    fig = go.Figure()
    for i, a in enumerate(data.athletes_for_sport(sport)):
        sub = combined[combined["athlete"] == a["name"]]
        fig.add_trace(go.Scatter(
            x=sub[metric_x], y=sub["readiness"], mode="markers",
            name=a["name"],
            marker=dict(size=9, color=theme.CHART_COLORS[i % len(theme.CHART_COLORS)],
                        line=dict(width=0.5, color="rgba(255,255,255,0.2)")),
            hovertemplate=a["name"] + "<br>" + metric_x + ": %{x:.1f}<br>Readiness: %{y:.0f}<extra></extra>",
        ))
    # Trend line.
    x = combined[metric_x].to_numpy()
    y = combined["readiness"].to_numpy()
    if len(x) > 1 and np.std(x) > 0:
        m, b = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 50)
        fig.add_trace(go.Scatter(
            x=xs, y=m * xs + b, mode="lines", name="Trend",
            line=dict(color=theme.TEXT, width=2, dash="dash"),
        ))
    theme.style_fig(fig, height=420,
                    title=f"{metric_x.capitalize()} vs readiness  (r = {corr:.2f})")
    fig.update_xaxes(title=metric_x.capitalize())
    fig.update_yaxes(title="Readiness", range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Correlation coefficient r = {corr:.2f}. "
        + ("A clear negative relationship - higher stress tends to lower readiness."
           if metric_x == "stress" and corr < 0 else
           "Use this to justify programming decisions with data, not guesswork.")
    )

    st.divider()

    # ---- Athlete drill-down ----
    st.markdown("### Athlete deep-dive")
    names = [a["name"] for a in data.athletes_for_sport(sport)]
    chosen = st.selectbox("Select an athlete", names)
    chosen_id = next(a["id"] for a in data.athletes_for_sport(sport) if a["name"] == chosen)
    d = data.generate_athlete_history(chosen_id)
    snap = data.latest_snapshot(d)

    cols = st.columns([0.35, 0.65])
    with cols[0]:
        st.plotly_chart(theme.readiness_gauge(snap["readiness"], f"{chosen.split()[0]}'s Readiness"),
                        use_container_width=True, config={"displayModeBar": False})
    with cols[1]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d["date"], y=d["readiness"], name="Readiness",
                                 line=dict(color=theme.PRIMARY, width=3)))
        fig.add_trace(go.Scatter(x=d["date"], y=d["recovery"], name="Recovery",
                                 line=dict(color=theme.GOOD, width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=d["date"], y=d["stress"] * 10, name="Stress (x10)",
                                 line=dict(color=theme.BAD, width=2, dash="dot")))
        theme.style_fig(fig, height=300, title=f"{chosen} - 45-day trend")
        fig.update_yaxes(range=[0, 100], title="Score")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"#### AthleteOS guidance for {chosen}")
    theme.render_recommendations(
        athlete_recommendations(snap),
        header="AthleteOS Recommendations",
        subtitle=f"Individual guidance for {chosen} you can action in today's session",
    )

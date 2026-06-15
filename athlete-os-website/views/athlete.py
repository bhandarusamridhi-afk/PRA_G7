"""AthleteOS - Athlete dashboard (US-04, US-05, US-09)."""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from core import data, theme
from core.recommendations import athlete_recommendations, readiness_status


def _kpi_delta(label, value, suffix="", delta=None, delta_color="normal", help_text=None):
    st.metric(label, f"{value}{suffix}", delta=delta, delta_color=delta_color, help=help_text)


def render(account: data.Account) -> None:
    df = data.generate_athlete_history(account.user_id)
    snap = data.latest_snapshot(df)

    # ---- Header ----
    top = st.columns([0.62, 0.38])
    with top[0]:
        theme.brand_header("Athlete Dashboard")
        label, sev = readiness_status(snap["readiness"])
        st.markdown(
            f"### Welcome back, {account.name.split()[0]}  "
            f"{theme.status_pill(label, sev)}",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color:{theme.TEXT_MUTED}'>"
            f"{account.sport} &nbsp;|&nbsp; {account.event} &nbsp;|&nbsp; Coached by "
            f"{data.coach_for_sport(account.sport)['name']}</span>",
            unsafe_allow_html=True,
        )
    with top[1]:
        st.plotly_chart(theme.readiness_gauge(snap["readiness"], "Today's Readiness"),
                        use_container_width=True, config={"displayModeBar": False})

    # ---- KPI row ----
    st.markdown("####  ")
    k = st.columns(4)
    with k[0]:
        _kpi_delta("Recovery", f"{snap['recovery']:.0f}", "/100",
                   help_text="Composite of sleep quality, HRV and fatigue.")
    with k[1]:
        _kpi_delta("Sleep", f"{snap['sleep_hours']:.1f}", " h",
                   help_text="Last night's sleep duration.")
    with k[2]:
        _kpi_delta("Stress", f"{snap['stress']:.0f}", "/10",
                   delta=f"{snap['stress'] - df.iloc[-2]['stress']:+.1f}",
                   delta_color="inverse", help_text="Self-reported daily stress.")
    with k[3]:
        _kpi_delta("Workload (ACWR)", f"{snap['acwr']:.2f}",
                   help_text="Acute:chronic workload ratio. Safe zone 0.8-1.3.")

    st.divider()

    # ---- AthleteOS Recommendations (pop-out panel) ----
    recs = athlete_recommendations(snap)
    theme.render_recommendations(recs)

    st.divider()

    # ---- Charts ----
    tabs = st.tabs(["Readiness Trend", "Training vs Mental", "Sleep Impact", "Mental Profile"])

    with tabs[0]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["readiness"], mode="lines",
            line=dict(color=theme.PRIMARY, width=3),
            fill="tozeroy", fillcolor="rgba(0,180,255,0.12)", name="Readiness",
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["recovery"], mode="lines",
            line=dict(color=theme.GOOD, width=2, dash="dot"), name="Recovery",
        ))
        fig.add_hline(y=60, line=dict(color=theme.WARN, width=1, dash="dash"),
                      annotation_text="Caution threshold", annotation_position="top left",
                      annotation_font_color=theme.WARN, annotation_yshift=10)
        theme.style_fig(fig, height=380, title="Readiness & Recovery (last 45 days)")
        fig.update_yaxes(range=[0, 100], title="Score")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        recent = df.tail(21)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=recent["date"], y=recent["acute_load"], name="Training load",
            marker_color="rgba(0,180,255,0.55)",
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=recent["date"], y=recent["stress"], name="Stress",
            line=dict(color=theme.BAD, width=2.5), mode="lines+markers",
        ), secondary_y=True)
        fig.add_trace(go.Scatter(
            x=recent["date"], y=recent["motivation"], name="Motivation",
            line=dict(color=theme.GOOD, width=2.5), mode="lines+markers",
        ), secondary_y=True)
        theme.style_fig(fig, height=400, title="Training load vs mental state (last 21 days)")
        fig.update_yaxes(title_text="Training load (vol x int)", secondary_y=False)
        fig.update_yaxes(title_text="Mental score (1-10)", range=[0, 10], secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["sleep_hours"], y=df["readiness"], mode="markers",
            marker=dict(size=11, color=df["recovery"], colorscale="Tealrose_r",
                        showscale=True, colorbar=dict(title="Recovery", tickfont=dict(color=theme.TEXT_MUTED),
                                                      title_font=dict(color=theme.TEXT_MUTED)),
                        line=dict(width=1, color="rgba(255,255,255,0.25)")),
            text=[d.strftime("%b %d") for d in df["date"]],
            hovertemplate="%{text}<br>Sleep: %{x:.1f}h<br>Readiness: %{y:.0f}<extra></extra>",
            name="Days",
        ))
        theme.style_fig(fig, height=400, title="How sleep duration affects readiness")
        fig.update_xaxes(title="Sleep (hours)")
        fig.update_yaxes(title="Readiness", range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Each dot is one day. Top-right clusters confirm: more sleep tends to lift readiness.")

    with tabs[3]:
        last7 = df.tail(7)[["focus", "confidence", "motivation", "stress"]].mean()
        categories = ["Focus", "Confidence", "Motivation", "Calm (low stress)"]
        values = [last7["focus"], last7["confidence"], last7["motivation"], 10 - last7["stress"]]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]], theta=categories + [categories[0]],
            fill="toself", fillcolor="rgba(0,180,255,0.25)",
            line=dict(color=theme.PRIMARY, width=2.5), name="7-day average",
        ))
        fig.update_layout(
            template="plotly_dark", height=400,
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color=theme.TEXT),
            margin=dict(l=40, r=40, t=50, b=40),
            polar=dict(
                bgcolor="rgba(255,255,255,0.02)",
                radialaxis=dict(range=[0, 10], color=theme.TEXT_MUTED, gridcolor="rgba(157,178,212,0.15)"),
                angularaxis=dict(color=theme.TEXT),
            ),
            title=dict(text="Mental profile (7-day average)", font=dict(color=theme.TEXT, size=17), x=0.01),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- Daily mental check-in (US-04) ----
    st.markdown("### 60-second mental check-in")
    st.caption("Log how you feel today. AthleteOS folds this into your readiness signals.")
    with st.form("checkin"):
        c = st.columns(4)
        with c[0]:
            stress_in = st.slider("Stress", 1, 10, int(round(snap["stress"])))
        with c[1]:
            focus_in = st.slider("Focus", 1, 10, int(round(snap["focus"])))
        with c[2]:
            conf_in = st.slider("Confidence", 1, 10, int(round(snap["confidence"])))
        with c[3]:
            mot_in = st.slider("Motivation", 1, 10, int(round(snap["motivation"])))
        submitted = st.form_submit_button("Submit check-in")
    if submitted:
        updated = dict(snap)
        updated.update({"stress": stress_in, "focus": focus_in,
                        "confidence": conf_in, "motivation": mot_in})
        st.success("Check-in recorded. Updated guidance below:")
        theme.render_recommendations(
            athlete_recommendations(updated),
            header="AthleteOS Recommendations (updated)",
            subtitle="Refreshed using the check-in you just submitted",
        )

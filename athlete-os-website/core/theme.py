"""
AthleteOS - Visual theme, custom CSS, and reusable UI components.

Electric-blue + dark mode. High-contrast, bright text, glowing accents,
and recommendation cards that visibly "pop".
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

# ---- Palette -------------------------------------------------------------
BG = "#0A0E1A"
SURFACE = "#131C30"
SURFACE_2 = "#1B2740"
PRIMARY = "#00B4FF"      # electric blue
PRIMARY_SOFT = "#3DD2FF"
ACCENT = "#FF6B35"       # energetic orange accent
TEXT = "#EAF2FF"
TEXT_MUTED = "#9DB2D4"
GOOD = "#23D18B"
WARN = "#FFB23E"
BAD = "#FF4D6D"

SEVERITY_COLORS = {
    "positive": GOOD,
    "info": PRIMARY,
    "warning": WARN,
    "critical": BAD,
}

# Consistent bright palette for charts.
CHART_COLORS = [PRIMARY, ACCENT, GOOD, WARN, PRIMARY_SOFT, "#C77DFF"]


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"], .stApp {{
            font-family: 'Inter', sans-serif;
            color: {TEXT};
        }}
        .stApp {{
            background:
                radial-gradient(1100px 600px at 12% -10%, rgba(0,180,255,0.12), transparent 60%),
                radial-gradient(900px 500px at 100% 0%, rgba(255,107,53,0.08), transparent 55%),
                {BG};
        }}

        /* Headings bright + tight */
        h1, h2, h3, h4 {{ color: {TEXT}; letter-spacing: -0.01em; }}
        p, span, label, li, div {{ color: {TEXT}; }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border-right: 1px solid rgba(0,180,255,0.18);
        }}

        /* Metric cards */
        div[data-testid="stMetric"] {{
            background: linear-gradient(160deg, {SURFACE} 0%, {SURFACE_2} 100%);
            border: 1px solid rgba(0,180,255,0.20);
            border-radius: 16px;
            padding: 16px 18px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.35);
        }}
        div[data-testid="stMetricValue"] {{ color: {TEXT}; font-weight: 800; }}
        div[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED}; font-weight: 600; }}

        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {PRIMARY} 0%, #0077FF 100%);
            color: #04111F;
            font-weight: 700;
            border: 0;
            border-radius: 12px;
            padding: 0.55rem 1.1rem;
            box-shadow: 0 6px 18px rgba(0,180,255,0.35);
            transition: transform .08s ease, box-shadow .2s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 10px 26px rgba(0,180,255,0.5);
            color: #04111F;
        }}

        /* Inputs */
        input, textarea, .stTextInput input, .stNumberInput input {{
            color: {TEXT} !important;
            background: {SURFACE} !important;
        }}

        /* Tabs */
        button[data-baseweb="tab"] {{ color: {TEXT_MUTED}; font-weight: 600; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ color: {PRIMARY}; }}

        /* Dataframe text brightness */
        .stDataFrame, .stDataFrame * {{ color: {TEXT}; }}

        /* --- Recommendation cards --- */
        .aos-rec-wrap {{ display: flex; flex-direction: column; gap: 12px; }}
        .aos-rec {{
            position: relative;
            background: linear-gradient(160deg, {SURFACE} 0%, {SURFACE_2} 100%);
            border-radius: 14px;
            padding: 14px 16px 14px 20px;
            box-shadow: 0 8px 22px rgba(0,0,0,0.40);
            overflow: hidden;
        }}
        .aos-rec::before {{
            content: "";
            position: absolute; left: 0; top: 0; bottom: 0;
            width: 6px; border-radius: 14px 0 0 14px;
        }}
        .aos-rec h4 {{ margin: 0 0 4px 0; font-size: 1.0rem; font-weight: 700; }}
        .aos-rec p {{ margin: 0; color: {TEXT_MUTED}; font-size: 0.92rem; line-height: 1.5; }}
        .aos-chip {{
            display: inline-block; font-size: 0.68rem; font-weight: 800;
            letter-spacing: .08em; text-transform: uppercase;
            padding: 2px 9px; border-radius: 999px; margin-bottom: 6px;
        }}

        /* Branded recommendation panel header */
        .aos-rec-header {{
            display:flex; align-items:center; gap:10px;
            background: linear-gradient(135deg, rgba(0,180,255,0.18), rgba(255,107,53,0.10));
            border: 1px solid rgba(0,180,255,0.35);
            border-radius: 14px; padding: 12px 16px; margin-bottom: 12px;
        }}
        .aos-rec-header .dot {{
            width: 12px; height: 12px; border-radius: 50%;
            background: {PRIMARY}; box-shadow: 0 0 14px {PRIMARY};
        }}
        .aos-rec-header .ttl {{ font-weight: 800; font-size: 1.05rem; }}
        .aos-rec-header .sub {{ color: {TEXT_MUTED}; font-size: 0.82rem; }}

        /* Brand header */
        .aos-brand {{
            display:flex; align-items:center; gap:14px; margin-bottom: 4px;
        }}
        .aos-logo {{
            width: 46px; height: 46px; border-radius: 13px;
            background: linear-gradient(135deg, {PRIMARY} 0%, #0066FF 100%);
            display:flex; align-items:center; justify-content:center;
            font-weight: 900; font-size: 1.4rem; color:#04111F;
            box-shadow: 0 0 22px rgba(0,180,255,0.55);
        }}
        .aos-brand .name {{ font-size: 1.6rem; font-weight: 800; line-height: 1; }}
        .aos-brand .name span {{ color: {PRIMARY}; }}
        .aos-brand .tag {{ color: {TEXT_MUTED}; font-size: 0.82rem; }}

        /* Status pill */
        .aos-pill {{
            display:inline-block; padding: 4px 12px; border-radius: 999px;
            font-weight: 700; font-size: 0.8rem;
        }}
        hr {{ border-color: rgba(157,178,212,0.18); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand_header(subtitle: str = "Athlete Performance Intelligence") -> None:
    st.markdown(
        f"""
        <div class="aos-brand">
            <div class="aos-logo">A</div>
            <div>
                <div class="name">Athlete<span>OS</span></div>
                <div class="tag">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendations(recs: list[dict], header: str = "AthleteOS Recommendations",
                           subtitle: str = "Personalized, data-backed guidance from your readiness signals") -> None:
    """Render the branded, glowing recommendation panel."""
    header_html = (
        '<div class="aos-rec-header">'
        '<div class="dot"></div>'
        f'<div><div class="ttl">{header}</div>'
        f'<div class="sub">{subtitle}</div></div>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    chip_labels = {
        "positive": "Green light",
        "info": "Guidance",
        "warning": "Watch",
        "critical": "Action needed",
    }

    cards = '<div class="aos-rec-wrap">'
    for r in recs:
        color = SEVERITY_COLORS.get(r["severity"], PRIMARY)
        chip_label = chip_labels.get(r["severity"], "Guidance")
        cards += (
            f'<div class="aos-rec" style="border:1px solid {color}40;">'
            f'<span style="position:absolute;left:0;top:0;bottom:0;width:6px;'
            f'background:{color};box-shadow:0 0 16px {color};"></span>'
            f'<span class="aos-chip" style="background:{color}26;color:{color};">{chip_label}</span>'
            f'<h4 style="color:{TEXT};">{r["title"]}</h4>'
            f'<p>{r["body"]}</p>'
            '</div>'
        )
    cards += "</div>"
    st.markdown(cards, unsafe_allow_html=True)


def readiness_gauge(value: float, title: str = "Readiness") -> go.Figure:
    if value >= 75:
        bar = GOOD
    elif value >= 60:
        bar = PRIMARY
    elif value >= 45:
        bar = WARN
    else:
        bar = BAD

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "", "font": {"size": 40, "color": TEXT}},
            title={"text": title, "font": {"size": 16, "color": TEXT_MUTED}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": TEXT_MUTED, "tickfont": {"color": TEXT_MUTED}},
                "bar": {"color": bar, "thickness": 0.28},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 45], "color": "rgba(255,77,109,0.18)"},
                    {"range": [45, 60], "color": "rgba(255,178,62,0.18)"},
                    {"range": [60, 75], "color": "rgba(0,180,255,0.16)"},
                    {"range": [75, 100], "color": "rgba(35,209,139,0.18)"},
                ],
                "threshold": {"line": {"color": bar, "width": 4}, "thickness": 0.8, "value": value},
            },
        )
    )
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT},
    )
    return fig


def style_fig(fig: go.Figure, height: int = 340, title: str | None = None) -> go.Figure:
    """Apply consistent dark, bright-text, well-spaced styling to any figure."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        title=dict(text=title or "", font=dict(color=TEXT, size=17), x=0.01, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color=TEXT, size=13),
        margin=dict(l=55, r=30, t=55 if title else 30, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(color=TEXT_MUTED, size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(bgcolor=SURFACE_2, font_color=TEXT),
    )
    fig.update_xaxes(gridcolor="rgba(157,178,212,0.12)", zeroline=False, color=TEXT_MUTED,
                     title_font=dict(color=TEXT_MUTED))
    fig.update_yaxes(gridcolor="rgba(157,178,212,0.12)", zeroline=False, color=TEXT_MUTED,
                     title_font=dict(color=TEXT_MUTED))
    return fig


def status_pill(label: str, severity: str) -> str:
    color = SEVERITY_COLORS.get(severity, PRIMARY)
    return f'<span class="aos-pill" style="background:{color}26;color:{color};">{label}</span>'

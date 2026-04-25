"""
Right Horizons Terminal — shared theme module.
Imported by Home.py and every page in pages/ so all four scanners
share the same gold/dark "Nifty Breadth Pro" aesthetic.
"""
import streamlit as st

# ─── BRAND PALETTE (matches the Nifty Breadth Pro terminal) ─────────
RH_GOLD       = "#B8881A"
RH_GOLD_LIGHT = "#D4A830"
RH_GOLD_DIM   = "#7A5C10"
RH_RED        = "#E74C3C"
RH_GREEN      = "#2ECC71"
RH_BG         = "#0D0D0D"
RH_SURFACE    = "#161616"
RH_SURFACE2   = "#1E1E1E"
RH_TEXT       = "#E8DFC8"
RH_MUTED      = "#7A7060"
RH_BORDER     = "rgba(184,136,26,0.2)"


def apply_theme():
    """Inject the global terminal stylesheet — call once at the top of every page."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

    #MainMenu, footer {{ visibility: hidden; }}

    /* Keep the Streamlit header visible — it contains the sidebar toggle button. */
    [data-testid="stHeader"] {{
        background: transparent !important;
        height: auto !important;
    }}

    /* ============================================================
       SIDEBAR TOGGLE BUTTON — make it large, gold, and unmissable
       ============================================================ */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="header"] {{
        background: {RH_GOLD} !important;
        color: {RH_BG} !important;
        border: 2px solid {RH_GOLD_LIGHT} !important;
        border-radius: 0 !important;
        padding: 8px 14px !important;
        min-width: 48px !important;
        height: 40px !important;
        z-index: 999999 !important;
        box-shadow: 0 0 12px rgba(184,136,26,0.5) !important;
        animation: rh-pulse 2s ease-in-out infinite !important;
    }}

    @keyframes rh-pulse {{
        0%, 100% {{ box-shadow: 0 0 12px rgba(184,136,26,0.5); }}
        50%      {{ box-shadow: 0 0 20px rgba(184,136,26,0.9); }}
    }}

    /* HIDE the broken Material Icons text labels ("keyboard_double_…") */
    [data-testid="collapsedControl"] *,
    [data-testid="stSidebarCollapseButton"] *,
    button[kind="header"] * {{
        font-size: 0 !important;
        color: transparent !important;
    }}

    /* Replace with a clean ASCII chevron — black on gold so it pops */
    [data-testid="collapsedControl"]::after,
    [data-testid="stSidebarCollapseButton"]::after,
    button[kind="header"]::after {{
        content: "≡ FILTERS" !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        color: {RH_BG} !important;
        letter-spacing: 0.12em !important;
        display: inline-block !important;
        line-height: 1 !important;
    }}

    /* Hover state */
    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover,
    button[kind="header"]:hover {{
        background: {RH_GOLD_LIGHT} !important;
        cursor: pointer !important;
    }}

    .stApp {{
        background: {RH_BG};
        color: {RH_TEXT};
        font-family: 'IBM Plex Mono', monospace;
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {{
        background: {RH_SURFACE};
        border-right: 1px solid {RH_BORDER};
    }}
    [data-testid="stSidebar"] * {{
        font-family: 'IBM Plex Mono', monospace !important;
    }}
    [data-testid="stSidebarNav"] a {{
        color: {RH_MUTED} !important;
        font-size: 11px !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        color: {RH_GOLD_LIGHT} !important;
    }}
    [data-testid="stSidebarNav"] [aria-current="page"] {{
        color: {RH_GOLD_LIGHT} !important;
        background: rgba(184,136,26,0.08) !important;
    }}

    /* ── BRAND HEADER ── */
    .rh-header {{
        display: flex;
        align-items: baseline;
        gap: 14px;
        padding: 6px 0 14px;
        border-bottom: 1px solid {RH_BORDER};
        margin-bottom: 18px;
    }}
    .rh-brand {{
        font-family: 'Fraunces', serif;
        font-size: 22px;
        font-weight: 700;
        color: {RH_GOLD_LIGHT};
        letter-spacing: 0.06em;
    }}
    .rh-brand-sub {{
        font-size: 10px;
        color: {RH_MUTED};
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }}
    .rh-live {{
        margin-left: auto;
        font-size: 10px;
        color: {RH_MUTED};
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }}
    .rh-dot {{
        display: inline-block;
        width: 6px; height: 6px;
        background: {RH_GREEN};
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.4; }}
    }}

    /* ── KPI METRIC CARDS ── */
    [data-testid="stMetric"] {{
        background: {RH_SURFACE};
        border: 1px solid {RH_BORDER};
        padding: 14px 16px;
        border-radius: 0;
    }}
    [data-testid="stMetricLabel"] {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 9px !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase;
        color: {RH_MUTED} !important;
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'Fraunces', serif !important;
        font-weight: 900 !important;
        color: {RH_TEXT} !important;
        font-size: 26px !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
    }}

    /* ── SECTION TITLES ── */
    h1, h2, h3 {{
        font-family: 'IBM Plex Mono', monospace !important;
        color: {RH_GOLD_DIM} !important;
        font-size: 11px !important;
        letter-spacing: 0.16em !important;
        text-transform: uppercase;
        font-weight: 400 !important;
    }}

    /* ── BUTTONS ── */
    .stButton > button {{
        background: transparent !important;
        border: 1px solid {RH_BORDER} !important;
        color: {RH_MUTED} !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 4px 10px !important;
        border-radius: 0 !important;
        height: 30px !important;
        min-height: 30px !important;
        transition: all 0.15s ease;
    }}
    .stButton > button:hover {{
        border-color: {RH_GOLD_DIM} !important;
        color: {RH_GOLD_LIGHT} !important;
        background: rgba(184,136,26,0.04) !important;
    }}
    .stButton > button:focus {{
        box-shadow: none !important;
    }}
    .stButton > button[kind="primary"] {{
        background: {RH_GOLD} !important;
        border-color: {RH_GOLD} !important;
        color: {RH_BG} !important;
        font-weight: 500 !important;
    }}

    /* ── FORM LABELS ── */
    .stRadio > label, .stSlider > label, .stSelectbox > label, .stMultiSelect > label {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 10px !important;
        color: {RH_MUTED} !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}

    /* ── MULTISELECT TAGS ── */
    .stMultiSelect [data-baseweb="tag"] {{
        background: {RH_GOLD} !important;
        color: {RH_BG} !important;
    }}
    .stMultiSelect [data-baseweb="select"] > div {{
        background: {RH_SURFACE} !important;
        border-color: {RH_BORDER} !important;
    }}

    /* ── DATAFRAME ── */
    .stDataFrame {{
        border: 1px solid {RH_BORDER};
        background: {RH_SURFACE};
    }}
    .stDataFrame [data-testid="stDataFrameResizable"] {{
        background: {RH_SURFACE};
    }}

    hr, .stDivider {{
        border-color: {RH_BORDER} !important;
        margin: 12px 0 !important;
    }}

    /* ── EXPANDER ── */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {{
        background: {RH_SURFACE} !important;
        border: 1px solid {RH_BORDER} !important;
        color: {RH_GOLD_LIGHT} !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase;
    }}

    /* ── ALERTS ── */
    .stAlert {{
        background: {RH_SURFACE} !important;
        border: 1px solid {RH_BORDER} !important;
        border-radius: 0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header(subtitle: str = "Quantitative Scanner Suite", show_live: bool = True):
    """Brand header bar. Use at the top of every page."""
    live_html = (
        f"<span class='rh-live'><span class='rh-dot'></span>LIVE</span>"
        if show_live else ""
    )
    st.markdown(f"""
    <div class="rh-header">
        <span class="rh-brand">RIGHT HORIZONS</span>
        <span class="rh-brand-sub">{subtitle}</span>
        {live_html}
    </div>
    """, unsafe_allow_html=True)

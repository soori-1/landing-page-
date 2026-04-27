"""
Right Horizons Terminal — shared theme module.
Light brand palette matching the Right Horizons logo:
  Maroon  #8B1A1A  — primary brand color
  Gold    #C8922A  — accent
  Cream   #F5ECD7  — background
  Ink     #2C1810  — dark text
"""
import streamlit as st

# ─── BRAND PALETTE ───────────────────────────────────────────────────
RH_MAROON     = "#8B1A1A"
RH_MAROON_DK  = "#6B1010"
RH_GOLD       = "#C8922A"
RH_GOLD_LIGHT = "#D4A830"
RH_GOLD_DIM   = "#A8741A"
RH_RED        = "#C0392B"
RH_GREEN      = "#2E7D32"
RH_BG         = "#F5ECD7"
RH_SURFACE    = "#FFFFFF"
RH_SURFACE2   = "#EDE2C8"
RH_TEXT       = "#2C1810"
RH_MUTED      = "#8B6A4A"
RH_BORDER     = "rgba(139,26,26,0.15)"


def apply_theme():
    """Inject the global stylesheet — call once at the top of every page."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

    #MainMenu, footer {{ visibility: hidden; }}

    [data-testid="stHeader"] {{
        background: transparent !important;
        height: auto !important;
    }}

    /* ── SIDEBAR TOGGLE — gold pill, clearly visible ── */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {{
        background: {RH_GOLD} !important;
        border: 2px solid {RH_MAROON} !important;
        border-radius: 0 !important;
        padding: 6px 10px !important;
        z-index: 999999 !important;
        box-shadow: 0 0 10px rgba(200,146,42,0.5) !important;
    }}
    [data-testid="collapsedControl"] *,
    [data-testid="stSidebarCollapseButton"] * {{
        font-size: 0 !important;
        color: transparent !important;
    }}
    [data-testid="collapsedControl"]::after,
    [data-testid="stSidebarCollapseButton"]::after {{
        content: "≡ FILTERS" !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        letter-spacing: 0.12em !important;
        display: inline-block !important;
        line-height: 1 !important;
    }}
    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover {{
        background: {RH_MAROON} !important;
        cursor: pointer !important;
    }}

    /* ── PAGE BACKGROUND ── */
    .stApp {{
        background-color: {RH_BG};
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
        background: linear-gradient(180deg, {RH_MAROON_DK} 0%, {RH_MAROON} 100%);
        border-right: 2px solid {RH_GOLD_DIM};
    }}
    [data-testid="stSidebar"] * {{
        color: {RH_BG} !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stCheckbox label {{
        color: {RH_GOLD_LIGHT} !important;
        font-size: 10px !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase;
        font-weight: 500 !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: rgba(200,146,42,0.3) !important;
    }}
    [data-testid="stSidebar"] h3 {{
        color: {RH_GOLD_LIGHT} !important;
        font-size: 11px !important;
        letter-spacing: 0.16em !important;
        text-transform: uppercase;
        font-weight: 400 !important;
    }}
    [data-testid="stSidebar"] .stMarkdown strong {{
        color: {RH_GOLD_LIGHT} !important;
        font-size: 10px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}
    /* ── SIDEBAR INPUTS — cream bg, dark ink text, clearly readable ── */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stSelectbox > div > div > div,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stNumberInput > div > div > input,
    [data-testid="stSidebar"] .stTextInput > div > div > input,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: {RH_BG} !important;
        border: 1px solid {RH_GOLD} !important;
        color: {RH_TEXT} !important;
        border-radius: 0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 12px !important;
    }}

    /* Dropdown option text */
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div,
    [data-testid="stSidebar"] .stSelectbox span {{
        color: {RH_TEXT} !important;
    }}

    /* Number input +/- buttons */
    [data-testid="stSidebar"] [data-testid="stNumberInputStepDown"],
    [data-testid="stSidebar"] [data-testid="stNumberInputStepUp"] {{
        background: {RH_GOLD} !important;
        color: #FFFFFF !important;
        border: none !important;
    }}

    /* Radio buttons in sidebar */
    [data-testid="stSidebar"] .stRadio > div {{
        gap: 12px;
    }}
    [data-testid="stSidebar"] .stRadio label span:last-child {{
        color: {RH_BG} !important;
        font-size: 13px !important;
    }}

    /* Checkbox in sidebar */
    [data-testid="stSidebar"] .stCheckbox label span:last-child {{
        color: {RH_BG} !important;
        font-size: 12px !important;
    }}

    /* Slider track and thumb */
    [data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div {{
        background: {RH_GOLD} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{
        background: {RH_MAROON} !important;
        border: 2px solid {RH_GOLD} !important;
    }}
    /* ── SIDEBAR INTERNAL COLLAPSE BUTTON ── */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] button[kind="header"] {{
        background: transparent !important;
        border: none !important;
        border-bottom: 1px solid rgba(200,146,42,0.3) !important;
        border-radius: 0 !important;
        width: 100% !important;
        padding: 10px 16px !important;
        margin: 0 0 12px 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        min-height: 36px !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stSidebar"] button[kind="header"] * {{
        font-size: 0 !important;
        color: transparent !important;
        line-height: 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]::after,
    [data-testid="stSidebar"] button[kind="header"]::after {{
        content: "✕ CLOSE" !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        color: rgba(245,236,215,0.6) !important;
        letter-spacing: 0.16em !important;
        display: block !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover::after,
    [data-testid="stSidebar"] button[kind="header"]:hover::after {{
        color: {RH_BG} !important;
        cursor: pointer !important;
    }}

    /* ── BRAND HEADER ── */
    .rh-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0 14px;
        border-bottom: 2px solid {RH_MAROON};
        margin-bottom: 18px;
    }}
    .rh-brand {{
        font-family: 'Fraunces', serif;
        font-size: 22px;
        font-weight: 700;
        color: {RH_MAROON};
        letter-spacing: 0.04em;
    }}
    .rh-brand-sub {{
        font-size: 10px;
        color: {RH_MUTED};
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-left: 4px;
    }}
    .rh-live {{
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
        border-top: 3px solid {RH_MAROON};
        padding: 14px 16px;
        border-radius: 0;
        box-shadow: 0 1px 4px rgba(139,26,26,0.08);
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
        color: {RH_MAROON} !important;
        font-size: 11px !important;
        letter-spacing: 0.16em !important;
        text-transform: uppercase;
        font-weight: 500 !important;
    }}

    /* ── BUTTONS ── */
    .stButton > button {{
        background: {RH_SURFACE} !important;
        border: 1px solid {RH_MAROON} !important;
        color: {RH_MAROON} !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 6px 12px !important;
        border-radius: 0 !important;
        height: 34px !important;
        min-height: 34px !important;
        transition: all 0.15s ease;
        font-weight: 500 !important;
    }}
    .stButton > button:hover {{
        background: {RH_MAROON} !important;
        color: #FFFFFF !important;
        border-color: {RH_MAROON} !important;
    }}
    .stButton > button:focus {{
        box-shadow: none !important;
    }}
    .stButton > button[kind="primary"] {{
        background: {RH_MAROON} !important;
        border-color: {RH_MAROON} !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: {RH_MAROON_DK} !important;
    }}

    /* ── FORM LABELS ── */
    .stRadio > label, .stSlider > label,
    .stSelectbox > label, .stMultiSelect > label,
    .stNumberInput > label, .stTextInput > label,
    .stCheckbox > label {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 10px !important;
        color: {RH_MUTED} !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}

    /* ── SELECT/INPUT BOXES ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {{
        background: {RH_SURFACE} !important;
        border: 1px solid {RH_BORDER} !important;
        border-radius: 0 !important;
        color: {RH_TEXT} !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }}

    /* ── MULTISELECT TAGS ── */
    .stMultiSelect [data-baseweb="tag"] {{
        background: {RH_MAROON} !important;
        color: #FFFFFF !important;
    }}

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent;
        border-bottom: 2px solid {RH_MAROON};
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: {RH_MUTED} !important;
        border: none !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase;
        padding: 8px 16px !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {RH_MAROON} !important;
        background: {RH_SURFACE2} !important;
        border-bottom: 3px solid {RH_MAROON} !important;
        font-weight: 600 !important;
    }}

    /* ── DATAFRAME ── */
    .stDataFrame {{
        border: 1px solid {RH_BORDER};
        background: {RH_SURFACE};
    }}

    /* ── DIVIDERS ── */
    hr, .stDivider {{
        border-color: {RH_BORDER} !important;
        margin: 12px 0 !important;
    }}

    /* ── EXPANDER ── */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] summary {{
        background: {RH_SURFACE} !important;
        border: 1px solid {RH_BORDER} !important;
        color: {RH_MAROON} !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase;
    }}

    /* ── ALERTS ── */
    .stAlert {{
        background: {RH_SURFACE} !important;
        border-left: 3px solid {RH_MAROON} !important;
        border-radius: 0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        color: {RH_TEXT} !important;
    }}

    /* ── DOWNLOAD BUTTON ── */
    .stDownloadButton > button {{
        background: {RH_SURFACE} !important;
        color: {RH_MAROON} !important;
        border: 1px solid {RH_MAROON} !important;
        border-radius: 0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.12em;
    }}
    .stDownloadButton > button:hover {{
        background: {RH_MAROON} !important;
        color: #FFFFFF !important;
    }}

    /* ── PROGRESS BAR ── */
    .stProgress > div > div {{
        background: linear-gradient(90deg, {RH_MAROON}, {RH_GOLD}) !important;
        border-radius: 0 !important;
    }}
    .stProgress > div {{
        background: {RH_SURFACE2} !important;
        border-radius: 0 !important;
    }}

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-track {{ background: {RH_BG}; }}
    ::-webkit-scrollbar-thumb {{ background: {RH_GOLD_DIM}; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {RH_MAROON}; }}

    /* ── SIDEBAR NAV LINKS ── */
    [data-testid="stSidebarNav"] a {{
        color: {RH_BG} !important;
        font-size: 11px !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        color: {RH_GOLD_LIGHT} !important;
    }}
    [data-testid="stSidebarNav"] [aria-current="page"] {{
        color: {RH_GOLD_LIGHT} !important;
        background: rgba(200,146,42,0.15) !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header(subtitle: str = "Quantitative Scanner Suite", show_live: bool = True):
    """Brand header bar with Right Horizons logo."""
    import base64, os

    live_html = (
        "<span class='rh-live'><span class='rh-dot'></span>LIVE</span>"
        if show_live else ""
    )

    cwd    = os.getcwd()
    here   = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)

    logo_candidates = [
        os.path.join(cwd,    "logo.png"),
        os.path.join(cwd,    "assets", "logo.png"),
        os.path.join(here,   "logo.png"),
        os.path.join(here,   "assets", "logo.png"),
        os.path.join(parent, "logo.png"),
        os.path.join(parent, "assets", "logo.png"),
        os.path.join(cwd,    "logo.jpg"),
        os.path.join(cwd,    "assets", "logo.jpg"),
    ]
    logo_path = next((p for p in logo_candidates if os.path.exists(p)), None)

    if logo_path:
        ext = "jpeg" if logo_path.endswith(".jpg") else "png"
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        img_tag = (
            '<img src="data:image/' + ext + ';base64,' + b64 + '"'
            ' style="height:52px;width:auto;object-fit:contain;display:block;"'
            ' alt="Right Horizons" />'
        )
    else:
        img_tag = "<span class='rh-brand'>RIGHT HORIZONS</span>"

    st.markdown(
        '<div class="rh-header">'
            '<div style="display:flex;align-items:center;gap:14px;flex-shrink:0;">'
                + img_tag +
                "<span class='rh-brand-sub'>" + subtitle + "</span>"
            "</div>"
            + live_html +
        "</div>",
        unsafe_allow_html=True
    )

"""
Right Horizons Terminal — authentication gate.
Call require_login() near the top of every page (after set_page_config + apply_theme).
If the session is not authenticated, renders the login form and halts page execution.
"""
import hashlib
import streamlit as st

_VALID_EMAIL    = "RIGHTHORIZONS"
_PASSWORD_HASH  = hashlib.sha256("LEFT@horizons".encode()).hexdigest()

_LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

/* push the login card into the vertical centre of the viewport */
section[data-testid="stMain"] > div:first-child {
    padding-top: 12vh !important;
    padding-bottom: 6vh !important;
}

.rh-login-card {
    background: #FFFFFF;
    border: 1px solid rgba(139,26,26,0.18);
    border-top: 4px solid #8B1A1A;
    padding: 44px 48px 40px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 4px 24px rgba(139,26,26,0.08);
}

.rh-login-logo-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin-bottom: 28px;
}

.rh-login-brand {
    font-family: 'Fraunces', serif;
    font-size: 20px;
    font-weight: 700;
    color: #8B1A1A;
    letter-spacing: 0.04em;
    line-height: 1.2;
}

.rh-login-brand-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    color: #8B6A4A;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}

.rh-login-divider {
    border: none;
    border-top: 1px solid rgba(139,26,26,0.12);
    margin: 0 0 28px;
}

.rh-login-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #8B6A4A;
    text-align: center;
    margin-bottom: 24px;
}

.rh-login-footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 8px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8B6A4A;
    text-align: center;
    margin-top: 20px;
    opacity: 0.7;
}

/* ── Form: match card width ── */
div[data-testid="stForm"] {
    width: 100% !important;
    max-width: 420px !important;
    box-sizing: border-box !important;
}

div[data-testid="stForm"] .stTextInput,
div[data-testid="stForm"] .stTextInput > div,
div[data-testid="stForm"] .stTextInput > div > div {
    width: 100% !important;
    box-sizing: border-box !important;
}

/* Label */
div[data-testid="stForm"] .stTextInput > label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: #8B6A4A !important;
}

/* Input — text must be dark/readable regardless of app theme */
div[data-testid="stForm"] .stTextInput > div > div > input {
    width: 100% !important;
    box-sizing: border-box !important;
    background: #F5ECD7 !important;
    border: 1px solid rgba(139,26,26,0.25) !important;
    border-radius: 0 !important;
    color: #1A1A1A !important;
    -webkit-text-fill-color: #1A1A1A !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
}

div[data-testid="stForm"] .stTextInput > div > div > input::placeholder {
    color: #9B8B7A !important;
    -webkit-text-fill-color: #9B8B7A !important;
}

div[data-testid="stForm"] .stTextInput > div > div > input:focus {
    border-color: #8B1A1A !important;
    box-shadow: 0 0 0 1px #8B1A1A !important;
    outline: none !important;
    color: #1A1A1A !important;
    -webkit-text-fill-color: #1A1A1A !important;
}

/* Button — centred, auto width, always white text */
div[data-testid="stForm"] .stButton {
    display: flex !important;
    justify-content: center !important;
}

div[data-testid="stForm"] .stButton > button {
    background: #8B1A1A !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: none !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 10px 40px !important;
    border-radius: 0 !important;
    height: 42px !important;
    width: auto !important;
    min-width: 180px !important;
    box-sizing: border-box !important;
    transition: background 0.15s ease !important;
}

div[data-testid="stForm"] .stButton > button:hover {
    background: #6B1010 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* ── Responsive: collapse side columns on narrow screens ── */
@media (max-width: 768px) {
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {
        display: none !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
        padding: 0 16px !important;
    }
    .rh-login-card {
        padding: 32px 24px 28px !important;
    }
}
</style>
"""


def require_login() -> None:
    """Block page rendering until the user is authenticated."""
    if st.session_state.get("_rh_authenticated"):
        return

    # Hide sidebar nav while on the login screen
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none!important;}"
        "[data-testid='collapsedControl']{display:none!important;}</style>",
        unsafe_allow_html=True,
    )

    st.markdown(_LOGIN_CSS, unsafe_allow_html=True)

    with st.container():
        _, mid, _ = st.columns([1, 1.6, 1])
        with mid:
            st.markdown(
                '<div class="rh-login-card">'
                '<div class="rh-login-logo-row">'
                '<div>'
                '<div class="rh-login-brand">RIGHT HORIZONS</div>'
                '<div class="rh-login-brand-sub">Quantitative Terminal</div>'
                '</div>'
                '</div>'
                '<hr class="rh-login-divider">'
                '<div class="rh-login-title">Secure Access · Internal Tool</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.form("rh_login_form", clear_on_submit=False):
                email = st.text_input("Email / Username", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In  →")

            if submitted:
                if (
                    email.strip() == _VALID_EMAIL
                    and hashlib.sha256(password.encode()).hexdigest() == _PASSWORD_HASH
                ):
                    st.session_state["_rh_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

            st.markdown(
                '<div class="rh-login-footer">'
                '◇ Right Horizons Wealth Management · For authorised users only'
                '</div>',
                unsafe_allow_html=True,
            )

    st.stop()


def render_logout_button() -> None:
    """Render a compact logout button in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        if st.button("⎋ Sign Out", key="_rh_logout", use_container_width=True):
            st.session_state["_rh_authenticated"] = False
            st.rerun()

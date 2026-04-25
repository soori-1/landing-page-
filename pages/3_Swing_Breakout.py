"""
Scanner 03 — NSE Swing Breakout
Detects swing-high breakouts on daily timeframe with volume confirmation.
Logic ported from nse-swing-screener.

Swing High = candle whose high is higher than N candles on both sides
Breakout   = today's close > most recent swing high
Confirmed  = today's volume > 1.2× 20-day average
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import (
    apply_theme, render_header,
    RH_GOLD, RH_GOLD_LIGHT, RH_GOLD_DIM, RH_RED, RH_GREEN,
    RH_BG, RH_SURFACE, RH_TEXT, RH_MUTED, RH_BORDER
)

st.set_page_config(layout="wide", page_title="RH | Swing Breakout")
apply_theme()
render_header("Scanner 03 · NSE Swing Breakout")


# ─────────────────────────────────────────────────────
#  DEFAULT NSE LARGE/MID-CAP UNIVERSE
#  (Replace with your actual ticker list, or pull from
#  a CSV at data/nse_universe.csv)
# ─────────────────────────────────────────────────────
DEFAULT_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "BAJFINANCE.NS",
    "HCLTECH.NS", "WIPRO.NS", "ULTRACEMCO.NS", "TITAN.NS", "SUNPHARMA.NS",
    "NESTLEIND.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "POWERGRID.NS", "NTPC.NS",
    "M&M.NS", "BAJAJFINSV.NS", "TECHM.NS", "ADANIPORTS.NS", "DRREDDY.NS",
    "JSWSTEEL.NS", "GRASIM.NS", "INDUSINDBK.NS", "CIPLA.NS", "BPCL.NS",
    "EICHERMOT.NS", "BRITANNIA.NS", "HEROMOTOCO.NS", "DIVISLAB.NS", "HINDALCO.NS",
    "COALINDIA.NS", "ONGC.NS", "UPL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS",
    "ADANIENT.NS", "BAJAJ-AUTO.NS", "SHREECEM.NS", "PIDILITIND.NS", "DABUR.NS",
    "GODREJCP.NS", "DMART.NS", "AMBUJACEM.NS", "BERGEPAINT.NS", "BIOCON.NS",
    "CHOLAFIN.NS", "COLPAL.NS", "BOSCHLTD.NS", "ESCORTS.NS", "GAIL.NS",
    "HAVELLS.NS", "HDFCLIFE.NS", "ICICIPRULI.NS", "IOC.NS", "LICHSGFIN.NS",
    "MARICO.NS", "MOTHERSON.NS", "MPHASIS.NS", "NMDC.NS", "PEL.NS",
    "PIIND.NS", "PNB.NS", "SBILIFE.NS", "SIEMENS.NS", "TORNTPHARM.NS",
    "TRENT.NS", "TVSMOTOR.NS", "VEDL.NS", "VOLTAS.NS", "ZYDUSLIFE.NS",
]


@st.cache_data(ttl=3600)
def fetch_history(tickers, period="6mo"):
    """Batch-download daily OHLCV for all tickers."""
    try:
        import yfinance as yf
        data = yf.download(tickers, period=period, interval="1d",
                           auto_adjust=True, progress=False, group_by='ticker')
        return data
    except Exception as e:
        st.error(f"Data fetch failed: {e}")
        return None


def find_swing_highs(highs, n=3):
    """Index positions of swing highs — high greater than N bars on each side."""
    swings = []
    for i in range(n, len(highs) - n):
        window_left = highs.iloc[i-n:i]
        window_right = highs.iloc[i+1:i+n+1]
        if highs.iloc[i] > window_left.max() and highs.iloc[i] > window_right.max():
            swings.append(i)
    return swings


def find_swing_lows(lows, n=3):
    """Index positions of swing lows."""
    swings = []
    for i in range(n, len(lows) - n):
        window_left = lows.iloc[i-n:i]
        window_right = lows.iloc[i+1:i+n+1]
        if lows.iloc[i] < window_left.min() and lows.iloc[i] < window_right.min():
            swings.append(i)
    return swings


def scan_ticker(ticker, df, n=3, vol_mult=1.2):
    """Returns dict if breakout detected today, else None."""
    if df is None or df.empty or len(df) < 30:
        return None
    try:
        df = df.dropna()
        if len(df) < 30:
            return None
        swing_highs_idx = find_swing_highs(df['High'], n=n)
        if not swing_highs_idx:
            return None

        last_swing_idx = swing_highs_idx[-1]
        last_swing_high = df['High'].iloc[last_swing_idx]
        last_swing_date = df.index[last_swing_idx]

        today_close = df['Close'].iloc[-1]
        today_vol = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].iloc[-21:-1].mean()

        if today_close > last_swing_high and avg_vol > 0:
            vol_ratio = today_vol / avg_vol
            if vol_ratio >= vol_mult:
                return {
                    "Ticker": ticker.replace(".NS", ""),
                    "Close": round(today_close, 2),
                    "Swing High": round(last_swing_high, 2),
                    "Breakout %": round((today_close - last_swing_high) / last_swing_high * 100, 2),
                    "Volume": int(today_vol),
                    "Vol Ratio": round(vol_ratio, 2),
                    "Swing Date": last_swing_date.strftime("%d %b %Y"),
                }
    except Exception:
        return None
    return None


# ─────────────────────────────────────────────────────
#  CONTROLS
# ─────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    n_swing = st.slider("Swing window (bars)", 2, 10, 3,
                         help="Higher value = stronger but rarer swings")
with col2:
    vol_mult = st.slider("Volume multiplier", 1.0, 3.0, 1.2, 0.1,
                          help="Today's volume must exceed N× the 20-day average")
with col3:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    run_scan = st.button("⟳ RUN SCAN", use_container_width=True, type="primary")


# ─────────────────────────────────────────────────────
#  SCAN
# ─────────────────────────────────────────────────────
if run_scan or 'swing_results' not in st.session_state:
    with st.spinner(f"Scanning {len(DEFAULT_TICKERS)} NSE tickers..."):
        history = fetch_history(DEFAULT_TICKERS)
        if history is None:
            st.session_state.swing_results = pd.DataFrame()
            st.session_state.swing_history = {}
        else:
            results = []
            histories = {}
            progress = st.progress(0, text="Detecting swing breakouts...")
            for i, t in enumerate(DEFAULT_TICKERS):
                try:
                    if t in history.columns.get_level_values(0):
                        df = history[t][['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                    else:
                        df = pd.DataFrame()
                    histories[t] = df
                    res = scan_ticker(t, df, n=n_swing, vol_mult=vol_mult)
                    if res:
                        results.append(res)
                except Exception:
                    pass
                progress.progress((i+1)/len(DEFAULT_TICKERS),
                                   text=f"Scanning {t}… ({i+1}/{len(DEFAULT_TICKERS)})")
            progress.empty()

            st.session_state.swing_results = pd.DataFrame(results)
            st.session_state.swing_history = histories

results = st.session_state.swing_results
histories = st.session_state.swing_history

# ─────────────────────────────────────────────────────
#  KPI ROW
# ─────────────────────────────────────────────────────
total_scanned = len(DEFAULT_TICKERS)
breakouts = len(results)
hit_rate = (breakouts / total_scanned * 100) if total_scanned else 0
avg_breakout = results['Breakout %'].mean() if not results.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Universe scanned", total_scanned)
c2.metric("Breakouts found", breakouts,
           f"{hit_rate:.1f}% hit rate" if breakouts else "No breakouts")
c3.metric("Avg breakout strength",
           f"{avg_breakout:.2f}%" if breakouts else "—")
c4.metric("Volume threshold", f"{vol_mult:.1f}×")

st.divider()

# ─────────────────────────────────────────────────────
#  RESULTS TABLE
# ─────────────────────────────────────────────────────
st.subheader("Breakout Signals")

if results.empty:
    st.info("No swing breakouts detected for current parameters. "
            "Try lowering the swing window or volume multiplier.")
else:
    sorted_results = results.sort_values(by='Breakout %', ascending=False).reset_index(drop=True)

    def color_pct(val):
        try:
            v = float(val)
            if v > 0: return f'color: {RH_GREEN}; font-weight:500'
        except (TypeError, ValueError):
            pass
        return ''

    st.dataframe(
        sorted_results.style.map(color_pct, subset=['Breakout %'])
            .format({'Close': '{:.2f}', 'Swing High': '{:.2f}',
                     'Breakout %': '{:+.2f}%', 'Volume': '{:,.0f}',
                     'Vol Ratio': '{:.2f}×'}),
        use_container_width=True, hide_index=True, height=380
    )

    st.divider()

    # ─────────────────────────────────────────────────────
    #  DETAIL CHART — pick a ticker to inspect
    # ─────────────────────────────────────────────────────
    st.subheader("Inspect Breakout")

    selected = st.selectbox(
        "Select ticker",
        options=sorted_results['Ticker'].tolist(),
        index=0
    )

    yf_ticker = selected + ".NS"
    if yf_ticker in histories:
        df_chart = histories[yf_ticker].tail(120)

        swing_highs = find_swing_highs(df_chart['High'], n=n_swing)
        swing_lows = find_swing_lows(df_chart['Low'], n=n_swing)

        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df_chart.index,
            open=df_chart['Open'], high=df_chart['High'],
            low=df_chart['Low'],   close=df_chart['Close'],
            name=selected,
            increasing=dict(line=dict(color=RH_GREEN, width=1), fillcolor=RH_GREEN),
            decreasing=dict(line=dict(color=RH_RED, width=1), fillcolor=RH_RED),
        ))

        # Swing high markers
        if swing_highs:
            fig.add_trace(go.Scatter(
                x=df_chart.index[swing_highs],
                y=df_chart['High'].iloc[swing_highs],
                mode='markers',
                marker=dict(symbol='triangle-down', size=10,
                             color=RH_GOLD_LIGHT, line=dict(color=RH_GOLD, width=1)),
                name='Swing high',
            ))

        # Swing low markers
        if swing_lows:
            fig.add_trace(go.Scatter(
                x=df_chart.index[swing_lows],
                y=df_chart['Low'].iloc[swing_lows],
                mode='markers',
                marker=dict(symbol='triangle-up', size=10,
                             color="#8E6FD8", line=dict(color="#6A4FA0", width=1)),
                name='Swing low',
            ))

        # Latest swing-high breakout level
        if swing_highs:
            last_swing = df_chart['High'].iloc[swing_highs[-1]]
            fig.add_hline(y=last_swing, line_dash="dash",
                           line_color=RH_GOLD, line_width=1,
                           annotation_text=f" Breakout {last_swing:.2f}",
                           annotation_position="top right",
                           annotation_font=dict(family="IBM Plex Mono",
                                                color=RH_GOLD_LIGHT, size=10))

        fig.update_layout(
            height=520,
            plot_bgcolor=RH_BG, paper_bgcolor=RH_BG,
            font=dict(color=RH_TEXT, family="IBM Plex Mono", size=11),
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=20, b=10),
            hoverlabel=dict(bgcolor=RH_SURFACE, bordercolor=RH_GOLD_DIM,
                            font=dict(family="IBM Plex Mono", color=RH_TEXT)),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                bgcolor=RH_SURFACE, bordercolor=RH_BORDER, borderwidth=1,
                font=dict(family="IBM Plex Mono", size=10, color=RH_MUTED)
            ),
        )
        fig.update_xaxes(
            showgrid=True, gridwidth=0.5, gridcolor='rgba(58,53,48,0.4)',
            tickfont=dict(color=RH_MUTED, size=9, family='IBM Plex Mono'),
            zeroline=False, linecolor=RH_BORDER,
        )
        fig.update_yaxes(
            showgrid=True, gridwidth=0.5, gridcolor='rgba(58,53,48,0.4)',
            tickfont=dict(color=RH_MUTED, size=9, family='IBM Plex Mono'),
            zeroline=False, linecolor=RH_BORDER,
        )

        st.plotly_chart(fig, use_container_width=True,
                         config={'displayModeBar': False})
    else:
        st.warning("No price history available for this ticker.")

st.markdown("<br>", unsafe_allow_html=True)
st.page_link("Home.py", label="← Back to scanner hub", use_container_width=True)

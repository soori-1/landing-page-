"""
Scanner 03 — NSE Breakout Watch
Full port of nse-swing.py from nse-swing-screener repo.
Original warm-paper aesthetic restyled to gold/dark RH terminal.

8 CMT-grade filters:
  1. Nifty regime (>50MA)
  2. Relative Strength vs Nifty (3M)
  3. ATR-normalized distance
  4. Tight base (15d SD ≤ 4%)
  5. Wyckoff up/down volume ratio
  6. Resistance level integrity
  7. Chop-zone rejection
  8. 2-candle or 1.5× volume confirmation
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import (
    apply_theme, render_header,
    RH_GOLD, RH_GOLD_LIGHT, RH_GOLD_DIM, RH_RED, RH_GREEN,
    RH_BG, RH_SURFACE, RH_SURFACE2, RH_TEXT, RH_MUTED, RH_BORDER
)

st.set_page_config(layout="wide", page_title="RH | Breakout Watch",
                   initial_sidebar_state="expanded")
apply_theme()
render_header("Scanner 03 · NSE Breakout Watch")


# ─────────────────────────────────────────────────────
#  PAGE-SPECIFIC STYLES (custom tables, pills, KPI tiles)
# ─────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* KPI row */
.kpi-row {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 22px;
}}
.kpi {{
    background: {RH_SURFACE};
    border: 1px solid {RH_BORDER};
    padding: 14px 16px;
    text-align: center;
    transition: border-color 0.2s ease;
}}
.kpi:hover {{ border-color: {RH_GOLD_DIM}; }}
.kpi-val {{
    font-family: 'Fraunces', serif;
    font-size: 1.9rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.02em;
}}
.kpi-lbl {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: {RH_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.16em;
    margin-top: 8px;
    font-weight: 400;
}}

/* Custom data table */
.tbl {{
    background: {RH_SURFACE};
    border: 1px solid {RH_BORDER};
    overflow: hidden;
    margin-bottom: 8px;
}}
.tbl-hdr {{
    display: grid;
    grid-template-columns: 110px 100px 115px 130px 150px 100px 105px 95px;
    padding: 10px 22px;
    background: {RH_SURFACE2};
    border-bottom: 1px solid {RH_BORDER};
}}
.tbl-hdr span {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: {RH_GOLD_DIM};
    text-transform: uppercase;
    letter-spacing: 0.16em;
    font-weight: 500;
}}
.tbl-row {{
    display: grid;
    grid-template-columns: 110px 100px 115px 130px 150px 100px 105px 95px;
    padding: 14px 22px;
    border-bottom: 1px solid rgba(58,53,48,0.5);
    transition: background 0.12s;
    align-items: center;
}}
.tbl-row:hover {{ background: rgba(184,136,26,0.04); }}
.tbl-row:last-child {{ border-bottom: none; }}
.scroll-body {{ max-height: 520px; overflow-y: auto; }}
.scroll-body::-webkit-scrollbar {{ width: 4px; }}
.scroll-body::-webkit-scrollbar-track {{ background: {RH_SURFACE}; }}
.scroll-body::-webkit-scrollbar-thumb {{ background: {RH_GOLD_DIM}; }}

.sym {{
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.0rem;
    color: {RH_TEXT};
    letter-spacing: -0.01em;
}}
.mono {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: {RH_TEXT};
}}

/* Tier pills */
.pill {{
    display: inline-block;
    padding: 3px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.12em;
}}
.pill-hot  {{ background: rgba(231,76,60,0.08);  color: {RH_RED};         border: 1px solid rgba(231,76,60,0.4); }}
.pill-warm {{ background: rgba(212,168,48,0.08); color: {RH_GOLD_LIGHT};  border: 1px solid rgba(212,168,48,0.4); }}
.pill-cool {{ background: rgba(142,111,216,0.08); color: #8E6FD8;          border: 1px solid rgba(142,111,216,0.4); }}

/* Sector tag */
.sec {{
    display: inline-block;
    padding: 2px 7px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}

/* Proximity bar */
.prox {{ display: flex; align-items: center; gap: 8px; }}
.prox-bg {{
    flex: 1;
    height: 4px;
    background: rgba(58,53,48,0.5);
    overflow: hidden;
}}
.prox-fill {{ height: 100%; }}

/* Section headings */
.section-head {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: {RH_GOLD_DIM};
    margin: 26px 0 12px;
    display: flex;
    align-items: baseline;
    gap: 14px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    font-weight: 400;
}}
.section-head::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {RH_BORDER};
    position: relative;
    top: -3px;
}}
.section-head-label {{
    color: {RH_GOLD_LIGHT};
    font-weight: 500;
}}

/* Empty state */
.empty-state {{
    text-align: center;
    padding: 80px 20px;
}}
.empty-state-orn {{
    font-family: 'Fraunces', serif;
    font-size: 3rem;
    color: {RH_GOLD_DIM};
    margin-bottom: 14px;
    line-height: 1;
}}
.empty-state-text {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.95rem;
    color: {RH_TEXT};
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
.empty-state-sub {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: {RH_MUTED};
    margin-top: 8px;
    letter-spacing: 0.06em;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 24px;
    border-bottom: 1px solid {RH_BORDER};
    background: transparent !important;
    padding: 0 4px;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    color: {RH_MUTED} !important;
    background: transparent !important;
    padding: 10px 0 !important;
    border: none !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase;
}}
.stTabs [aria-selected="true"] {{
    color: {RH_GOLD_LIGHT} !important;
    border-bottom: 2px solid {RH_GOLD} !important;
}}

/* Sidebar slider labels */
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stCheckbox label {{
    color: {RH_GOLD_DIM} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.62rem !important;
    text-transform: uppercase;
    letter-spacing: 0.12em !important;
    font-weight: 500 !important;
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  WATCHLIST + SECTOR MAP
# ═══════════════════════════════════════════════════════════════
WATCHLIST = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","SBIN.NS","BAJFINANCE.NS","BHARTIARTL.NS","KOTAKBANK.NS",
    "AXISBANK.NS","LT.NS","HCLTECH.NS","ASIANPAINT.NS","WIPRO.NS",
    "MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS",
    "ONGC.NS","POWERGRID.NS","NTPC.NS","TECHM.NS","BAJAJFINSV.NS",
    "TATAMOTORS.NS","DRREDDY.NS","DIVISLAB.NS","CIPLA.NS","ADANIPORTS.NS",
    "COALINDIA.NS","GRASIM.NS","HINDALCO.NS","JSWSTEEL.NS","TATASTEEL.NS",
    "BPCL.NS","IOC.NS","HEROMOTOCO.NS","EICHERMOT.NS","BAJAJ-AUTO.NS",
    "BRITANNIA.NS","DABUR.NS","MARICO.NS","COLPAL.NS","GODREJCP.NS",
    "PIDILITIND.NS","BERGEPAINT.NS","HAVELLS.NS","VOLTAS.NS","ITC.NS",
    "PERSISTENT.NS","MPHASIS.NS","LTIM.NS","COFORGE.NS","ZOMATO.NS",
    "IRCTC.NS","INDHOTEL.NS","RVNL.NS","IRFC.NS","RECLTD.NS",
    "PFC.NS","BANKBARODA.NS","CANBK.NS","PNB.NS","FEDERALBNK.NS",
    "IDFCFIRSTB.NS","INDUSINDBK.NS","AUBANK.NS","CHOLAFIN.NS","MUTHOOTFIN.NS",
    "APOLLOHOSP.NS","FORTIS.NS","AUROPHARMA.NS","LUPIN.NS","TORNTPHARM.NS",
    "TATAPOWER.NS","ADANIGREEN.NS","NAUKRI.NS","INDIGO.NS","OFSS.NS",
    "DIXON.NS","TATACONSUM.NS","MOTHERSON.NS","BALKRISIND.NS","DMART.NS",
    "ABCAPITAL.NS","MFSL.NS","SBICARD.NS","HDFCAMC.NS","NIPPONLIFE.NS",
    "ANGELONE.NS","ICICIPRULI.NS","HDFCLIFE.NS","360ONE.NS","MOTILALOFS.NS",
    "ICICIGI.NS","STARHEALTH.NS","NUVAMA.NS","HAL.NS","BEL.NS","BHEL.NS",
    "COCHINSHIP.NS","CGPOWER.NS","SIEMENS.NS","ABB.NS","CUMMINSIND.NS",
    "THERMAX.NS","TRENT.NS","KALYANKJIL.NS","VBL.NS","KPITTECH.NS",
    "SUPREMEIND.NS","GRINDWELL.NS","TIMKEN.NS","SCHAEFFLER.NS",
]

SECTOR_MAP = {
    "RELIANCE.NS":"Energy","TCS.NS":"IT","HDFCBANK.NS":"Banking","INFY.NS":"IT",
    "ICICIBANK.NS":"Banking","HINDUNILVR.NS":"FMCG","SBIN.NS":"Banking",
    "BAJFINANCE.NS":"Finance","BHARTIARTL.NS":"Telecom","KOTAKBANK.NS":"Banking",
    "AXISBANK.NS":"Banking","LT.NS":"Infra","HCLTECH.NS":"IT","ASIANPAINT.NS":"Consumer",
    "WIPRO.NS":"IT","MARUTI.NS":"Auto","SUNPHARMA.NS":"Pharma","TITAN.NS":"Consumer",
    "ULTRACEMCO.NS":"Cement","NESTLEIND.NS":"FMCG","ONGC.NS":"Energy",
    "POWERGRID.NS":"Energy","NTPC.NS":"Energy","TECHM.NS":"IT","BAJAJFINSV.NS":"Finance",
    "TATAMOTORS.NS":"Auto","DRREDDY.NS":"Pharma","DIVISLAB.NS":"Pharma",
    "CIPLA.NS":"Pharma","ADANIPORTS.NS":"Infra","COALINDIA.NS":"Energy",
    "GRASIM.NS":"Cement","HINDALCO.NS":"Metal","JSWSTEEL.NS":"Metal",
    "TATASTEEL.NS":"Metal","BPCL.NS":"Energy","IOC.NS":"Energy","HEROMOTOCO.NS":"Auto",
    "EICHERMOT.NS":"Auto","BAJAJ-AUTO.NS":"Auto","BRITANNIA.NS":"FMCG",
    "DABUR.NS":"FMCG","MARICO.NS":"FMCG","COLPAL.NS":"FMCG","GODREJCP.NS":"FMCG",
    "PIDILITIND.NS":"Consumer","BERGEPAINT.NS":"Consumer","HAVELLS.NS":"Consumer",
    "VOLTAS.NS":"Consumer","ITC.NS":"FMCG","PERSISTENT.NS":"IT","MPHASIS.NS":"IT",
    "LTIM.NS":"IT","COFORGE.NS":"IT","ZOMATO.NS":"Consumer","IRCTC.NS":"Consumer",
    "INDHOTEL.NS":"Consumer","RVNL.NS":"Infra","IRFC.NS":"Finance","RECLTD.NS":"Finance",
    "PFC.NS":"Finance","BANKBARODA.NS":"Banking","CANBK.NS":"Banking","PNB.NS":"Banking",
    "FEDERALBNK.NS":"Banking","IDFCFIRSTB.NS":"Banking","INDUSINDBK.NS":"Banking",
    "AUBANK.NS":"Banking","CHOLAFIN.NS":"Finance","MUTHOOTFIN.NS":"Finance",
    "APOLLOHOSP.NS":"Pharma","FORTIS.NS":"Pharma","AUROPHARMA.NS":"Pharma",
    "LUPIN.NS":"Pharma","TORNTPHARM.NS":"Pharma","TATAPOWER.NS":"Energy",
    "ADANIGREEN.NS":"Energy","NAUKRI.NS":"IT","INDIGO.NS":"Consumer","OFSS.NS":"IT",
    "DIXON.NS":"Consumer","TATACONSUM.NS":"FMCG","MOTHERSON.NS":"Auto",
    "BALKRISIND.NS":"Auto","DMART.NS":"Consumer","ABCAPITAL.NS":"Finance",
    "MFSL.NS":"Finance","SBICARD.NS":"Finance","HDFCAMC.NS":"Finance","NIPPONLIFE.NS":"Finance",
    "ANGELONE.NS":"Finance","ICICIPRULI.NS":"Finance","HDFCLIFE.NS":"Finance",
    "360ONE.NS":"Finance","MOTILALOFS.NS":"Finance","ICICIGI.NS":"Finance",
    "STARHEALTH.NS":"Finance","NUVAMA.NS":"Finance",
    "HAL.NS":"Defence","BEL.NS":"Defence","BHEL.NS":"Infra","COCHINSHIP.NS":"Defence",
    "CGPOWER.NS":"CapGoods","SIEMENS.NS":"CapGoods","ABB.NS":"CapGoods",
    "CUMMINSIND.NS":"CapGoods","THERMAX.NS":"CapGoods",
    "TRENT.NS":"Consumer","KALYANKJIL.NS":"Consumer","VBL.NS":"FMCG",
    "KPITTECH.NS":"IT","SUPREMEIND.NS":"Consumer","GRINDWELL.NS":"CapGoods",
    "TIMKEN.NS":"CapGoods","SCHAEFFLER.NS":"CapGoods",
}

# Sector colors retuned to gold/dark complementary palette
SECTOR_COLORS = {
    "Banking":"#4A7A8B", "IT":"#8E6FD8", "FMCG":"#D4A442", "Finance":"#7A8B3F",
    "Energy":"#E74C3C", "Infra":"#5A7A8B", "Auto":"#C8922A", "Pharma":"#B85A8B",
    "Consumer":"#9DA856", "Metal":"#7A7060", "Cement":"#A8841E", "Telecom":"#5DA9C7",
    "Defence":"#7257B3", "CapGoods":"#7A8B5A",
}


# ═══════════════════════════════════════════════════════════════
#  CMT LOGIC (verbatim from nse-swing.py)
# ═══════════════════════════════════════════════════════════════
def calculate_atr(df, period=14):
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift()).abs()
    lc = (df['Low']  - df['Close'].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])


def calculate_adx(df, period=14):
    h, l, c = df['High'], df['Low'], df['Close']
    plus_dm  = h.diff().where((h.diff() > -l.diff()) & (h.diff() > 0), 0)
    minus_dm = (-l.diff()).where((-l.diff() > h.diff()) & (-l.diff() > 0), 0)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_s = tr.rolling(period).mean()
    pd_  = 100 * plus_dm.rolling(period).mean()  / atr_s
    md_  = 100 * minus_dm.rolling(period).mean() / atr_s
    dx   = 100 * (pd_ - md_).abs() / (pd_ + md_ + 1e-9)
    adx  = dx.rolling(period).mean()
    return float(adx.iloc[-1]) if not adx.empty else 0


def find_swings(df, lookback=10):
    highs, lows, n = df['High'].values, df['Low'].values, len(df)
    sh, sl = [], []
    for i in range(lookback, n - lookback):
        if highs[i] == max(highs[i - lookback: i + lookback + 1]):
            sh.append((df.index[i], round(float(highs[i]), 2)))
        if lows[i] == min(lows[i - lookback: i + lookback + 1]):
            sl.append((df.index[i], round(float(lows[i]), 2)))
    return sh, sl


@st.cache_data(ttl=1800, show_spinner=False)
def get_market_regime():
    try:
        import yfinance as yf
        n = yf.Ticker("^NSEI").history(period="6mo")
        if n.empty or len(n) < 50:
            return True, 0
        close = float(n['Close'].iloc[-1])
        ma50  = float(n['Close'].iloc[-50:].mean())
        return close > ma50, round((close - ma50) / ma50 * 100, 2)
    except Exception:
        return True, 0


@st.cache_data(ttl=1800, show_spinner=False)
def get_nifty_return(period_days=63):
    try:
        import yfinance as yf
        n = yf.Ticker("^NSEI").history(period="1y")
        if n.empty or len(n) < period_days:
            return 0
        return float((n['Close'].iloc[-1] / n['Close'].iloc[-period_days] - 1) * 100)
    except Exception:
        return 0


def check_rs(df, nifty_ret, period_days=63):
    if len(df) < period_days:
        return False, 0, 0
    ret = float((df['Close'].iloc[-1] / df['Close'].iloc[-period_days] - 1) * 100)
    return ret > nifty_ret, round(ret, 2), round(ret - nifty_ret, 2)


def wyckoff_check(df, sh_idx, lo_idx):
    if lo_idx <= sh_idx:
        return True, 1.0
    seg = df.iloc[sh_idx: lo_idx + 1]
    if len(seg) < 3:
        return True, 1.0
    up = seg[seg['Close'] > seg['Open']]['Volume'].sum()
    dn = seg[seg['Close'] < seg['Open']]['Volume'].sum()
    if dn == 0:
        return True, 2.0
    return (up / dn) >= 0.6, round(float(up / dn), 2)


def tight_base(df, period=15, max_sd_pct=4.0):
    if len(df) < period:
        return True, 0
    c = df['Close'].iloc[-period:]
    sd = float(c.std() / c.mean() * 100)
    return sd <= max_sd_pct, round(sd, 2)


def find_valid_resistance(df, swing_highs, threshold_atr_mult=1.5,
                           min_pullback_pct=5.0, min_sh_age=12, min_pb_age=10):
    if not swing_highs:
        return None
    close   = float(df['Close'].iloc[-1])
    closes  = df['Close'].values
    highs_a = df['High'].values
    lows_a  = df['Low'].values
    n       = len(df)

    if n >= 50 and close < float(df['Close'].iloc[-50:].mean()) * 0.97:
        return None

    atr = calculate_atr(df)
    if atr == 0 or np.isnan(atr):
        return None

    for sh_date, sh_price in reversed(swing_highs):
        if sh_price <= close:
            continue
        try:
            bar_idx = df.index.get_loc(sh_date)
        except Exception:
            continue
        if (n - 1 - bar_idx) < min_sh_age:
            continue

        post_lows = lows_a[bar_idx + 1:]
        if len(post_lows) == 0:
            continue
        lo_rel = int(np.argmin(post_lows))
        lo_abs = bar_idx + 1 + lo_rel
        lo_val = float(post_lows[lo_rel])
        pb_pct = (sh_price - lo_val) / sh_price * 100
        if pb_pct < min_pullback_pct:
            continue

        if (n - 1 - lo_abs) < min_pb_age:
            continue

        if lo_abs < n - 1:
            hs = highs_a[lo_abs: n - 1]
            if len(hs) > 0 and float(hs.max()) > sh_price * 1.002:
                continue

        if int(np.sum(closes > sh_price * 1.002)) / n > 0.10:
            continue

        win_len = min(120, bar_idx)
        if win_len > 20:
            pre = highs_a[bar_idx - win_len: bar_idx]
            if len(pre) > 0 and float(pre.max()) > sh_price:
                continue

        gap_pts = sh_price - close
        gap_atr = round(gap_pts / atr, 2)
        if gap_atr > threshold_atr_mult:
            continue

        base_ok, base_sd = tight_base(df)
        if not base_ok:
            continue

        wy_ok, wy_ratio = wyckoff_check(df, bar_idx, lo_abs)

        tier = "HOT" if gap_atr <= 0.5 else "WARM" if gap_atr <= 1.0 else "CLOSE"

        return {
            "price": sh_price, "date": sh_date,
            "gap_pct": round(gap_pts/sh_price*100, 2),
            "gap_atr": gap_atr, "tier": tier,
            "pullback_pct": round(pb_pct, 2),
            "pullback_low": round(lo_val, 2),
            "base_sd_pct": base_sd,
            "wyckoff_ok": wy_ok, "wyckoff_ratio": wy_ratio,
            "atr": round(atr, 2),
        }
    return None


@st.cache_data(ttl=900, show_spinner=False)
def run_approaching(lookback, min_mcap, threshold_atr):
    import yfinance as yf
    risk_on, _ = get_market_regime()
    nifty_ret = get_nifty_return(63)
    results = []
    for sym in WATCHLIST:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="2y", interval="1d")
            if df.empty or len(df) < 80:
                continue
            mcap_cr = (getattr(t.fast_info, "market_cap", 0) or 0) / 1e7
            if mcap_cr < min_mcap:
                continue
            rs_ok, stock_ret, rs_diff = check_rs(df, nifty_ret)
            if not rs_ok:
                continue
            sh, sl = find_swings(df, lookback)
            r = find_valid_resistance(df, sh, threshold_atr_mult=threshold_atr)
            if not r:
                continue
            close = round(float(df['Close'].iloc[-1]), 2)
            prev  = round(float(df['Close'].iloc[-2]), 2)
            day_chg = round((close - prev) / prev * 100, 2)
            vn = float(df['Volume'].iloc[-1])
            va = float(df['Volume'].iloc[-21:-1].mean())
            vr = round(vn / va, 2) if va > 0 else 0
            adx = round(calculate_adx(df), 1)
            results.append({
                "symbol": sym.replace(".NS", ""), "full_sym": sym,
                "close": close, "day_chg": day_chg,
                "swing_high": r["price"], "sh_date": r["date"].strftime("%d %b '%y"),
                "swing_low": sl[-1][1] if sl else None,
                "gap_pct": r["gap_pct"], "gap_atr": r["gap_atr"], "tier": r["tier"],
                "pullback": r["pullback_pct"], "base_sd": r["base_sd_pct"],
                "wyckoff_ok": r["wyckoff_ok"], "wyckoff_ratio": r["wyckoff_ratio"],
                "vol_ratio": vr, "adx": adx,
                "rs_diff": rs_diff, "stock_ret": stock_ret,
                "mcap_cr": round(mcap_cr), "sector": SECTOR_MAP.get(sym, "Other"),
                "sh_list": [(d.strftime("%Y-%m-%d"), p) for d, p in sh[-8:]],
                "sl_list": [(d.strftime("%Y-%m-%d"), p) for d, p in sl[-8:]],
            })
        except Exception:
            continue
    order = {"HOT": 0, "WARM": 1, "CLOSE": 2}
    return sorted(results, key=lambda x: (order[x["tier"]], x["gap_atr"])), risk_on


@st.cache_data(ttl=900, show_spinner=False)
def run_breakouts(lookback, min_mcap, days_back=5):
    import yfinance as yf
    risk_on, _ = get_market_regime()
    nifty_ret = get_nifty_return(63)
    results = []
    for sym in WATCHLIST:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="2y", interval="1d")
            if df.empty or len(df) < 80:
                continue
            mcap_cr = (getattr(t.fast_info, "market_cap", 0) or 0) / 1e7
            if mcap_cr < min_mcap:
                continue
            rs_ok, stock_ret, rs_diff = check_rs(df, nifty_ret)
            if not rs_ok:
                continue
            sh, sl = find_swings(df, lookback)
            n = len(df)
            closes = df['Close'].values
            vols   = df['Volume'].values

            bo_days = None; bo_level = None; bo_date = None; conf = None
            for days_ago in range(1, days_back + 1):
                cidx = n - days_ago
                c_close = float(closes[cidx]); p_close = float(closes[cidx - 1])
                df_s = df.iloc[:cidx]
                sh_s, _ = find_swings(df_s, lookback)
                v = find_valid_resistance(df_s, sh_s, threshold_atr_mult=10.0)
                if not v:
                    continue
                res = v["price"]
                if c_close > res and p_close <= res:
                    next_idx = cidx + 1
                    got = None
                    if next_idx < n and float(closes[next_idx]) > res:
                        got = "2-candle"
                    else:
                        va_ = float(vols[max(0, cidx - 20):cidx].mean())
                        if va_ > 0 and float(vols[cidx]) / va_ >= 1.5:
                            got = "volume"
                    if got is None and days_ago == 1:
                        got = "pending"
                    elif got is None:
                        continue
                    bo_days = days_ago; bo_level = res
                    bo_date = v["date"]; conf = got
                    break
            if bo_days is None:
                continue

            close = round(float(closes[-1]), 2)
            prev  = round(float(closes[-2]), 2)
            day_chg = round((close - prev) / prev * 100, 2)
            bo_pct  = round((close - bo_level) / bo_level * 100, 2)
            lbl = "TODAY" if bo_days == 1 else f"{bo_days}D AGO"
            adx = round(calculate_adx(df), 1)
            vn = float(df['Volume'].iloc[-1]); va = float(df['Volume'].iloc[-21:-1].mean())
            vr = round(vn / va, 2) if va > 0 else 0

            results.append({
                "symbol": sym.replace(".NS", ""), "full_sym": sym,
                "close": close, "day_chg": day_chg,
                "broken_sh": bo_level,
                "sh_date": bo_date.strftime("%d %b '%y") if bo_date else "—",
                "bo_pct": bo_pct, "days_ago": bo_days, "label": lbl,
                "confirmation": conf,
                "swing_low": sl[-1][1] if sl else None,
                "vol_ratio": vr, "adx": adx, "rs_diff": rs_diff,
                "mcap_cr": round(mcap_cr), "sector": SECTOR_MAP.get(sym, "Other"),
                "sh_list": [(d.strftime("%Y-%m-%d"), p) for d, p in sh[-8:]],
                "sl_list": [(d.strftime("%Y-%m-%d"), p) for d, p in sl[-8:]],
            })
        except Exception:
            continue
    return sorted(results, key=lambda x: (x["days_ago"], -x["bo_pct"])), risk_on


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding:12px 0 16px; border-bottom:1px solid {RH_BORDER}; margin-bottom:14px;'>
        <div style='font-family:Fraunces,serif; font-size:1.2rem; font-weight:700;
                    color:{RH_GOLD_LIGHT}; letter-spacing:0.04em;'>△ Breakout Watch</div>
        <div style='font-family:IBM Plex Mono,monospace; font-size:0.62rem;
                    color:{RH_MUTED}; margin-top:6px; letter-spacing:0.18em;
                    text-transform:uppercase;'>NSE · Daily · CMT</div>
    </div>""", unsafe_allow_html=True)

    threshold_atr = st.slider("Gap to SH (ATRs)", 0.3, 3.0, 1.5, 0.1)
    lookback      = st.slider("Swing lookback", 5, 15, 10)
    min_mcap      = st.slider("Min market cap (₹ Cr)", 500, 10000, 500, 250)
    days_back     = st.slider("Breakout window (days)", 1, 10, 5, 1)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    run_btn = st.button("RUN SCREEN", use_container_width=True, type="primary")

    st.markdown(f"""
    <div style='margin-top:22px; padding:12px; background:{RH_BG};
                border:1px solid {RH_BORDER};'>
        <div style='font-family:IBM Plex Mono,monospace; font-size:0.58rem;
                    color:{RH_GOLD_LIGHT}; text-transform:uppercase;
                    letter-spacing:0.16em; margin-bottom:10px; font-weight:500;'>
            Active Filters · CMT
        </div>
        <div style='font-family:IBM Plex Mono,monospace; font-size:0.7rem;
                    color:{RH_TEXT}; line-height:1.9; letter-spacing:0.04em;'>
            ① Nifty regime check<br>
            ② Relative Strength &gt; Nifty<br>
            ③ ATR-normalized distance<br>
            ④ Tight base (SD ≤ 4%)<br>
            ⑤ Wyckoff volume absorption<br>
            ⑥ Level integrity<br>
            ⑦ Chop zone rejection<br>
            ⑧ 2-candle confirmation
        </div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "sw_results"   not in st.session_state: st.session_state.sw_results = None
if "sw_breakouts" not in st.session_state: st.session_state.sw_breakouts = None
if "sw_risk_on"   not in st.session_state: st.session_state.sw_risk_on = True

if run_btn:
    with st.spinner("Scanning 110 stocks · applying 8 CMT filters..."):
        st.session_state.sw_results,   st.session_state.sw_risk_on = run_approaching(
            lookback, min_mcap, threshold_atr
        )
        st.session_state.sw_breakouts, _ = run_breakouts(lookback, min_mcap, days_back)


if st.session_state.sw_results is None:
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-orn">△</div>
        <div class="empty-state-text">Awaiting your instructions</div>
        <div class="empty-state-sub">Configure filters and press Run Screen</div>
        <div style='margin-top:36px; padding:16px 24px; display:inline-block;
                    background:{RH_SURFACE}; border:1px solid {RH_GOLD_DIM};
                    font-family:IBM Plex Mono,monospace; font-size:0.78rem;
                    color:{RH_GOLD_LIGHT}; letter-spacing:0.08em;'>
            ◀ Open the sidebar from the top-left to access filters
        </div>
        <div style='margin-top:14px; font-family:IBM Plex Mono,monospace;
                    font-size:0.68rem; color:{RH_MUTED}; letter-spacing:0.06em;'>
            If the sidebar arrow isn't visible, look for "&gt;" at the very
            top-left edge of the page · or use the keyboard shortcut
            <kbd style='background:{RH_BG}; padding:2px 6px; border:1px solid {RH_BORDER};
                        color:{RH_GOLD_LIGHT};'>Ctrl/Cmd + Shift + .</kbd>
        </div>
    </div>""", unsafe_allow_html=True)
    if st.button("← BACK TO HUB", key="back_empty"):
        st.switch_page("Home.py")
    st.stop()


# Risk-off banner
if not st.session_state.sw_risk_on:
    st.markdown(f"""
    <div style='background:rgba(231,76,60,0.06); border:1px solid {RH_RED};
                border-left:4px solid {RH_RED}; padding:14px 20px;
                margin-bottom:18px;'>
        <div style='font-family:Fraunces,serif; font-weight:700; color:{RH_RED};
                    font-size:0.95rem;'>
            ⚠ Market Regime: RISK-OFF
        </div>
        <div style='font-family:IBM Plex Mono,monospace; font-size:0.72rem;
                    color:{RH_TEXT}; margin-top:6px; letter-spacing:0.04em;'>
            Nifty is below its 50-day MA. Breakouts fail more often in such phases.
            Consider waiting for regime confirmation.
        </div>
    </div>""", unsafe_allow_html=True)


tab1, tab2, tab3 = st.tabs(["APPROACHING", "RECENT BREAKOUTS", "VALIDATE LOGIC"])


# ─────────────────────────────────────────────────────
#  CHART RENDERER (shared between tabs 1 and 2)
# ─────────────────────────────────────────────────────
def render_chart(sel):
    try:
        import yfinance as yf
        df_c = yf.Ticker(sel["full_sym"]).history(period="1y", interval="1d")
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            row_heights=[0.72, 0.28], vertical_spacing=0.03
        )
        fig.add_trace(go.Candlestick(
            x=df_c.index, open=df_c['Open'], high=df_c['High'],
            low=df_c['Low'], close=df_c['Close'],
            increasing_line_color=RH_GREEN, decreasing_line_color=RH_RED,
            increasing_fillcolor=RH_GREEN, decreasing_fillcolor=RH_RED,
            name="Price", line_width=1
        ), row=1, col=1)

        sh_level = sel.get("swing_high") or sel.get("broken_sh")
        if sh_level:
            label = f"Resistance ₹{sh_level:,}"
            if sel.get("gap_pct") is not None:
                label += f"  ·  {sel.get('gap_pct')}% / {sel.get('gap_atr','?')} ATR"
            elif sel.get("bo_pct"):
                label += f"  ·  broke +{sel['bo_pct']}%"
            fig.add_hline(
                y=sh_level, line_dash="dash", line_color=RH_GOLD, line_width=1.5,
                annotation_text=label, annotation_position="top left",
                annotation_font=dict(color=RH_GOLD_LIGHT, size=10, family="IBM Plex Mono"),
                row=1, col=1
            )
        if sel.get("swing_low"):
            fig.add_hline(
                y=sel["swing_low"], line_dash="dot", line_color="#5DA9C7", line_width=1.2,
                annotation_text=f"Support ₹{sel['swing_low']:,}",
                annotation_position="bottom left",
                annotation_font=dict(color="#5DA9C7", size=10, family="IBM Plex Mono"),
                row=1, col=1
            )

        sh_d = [s[0] for s in sel["sh_list"]]
        sh_p = [s[1] for s in sel["sh_list"]]
        fig.add_trace(go.Scatter(
            x=sh_d, y=sh_p, mode='markers',
            marker=dict(color=RH_GOLD, size=8, symbol='triangle-down',
                        line=dict(color=RH_GOLD_DIM, width=1)),
            name="Swing Highs"
        ), row=1, col=1)

        sl_d = [s[0] for s in sel["sl_list"]]
        sl_p = [s[1] for s in sel["sl_list"]]
        fig.add_trace(go.Scatter(
            x=sl_d, y=sl_p, mode='markers',
            marker=dict(color="#5DA9C7", size=8, symbol='triangle-up',
                        line=dict(color="#3A7A95", width=1)),
            name="Swing Lows"
        ), row=1, col=1)

        vol_c = ['rgba(46,204,113,0.5)' if c >= o else 'rgba(231,76,60,0.5)'
                 for c, o in zip(df_c['Close'], df_c['Open'])]
        fig.add_trace(go.Bar(x=df_c.index, y=df_c['Volume'],
                              marker_color=vol_c, showlegend=False), row=2, col=1)

        avg_v = df_c['Volume'].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df_c.index, y=avg_v,
            line=dict(color='rgba(212,168,48,0.6)', width=1, dash='dot'),
            showlegend=False
        ), row=2, col=1)

        fig.update_layout(
            height=500, plot_bgcolor=RH_BG, paper_bgcolor=RH_BG,
            font=dict(family='IBM Plex Mono', color=RH_MUTED, size=10),
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation='h', y=1.04, x=0,
                         font=dict(size=9, color=RH_MUTED),
                         bgcolor='rgba(0,0,0,0)'),
            hoverlabel=dict(bgcolor=RH_SURFACE, bordercolor=RH_GOLD_DIM,
                             font=dict(family='IBM Plex Mono', color=RH_TEXT))
        )
        fig.update_xaxes(gridcolor='rgba(58,53,48,0.5)', zeroline=False,
                          linecolor=RH_BORDER)
        fig.update_yaxes(gridcolor='rgba(58,53,48,0.5)', zeroline=False,
                          linecolor=RH_BORDER)
        st.plotly_chart(fig, use_container_width=True,
                         config={"displayModeBar": False})
    except Exception as e:
        st.error(f"Chart error: {e}")


# ═══════════════════════════════════════════════════════════════
#  TAB 1 — APPROACHING
# ═══════════════════════════════════════════════════════════════
with tab1:
    results = st.session_state.sw_results
    total = len(results)
    hot   = sum(1 for r in results if r["tier"] == "HOT")
    warm  = sum(1 for r in results if r["tier"] == "WARM")
    wy    = sum(1 for r in results if r["wyckoff_ok"])
    avg_rs = round(sum(r["rs_diff"] for r in results) / total, 1) if total else 0

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi"><div class="kpi-val" style="color:{RH_GOLD_LIGHT}">{total}</div>
            <div class="kpi-lbl">Setups</div></div>
        <div class="kpi"><div class="kpi-val" style="color:{RH_RED}">{hot}</div>
            <div class="kpi-lbl">Hot ≤ 0.5 ATR</div></div>
        <div class="kpi"><div class="kpi-val" style="color:{RH_GOLD_LIGHT}">{warm}</div>
            <div class="kpi-lbl">Warm ≤ 1.0 ATR</div></div>
        <div class="kpi"><div class="kpi-val" style="color:{RH_GREEN}">{wy}</div>
            <div class="kpi-lbl">Wyckoff Accumulation</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#5DA9C7">+{avg_rs}%</div>
            <div class="kpi-lbl">Avg RS vs Nifty</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="section-head">
        <span class="section-head-label">Dispatch 01</span>
        Stocks Approaching Resistance
    </div>""", unsafe_allow_html=True)

    if not results:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-orn">∅</div>
            <div class="empty-state-text">No approaching setups</div>
            <div class="empty-state-sub">All 8 CMT filters applied — market may be thin today</div>
        </div>""", unsafe_allow_html=True)
    else:
        rows_html = ""
        for r in results:
            sc = SECTOR_COLORS.get(r["sector"], RH_MUTED)
            dc = RH_GREEN if r["day_chg"] >= 0 else RH_RED
            pcls = {"HOT": "pill-hot", "WARM": "pill-warm", "CLOSE": "pill-cool"}[r["tier"]]
            plbl = {"HOT": "◆ HOT", "WARM": "◇ WARM", "CLOSE": "◌ CLOSE"}[r["tier"]]
            prox_pct = max(0, min(100, round((1 - r["gap_atr"] / max(threshold_atr, 0.1)) * 100)))
            pcol = RH_RED if r["tier"] == "HOT" else RH_GOLD_LIGHT if r["tier"] == "WARM" else "#8E6FD8"
            wy_badge = "◉" if r["wyckoff_ok"] else "◎"
            wy_col   = RH_GREEN if r["wyckoff_ok"] else RH_MUTED
            rs_col   = RH_GREEN if r["rs_diff"] > 5 else RH_GOLD_LIGHT if r["rs_diff"] > 0 else RH_MUTED

            rows_html += f"""
            <div class="tbl-row">
                <span class="sym">{r['symbol']}</span>
                <span><span class="pill {pcls}">{plbl}</span></span>
                <span class="mono">₹{r['close']:,}<br>
                    <span style="font-size:0.68rem; color:{dc}; font-weight:500;">
                        {'+' if r['day_chg']>=0 else ''}{r['day_chg']}%</span>
                </span>
                <span class="mono">₹{r['swing_high']:,}<br>
                    <span style="font-size:0.62rem; color:{RH_MUTED};">{r['sh_date']}</span>
                </span>
                <span>
                    <div class="prox">
                        <div class="prox-bg">
                            <div class="prox-fill"
                                 style="width:{prox_pct}%; background:{pcol};
                                        box-shadow:0 0 6px {pcol}60;"></div>
                        </div>
                        <span style="font-family:IBM Plex Mono; font-size:0.7rem;
                                     color:{pcol}; min-width:48px; font-weight:500;">
                            {r['gap_atr']}σ
                        </span>
                    </div>
                    <div style="font-size:0.58rem; color:{RH_MUTED};
                                font-family:IBM Plex Mono; margin-top:3px;">
                        {r['gap_pct']}% · pb {r['pullback']}% · base σ{r['base_sd']}%
                    </div>
                </span>
                <span style="font-family:IBM Plex Mono; font-size:0.74rem; color:{wy_col};">
                    {wy_badge} {r['vol_ratio']}×
                    <div style="font-size:0.58rem; color:{RH_MUTED}; margin-top:2px;">
                        U/D {r['wyckoff_ratio']}
                    </div>
                </span>
                <span style="font-family:IBM Plex Mono; font-size:0.7rem;
                             color:{rs_col}; font-weight:500;">
                    {'+' if r['rs_diff']>=0 else ''}{r['rs_diff']}%
                    <div style="font-size:0.56rem; color:{RH_MUTED}; font-weight:400;
                                text-transform:uppercase; letter-spacing:0.1em;">
                        RS · ADX {r['adx']}
                    </div>
                </span>
                <span>
                    <span class="sec" style="background:{sc}18; color:{sc};
                                              border:1px solid {sc}50;">
                        {r['sector']}
                    </span>
                    <div style="font-family:IBM Plex Mono; font-size:0.58rem;
                                color:{RH_MUTED}; margin-top:4px;">
                        ₹{r['mcap_cr']:,}Cr
                    </div>
                </span>
            </div>"""

        st.markdown(f"""
        <div class="tbl">
          <div class="tbl-hdr">
            <span>Symbol</span><span>Tier</span><span>Close</span>
            <span>Resistance</span><span>Distance</span>
            <span>Vol / Wyckoff</span><span>RS / ADX</span><span>Sector</span>
          </div>
          <div class="scroll-body">{rows_html}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="section-head">
            <span class="section-head-label">Visual</span>
            Chart Detail
        </div>""", unsafe_allow_html=True)
        sel_sym = st.selectbox(
            "Select stock", [r["symbol"] for r in results],
            key="sel_t1", label_visibility="collapsed"
        )
        if sel_sym:
            s = next(r for r in results if r["symbol"] == sel_sym)
            render_chart(s)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Close",      f"₹{s['close']:,}",       f"{s['day_chg']}%")
            c2.metric("Resistance", f"₹{s['swing_high']:,}",  f"{s['gap_atr']}σ")
            c3.metric("Pullback",   f"{s['pullback']}%",      f"base σ{s['base_sd']}%")
            c4.metric("RS (3M)",    f"+{s['rs_diff']}%",      f"ADX {s['adx']}")
            c5.metric(
                "Wyckoff",
                "Accumulation" if s['wyckoff_ok'] else "Weak",
                f"U/D {s['wyckoff_ratio']}"
            )


# ═══════════════════════════════════════════════════════════════
#  TAB 2 — RECENT BREAKOUTS
# ═══════════════════════════════════════════════════════════════
with tab2:
    bos = st.session_state.sw_breakouts or []
    total_b = len(bos)
    today_b = sum(1 for b in bos if b["days_ago"] == 1)
    conf_b  = sum(1 for b in bos if b["confirmation"] in ("2-candle", "volume"))
    avg_bo  = round(sum(b["bo_pct"] for b in bos) / total_b, 2) if total_b else 0

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi"><div class="kpi-val" style="color:{RH_GOLD_LIGHT}">{total_b}</div>
            <div class="kpi-lbl">Breakouts</div></div>
        <div class="kpi"><div class="kpi-val" style="color:{RH_RED}">{today_b}</div>
            <div class="kpi-lbl">Today</div></div>
        <div class="kpi"><div class="kpi-val" style="color:{RH_GOLD_LIGHT}">{total_b - today_b}</div>
            <div class="kpi-lbl">Last {days_back}d</div></div>
        <div class="kpi"><div class="kpi-val" style="color:{RH_GREEN}">{conf_b}</div>
            <div class="kpi-lbl">Confirmed</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#5DA9C7">+{avg_bo}%</div>
            <div class="kpi-lbl">Avg Breakout</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="section-head">
        <span class="section-head-label">Dispatch 02</span>
        Confirmed Breakouts
    </div>""", unsafe_allow_html=True)

    if not bos:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-orn">∅</div>
            <div class="empty-state-text">No confirmed breakouts</div>
            <div class="empty-state-sub">Requires 2-candle hold or 1.5× volume</div>
        </div>""", unsafe_allow_html=True)
    else:
        bo_html = ""
        for b in bos:
            sc = SECTOR_COLORS.get(b["sector"], RH_MUTED)
            dc = RH_GREEN if b["day_chg"] >= 0 else RH_RED
            day_pill = "pill-hot" if b["days_ago"] == 1 else "pill-warm"
            conf = b["confirmation"]
            conf_badge = ("◉ 2-candle" if conf == "2-candle"
                          else "◉ volume" if conf == "volume"
                          else "◎ pending")
            conf_col = RH_GREEN if conf != "pending" else RH_GOLD_LIGHT
            rs_col = RH_GREEN if b["rs_diff"] > 5 else RH_GOLD_LIGHT if b["rs_diff"] > 0 else RH_MUTED

            bo_html += f"""
            <div class="tbl-row">
                <span class="sym">{b['symbol']}</span>
                <span><span class="pill {day_pill}">{b['label']}</span></span>
                <span class="mono">₹{b['close']:,}<br>
                    <span style="font-size:0.68rem; color:{dc}; font-weight:500;">
                        {'+' if b['day_chg']>=0 else ''}{b['day_chg']}%</span>
                </span>
                <span class="mono">₹{b['broken_sh']:,}<br>
                    <span style="font-size:0.58rem; color:{RH_MUTED};">set {b['sh_date']}</span>
                </span>
                <span style="font-family:Fraunces,serif; font-size:1rem;
                             color:{RH_GREEN}; font-weight:700;">
                    +{b['bo_pct']}%
                    <div style="font-family:IBM Plex Mono; font-size:0.6rem;
                                color:{conf_col}; font-weight:500; margin-top:2px;">
                        {conf_badge}
                    </div>
                </span>
                <span style="font-family:IBM Plex Mono; font-size:0.74rem; color:{RH_TEXT};">
                    {b['vol_ratio']}×
                    <div style="font-size:0.56rem; color:{RH_MUTED}; margin-top:2px;">
                        ADX {b['adx']}
                    </div>
                </span>
                <span style="font-family:IBM Plex Mono; font-size:0.7rem;
                             color:{rs_col}; font-weight:500;">
                    +{b['rs_diff']}%
                    <div style="font-size:0.56rem; color:{RH_MUTED}; font-weight:400;
                                text-transform:uppercase; letter-spacing:0.1em;">RS</div>
                </span>
                <span>
                    <span class="sec" style="background:{sc}18; color:{sc};
                                              border:1px solid {sc}50;">
                        {b['sector']}
                    </span>
                    <div style="font-family:IBM Plex Mono; font-size:0.58rem;
                                color:{RH_MUTED}; margin-top:4px;">
                        ₹{b['mcap_cr']:,}Cr
                    </div>
                </span>
            </div>"""

        st.markdown(f"""
        <div class="tbl">
          <div class="tbl-hdr">
            <span>Symbol</span><span>When</span><span>Close</span>
            <span>Broken Level</span><span>Breakout</span>
            <span>Volume</span><span>RS</span><span>Sector</span>
          </div>
          <div class="scroll-body">{bo_html}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="section-head">
            <span class="section-head-label">Visual</span>
            Chart Detail
        </div>""", unsafe_allow_html=True)
        sel2 = st.selectbox(
            "Select stock", [b["symbol"] for b in bos],
            key="sel_t2", label_visibility="collapsed"
        )
        if sel2:
            b = next(x for x in bos if x["symbol"] == sel2)
            render_chart(b)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Close",    f"₹{b['close']:,}",     f"{b['day_chg']}%")
            c2.metric("Broke",    f"₹{b['broken_sh']:,}", b['label'])
            c3.metric("Breakout", f"+{b['bo_pct']}%",     b["confirmation"])
            c4.metric("Volume",   f"{b['vol_ratio']}×",   f"ADX {b['adx']}")
            c5.metric("RS (3M)",  f"+{b['rs_diff']}%")


# ═══════════════════════════════════════════════════════════════
#  TAB 3 — VALIDATE LOGIC (BACKTEST)
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div style='background:{RH_SURFACE}; border:1px solid {RH_BORDER};
                border-left:3px solid {RH_GOLD_DIM}; padding:16px 20px;
                margin-bottom:22px;'>
        <div style='font-family:Fraunces,serif; font-size:1rem; font-weight:700;
                    color:{RH_GOLD_LIGHT}; margin-bottom:8px;'>
            Validating the Screener's Historical Accuracy
        </div>
        <div style='font-family:IBM Plex Mono,monospace; font-size:0.78rem;
                    color:{RH_TEXT}; line-height:1.7; letter-spacing:0.04em;'>
            Select any stock. The engine walks through 2 years of history, flags every
            breakout the screener would have caught, and marks each as
            <span style='color:{RH_GREEN};'>Real</span>,
            <span style='color:{RH_GOLD_LIGHT};'>Weak</span>, or
            <span style='color:{RH_RED};'>False</span>.
        </div>
    </div>""", unsafe_allow_html=True)

    all_symbols = sorted([s.replace(".NS", "") for s in WATCHLIST])
    bt_symbol = st.selectbox(
        "Stock to validate", all_symbols, key="bt_sym",
        index=all_symbols.index("TITAN") if "TITAN" in all_symbols else 0
    )
    bt_run = st.button("VALIDATE", key="bt_btn", use_container_width=True)

    if bt_run:
        with st.spinner(f"Walking through 2 years of {bt_symbol}..."):
            try:
                import yfinance as yf
                df = yf.Ticker(f"{bt_symbol}.NS").history(period="2y", interval="1d")
                if df.empty:
                    st.error("No data available.")
                    st.stop()
                signals = []
                checked = set()
                closes  = df['Close'].values
                min_bars = lookback * 2 + 30
                for i in range(min_bars, len(df)):
                    df_s = df.iloc[:i]
                    sh_s, _ = find_swings(df_s, lookback)
                    close_now  = float(df_s['Close'].iloc[-1])
                    prev_close = float(df_s['Close'].iloc[-2])
                    if i >= 50:
                        ma50 = float(df_s['Close'].iloc[-50:].mean())
                        if close_now < ma50 * 0.97:
                            continue
                    val = find_valid_resistance(df_s, sh_s, threshold_atr_mult=10.0)
                    if not val:
                        continue
                    sh_price = val["price"]
                    key = round(sh_price, 1)
                    if key in checked:
                        continue
                    if prev_close <= sh_price < close_now:
                        checked.add(key)
                        future = closes[i: i + 10]
                        if len(future) > 0:
                            max_gain = round((future.max() - sh_price) / sh_price * 100, 2)
                            min_draw = round((future.min() - sh_price) / sh_price * 100, 2)
                            if max_gain >= 3:
                                result, tag = f"Real breakout (+{max_gain}% in 10d)", "real"
                            elif max_gain >= 1:
                                result, tag = f"Weak follow-through (peak +{max_gain}%)", "weak"
                            else:
                                result, tag = f"False breakout ({min_draw}% to +{max_gain}%)", "false"
                        else:
                            result, tag = "Too recent", "recent"
                        signals.append({
                            "Date": df_s.index[-1].strftime("%d %b '%y"),
                            "Broke Above": f"₹{sh_price:,}",
                            "Set On": val["date"].strftime("%d %b '%y"),
                            "Pullback": f"{val['pullback_pct']}%",
                            "Gap (ATR)": f"{val['gap_atr']}σ",
                            "Base SD": f"{val['base_sd_pct']}%",
                            "Outcome": result, "_tag": tag,
                        })

                total = len(signals)
                real  = sum(1 for s in signals if s["_tag"] == "real")
                weak  = sum(1 for s in signals if s["_tag"] == "weak")
                false = sum(1 for s in signals if s["_tag"] == "false")
                acc   = round(real / total * 100, 1) if total else 0

                if acc >= 70:
                    verdict, vc = "LOGIC IS SOLID", RH_GREEN
                elif acc >= 50:
                    verdict, vc = "LOGIC IS DECENT", RH_GOLD_LIGHT
                elif total == 0:
                    verdict, vc = "NO BREAKOUTS IN 2Y", RH_MUTED
                else:
                    verdict, vc = "LOGIC NEEDS WORK", RH_RED

                st.markdown("""<div class="section-head">
                    <span class="section-head-label">Report</span>
                    Signal Accuracy
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="kpi-row">
                    <div class="kpi"><div class="kpi-val" style="color:{RH_GOLD_LIGHT}">{total}</div>
                        <div class="kpi-lbl">Detected</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:{RH_GREEN}">{real}</div>
                        <div class="kpi-lbl">Real</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:{RH_GOLD_LIGHT}">{weak}</div>
                        <div class="kpi-lbl">Weak</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:{RH_RED}">{false}</div>
                        <div class="kpi-lbl">False</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:{vc}">{acc}%</div>
                        <div class="kpi-lbl">{verdict}</div></div>
                </div>""", unsafe_allow_html=True)

                if signals:
                    st.markdown("""<div class="section-head">
                        <span class="section-head-label">Detail</span>
                        Every Historical Breakout
                    </div>""", unsafe_allow_html=True)
                    for s in signals:
                        s.pop("_tag", None)
                    df_sig = pd.DataFrame(signals)
                    st.dataframe(
                        df_sig, use_container_width=True, hide_index=True,
                        height=min(500, 42 * len(signals) + 45)
                    )

                    st.markdown("""<div class="section-head">
                        <span class="section-head-label">Visual</span>
                        Breakouts Plotted on Chart
                    </div>""", unsafe_allow_html=True)
                    fig = make_subplots(rows=1, cols=1)
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'],
                        increasing_line_color=RH_GREEN, decreasing_line_color=RH_RED,
                        increasing_fillcolor=RH_GREEN, decreasing_fillcolor=RH_RED,
                        name="Price", line_width=1
                    ))
                    bo_dates, bo_prices, bo_colors = [], [], []
                    for s in signals:
                        try:
                            dt = datetime.strptime(s["Date"], "%d %b '%y")
                            bo_dates.append(dt)
                            bo_prices.append(float(s["Broke Above"].replace("₹", "").replace(",", "")))
                            if "Real" in s["Outcome"]:    bo_colors.append(RH_GREEN)
                            elif "Weak" in s["Outcome"]:  bo_colors.append(RH_GOLD_LIGHT)
                            else:                          bo_colors.append(RH_RED)
                        except Exception:
                            continue
                    if bo_dates:
                        fig.add_trace(go.Scatter(
                            x=bo_dates, y=bo_prices, mode='markers',
                            marker=dict(symbol='diamond', size=14, color=bo_colors,
                                         line=dict(color=RH_BG, width=1)),
                            name="Signals"
                        ))
                    fig.update_layout(
                        height=480, plot_bgcolor=RH_BG, paper_bgcolor=RH_BG,
                        font=dict(family='IBM Plex Mono', color=RH_MUTED, size=10),
                        xaxis_rangeslider_visible=False, showlegend=False,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    fig.update_xaxes(gridcolor='rgba(58,53,48,0.5)', zeroline=False,
                                      linecolor=RH_BORDER)
                    fig.update_yaxes(gridcolor='rgba(58,53,48,0.5)', zeroline=False,
                                      linecolor=RH_BORDER)
                    st.plotly_chart(fig, use_container_width=True,
                                     config={"displayModeBar": False})

                    st.markdown(f"""
                    <div style='font-family:IBM Plex Mono,monospace; font-size:0.65rem;
                                color:{RH_MUTED}; margin-top:8px; line-height:2;
                                letter-spacing:0.06em;'>
                        ◆ <span style='color:{RH_GREEN};'>GREEN</span> — real (≥3% in 10d)  ·
                        ◆ <span style='color:{RH_GOLD_LIGHT};'>GOLD</span> — weak follow-through  ·
                        ◆ <span style='color:{RH_RED};'>RED</span> — false breakout
                    </div>""", unsafe_allow_html=True)
                else:
                    st.info("No breakouts detected — the stock had no clean setups in 2 years.")
            except Exception as e:
                st.error(f"Validation failed: {e}")


st.markdown("<br>", unsafe_allow_html=True)
if st.button("← BACK TO HUB", key="back_bottom", use_container_width=True):
    st.switch_page("Home.py")

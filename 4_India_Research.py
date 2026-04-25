"""
Scanner 04 — India Custom Research
Fundamentals screener over 700+ NSE tickers — reads from data/companies.json
(produced by the india-research repo's GitHub Actions pipeline).

The pipeline runs monthly via Actions. This UI consumes the JSON snapshot.
"""
import streamlit as st
import pandas as pd
import json
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import (
    apply_theme, render_header,
    RH_GOLD, RH_GOLD_LIGHT, RH_GOLD_DIM, RH_RED, RH_GREEN,
    RH_BG, RH_SURFACE, RH_TEXT, RH_MUTED, RH_BORDER
)

st.set_page_config(layout="wide", page_title="RH | India Research")
apply_theme()
render_header("Scanner 04 · India Custom Research")


# ─────────────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_companies():
    """Load the JSON snapshot produced by the india-research pipeline."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(root, "data", "companies.json"),
        os.path.join(root, "companies.json"),
    ]
    json_path = next((p for p in candidates if os.path.exists(p)), None)
    if not json_path:
        return pd.DataFrame(), None

    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        # Handle both "list of records" and "dict of ticker -> record" formats
        if isinstance(data, dict):
            records = []
            for ticker, payload in data.items():
                if isinstance(payload, dict):
                    payload['Ticker'] = ticker
                    records.append(payload)
            df = pd.DataFrame(records)
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            return pd.DataFrame(), None

        # Try to find a meta file with last-update timestamp
        meta_path = os.path.join(os.path.dirname(json_path), "meta.json")
        meta = None
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
            except Exception:
                pass

        return df, meta
    except Exception as e:
        st.error(f"Could not parse companies.json: {e}")
        return pd.DataFrame(), None


df, meta = load_companies()


# ─────────────────────────────────────────────────────
#  EMPTY STATE — first-time setup
# ─────────────────────────────────────────────────────
if df.empty:
    st.markdown(f"""
    <div style='background:{RH_SURFACE}; border:1px solid {RH_BORDER};
                padding:36px 28px; margin:24px 0; text-align:center;'>
        <div style='font-family:Fraunces, serif; font-size:48px; font-weight:900;
                    color:{RH_GOLD_DIM}; line-height:1; margin-bottom:8px;'>04</div>
        <div style='font-family:IBM Plex Mono, monospace; font-size:11px; letter-spacing:0.2em;
                    color:{RH_GOLD_LIGHT}; text-transform:uppercase; margin-bottom:18px;'>
            India Custom Research
        </div>
        <div style='font-family:IBM Plex Mono, monospace; font-size:13px; color:{RH_TEXT};
                    line-height:1.7; max-width:520px; margin:0 auto 18px;'>
            Awaiting data snapshot.
        </div>
        <div style='font-family:IBM Plex Mono, monospace; font-size:11px; color:{RH_MUTED};
                    line-height:1.7; max-width:560px; margin:0 auto;'>
            This scanner reads <code style='color:{RH_GOLD_LIGHT};'>data/companies.json</code>,
            produced by the india-research GitHub Actions pipeline.
            Trigger the workflow once (Actions → Data refresh → Run workflow) — it takes ~25 minutes
            for the first full fetch. After that the file refreshes monthly on its own.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.page_link("Home.py", label="← Back to scanner hub", use_container_width=True)
    st.stop()


# ─────────────────────────────────────────────────────
#  NORMALIZE COLUMNS
#  The JSON schema may vary; we look for common field names.
# ─────────────────────────────────────────────────────
def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


col_name    = find_col(df, ['Name', 'name', 'company_name', 'longName'])
col_sector  = find_col(df, ['Sector', 'sector'])
col_industry = find_col(df, ['Industry', 'industry'])
col_price   = find_col(df, ['Price', 'price', 'currentPrice', 'CMP', 'cmp'])
col_mcap    = find_col(df, ['MarketCap', 'market_cap', 'marketCap', 'Market Cap'])
col_pe      = find_col(df, ['PE', 'pe', 'trailingPE', 'P/E'])
col_pb      = find_col(df, ['PB', 'pb', 'priceToBook', 'P/B'])
col_roe     = find_col(df, ['ROE', 'roe', 'returnOnEquity'])
col_de      = find_col(df, ['DebtToEquity', 'debt_to_equity', 'debtToEquity', 'D/E'])
col_div     = find_col(df, ['DividendYield', 'dividend_yield', 'dividendYield'])
col_52h     = find_col(df, ['52W High', 'fiftyTwoWeekHigh', '52w_high'])
col_52l     = find_col(df, ['52W Low', 'fiftyTwoWeekLow', '52w_low'])

# ─────────────────────────────────────────────────────
#  KPI ROW
# ─────────────────────────────────────────────────────
total = len(df)
sectors_count = df[col_sector].nunique() if col_sector else 0
last_update = "—"
if meta and 'last_update' in meta:
    last_update = meta['last_update']
elif meta and 'financials' in meta:
    last_update = meta['financials']

c1, c2, c3, c4 = st.columns(4)
c1.metric("Companies tracked", f"{total:,}")
c2.metric("Sectors covered", sectors_count)
if col_mcap:
    avg_mcap = pd.to_numeric(df[col_mcap], errors='coerce').mean()
    c3.metric("Avg market cap",
              f"₹{avg_mcap/1e7:,.0f} Cr" if pd.notna(avg_mcap) else "—")
else:
    c3.metric("Avg market cap", "—")
c4.metric("Last refresh", last_update if last_update != "—" else "Manual")

st.divider()


# ─────────────────────────────────────────────────────
#  FILTERS
# ─────────────────────────────────────────────────────
with st.expander("FILTERS", expanded=True):
    fc1, fc2 = st.columns(2)

    with fc1:
        sel_sectors = []
        if col_sector:
            sectors = sorted(df[col_sector].dropna().unique().tolist())
            sel_sectors = st.multiselect("Sector", options=sectors)

        if col_pe:
            pe_max = st.slider("Max P/E ratio", 0, 200, 50,
                                help="Filters out tickers above this P/E")
        else:
            pe_max = None

    with fc2:
        if col_mcap:
            mcap_min_cr = st.number_input("Min market cap (₹ Cr)",
                                            min_value=0, value=500, step=100)
        else:
            mcap_min_cr = None

        if col_roe:
            roe_min = st.slider("Min ROE (%)", 0, 50, 0,
                                 help="Returns ≥ this ROE")
        else:
            roe_min = None


# ─────────────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────────────
filtered = df.copy()

if sel_sectors and col_sector:
    filtered = filtered[filtered[col_sector].isin(sel_sectors)]

if pe_max is not None and col_pe:
    pe_numeric = pd.to_numeric(filtered[col_pe], errors='coerce')
    filtered = filtered[pe_numeric.between(0, pe_max)]

if mcap_min_cr is not None and col_mcap:
    mcap_numeric = pd.to_numeric(filtered[col_mcap], errors='coerce')
    filtered = filtered[mcap_numeric >= mcap_min_cr * 1e7]

if roe_min is not None and roe_min > 0 and col_roe:
    roe_numeric = pd.to_numeric(filtered[col_roe], errors='coerce')
    # ROE may be in fraction (0.18) or percent (18.0). Normalize.
    if roe_numeric.dropna().abs().median() < 1.5:
        roe_numeric = roe_numeric * 100
    filtered = filtered[roe_numeric >= roe_min]

st.markdown(
    f"<div style='color:{RH_GOLD_LIGHT}; font-family:IBM Plex Mono; font-size:11px; "
    f"letter-spacing:0.12em; text-transform:uppercase; padding:8px 0;'>"
    f"<strong style='color:{RH_TEXT}; font-weight:500;'>{len(filtered):,}</strong> "
    f"<span style='color:{RH_MUTED};'>matches · {len(df):,} total</span></div>",
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────────────
#  RESULTS TABLE
# ─────────────────────────────────────────────────────
st.subheader("Screener Results")

if filtered.empty:
    st.info("No companies match the selected filters. Try widening the criteria.")
else:
    display_cols = [c for c in [
        'Ticker', col_name, col_sector, col_industry,
        col_price, col_mcap, col_pe, col_pb, col_roe, col_de, col_div
    ] if c is not None and c in filtered.columns]

    show_df = filtered[display_cols].copy()

    # Rename columns for display
    rename_map = {}
    if col_name:    rename_map[col_name] = 'Name'
    if col_sector:  rename_map[col_sector] = 'Sector'
    if col_industry: rename_map[col_industry] = 'Industry'
    if col_price:   rename_map[col_price] = 'CMP'
    if col_mcap:    rename_map[col_mcap] = 'M.Cap'
    if col_pe:      rename_map[col_pe] = 'P/E'
    if col_pb:      rename_map[col_pb] = 'P/B'
    if col_roe:     rename_map[col_roe] = 'ROE'
    if col_de:      rename_map[col_de] = 'D/E'
    if col_div:     rename_map[col_div] = 'Div Yield'
    show_df = show_df.rename(columns=rename_map)

    # Format columns that exist
    fmt = {}
    if 'CMP' in show_df.columns: fmt['CMP'] = '{:,.2f}'
    if 'P/E' in show_df.columns: fmt['P/E'] = '{:.1f}'
    if 'P/B' in show_df.columns: fmt['P/B'] = '{:.2f}'
    if 'ROE' in show_df.columns: fmt['ROE'] = '{:.1f}'
    if 'D/E' in show_df.columns: fmt['D/E'] = '{:.2f}'
    if 'Div Yield' in show_df.columns: fmt['Div Yield'] = '{:.2f}%'
    if 'M.Cap' in show_df.columns:
        # Convert to crores for readability
        show_df['M.Cap'] = pd.to_numeric(show_df['M.Cap'], errors='coerce') / 1e7
        fmt['M.Cap'] = '₹{:,.0f} Cr'

    sort_col = 'M.Cap' if 'M.Cap' in show_df.columns else show_df.columns[0]
    show_df = show_df.sort_values(by=sort_col, ascending=False).reset_index(drop=True)

    st.dataframe(
        show_df.style.format(fmt, na_rep="—"),
        use_container_width=True, hide_index=True, height=500
    )

    # Quick CSV export
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "DOWNLOAD AS CSV",
        data=csv,
        file_name="india_research_filtered.csv",
        mime="text/csv",
    )

st.markdown("<br>", unsafe_allow_html=True)
st.page_link("Home.py", label="← Back to scanner hub", use_container_width=True)

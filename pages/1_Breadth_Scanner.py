"""
Scanner 01 — Nifty 500 Breadth
Synchronized price + breadth indicator with full zoom & range controls.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import (
    apply_theme, render_header,
    RH_GOLD, RH_GOLD_LIGHT, RH_GOLD_DIM, RH_RED, RH_GREEN,
    RH_BG, RH_SURFACE, RH_TEXT, RH_MUTED, RH_BORDER
)

st.set_page_config(layout="wide", page_title="RH | Breadth Scanner")
apply_theme()
render_header("Scanner 01 · Nifty 500 Breadth")


@st.cache_data(ttl=3600)
def load_data():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(root, "data", "Nifty500_Master_Data.csv"),
        os.path.join(root, "Nifty500_Master_Data.csv"),
        "Nifty500_Master_Data.csv",
    ]
    csv_path = next((p for p in candidates if os.path.exists(p)), None)
    if not csv_path:
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values(by='DATE').reset_index(drop=True)
    df['NIFTY_500_CLOSE'] = df['NIFTY_500_CLOSE'].ffill()
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    df['NIFTY_200_SMA'] = df['NIFTY_500_CLOSE'].rolling(window=200, min_periods=1).mean()

    if 'PCT_ABOVE_200SMA' not in df.columns:
        df['PCT_ABOVE_200SMA'] = 0.0
        df['ABOVE_200SMA'] = 0
    return df


df = load_data()

if df.empty:
    st.error("Data not found. Place `Nifty500_Master_Data.csv` at the project root or in `/data`.")
    if st.button("← BACK TO HUB", key="back_top"):
        st.switch_page("Home.py")
    st.stop()

latest, prev = df.iloc[-1], df.iloc[-2]

# ── KPI ROW ──
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Nifty 500 Index", f"{latest['NIFTY_500_CLOSE']:,.2f}",
              f"{latest['NIFTY_500_CLOSE'] - prev['NIFTY_500_CLOSE']:,.2f}")
with c2:
    st.metric("New 52W Highs", int(latest['52W_HIGH']),
              int(latest['52W_HIGH'] - prev['52W_HIGH']))
with c3:
    st.metric("New 52W Lows", int(latest['52W_LOW']),
              int(latest['52W_LOW'] - prev['52W_LOW']), delta_color="inverse")
with c4:
    st.metric("Net Breadth (H−L)", int(latest['Net_Highs']),
              int(latest['Net_Highs'] - prev['Net_Highs']))
with c5:
    st.metric("Stocks > 200 SMA", f"{latest['PCT_ABOVE_200SMA']:.1f}%",
              f"{latest['PCT_ABOVE_200SMA'] - prev['PCT_ABOVE_200SMA']:.1f}%")

st.divider()

# ── CONTROLS ──
ctrl1, ctrl2 = st.columns([2, 1])
with ctrl1:
    chart_choice = st.radio(
        "Lower Indicator",
        ["Net Highs (H-L)", "Stocks > 200 SMA (%)", "52-Week Highs", "52-Week Lows"],
        horizontal=True, key="indicator"
    )
with ctrl2:
    split_ratio = st.slider("Chart Split (Price Area %)", 40, 90, 70, 5)

if 'range_days' not in st.session_state:
    st.session_state.range_days = 90

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
st.markdown(
    f"<div style='font-size:9px; color:{RH_MUTED}; letter-spacing:0.15em; "
    f"text-transform:uppercase; margin-bottom:6px;'>Time Range</div>",
    unsafe_allow_html=True
)

range_options = [
    ("1W", 7), ("1M", 30), ("3M", 90), ("6M", 180),
    ("1Y", 365), ("2Y", 730), ("5Y", 1825), ("ALL", None)
]
range_cols = st.columns(len(range_options))
for i, (label, days) in enumerate(range_options):
    with range_cols[i]:
        is_active = st.session_state.range_days == days
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"r_{label}", use_container_width=True, type=btn_type):
            st.session_state.range_days = days
            st.rerun()

end_date = df['DATE'].max()
if st.session_state.range_days is None:
    start_date = df['DATE'].min()
else:
    start_date = end_date - timedelta(days=st.session_state.range_days)
    start_date = max(start_date, df['DATE'].min())

# ── CHART ──
top_h = split_ratio / 100.0
bot_h = 1.0 - top_h
df_plot = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)].copy()

price_min = df_plot['NIFTY_500_CLOSE'].min() * 0.985
price_max = df_plot['NIFTY_500_CLOSE'].max() * 1.015

fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    row_heights=[top_h, bot_h], vertical_spacing=0.04
)

fig.add_trace(go.Scattergl(
    x=df_plot['DATE'], y=df_plot['NIFTY_500_CLOSE'], name="Nifty 500",
    line=dict(color=RH_GOLD_LIGHT, width=1.8),
    fill='tozeroy', fillcolor='rgba(184,136,26,0.06)',
    hovertemplate='<b>%{y:,.2f}</b><extra></extra>'
), row=1, col=1)

fig.add_trace(go.Scattergl(
    x=df_plot['DATE'], y=df_plot['NIFTY_200_SMA'], name="200 SMA",
    line=dict(color=RH_RED, width=1.2, dash='dot'),
    hovertemplate='SMA <b>%{y:,.2f}</b><extra></extra>'
), row=1, col=1)

if chart_choice == "Net Highs (H-L)":
    fig.add_trace(go.Scattergl(
        x=df_plot['DATE'], y=df_plot['Net_Highs'], name="Net Highs",
        line=dict(color=RH_GOLD, width=1.5),
        fill='tozeroy', fillcolor='rgba(184,136,26,0.07)',
        hovertemplate='Net <b>%{y}</b><extra></extra>'
    ), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color=RH_RED, line_width=1, row=2, col=1)
    ind_label = "NET HIGHS (H−L)"
elif chart_choice == "Stocks > 200 SMA (%)":
    fig.add_trace(go.Scattergl(
        x=df_plot['DATE'], y=df_plot['PCT_ABOVE_200SMA'], name="% > 200 SMA",
        line=dict(color="#8E6FD8", width=1.5),
        fill='tozeroy', fillcolor='rgba(142,111,216,0.07)',
        hovertemplate='<b>%{y:.1f}%</b><extra></extra>'
    ), row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color=RH_MUTED, line_width=1, row=2, col=1)
    ind_label = "% STOCKS > 200 SMA"
elif chart_choice == "52-Week Highs":
    fig.add_trace(go.Scattergl(
        x=df_plot['DATE'], y=df_plot['52W_HIGH'], name="Highs",
        line=dict(color=RH_GREEN, width=1.5),
        fill='tozeroy', fillcolor='rgba(46,204,113,0.07)',
        hovertemplate='Highs <b>%{y}</b><extra></extra>'
    ), row=2, col=1)
    ind_label = "52-WEEK HIGHS"
else:
    fig.add_trace(go.Scattergl(
        x=df_plot['DATE'], y=df_plot['52W_LOW'], name="Lows",
        line=dict(color=RH_RED, width=1.5),
        fill='tozeroy', fillcolor='rgba(231,76,60,0.07)',
        hovertemplate='Lows <b>%{y}</b><extra></extra>'
    ), row=2, col=1)
    ind_label = "52-WEEK LOWS"

fig.update_layout(
    height=700, plot_bgcolor=RH_BG, paper_bgcolor=RH_BG,
    font=dict(color=RH_TEXT, family="IBM Plex Mono", size=11),
    hovermode="x unified",
    hoverlabel=dict(bgcolor=RH_SURFACE, bordercolor=RH_GOLD_DIM,
                    font=dict(family="IBM Plex Mono", color=RH_TEXT, size=11)),
    showlegend=False, margin=dict(l=10, r=10, t=20, b=10),
    dragmode="zoom",
    transition=dict(duration=400, easing='cubic-in-out'),
)

fig.update_xaxes(
    showgrid=True, gridwidth=0.5, gridcolor='rgba(58,53,48,0.4)',
    showspikes=True, spikecolor=RH_GOLD_DIM, spikesnap="cursor",
    spikemode="across", spikethickness=1, spikedash='solid',
    tickfont=dict(color=RH_MUTED, size=9, family='IBM Plex Mono'),
    zeroline=False, linecolor=RH_BORDER, linewidth=1,
    rangeslider=dict(visible=True, thickness=0.06, bgcolor=RH_SURFACE,
                     bordercolor=RH_GOLD_DIM, borderwidth=1),
    row=2, col=1
)
fig.update_xaxes(
    showgrid=True, gridwidth=0.5, gridcolor='rgba(58,53,48,0.4)',
    showspikes=True, spikecolor=RH_GOLD_DIM, spikesnap="cursor",
    spikemode="across", spikethickness=1, spikedash='solid',
    showticklabels=False, zeroline=False, linecolor=RH_BORDER, linewidth=1,
    row=1, col=1
)
fig.update_yaxes(
    showgrid=True, gridwidth=0.5, gridcolor='rgba(58,53,48,0.4)',
    showspikes=True, spikecolor=RH_GOLD_DIM, spikethickness=1,
    tickfont=dict(color=RH_MUTED, size=9, family='IBM Plex Mono'),
    zeroline=False, linecolor=RH_BORDER, linewidth=1
)
fig.update_yaxes(range=[price_min, price_max], row=1, col=1)

fig.add_annotation(
    text=ind_label, xref="paper", yref="paper",
    x=0, y=bot_h + 0.005, xanchor='left', yanchor='bottom', showarrow=False,
    font=dict(family='IBM Plex Mono', size=9, color=RH_GOLD_DIM),
)

st.plotly_chart(
    fig, use_container_width=True,
    config={
        'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'toggleSpikelines',
                                   'hoverCompareCartesian', 'hoverClosestCartesian'],
        'doubleClick': 'reset+autosize',
        'showAxisDragHandles': True, 'showAxisRangeEntryBoxes': False,
    }
)

st.markdown(
    f"<div style='font-size:9px; color:{RH_MUTED}; letter-spacing:0.1em; "
    f"text-transform:uppercase; margin-top:-8px; padding:6px 0 12px; "
    f"border-bottom:1px solid {RH_BORDER};'>"
    f"◇ Scroll to zoom · Click-drag to select region · Double-click to reset · Drag the bottom strip to pan"
    f"</div>", unsafe_allow_html=True
)

# ── LEDGER ──
st.subheader("Historical Ledger")
display_df = df.sort_values(by='DATE', ascending=False).head(30).copy()
display_df['DATE'] = display_df['DATE'].dt.strftime('%d %b %Y')

st.dataframe(
    display_df[['DATE', 'NIFTY_500_CLOSE', '52W_HIGH', '52W_LOW',
                'Net_Highs', 'PCT_ABOVE_200SMA']],
    use_container_width=True, hide_index=True,
    column_config={
        "DATE": "Trading Date",
        "NIFTY_500_CLOSE": st.column_config.NumberColumn("Index Close", format="%.2f"),
        "52W_HIGH": st.column_config.NumberColumn("Highs"),
        "52W_LOW": st.column_config.NumberColumn("Lows"),
        "Net_Highs": st.column_config.NumberColumn("Net (H−L)"),
        "PCT_ABOVE_200SMA": st.column_config.NumberColumn("% > 200 SMA", format="%.1f%%")
    }
)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("← BACK TO HUB", use_container_width=True, key="back_bottom"):
    st.switch_page("Home.py")

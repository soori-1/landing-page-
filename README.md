# Right Horizons — Scanner Terminal

A unified multi-page Streamlit app housing all four quantitative scanners
under one terminal aesthetic: gold + dark, IBM Plex Mono + Fraunces.

```
right_horizons_terminal/
├── Home.py                          # Hub landing page (2×2 grid of scanners)
├── theme.py                         # Shared brand styling (imported by all pages)
├── requirements.txt
├── README.md
├── data/                            # Drop your CSVs and JSONs here
│   ├── Nifty500_Master_Data.csv     # Scanner 01 input
│   ├── historical_baseline.csv     # Scanner 02 input
│   └── companies.json               # Scanner 04 input
└── pages/
    ├── 1_Breadth_Scanner.py         # Nifty 500 breadth — synced price + indicators
    ├── 2_ETF_Screener.py            # Global ETF treemap
    ├── 3_Swing_Breakout.py          # NSE swing breakout detector
    └── 4_India_Research.py          # India fundamentals screener
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

The app opens at `http://localhost:8501`. Navigation is in the left sidebar —
click any scanner to drill in, click "← Back to scanner hub" inside any scanner
to return.

## Data files

Each scanner expects a specific input file, dropped under `data/` (or at the
project root — both locations are checked).

| Scanner | File | Source |
|---|---|---|
| 01 Breadth | `Nifty500_Master_Data.csv` | Your existing pipeline (DATE, NIFTY_500_CLOSE, 52W_HIGH, 52W_LOW, PCT_ABOVE_200SMA) |
| 02 ETF | `historical_baseline.csv` | Run `update_baseline.py` from the etf-screener-app repo |
| 03 Swing | _none_ — pulls live from yfinance | Edit `DEFAULT_TICKERS` in `pages/3_Swing_Breakout.py` to change universe |
| 04 India Research | `data/companies.json` | Run the india-research GitHub Action once (~25 min first run, monthly thereafter) |

Each page handles missing data gracefully — Scanner 04 shows an "awaiting data"
state if the JSON isn't there yet, with instructions for triggering the pipeline.

## Deploy to Streamlit Cloud

1. Push this entire folder to a GitHub repo
2. Go to share.streamlit.io → New app
3. Repository: your repo
4. Branch: `main`
5. Main file path: `Home.py`
6. Click Deploy

Streamlit auto-detects everything in `pages/` and adds it to the sidebar.

## Adding a new scanner

1. Create `pages/5_Your_Scanner.py` — copy `pages/1_Breadth_Scanner.py` as
   a template (it shows the standard imports and theme-call pattern).
2. Add a new entry to the `SCANNERS` list at the top of `Home.py`:
   ```python
   {
       "n": "05",
       "title": "Your Scanner",
       "tagline": "What it does",
       "desc": "Longer description.",
       "metrics": [
           ("Label A", "Value", "Delta", "up"),
           ("Label B", "Value", "Delta", "neutral"),
       ],
       "tags": ["Tag1", "Tag2"],
       "page": "5_Your_Scanner",   # matches the filename
       "status": "LIVE",
   }
   ```
3. Adjust `Home.py` row layout if you go past 4 scanners — change
   `cols = st.columns(2)` to a 3-column grid for 6+ scanners.

## Theming

All colors and fonts live in `theme.py`. The brand palette:

```python
RH_GOLD       = "#B8881A"   # Primary accent (price line, active states)
RH_GOLD_LIGHT = "#D4A830"   # Brand text, hover states
RH_GOLD_DIM   = "#7A5C10"   # Section labels, dimmed accents
RH_RED        = "#E74C3C"   # Negative deltas, SMA overlay
RH_GREEN      = "#2ECC71"   # Positive deltas, live indicator
RH_BG         = "#0D0D0D"   # Page background
RH_SURFACE    = "#161616"   # Card surfaces
RH_TEXT       = "#E8DFC8"   # Body text
RH_MUTED      = "#7A7060"   # Labels, axis ticks
```

Change a value in `theme.py` and every page updates.

## Architecture notes

- **`@st.cache_data`** is used aggressively — Scanner 02 caches yfinance hits
  for 10 minutes, Scanner 01 for 1 hour. Refresh buttons trigger `st.rerun()`
  to bypass the cache.
- **`st.session_state`** holds per-scanner state independently
  (`range_days`, `etf_df_merged`, `swing_results`) so navigating between pages
  doesn't lose your scan results.
- **`Scattergl` over `Scatter`** — the breadth chart uses WebGL for smooth
  zoom/pan on multi-year ranges.
- **Path resolution** — every page checks both `data/<file>` and `<file>` at
  the project root, so you can drop CSVs in either spot.

---

© Right Horizons Wealth Management — Internal quantitative tool

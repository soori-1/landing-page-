"""
update_breadth.py
-----------------
Runs daily via GitHub Actions after NSE market close.
Downloads Nifty 500 breadth data and saves to data/Nifty500_Master_Data.csv.

Can also be run manually:
    pip install yfinance pandas requests
    python update_breadth.py
"""
import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime, timedelta

OUTPUT_DIR  = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Nifty500_Master_Data.csv")
NSE_URL     = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
START_DATE  = "2000-01-01"


def get_tickers():
    """Fetch live Nifty 500 constituent list from NSE. Falls back to hardcoded list."""
    try:
        df = pd.read_csv(NSE_URL)
        tickers = [s.strip() + ".NS" for s in df['Symbol'].tolist()]
        print(f"  Loaded {len(tickers)} tickers from NSE")
        return tickers
    except Exception as e:
        print(f"  NSE URL failed ({e}), using hardcoded list")
        return FALLBACK_TICKERS


def run_update():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today    = datetime.now()
    # yfinance end date is EXCLUSIVE — pass tomorrow to include today's data
    end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"\n{'='*55}")
    print(f"  Nifty 500 Breadth Update — {today.strftime('%Y-%m-%d')}")
    print(f"{'='*55}")

    # ── STEP 1: Nifty 500 Index price ─────────────────────
    print("\n[1/4] Downloading Nifty 500 index price...")
    idx_raw = yf.download("^CRSLDX", start=START_DATE, end=end_date,
                           progress=False, auto_adjust=True)
    if idx_raw.empty:
        print("  ^CRSLDX failed, falling back to ^NSEI (Nifty 50)...")
        idx_raw = yf.download("^NSEI", start=START_DATE, end=end_date,
                               progress=False, auto_adjust=True)

    if isinstance(idx_raw.columns, pd.MultiIndex):
        nifty_series = idx_raw['Close'].iloc[:, 0]
    else:
        nifty_series = idx_raw['Close'] if 'Close' in idx_raw.columns else idx_raw.iloc[:, 0]

    nifty_series  = nifty_series.dropna()
    master_index  = nifty_series.index
    print(f"  Master timeline: {len(master_index)} trading days "
          f"({master_index[0].date()} → {master_index[-1].date()})")

    if len(master_index) == 0:
        print("  ERROR: No index data. Aborting.")
        return

    # ── STEP 2: Constituent tickers ───────────────────────
    print("\n[2/4] Getting Nifty 500 constituents...")
    tickers = get_tickers()

    # ── STEP 3: Batch download all stocks ─────────────────
    print(f"\n[3/4] Downloading {len(tickers)} stocks in batches...")
    all_highs  = pd.DataFrame(index=master_index)
    all_lows   = pd.DataFrame(index=master_index)
    all_closes = pd.DataFrame(index=master_index)
    batch_size = 50

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i: i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(tickers) + batch_size - 1) // batch_size
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} tickers)...", end=" ")
        try:
            data = yf.download(batch, start=START_DATE, end=end_date,
                               progress=False, auto_adjust=True)
            if not data.empty:
                if 'High' in data.columns:
                    all_highs  = all_highs.join(data['High'],  how='left')
                if 'Low' in data.columns:
                    all_lows   = all_lows.join(data['Low'],   how='left')
                if 'Close' in data.columns:
                    all_closes = all_closes.join(data['Close'], how='left')
            print("done")
        except Exception as e:
            print(f"failed ({e})")
        time.sleep(1.5)

    # ── STEP 4: Compute breadth metrics ───────────────────
    print("\n[4/4] Computing breadth metrics...")

    all_highs  = all_highs.ffill()
    all_lows   = all_lows.ffill()
    all_closes = all_closes.ffill()

    # 52-week highs / lows (compare today vs prior 252 days)
    prev_52w_highs = all_highs.shift(1).rolling(window=252, min_periods=50).max()
    prev_52w_lows  = all_lows.shift(1).rolling(window=252, min_periods=50).min()
    high_counts    = (all_highs  >= prev_52w_highs).sum(axis=1)
    low_counts     = (all_lows   <= prev_52w_lows).sum(axis=1)
    active_count   = all_highs.notna().sum(axis=1).replace(0, 1)  # avoid /0

    # % above individual 200-day SMA
    sma_200           = all_closes.rolling(window=200, min_periods=50).mean()
    above_200_counts  = (all_closes > sma_200).sum(axis=1)

    final_df = pd.DataFrame({
        'DATE':            master_index,
        'NIFTY_500_CLOSE': nifty_series.values.flatten(),
        '52W_HIGH':        high_counts.values.flatten(),
        '52W_LOW':         low_counts.values.flatten(),
        'PCT_HIGH':        ((high_counts / active_count) * 100).fillna(0).round(1).values.flatten(),
        'ABOVE_200SMA':    above_200_counts.values.flatten(),
        'PCT_ABOVE_200SMA':((above_200_counts / active_count) * 100).fillna(0).round(1).values.flatten(),
    })

    final_df['DATE'] = pd.to_datetime(final_df['DATE'])
    final_df = final_df[final_df['DATE'] >= '2000-01-01'].reset_index(drop=True)
    final_df.to_csv(OUTPUT_FILE, index=False)

    latest = final_df.iloc[-1]
    print(f"\n  ✓ Saved {len(final_df):,} rows to {OUTPUT_FILE}")
    print(f"  ✓ Latest date  : {latest['DATE'].strftime('%d %b %Y')}")
    print(f"  ✓ Nifty 500    : {latest['NIFTY_500_CLOSE']:,.2f}")
    print(f"  ✓ 52W Highs    : {int(latest['52W_HIGH'])}")
    print(f"  ✓ 52W Lows     : {int(latest['52W_LOW'])}")
    print(f"  ✓ % > 200 SMA  : {latest['PCT_ABOVE_200SMA']:.1f}%")


# ── FALLBACK TICKERS (used if NSE URL is unreachable) ─────────────────
FALLBACK_TICKERS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS",
    "INFOSYS.NS","SBIN.NS","HINDUNILVR.NS","ITC.NS","LT.NS",
    "KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS",
    "SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","NTPC.NS",
    "POWERGRID.NS","ONGC.NS","HCLTECH.NS","NESTLEIND.NS","TATAMOTORS.NS",
    "BAJAJFINSV.NS","ADANIPORTS.NS","JSWSTEEL.NS","COALINDIA.NS","INDUSINDBK.NS",
    "TECHM.NS","DRREDDY.NS","GRASIM.NS","DIVISLAB.NS","CIPLA.NS",
    "EICHERMOT.NS","TATASTEEL.NS","HINDALCO.NS","APOLLOHOSP.NS","BPCL.NS",
    "HEROMOTOCO.NS","BRITANNIA.NS","ADANIENT.NS","TATACONSUM.NS","SBILIFE.NS",
    "HDFCLIFE.NS","BAJAJ-AUTO.NS","LTF.NS","SHREECEM.NS","DMART.NS",
    "ABB.NS","ADANIGREEN.NS","AMBUJACEM.NS","AUROPHARMA.NS","BANDHANBNK.NS",
    "BERGEPAINT.NS","BOSCHLTD.NS","CANBK.NS","CHOLAFIN.NS","COLPAL.NS",
    "DABUR.NS","DLF.NS","GAIL.NS","GODREJCP.NS","GODREJPROP.NS",
    "HAL.NS","HAVELLS.NS","ICICIGI.NS","ICICIPRULI.NS","INDUSTOWER.NS",
    "IRCTC.NS","JINDALSTEL.NS","JUBLFOOD.NS","LUPIN.NS","MARICO.NS",
    "MUTHOOTFIN.NS","NAUKRI.NS","NHPC.NS","PAGEIND.NS","PIDILITIND.NS",
    "PIIND.NS","PNB.NS","RECLTD.NS","SAIL.NS","SIEMENS.NS",
    "SRF.NS","TORNTPHARM.NS","TRENT.NS","UPL.NS","VEDL.NS",
    "VOLTAS.NS","ZOMATO.NS","NYKAA.NS","INDIGO.NS","JIOFIN.NS",
    "TATAPOWER.NS","IRFC.NS","MOTHERSON.NS","POLYCAB.NS","PAYTM.NS",
    "ABCAPITAL.NS","ACC.NS","AIAENG.NS","ALKEM.NS","ASTRAL.NS",
    "ATUL.NS","AUBANK.NS","BALKRISIND.NS","BATAINDIA.NS","BEL.NS",
    "BHARATFORG.NS","BHEL.NS","BIOCON.NS","CEATLTD.NS","COFORGE.NS",
    "CROMPTON.NS","CUMMINSIND.NS","DEEPAKNTR.NS","DIXON.NS","ELGIEQUIP.NS",
    "EMAMILTD.NS","ENDURANCE.NS","ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS",
    "FORTIS.NS","GLENMARK.NS","GRANULES.NS","GUJGASLTD.NS","HINDPETRO.NS",
    "IDFCFIRSTB.NS","IEX.NS","INDHOTEL.NS","IOC.NS","JKCEMENT.NS",
    "JSWENERGY.NS","KAJARIACER.NS","KEC.NS","KPITTECH.NS","LALPATHLAB.NS",
    "LAURUSLABS.NS","LICHSGFIN.NS","LTTS.NS","MANAPPURAM.NS","MAXHEALTH.NS",
    "MCX.NS","METROPOLIS.NS","MPHASIS.NS","MRF.NS","NATIONALUM.NS",
    "NAVINFLUOR.NS","NCC.NS","NMDC.NS","OBEROIRLTY.NS","OFSS.NS",
    "OIL.NS","PERSISTENT.NS","PETRONET.NS","PHOENIXLTD.NS","PRESTIGE.NS",
    "RAMCOCEM.NS","RITES.NS","SCHAEFFLER.NS","SOBHA.NS","SONACOMS.NS",
    "STARHEALTH.NS","SUNDRMFAST.NS","SUNTV.NS","SUPREMEIND.NS","SYNGENE.NS",
    "TATACHEM.NS","TATACOMM.NS","TATAELXSI.NS","TATATECH.NS","THERMAX.NS",
    "TIMKEN.NS","TORNTPOWER.NS","TRIDENT.NS","TVSMOTORS.NS","UNIONBANK.NS",
    "VGUARD.NS","ZYDUSLIFE.NS","AAVAS.NS","ANGELONE.NS","ASHOKLEY.NS",
    "ATGL.NS","BEML.NS","BLUESTARCO.NS","BRIGADE.NS","CARBORUNIV.NS",
    "CESC.NS","COCHINSHIP.NS","COROMANDEL.NS","CREDITACC.NS","CYIENT.NS",
    "DELHIVERY.NS","DEVYANI.NS","ECLERX.NS","ELECON.NS","EQUITASBNK.NS",
    "FINEORG.NS","FLUOROCHEM.NS","FORCEMOT.NS","GHCL.NS","GICRE.NS",
    "GILLETTE.NS","GLAXO.NS","GPIL.NS","GRSE.NS","GSFC.NS",
    "HAPPSTMNDS.NS","HATSUN.NS","HIKAL.NS","HIMADRI.NS","HOMEFIRST.NS",
    "HUDCO.NS","IPCALAB.NS","IRCON.NS","IRB.NS","ISEC.NS",
    "JMFINANCIL.NS","JSWINFRA.NS","JYOTHYLAB.NS","KANSAINER.NS","KAYNES.NS",
    "KFINTECH.NS","KNRCON.NS","KPIL.NS","KPRMILL.NS","LATENTVIEW.NS",
    "LUXIND.NS","MANKIND.NS","MASTEK.NS","MEDANTA.NS","MOTILALOFS.NS",
    "NATCOPHARM.NS","NEWGEN.NS","NOCIL.NS","NUVOCO.NS","OLECTRA.NS",
    "PFIZER.NS","PNBHOUSING.NS","POLYMED.NS","PRAJ.NS","PSPPROJECT.NS",
    "RAINBOW.NS","RALLIS.NS","RBLBANK.NS","REDINGTON.NS","ROSSARI.NS",
    "ROUTE.NS","SAREGAMA.NS","SBICARD.NS","SEQUENT.NS","SKIPPER.NS",
    "SPANDANA.NS","STLTECH.NS","SUBROS.NS","SUMICHEM.NS","SYMPHONY.NS",
    "TANLA.NS","TEAMLEASE.NS","THYROCARE.NS","TITAGARH.NS","TTKPRESTIG.NS",
    "UNIPARTS.NS","UTIAMC.NS","VBL.NS","VINATIORGA.NS","WAAREEENER.NS",
    "WELCORP.NS","ZENSARTECH.NS","ZYDUSWELL.NS","360ONE.NS","CGPOWER.NS",
    "HDFCAMC.NS","NIPPONLIFE.NS","ICICIPRULI.NS","HDFCLIFE.NS","SBICARD.NS",
    "ICICIGI.NS","STARHEALTH.NS","NUVAMA.NS","PFC.NS","BANKBARODA.NS",
    "RVNL.NS","PVRINOX.NS","KALYANKJIL.NS","GRINDWELL.NS","DHANUKA.NS",
]


if __name__ == "__main__":
    run_update()

"""
SPY weight-discrepancy diagnostic.

Drop this file alongside app.py in your repo as `diagnose_spy.py`, then
deploy/open it via:  streamlit run diagnose_spy.py
(or change Streamlit Cloud's main module to this file temporarily).

It loads SPY.xlsx, fetches Yahoo prev-close prices, and shows where
file-reported weights diverge from shares × prev_close. The answer to
"why does SPY's screener show +0.58% while SPY closed +0.55%" will
be in one of these tables.

Removes after diagnosis — not for production.
"""

import os
import re
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="SPY Diagnostic", layout="wide")
st.title("SPY Weight & Return Diagnostic")

# ── Locate the file ──────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
candidates = [
    os.path.join(HERE, "data", "SPY.xlsx"),
    os.path.join(HERE, "SPY.xlsx"),
    os.path.join(os.getcwd(), "data", "SPY.xlsx"),
]
spy_path = next((p for p in candidates if os.path.exists(p)), None)
if not spy_path:
    st.error(f"SPY.xlsx not found. Tried: {candidates}")
    st.stop()
st.caption(f"Reading: `{spy_path}`")

# ── Load ─────────────────────────────────────────────────────────────────
spy = pd.read_excel(spy_path, sheet_name="holdings")
spy = spy.rename(columns={
    "Name": "company", "Ticker": "ticker_raw",
    "Weight": "weight_file", "Shares Held": "shares",
})

def to_yf(t): return str(t).strip().upper().replace(".", "-")
def is_priceable(raw):
    t = to_yf(raw)
    if t in ("USD", "--", "-", "", "NAN", "NONE"): return False
    if re.search(r"\d", t): return False
    return bool(re.match(r"^[A-Z][A-Z\-]{0,6}$", t))

spy["ticker"]    = spy["ticker_raw"].apply(to_yf)
spy["priceable"] = spy["ticker_raw"].astype(str).apply(is_priceable)
priced_df = spy[spy["priceable"]].copy().reset_index(drop=True)
non_pr    = spy[~spy["priceable"]].copy()
st.write(f"Priceable: **{len(priced_df)}** | Non-priceable: **{len(non_pr)}**")

# ── Fetch Yahoo prev close & today's close ────────────────────────────────
with st.spinner("Fetching Yahoo daily prices (last 5d)…"):
    raw = yf.download(
        priced_df["ticker"].tolist(),
        period="5d", interval="1d",
        auto_adjust=True, progress=False, threads=True,
    )
close = raw["Close"]

# Last completed session = the most recent daily bar (markets are closed,
# so iloc[-1] is the legit close; iloc[-2] is the session before).
if len(close) < 2:
    st.error("Not enough daily history returned.")
    st.stop()

last_close_map = {tk: float(close[tk].dropna().iloc[-1]) for tk in close.columns if close[tk].notna().any()}
prev_close_map = {tk: float(close[tk].dropna().iloc[-2]) for tk in close.columns if close[tk].dropna().shape[0] >= 2}

priced_df["last_close"] = priced_df["ticker"].map(last_close_map)
priced_df["prev_close"] = priced_df["ticker"].map(prev_close_map)
priced_df["chg_pct"]    = (priced_df["last_close"] / priced_df["prev_close"] - 1) * 100

# ── Compute weights two ways ──────────────────────────────────────────────
# Method A: shares × prev_close, normalized over priceable equities (what your
# screener currently does, ignoring cash).
priced_df["mkt_val"] = priced_df["shares"] * priced_df["prev_close"]
total_mv = priced_df["mkt_val"].sum()
priced_df["w_computed_equityonly"] = priced_df["mkt_val"] / total_mv

# Method B: shares × prev_close, scaled to (1 - cash_share) — the new method.
cash_share = float(non_pr["weight_file"].fillna(0).sum())
priced_df["w_computed_navbase"] = priced_df["w_computed_equityonly"] * (1 - cash_share)

# Method C: file's reported weight (which already includes cash drag).
priced_df["w_file"] = priced_df["weight_file"]

# ── Compute four candidate returns ────────────────────────────────────────
ret_A = float((priced_df["w_computed_equityonly"] * priced_df["chg_pct"]).sum())
ret_B = float((priced_df["w_computed_navbase"]    * priced_df["chg_pct"]).sum())
ret_C = float((priced_df["w_file"]                * priced_df["chg_pct"]).sum())

# ── Display ────────────────────────────────────────────────────────────────
st.header("Four candidate SPY returns")
st.markdown(f"""
| Method | Weight basis | SPY Return |
|---|---|---|
| **A** Current screener | shares × prev_close, equity-only (renormalized to 100%) | **{ret_A:+.4f}%** |
| **B** Cash-aware (new code) | shares × prev_close × (1 − cash_share); cash in denom | **{ret_B:+.4f}%** |
| **C** File-weight | file's reported weight × chg | **{ret_C:+.4f}%** |
| **Target** | SPY's quoted daily return | (compare to Yahoo) |

Cash sleeve from file: **{cash_share*100:.4f}%** of NAV.
""")
st.caption("If C matches Yahoo's SPY closely and A/B don't, the gap is computed-vs-file weights "
           "(i.e. my shares×price differs from iShares's official weights). "
           "If C also differs, the gap is shares drift, dividends, or chg% data.")

# ── Where do computed weights diverge from file weights, for top names? ───
st.header("Top 20 names: computed vs file weight (largest divergence first)")
top20 = priced_df.nlargest(20, "w_file").copy()
top20["w_computed_pct"] = top20["w_computed_navbase"] * 100
top20["w_file_pct"]     = top20["w_file"]             * 100
top20["delta_bps"]      = (top20["w_computed_navbase"] - top20["w_file"]) * 10000
top20["contrib_delta_bps"] = top20["delta_bps"] * top20["chg_pct"] / 100  # bps of index-return swing from this weight error
top20 = top20.sort_values("contrib_delta_bps", key=abs, ascending=False)
st.dataframe(
    top20[["ticker","company","shares","prev_close","chg_pct",
           "w_file_pct","w_computed_pct","delta_bps","contrib_delta_bps"]]
        .rename(columns={
            "w_file_pct":"file_weight_%",
            "w_computed_pct":"computed_weight_%",
            "delta_bps":"weight_gap_bps",
            "contrib_delta_bps":"return_swing_bps",
        })
        .round(4),
    width="stretch",
)

st.markdown(
    f"**Sum of |return_swing_bps| across top 20: "
    f"{top20['contrib_delta_bps'].abs().sum():.2f} bps**  "
    f"— this is how much weight-discrepancy alone can move the SPY return figure."
)

# ── Bottom-of-page summary so it's easy to screenshot ─────────────────────
st.divider()
st.subheader("Screenshot this for diagnosis")
st.code(f"""
Method A (equity-only):  {ret_A:+.4f}%
Method B (cash-aware):   {ret_B:+.4f}%
Method C (file-weight):  {ret_C:+.4f}%
Cash sleeve:             {cash_share*100:.4f}%
Top-20 weight-gap swing: {top20['contrib_delta_bps'].abs().sum():.2f} bps
""", language="text")

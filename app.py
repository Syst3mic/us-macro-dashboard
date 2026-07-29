"""
US Macro Dashboard — Streamlit
Data: BLS Official API v2 + FRED API
Indicators: CPI · Core CPI · PPI · Unemployment · NFP · Initial Claims · ADP · Michigan Sentiment
"""

import streamlit as st
import streamlit.components.v1 as components
import html
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta, date
import yfinance as yf

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="US Macro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
/* ── Global ── */
html, body, [data-testid="stApp"] {
    background-color: #FFFFFF;
    color: #1A2540;
    font-family: 'Inter', sans-serif;
}
[data-testid="stAppViewContainer"] { background-color: #FFFFFF; }
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #F4F6FA; }

/* ── Sidebar layout ── */
section[data-testid="stSidebar"] > div:first-child {
    padding: 1.2rem 1rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 0;
}
.sb-logo {
    padding: 4px 0 20px;
    border-bottom: 1px solid rgba(0,0,0,.1);
    margin-bottom: 16px;
}
.sb-logo-title {
    font-size: 16px; font-weight: 700;
    color: #1A2540; letter-spacing: -.2px;
}
.sb-logo-sub {
    font-size: 10px; color: rgba(0,0,0,.4);
    letter-spacing: .06em; margin-top: 3px;
    text-transform: uppercase;
}
.sb-section-label {
    font-size: 9px; font-weight: 700; letter-spacing: .1em;
    color: rgba(0,0,0,.35); text-transform: uppercase;
    margin: 14px 0 6px; padding-left: 2px;
}
.sb-divider {
    border: none; border-top: 1px solid rgba(0,0,0,.1);
    margin: 14px 0;
}
.sb-footnote {
    font-size: 10px; color: #4D6080;
    line-height: 1.6; margin-top: 4px;
}
/* Active nav button styles injected dynamically via f-string CSS */

/* ── Hide Streamlit chrome ── */
/* Hide the hamburger menu, footer, and toolbar (Deploy button, status
   widget) individually — NOT the whole <header>, because in current
   Streamlit versions the sidebar's native collapse/expand chevron lives
   inside the header. Hiding the header outright hides that control too,
   leaving no way to reopen the sidebar. */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stStatusWidget"] { visibility: hidden; }
[data-testid="stHeader"] {
    background: transparent;
    z-index: 999999;
}
/* Make sure the sidebar toggle itself is never accidentally caught by any
   of the rules above, whatever Streamlit's internal testid for it is. */
[data-testid="stHeader"] button {
    visibility: visible !important;
    display: flex !important;
}
.block-container { padding: 0 2rem 4rem; }

/* ── Divider ── */
hr { border-color: rgba(120,140,200,.1) !important; margin: 0.5rem 0 !important; }

/* ── Hero banner ── */
.hero-banner {
    background: #FFFFFF;
    border-bottom: 1px solid rgba(91,141,239,.15);
    padding: 28px 32px 24px;
    margin: 0 -2rem 28px;
    position: relative;
    overflow: visible;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #5B8DEF, #22D3EE, #0FD68A);
}
.hero-banner::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(91,141,239,.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}
.hero-left { display: flex; flex-direction: column; gap: 6px; }
.hero-title {
    font-size: 28px;
    font-weight: 800;
    color: #000000;
    letter-spacing: -.5px;
    line-height: 1;
    font-family: 'Inter', sans-serif;
}
.hero-title span {
    color: #000000;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: #4D6080;
    letter-spacing: .5px;
}
.hero-right { display: flex; align-items: center; gap: 10px; }
.bls-tag {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 700; letter-spacing: .7px;
    padding: 6px 14px; border-radius: 5px;
    background: rgba(91,141,239,.1);
    border: 1px solid rgba(91,141,239,.3);
    color: #7BA4F5;
}
.refresh-icon-btn {
    width: 34px; height: 34px; border-radius: 6px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(120,140,200,.15);
    color: #FFFFFF; font-size: 16px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; transition: all .15s;
}
.refresh-icon-btn:hover {
    background: rgba(91,141,239,.15);
    border-color: rgba(91,141,239,.4);
}
/* .hero-stats removed — replaced with hover tooltip */

/* ── Section headers ── */
.section-header {
    font-size: 20px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #1A2540;
    padding: 6px 0 14px;
    border-bottom: 1px solid rgba(91,141,239,.15);
    margin-bottom: 16px;
    font-family: 'Inter', sans-serif;
}
.section-header .section-icon {
    color: #5B8DEF;
    margin-right: 8px;
}

/* ── Indicator name ── */
.ind-name {
    font-size: 18px !important;
    font-weight: 700 !important;
    letter-spacing: .3px !important;
    color: #1A2540 !important;
    font-family: 'Inter', sans-serif !important;
}
.ind-src {
    font-size: 9px; font-weight: 700; letter-spacing: .5px;
    padding: 3px 8px; border-radius: 3px;
    background: rgba(91,141,239,.1);
    border: 1px solid rgba(91,141,239,.2);
    color: #3D6DD6;
    font-family: 'Inter', sans-serif;
}
.ind-freq {
    font-size: 9px; color: #4D6080;
    padding: 3px 8px; border-radius: 3px;
    background: rgba(91,141,239,.06);
    border: 1px solid rgba(91,141,239,.12);
    font-family: 'Inter', sans-serif;
}

/* ── Stat boxes ── */
.stat-box {
    background: #F0F4FF;
    border: 1px solid rgba(91,141,239,.15);
    border-radius: 10px;
    padding: 18px 20px 14px;
    transition: border-color .2s;
}
.stat-box:hover { border-color: rgba(91,141,239,.35); }
.stat-period {
    font-size: 14px; font-weight: 700; letter-spacing: .5px;
    text-transform: uppercase; color: #4D6080;
    margin-bottom: 10px;
    font-family: 'Inter', sans-serif;
}
.stat-val {
    font-size: 30px; font-weight: 700; color: #1A2540;
    font-family: 'Inter', sans-serif;
    letter-spacing: -1px; line-height: 1;
}
.stat-delta {
    font-size: 11px; font-weight: 600;
    font-family: 'Inter', sans-serif;
    margin-top: 8px; display: inline-block;
    padding: 3px 9px; border-radius: 4px;
}
.stat-up { color: #0CA86C; background: rgba(12,168,108,.08); border: 1px solid rgba(12,168,108,.22); }
.stat-dn { color: #C8303F; background: rgba(200,48,63,.08);  border: 1px solid rgba(200,48,63,.22); }
.stat-date {
    font-size: 10px; color: #4D6080;
    margin-top: 5px; font-family: 'Inter', sans-serif;
    opacity: .85;
}

/* ── Release table ── */
.rel-table { width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 12px; }
.rel-table th {
    text-align: left; padding: 8px 12px;
    font-size: 10px; font-weight: 700; letter-spacing: .6px; text-transform: uppercase;
    color: #1A2540; background: #EEF2FC;
    border-bottom: 1px solid rgba(91,141,239,.15);
    opacity: .8;
}
.rel-table td {
    padding: 8px 12px; color: #1A2540;
    border-bottom: 1px solid rgba(91,141,239,.08);
    opacity: .85;
}
.rel-table tr:first-child td { opacity: 1; font-weight: 600; }
.pos { color: #0CA86C !important; opacity: 1 !important; }
.neg { color: #C8303F !important; opacity: 1 !important; }

/* ── Chart expand button ── */
.chart-expand-btn {
    font-family: 'Inter', sans-serif;
    font-size: 9px; font-weight: 700; letter-spacing: .4px;
    padding: 3px 9px; border-radius: 4px;
    background: rgba(91,141,239,.08);
    border: 1px solid rgba(91,141,239,.2);
    color: #7BA4F5; cursor: pointer;
    transition: all .15s;
}
.chart-expand-btn:hover {
    background: rgba(91,141,239,.18);
    border-color: rgba(91,141,239,.4);
    color: #1A2540;
}

/* ── Modal overlay ── */
.modal-overlay {
    display: none;
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,.85);
    z-index: 9999;
    align-items: center; justify-content: center;
    backdrop-filter: blur(4px);
}
.modal-overlay.open { display: flex; }
.modal-box {
    background: #0B1020;
    border: 1px solid rgba(91,141,239,.25);
    border-radius: 14px;
    padding: 24px;
    width: 90vw; max-width: 1100px;
    position: relative;
    box-shadow: 0 24px 80px rgba(0,0,0,.7);
}
.modal-close {
    position: absolute; top: 16px; right: 16px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(120,140,200,.15);
    color: #FFFFFF; font-size: 18px;
    width: 32px; height: 32px; border-radius: 6px;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: all .15s;
}
.modal-close:hover { background: rgba(240,72,90,.15); border-color: rgba(240,72,90,.3); }
.modal-title {
    font-family: 'Inter', sans-serif;
    font-size: 16px; font-weight: 700; color: #FFFFFF;
    margin-bottom: 16px; letter-spacing: -.2px;
}

/* ── Data hover bar ── */
.data-hover-wrap {
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid rgba(120,140,200,.08);
    position: relative;
    display: flex;
    flex-direction: row;
    align-items: center;
}
.data-hover-trigger {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .8px;
    color: #7BA4F5;
    cursor: default;
    user-select: none;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 5px;
    background: rgba(91,141,239,.08);
    border: 1px solid rgba(91,141,239,.2);
    transition: background .15s, border-color .15s;
}
.data-hover-wrap:hover .data-hover-trigger {
    background: rgba(91,141,239,.16);
    border-color: rgba(91,141,239,.4);
}
.data-q {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 14px; height: 14px;
    border-radius: 50%;
    background: rgba(91,141,239,.25);
    border: 1px solid rgba(91,141,239,.4);
    font-size: 9px;
    color: #FFFFFF;
    font-weight: 700;
}
/* Horizontal bar — hidden until hover, inline next to trigger */
.data-hover-bar {
    display: none;
    position: relative;
    z-index: 999;
    background: rgba(13,22,40,.92);
    border: 1px solid rgba(91,141,239,.2);
    border-radius: 8px;
    padding: 8px 18px;
    white-space: nowrap;
    flex-direction: row;
    align-items: center;
    gap: 0;
    box-shadow: 0 4px 20px rgba(0,0,0,.4);
    margin-left: 10px;
}
.data-hover-wrap:hover .data-hover-bar {
    display: flex;
}
.data-hover-item {
    display: flex;
    flex-direction: column;
    gap: 3px;
    padding: 0 18px;
}
.data-hover-item:first-child { padding-left: 0; }
.data-hover-item:last-child  { padding-right: 0; }
.data-hover-label {
    font-family: 'Inter', sans-serif;
    font-size: 8px;
    font-weight: 700;
    letter-spacing: .7px;
    text-transform: uppercase;
    color: #4D6080;
}
.data-hover-val {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: #FFFFFF;
}
.data-hover-divider {
    width: 1px;
    height: 32px;
    background: rgba(120,140,200,.12);
    flex-shrink: 0;
}

/* ── Streamlit button overrides (refresh) ── */
[data-testid="stButton"] button {
    background: rgba(91,141,239,.07) !important;
    border: 1px solid rgba(91,141,239,.2) !important;
    color: #1A2540 !important;
    font-size: 18px !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 34px !important;
    line-height: 1 !important;
}
[data-testid="stButton"] button:hover {
    background: rgba(91,141,239,.15) !important;
    border-color: rgba(91,141,239,.4) !important;
}

/* ── Status text ── */
.status-ok  { font-family: 'Inter', sans-serif; font-size: 12px; color: #0FD68A; }
.status-warn{ font-family: 'Inter', sans-serif; font-size: 12px; color: #F59E0B; }

/* ── Index selector buttons — active = bright white filled, inactive = dim ── */
.idx-active button {
    background: rgba(255,255,255,.12) !important;
    border-color: rgba(255,255,255,.5) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 0 12px rgba(255,255,255,.08) !important;
}
.idx-inactive button {
    background: transparent !important;
    border-color: rgba(120,140,200,.2) !important;
    color: rgba(255,255,255,.35) !important;
    font-weight: 400 !important;
}

/* ── Screener view buttons — Gainers green, Losers red ── */
div[data-testid="stButton"]:has(button[kind="primaryFormSubmit"]) { display:none; }
/* Target by button text content via CSS attribute trick */
.gainers-active button  { color: #0FD68A !important; border-color: rgba(15,214,138,.4) !important; background: rgba(15,214,138,.1) !important; }
.losers-active  button  { color: #F0485A !important; border-color: rgba(240,72,90,.4)  !important; background: rgba(240,72,90,.1)  !important; }
.gainers-inactive button{ color: #0FD68A !important; opacity: .5; }
.losers-inactive  button{ color: #F0485A !important; opacity: .5; }

/* ── Page toggle (MACRO / MARKETS) ── */
.page-toggle {
    display: flex; gap: 4px;
    background: #0D1628;
    border: 1px solid rgba(120,140,200,.12);
    border-radius: 8px; padding: 4px;
    margin-bottom: 24px; width: fit-content;
}
.ptbtn {
    padding: 8px 28px; border-radius: 5px;
    font-size: 12px; font-weight: 700;
    font-family: 'Inter', sans-serif;
    letter-spacing: .5px; cursor: pointer;
    border: none; transition: all .15s;
    background: transparent; color: #4D6080;
}
.ptbtn.active {
    background: linear-gradient(135deg, #5B8DEF, #22D3EE);
    color: #FFFFFF;
    box-shadow: 0 0 16px rgba(91,141,239,.35);
}
.ptbtn:hover:not(.active) { color: #FFFFFF; background: rgba(255,255,255,.05); }

/* ── Screener ── */
.screener-header {
    display: flex; align-items: center;
    justify-content: space-between;
    flex-wrap: wrap; gap: 12px;
    margin-bottom: 16px;
}
.screener-title {
    font-family: 'Inter', sans-serif;
    font-size: 20px; font-weight: 700;
    color: #FFFFFF; letter-spacing: -.2px;
}
.screener-meta {
    font-family: 'Inter', sans-serif;
    font-size: 10px; color: #4D6080; letter-spacing: .4px;
}
.pill-bar { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
.pill {
    padding: 5px 14px; border-radius: 20px;
    font-size: 10px; font-weight: 700;
    font-family: 'Inter', sans-serif;
    letter-spacing: .4px; cursor: pointer;
    border: 1px solid rgba(120,140,200,.15);
    background: rgba(255,255,255,.03); color: #8898BB;
    transition: all .15s;
}
.pill.active {
    background: rgba(91,141,239,.15);
    border-color: rgba(91,141,239,.4); color: #FFFFFF;
}
.stock-table { width: 100%; border-collapse: collapse; }
.stock-table th {
    font-family: 'Inter', sans-serif;
    font-size: 9px; font-weight: 700; letter-spacing: .7px;
    text-transform: uppercase; color: #FFFFFF;
    padding: 8px 12px; border-bottom: 1px solid rgba(120,140,200,.1);
    text-align: left; background: #080C16;
}
.stock-table td {
    font-family: 'Inter', sans-serif;
    font-size: 12px; padding: 9px 12px;
    border-bottom: 1px solid rgba(120,140,200,.05);
    color: #FFFFFF;
}
.stock-table tr:hover td { background: rgba(91,141,239,.04); }
.chg-pos { color: #0FD68A !important; font-weight: 700; }
.chg-neg { color: #F0485A !important; font-weight: 700; }
.ticker-badge {
    font-weight: 700; color: #7BA4F5;
    background: rgba(91,141,239,.08);
    padding: 2px 7px; border-radius: 4px;
    font-size: 11px;
}
.sector-tag {
    font-size: 9px; padding: 2px 7px; border-radius: 3px;
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(120,140,200,.1);
    color: #FFFFFF; white-space: nowrap;
}
.mkt-status-open  { color: #0FD68A; font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 700; }
.mkt-status-closed{ color: #F59E0B; font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 700; }
</style>

<!-- Modal HTML (shared, one instance) -->
<div class="modal-overlay" id="chartModal" onclick="if(event.target===this)closeModal()">
  <div class="modal-box">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="modal-title" id="modalTitle"></div>
    <div id="modalChart"></div>
  </div>
</div>

<script>
function openModal(title, chartDivId) {
    document.getElementById('modalTitle').innerText = title;
    var src = document.getElementById(chartDivId);
    var dest = document.getElementById('modalChart');
    if (src) {
        dest.innerHTML = src.innerHTML;
        // Resize the plotly chart inside modal
        var plots = dest.querySelectorAll('.js-plotly-plot');
        plots.forEach(function(p) {
            if (window.Plotly) Plotly.relayout(p, {height: 480});
        });
    }
    document.getElementById('chartModal').classList.add('open');
    document.body.style.overflow = 'hidden';
}
function closeModal() {
    document.getElementById('chartModal').classList.remove('open');
    document.body.style.overflow = '';
    document.getElementById('modalChart').innerHTML = '';
}
document.addEventListener('keydown', function(e) { if(e.key==='Escape') closeModal(); });
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BLS SERIES CONFIG
# ─────────────────────────────────────────────────────────────────────────────
SERIES = {
    "cpi": {
        "id":     "CUSR0000SA0",     # SA  — used for MoM
        "id_nsa": "CUUR0000SA0",     # NSA — used for YoY (BLS headline convention)
        "name": "CPI",
        "full": "Consumer Price Index — All Items SA",
        "transform": "price_index",
        "color": "#5B8DEF",
        "unit_mom": "%", "unit_yoy": "%", "dp": 2,
    },
    "corecpi": {
        "id":     "CUSR0000SA0L1E",  # SA  — used for MoM
        "id_nsa": "CUUR0000SA0L1E",  # NSA — used for YoY (BLS headline convention)
        "name": "Core CPI",
        "full": "CPI ex Food & Energy SA",
        "transform": "price_index",
        "color": "#22D3EE",
        "unit_mom": "%", "unit_yoy": "%", "dp": 2,
    },
    "ppi": {
        "id":     "WPSFD4",          # SA  — used for MoM
        "id_nsa": "WPUFD4",          # NSA — used for YoY (mirror of the SA id, S->U)
        "name": "PPI",
        "full": "PPI Final Demand",
        "transform": "price_index",
        "color": "#A78BFA",
        "unit_mom": "%", "unit_yoy": "%", "dp": 2,
    },
    "unemp": {
        "id": "LNS14000000",
        "name": "Unemployment Rate",
        "full": "Civilian Unemployment Rate (U-3) SA",
        "transform": "rate",
        "color": "#F59E0B",
        "unit_mom": "pp", "unit_yoy": "pp", "dp": 1,
    },
    "nfp": {
        "id": "CES0000000001",
        "name": "Nonfarm Payrolls",
        "full": "Total Nonfarm Payrolls SA",
        "transform": "nfp",
        "color": "#0FD68A",
        "unit_mom": "K", "unit_yoy": "K", "dp": 0,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# FRED SERIES CONFIG  (for indicators not on BLS)
# ─────────────────────────────────────────────────────────────────────────────
FRED_SERIES = {
    "corepce": {
        "id":        "PCEPILFE",
        "name":      "Core PCE",
        "full":      "PCE Excluding Food & Energy — BEA",
        "transform": "price_index",
        "color":     "#F472B6",
        "unit_mom":  "%",
        "unit_yoy":  "%",
        "dp":        2,
        "freq":      "Monthly",
        "source":    "BEA via FRED",
    },
    "claims": {
        "id":        "ICSA",
        "name":      "Initial Jobless Claims",
        "full":      "Initial Unemployment Insurance Claims (Weekly SA)",
        "transform": "claims",    # weekly level, show actual print + WoW change
        "color":     "#F97316",
        "unit":      "K",
        "dp":        0,
        "freq":      "Weekly",
        "source":    "DOL via FRED",
    },


}

# ─────────────────────────────────────────────────────────────────────────────
# BLS API FETCH
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bls_data() -> dict:
    api_key    = st.secrets["BLS_API_KEY"]
    series_ids = [cfg["id"] for cfg in SERIES.values()]
    series_ids += [cfg["id_nsa"] for cfg in SERIES.values() if "id_nsa" in cfg]
    id_to_key  = {cfg["id"]: k for k, cfg in SERIES.items()}
    id_to_key.update({cfg["id_nsa"]: f"{k}__nsa"
                      for k, cfg in SERIES.items() if "id_nsa" in cfg})
    end_year   = datetime.now().year
    start_year = end_year - 10

    payload = {
        "seriesid":        series_ids,
        "startyear":       str(start_year),
        "endyear":         str(end_year),
        "registrationkey": api_key,
        "calculations":    True,       # request BLS pre-computed pct changes
    }
    resp = requests.post(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        json=payload, timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        msgs = data.get("message", ["Unknown BLS error"])
        raise ValueError("BLS API error: " + "; ".join(msgs))

    result = {}
    for series in data["Results"]["series"]:
        key = id_to_key.get(series["seriesID"])
        if not key:
            continue
        rows = []
        for obs in series["data"]:
            if obs["period"] == "M13" or obs["value"] in ("-", ""):
                continue
            month = int(obs["period"][1:])
            calcs = obs.get("calculations", {}).get("pct_changes", {})
            rows.append({
                "date":    pd.Timestamp(year=int(obs["year"]), month=month, day=1),
                "value":   float(obs["value"]),
                "mom_bls": float(calcs["1"])  if "1"  in calcs else None,  # BLS 1-month %chg
                "yoy_bls": float(calcs["12"]) if "12" in calcs else None,  # BLS 12-month %chg
            })
        df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
        result[key] = df

    # Attach the unadjusted (NSA) level as `value_nsa` AND the NSA-sourced
    # yoy_bls so compute_series uses BLS's own NSA 12-month percent changes
    # for the YoY headline (BLS convention: YoY = NSA, MoM = SA).
    # The SA series' own calculations block returns a SA-based YoY which does
    # NOT match the published headline — the NSA yoy_bls overrides it here.
    # If an NSA companion is missing the SA series is left untouched and YoY
    # silently falls back to pct_change(12) on value_nsa in compute_series().
    for k in list(SERIES.keys()):
        nsa_key = f"{k}__nsa"
        if nsa_key in result and k in result:
            nsa_df = result.pop(nsa_key)
            # Columns to carry over from NSA series: level + BLS NSA YoY calc
            nsa_cols = {"value": "value_nsa"}
            if "yoy_bls" in nsa_df.columns:
                nsa_cols["yoy_bls"] = "yoy_bls_nsa"
            nsa = nsa_df[["date"] + list(nsa_cols.keys())].rename(columns=nsa_cols)
            result[k] = result[k].merge(nsa, on="date", how="left")
            # Prefer NSA yoy_bls over SA yoy_bls — overwrite if present
            if "yoy_bls_nsa" in result[k].columns:
                result[k]["yoy_bls"] = result[k]["yoy_bls_nsa"].combine_first(
                    result[k].get("yoy_bls")
                )
                result[k].drop(columns=["yoy_bls_nsa"], inplace=True)

    return result

# ─────────────────────────────────────────────────────────────────────────────
# FRED API FETCH
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fred_data() -> dict:
    """
    Fetch ICSA and Core PCE from FRED API.
    For Core PCE (price_index transform), also fetches FRED's pre-computed
    MoM (units=pch) and YoY (units=pc1) percent-change series so
    compute_series can use official BEA prints rather than deriving them
    from the rounded index level.
    Server-side GET — no CORS, no proxy needed.
    """
    fred_key = st.secrets["FRED_API_KEY"]
    result   = {}

    def _fred_get(series_id, limit, units=None):
        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}"
            f"&api_key={fred_key}"
            f"&file_type=json"
            f"&sort_order=desc"
            f"&limit={limit}"
        )
        if units:
            url += f"&units={units}"
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.json()

    for key, cfg in FRED_SERIES.items():
        # Weekly series: fetch 3 years (156 weeks). Monthly: 10 years.
        limit = 156 if cfg["freq"] == "Weekly" else 120
        try:
            data = _fred_get(cfg["id"], limit)
            rows = []
            for obs in data.get("observations", []):
                if obs["value"] in (".", ""):
                    continue
                rows.append({
                    "date":  pd.Timestamp(obs["date"]),
                    "value": float(obs["value"]),
                })
            df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

            # Claims: convert from persons to thousands
            if key == "claims":
                df["value"] = df["value"] / 1000

            # Core PCE: fetch FRED's pre-computed MoM and YoY pct-change series
            # so compute_series uses official BEA prints (same principle as the
            # BLS calculations block for CPI/PPI). FRED exposes these via the
            # units= parameter: pch = period pct change (MoM), pc1 = pct change
            # from a year ago (YoY).
            if key == "corepce" and cfg.get("transform") == "price_index":
                try:
                    mom_data = _fred_get(cfg["id"], limit, units="pch")
                    mom_rows = []
                    for obs in mom_data.get("observations", []):
                        if obs["value"] in (".", ""):
                            continue
                        mom_rows.append({
                            "date":    pd.Timestamp(obs["date"]),
                            "mom_bls": float(obs["value"]),
                        })
                    if mom_rows:
                        mom_df = pd.DataFrame(mom_rows).sort_values("date").reset_index(drop=True)
                        df = df.merge(mom_df, on="date", how="left")
                except Exception as e:
                    print(f"FRED Core PCE MoM fetch failed: {e}")

                try:
                    yoy_data = _fred_get(cfg["id"], limit, units="pc1")
                    yoy_rows = []
                    for obs in yoy_data.get("observations", []):
                        if obs["value"] in (".", ""):
                            continue
                        yoy_rows.append({
                            "date":    pd.Timestamp(obs["date"]),
                            "yoy_bls": float(obs["value"]),
                        })
                    if yoy_rows:
                        yoy_df = pd.DataFrame(yoy_rows).sort_values("date").reset_index(drop=True)
                        df = df.merge(yoy_df, on="date", how="left")
                except Exception as e:
                    print(f"FRED Core PCE YoY fetch failed: {e}")

            result[key] = df
        except Exception as e:
            print(f"FRED fetch failed [{key}]: {e}")
            result[key] = pd.DataFrame(columns=["date", "value"])

    return result

# ─────────────────────────────────────────────────────────────────────────────
# TRANSFORMATIONS
# ─────────────────────────────────────────────────────────────────────────────
def compute_series(df: pd.DataFrame, transform: str) -> pd.DataFrame:
    df = df.copy()
    if transform == "price_index":
        # Prefer BLS pre-computed %changes (from calculations block in the API
        # response) — these match official headline prints exactly because BLS
        # computes them from internal unrounded index levels. Fall back to
        # pct_change() only for data points where the BLS didn't return calcs
        # (e.g. the oldest observations at the start of the history window).
        # FRED cards (Core PCE) carry no mom_bls/yoy_bls columns and correctly
        # use the pct_change() fallback throughout.
        if "mom_bls" in df.columns:
            derived_mom = df["value"].pct_change(1) * 100
            df["mom"] = df["mom_bls"].fillna(derived_mom)
        else:
            df["mom"] = df["value"].pct_change(1) * 100

        if "yoy_bls" in df.columns:
            yoy_src      = df["value_nsa"] if "value_nsa" in df.columns else df["value"]
            derived_yoy  = yoy_src.pct_change(12) * 100
            df["yoy"] = df["yoy_bls"].fillna(derived_yoy)
        else:
            yoy_src   = df["value_nsa"] if "value_nsa" in df.columns else df["value"]
            df["yoy"] = yoy_src.pct_change(12) * 100
    elif transform in ("rate", "nfp"):
        df["mom"] = df["value"].diff(1)
        df["yoy"] = df["value"].diff(12)
    return df

# ─────────────────────────────────────────────────────────────────────────────
# FORMAT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_val(v: float, cfg: dict, which: str) -> str:
    sign = "+" if v >= 0 else ""
    dp   = cfg["dp"]
    unit = cfg[f"unit_{which}"]
    if cfg["transform"] == "nfp":
        return f"{sign}{int(round(v))}K"
    return f"{sign}{v:.{dp}f}{unit}"

def is_positive_signal(v: float, key: str) -> bool:
    if key == "nfp":   return v >= 0
    return v <= 0  # lower inflation / lower unemployment = positive

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART
# ─────────────────────────────────────────────────────────────────────────────
CHART_BG  = "#FFFFFF"
GRID_COL  = "rgba(0,0,0,.07)"
AXIS_COL  = "#4D6080"
FONT_MONO = "Inter, sans-serif"

def make_chart(df: pd.DataFrame, cfg: dict, which: str = "yoy",
               height: int = 200) -> go.Figure:
    color      = cfg["color"]
    fig        = go.Figure()
    yaxis_opts = {}

    def hex_fill(hex_col, alpha=0.1):
        r = int(hex_col[1:3], 16)
        g = int(hex_col[3:5], 16)
        b = int(hex_col[5:7], 16)
        return f"rgba({r},{g},{b},{alpha})"

    # ── Rate (Unemployment): plot raw level — actual % prints ──────────────
    # Both MoM and YoY tabs show the same historical rate series so the user
    # sees real prints (4.3%, 4.4% etc.), not percentage-point diffs.
    if cfg["transform"] == "rate":
        plot_df = df.dropna(subset=["value"]).tail(60)
        fig.add_trace(go.Scatter(
            x=plot_df["date"], y=plot_df["value"],
            mode="lines",
            line=dict(color=color, width=1.8),
            fill="tozeroy",
            fillcolor=hex_fill(color, 0.1),
            hovertemplate="%{x|%b %Y}<br><b>%{y:.1f}%</b><extra></extra>",
        ))
        # Floor y-axis close to data so small moves are visible
        y_min = max(0, plot_df["value"].min() - 0.5)
        y_max = plot_df["value"].max() + 0.5
        yaxis_opts["range"] = [y_min, y_max]

    # ── NFP: bar chart of MoM net jobs added ───────────────────────────────
    elif cfg["transform"] == "nfp":
        plot_df    = df.dropna(subset=[which]).tail(60)
        bar_colors = ["rgba(15,214,138,.7)"  if v >= 0 else "rgba(240,72,90,.7)"  for v in plot_df[which]]
        bar_borders= ["rgba(15,214,138,.95)" if v >= 0 else "rgba(240,72,90,.95)" for v in plot_df[which]]
        fig.add_trace(go.Bar(
            x=plot_df["date"], y=plot_df[which],
            marker_color=bar_colors,
            marker_line_color=bar_borders,
            marker_line_width=1,
            hovertemplate="%{x|%b %Y}<br><b>%{y:+.0f}K</b><extra></extra>",
        ))
        fig.add_hline(y=0, line_color="rgba(0,0,0,.12)", line_width=1)

    # ── Price index (CPI / Core CPI / PPI): MoM% or YoY% changes ──────────
    else:
        plot_df = df.dropna(subset=[which]).tail(60)
        unit    = cfg[f"unit_{which}"]
        fig.add_trace(go.Scatter(
            x=plot_df["date"], y=plot_df[which],
            mode="lines",
            line=dict(color=color, width=1.8),
            fill="tozeroy",
            fillcolor=hex_fill(color, 0.1),
            hovertemplate=f"%{{x|%b %Y}}<br><b>%{{y:+.2f}}{unit}</b><extra></extra>",
        ))
        fig.add_hline(y=0, line_color="rgba(0,0,0,.12)", line_width=1)

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_MONO, color=AXIS_COL, size=10),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=10, color="#1A2540"),
            tickformat="%b '%y", nticks=6,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID_COL, zeroline=False,
            tickfont=dict(size=10, color="#1A2540"), nticks=5,
            **yaxis_opts,
        ),
        hoverlabel=dict(
            bgcolor="#F0F4FF",
            bordercolor="rgba(91,141,239,.3)",
            font=dict(family=FONT_MONO, size=12, color="#1A2540"),
        ),
        showlegend=False,
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# STAT BOX HTML
# ─────────────────────────────────────────────────────────────────────────────
def stat_box_html(label: str, value_str: str, delta_str: str,
                  is_up: bool, date_str: str) -> str:
    arrow     = "▲" if is_up else "▼"
    delta_cls = "stat-up" if is_up else "stat-dn"
    return f"""
    <div class="stat-box">
      <div class="stat-period">{label}</div>
      <div class="stat-val">{value_str}</div>
      <span class="stat-delta {delta_cls}">{arrow} {delta_str}</span>
      <div class="stat-date">{date_str}</div>
    </div>
    """

# ─────────────────────────────────────────────────────────────────────────────
# NFP RELEASE TABLE
# ─────────────────────────────────────────────────────────────────────────────
def nfp_release_table(df: pd.DataFrame) -> str:
    recent = df.dropna(subset=["mom"]).tail(6).iloc[::-1]
    rows   = ""
    for i, (_, row) in enumerate(recent.iterrows()):
        mom  = row["mom"]
        cls  = "pos" if mom >= 0 else "neg"
        sign = "+" if mom >= 0 else ""
        rows += f"""
        <tr>
          <td>{row['date'].strftime('%b %Y')}</td>
          <td class="{cls}">{sign}{int(round(mom))}K</td>
          <td style="color:#4D6080">—</td>
        </tr>"""
    return f"""
    <table class="rel-table">
      <thead><tr><th>Release</th><th>Actual</th><th>Consensus</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>"""

# ─────────────────────────────────────────────────────────────────────────────
# RENDER ONE INDICATOR CARD
# ─────────────────────────────────────────────────────────────────────────────
def render_card(key: str, cfg: dict, df) -> None:
    # ── Label row ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="width:9px;height:9px;border-radius:50%;background:{cfg['color']};
               box-shadow:0 0 10px {cfg['color']}70;display:inline-block;flex-shrink:0"></span>
        <span class="ind-name">{cfg['name']}</span>
      </div>
      <div style="display:flex;gap:6px;align-items:center">
        <span class="ind-src">BLS</span>
        <span class="ind-freq">MONTHLY</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Data unavailable", icon="⚠️")
        return

    # ── Compute ───────────────────────────────────────────────────────────
    df_c  = compute_series(df, cfg["transform"])
    valid = df_c.dropna(subset=["mom", "yoy"])
    if len(valid) < 2:
        st.warning("Insufficient data", icon="⚠️")
        return

    last     = valid.iloc[-1]
    prev     = valid.iloc[-2]   # one period back
    date_str = last["date"].strftime("%b %Y")

    mom_val  = last["mom"]   # MoM change (pp or % or K)
    yoy_val  = last["yoy"]   # YoY change (pp or % or K)
    level    = last["value"] # Raw level (unemployment rate %, NFP thousands)

    # ── Pull prior period level values for badges ─────────────────────────
    # prev_mom_level  = level 1 month ago  (for MoM box badge)
    # prev_yoy_level  = level 12 months ago (for YoY box badge)
    # These come from the raw df (before diffs), aligned by date
    df_raw   = df.sort_values("date").reset_index(drop=True)
    last_date = last["date"]  # e.g. 2026-04-01

    # Look up exactly 1 month prior by date arithmetic (not index offset)
    prev1_target  = last_date - pd.DateOffset(months=1)
    prev12_target = last_date - pd.DateOffset(months=12)

    prev1_row  = df_raw[df_raw["date"] == prev1_target]
    prev12_row = df_raw[df_raw["date"] == prev12_target]

    prev1_val   = prev1_row.iloc[0]["value"]            if not prev1_row.empty  else None
    prev12_val  = prev12_row.iloc[0]["value"]           if not prev12_row.empty else None
    prev1_date  = prev1_row.iloc[0]["date"].strftime("%b %Y")  if not prev1_row.empty  else "—"
    prev12_date = prev12_row.iloc[0]["date"].strftime("%b %Y") if not prev12_row.empty else "—"

    # ── Headline value ────────────────────────────────────────────────────
    # price_index : headline = MoM% change (e.g. +0.64%) / YoY% change (e.g. +3.95%)
    # rate        : headline = actual rate level (e.g. 4.3%) — same in both boxes
    # nfp         : headline = MoM net jobs (e.g. +177K) / YoY net (e.g. +2100K)
    if cfg["transform"] == "price_index":
        mom_headline = fmt_val(mom_val, cfg, "mom")
        yoy_headline = fmt_val(yoy_val, cfg, "yoy")
    elif cfg["transform"] == "rate":
        mom_headline = f"{level:.1f}%"
        yoy_headline = f"{level:.1f}%"
    else:  # nfp — show actual MoM net jobs in both boxes
        mom_headline = fmt_val(mom_val, cfg, "mom")   # e.g. +115K
        yoy_headline = fmt_val(mom_val, cfg, "mom")   # same print, badge shows YoY comparison

    # ── Delta badges ──────────────────────────────────────────────────────
    # price_index:
    #   MoM box → change vs prior MoM print  (e.g. +0.64% vs prior +0.38%)
    #   YoY box → change vs prior YoY print  (e.g. +3.95% vs prior +2.40%)
    # rate:
    #   MoM box → "vs {prev month}: {prev_val}%"  (e.g. vs Mar: 4.3%)
    #   YoY box → "vs {12mo ago}: {prev12_val}%"  (e.g. vs Apr 2025: 4.2%)
    # nfp:
    #   MoM box → change vs prior MoM print
    #   YoY box → change vs prior YoY print

    if cfg["transform"] == "rate":
        # MoM badge: show prior month actual rate
        mom_dlt_str = f"vs {prev1_date}: {prev1_val:.1f}%" if prev1_val is not None else "—"
        yoy_dlt_str = f"vs {prev12_date}: {prev12_val:.1f}%" if prev12_val is not None else "—"
        delta_up    = is_positive_signal(mom_val, key)
        yoy_dlt_up  = is_positive_signal(yoy_val, key)

    elif cfg["transform"] == "nfp":
        # All comparisons use MoM diff values (net jobs), not raw levels.
        # mom_val  = Apr 2026 print  = diff(Apr26 level - Mar26 level) e.g. +115K
        # We need Apr 2025 print     = diff(Apr25 level - Mar25 level) e.g. +108K
        # Retrieve from df_c (which has the mom column computed) by exact date match.

        prev1_target_nfp  = last["date"] - pd.DateOffset(months=1)   # Mar 2026
        prev12_target_nfp = last["date"] - pd.DateOffset(months=12)  # Apr 2025

        prev1_row_nfp  = df_c[df_c["date"] == prev1_target_nfp]
        prev12_row_nfp = df_c[df_c["date"] == prev12_target_nfp]

        prev1_mom  = prev1_row_nfp.iloc[0]["mom"]  if not prev1_row_nfp.empty  else None
        prev12_mom = prev12_row_nfp.iloc[0]["mom"] if not prev12_row_nfp.empty else None

        prev1_date_nfp  = prev1_row_nfp.iloc[0]["date"].strftime("%b %Y")  if not prev1_row_nfp.empty  else "—"
        prev12_date_nfp = prev12_row_nfp.iloc[0]["date"].strftime("%b %Y") if not prev12_row_nfp.empty else "—"

        # MoM badge: vs prior month print  e.g. "vs Mar 2026: +185K"
        if prev1_mom is not None:
            s = "+" if prev1_mom >= 0 else ""
            mom_dlt_str = f"vs {prev1_date_nfp}: {s}{int(round(prev1_mom))}K"
        else:
            mom_dlt_str = "—"

        # YoY badge: diff vs same month last year  e.g. "+7K vs Apr 2025: +108K"
        if prev12_mom is not None:
            yoy_diff = mom_val - prev12_mom   # e.g. 115 - 108 = +7
            diff_s   = "+" if yoy_diff  >= 0 else ""
            prev_s   = "+" if prev12_mom >= 0 else ""
            yoy_dlt_str = f"{diff_s}{int(round(yoy_diff))}K vs {prev12_date_nfp}: {prev_s}{int(round(prev12_mom))}K"
        else:
            yoy_dlt_str = "—"

        delta_up   = is_positive_signal(mom_val - (prev1_mom  or 0), key)
        yoy_dlt_up = is_positive_signal(mom_val - (prev12_mom or 0), key)

    else:
        mom_delta   = mom_val - prev["mom"]
        yoy_delta   = yoy_val - prev["yoy"]
        mom_dlt_str = fmt_val(mom_delta, cfg, "mom") + " vs prior"
        yoy_dlt_str = fmt_val(yoy_delta, cfg, "yoy") + " vs prior"
        delta_up    = is_positive_signal(mom_delta, key)
        yoy_dlt_up  = is_positive_signal(yoy_delta, key)

    # ── Stat pair ─────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(stat_box_html(
            "Month-over-Month", mom_headline,
            mom_dlt_str, delta_up, date_str
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_box_html(
            "Year-over-Year", yoy_headline,
            yoy_dlt_str, yoy_dlt_up, date_str
        ), unsafe_allow_html=True)

    # NFP release table removed — chart shows the actual prints directly

    # ── Chart section ─────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)

    # Rate (unemployment) and NFP: no tab toggle — render chart directly
    if cfg["transform"] in ("rate", "nfp"):
        fig_direct = make_chart(df_c, cfg, "mom", height=200)
        col_chart, col_btn = st.columns([10, 1])
        with col_chart:
            st.plotly_chart(
                fig_direct, use_container_width=True,
                config={"displayModeBar": False},
                key=f"plt_direct_{key}"
            )
        with col_btn:
            if st.button("⛶", key=f"exp_direct_{key}", help="Expand chart"):
                st.session_state["expanded"] = {
                    "key": key, "which": "mom",
                    "title": f"{cfg['name']} — Actual Prints",
                    "cfg": cfg, "df_c": df_c
                }
                st.rerun()
        st.caption(cfg["full"])

    # Price index indicators (CPI / Core CPI / PPI): MoM / YoY tab toggle
    else:
        tab_mom, tab_yoy = st.tabs(["  MoM  ", "  YoY  "])

        with tab_mom:
            fig_mom = make_chart(df_c, cfg, "mom", height=200)
            col_chart, col_btn = st.columns([10, 1])
            with col_chart:
                st.plotly_chart(
                    fig_mom, use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"plt_mom_{key}"
                )
            with col_btn:
                if st.button("⛶", key=f"exp_mom_{key}", help="Expand chart"):
                    st.session_state["expanded"] = {
                        "key": key, "which": "mom",
                        "title": f"{cfg['name']} — Month-over-Month",
                        "cfg": cfg, "df_c": df_c
                    }
                    st.rerun()
            st.caption(cfg["full"])

        with tab_yoy:
            fig_yoy = make_chart(df_c, cfg, "yoy", height=200)
            col_chart2, col_btn2 = st.columns([10, 1])
            with col_chart2:
                st.plotly_chart(
                    fig_yoy, use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"plt_yoy_{key}"
                )
            with col_btn2:
                if st.button("⛶", key=f"exp_yoy_{key}", help="Expand chart"):
                    st.session_state["expanded"] = {
                        "key": key, "which": "yoy",
                        "title": f"{cfg['name']} — Year-over-Year",
                        "cfg": cfg, "df_c": df_c
                    }
                    st.rerun()
            st.caption(cfg["full"])

    st.markdown("</div>", unsafe_allow_html=True)

    # Modal handled at top level in main() via st.session_state["expanded"]

# ─────────────────────────────────────────────────────────────────────────────
# FRED CARD RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_fred_card(key: str, cfg: dict, df) -> None:
    """
    Renders a card for FRED-sourced indicators.
    Layout:
      Claims   — headline = latest weekly print (K), badge = WoW change
      ADP      — headline = latest MoM print (K),    badge = vs same month prior year
      Sentiment— headline = latest index level,       badge = MoM change + YoY comparison
    Chart shows actual prints (no MoM/YoY toggle), with expand button.
    """
    color = cfg["color"]

    # ── Price index (Core PCE): delegate to render_card with FRED badge ──
    if cfg.get("transform") == "price_index":
        # render_card handles all price_index logic (MoM%/YoY%, charts, tabs)
        # Override the source badge to show FRED instead of BLS
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
          <div style="display:flex;align-items:center;gap:10px">
            <span style="width:9px;height:9px;border-radius:50%;background:{color};
                   box-shadow:0 0 10px {color}70;display:inline-block;flex-shrink:0"></span>
            <span class="ind-name">{cfg['name']}</span>
          </div>
          <div style="display:flex;gap:6px;align-items:center">
            <span class="ind-src" style="background:rgba(251,191,36,.07);border-color:rgba(251,191,36,.2);color:#FCD34D">FRED</span>
            <span class="ind-freq">{cfg['freq'].upper()}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if df is None or df.empty:
            st.warning("Data unavailable", icon="⚠️")
            return
        # Use compute_series + same stat/chart logic as BLS price_index cards
        df_c  = compute_series(df, "price_index")
        valid = df_c.dropna(subset=["mom", "yoy"])
        if len(valid) < 2:
            st.warning("Insufficient data", icon="⚠️")
            return
        last     = valid.iloc[-1]
        prev     = valid.iloc[-2]
        date_str = last["date"].strftime("%b %Y")
        mom_val  = last["mom"]
        yoy_val  = last["yoy"]
        mom_delta  = mom_val - prev["mom"]
        yoy_delta  = yoy_val - prev["yoy"]
        mom_up     = is_positive_signal(mom_val,   key)
        delta_up   = is_positive_signal(mom_delta, key)
        yoy_dlt_up = is_positive_signal(yoy_delta, key)
        mom_str     = fmt_val(mom_val,   cfg, "mom")
        yoy_str     = fmt_val(yoy_val,   cfg, "yoy")
        mom_dlt_str = fmt_val(mom_delta, cfg, "mom") + " vs prior"
        yoy_dlt_str = fmt_val(yoy_delta, cfg, "yoy") + " vs prior"
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(stat_box_html("Month-over-Month", mom_str, mom_dlt_str, delta_up, date_str), unsafe_allow_html=True)
        with c2:
            st.markdown(stat_box_html("Year-over-Year",   yoy_str, yoy_dlt_str, yoy_dlt_up, date_str), unsafe_allow_html=True)
        # Charts with MoM/YoY toggle — same as BLS price_index cards
        st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)
        tab_mom, tab_yoy = st.tabs(["  MoM  ", "  YoY  "])
        with tab_mom:
            fig_mom = make_chart(df_c, cfg, "mom", height=200)
            col_chart, col_btn = st.columns([10, 1])
            with col_chart:
                st.plotly_chart(fig_mom, use_container_width=True, config={"displayModeBar": False}, key=f"plt_mom_{key}")
            with col_btn:
                if st.button("⛶", key=f"exp_mom_{key}", help="Expand chart"):
                    st.session_state["expanded"] = {"key": key, "which": "mom", "title": f"{cfg['name']} — Month-over-Month", "cfg": cfg, "df_c": df_c}
                    st.rerun()
            st.caption(cfg["full"])
        with tab_yoy:
            fig_yoy = make_chart(df_c, cfg, "yoy", height=200)
            col_chart2, col_btn2 = st.columns([10, 1])
            with col_chart2:
                st.plotly_chart(fig_yoy, use_container_width=True, config={"displayModeBar": False}, key=f"plt_yoy_{key}")
            with col_btn2:
                if st.button("⛶", key=f"exp_yoy_{key}", help="Expand chart"):
                    st.session_state["expanded"] = {"key": key, "which": "yoy", "title": f"{cfg['name']} — Year-over-Year", "cfg": cfg, "df_c": df_c}
                    st.rerun()
            st.caption(cfg["full"])
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Label row ─────────────────────────────────────────────────────────
    src_label = cfg.get("source", "FRED")
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="width:9px;height:9px;border-radius:50%;background:{color};
               box-shadow:0 0 10px {color}70;display:inline-block;flex-shrink:0"></span>
        <span class="ind-name">{cfg['name']}</span>
      </div>
      <div style="display:flex;gap:6px;align-items:center">
        <span class="ind-src" style="background:rgba(251,191,36,.07);border-color:rgba(251,191,36,.2);color:#FCD34D">FRED</span>
        <span class="ind-freq">{cfg['freq'].upper()}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty or len(df) < 2:
        st.warning("Data unavailable", icon="⚠️")
        return

    df = df.sort_values("date").reset_index(drop=True)
    last      = df.iloc[-1]
    prev1     = df.iloc[-2]
    last_val  = last["value"]
    prev1_val = prev1["value"]
    date_str  = last["date"].strftime("%d %b %Y") if cfg["freq"] == "Weekly" else last["date"].strftime("%b %Y")

    def fmt_k(v, sign=True):
        s = "+" if (v >= 0 and sign) else ("" if not sign else "")
        return f"{s}{int(round(v))}K"

    def fmt_idx(v):
        return f"{v:.1f}"

    # ── Claims ────────────────────────────────────────────────────────────
    if cfg["transform"] == "claims":
        wow        = last_val - prev1_val
        wow_up     = wow <= 0    # fewer claims = positive signal
        wow_sign   = "+" if wow >= 0 else ""
        wow_str    = f"{wow_sign}{int(round(wow))}K vs prior week"
        prev_str   = f"Prior: {int(round(prev1_val))}K ({prev1['date'].strftime('%d %b')})"

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(stat_box_html(
                "Latest Print", fmt_k(last_val, sign=False),
                wow_str, wow_up, date_str
            ), unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-period">Prior Week</div>
              <div class="stat-val">{fmt_k(prev1_val, sign=False)}</div>
              <div class="stat-date">{prev1['date'].strftime('%d %b %Y')}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── ADP ───────────────────────────────────────────────────────────────
    elif cfg["transform"] == "adp":
        # ADP series is already a change (K) — last_val IS the MoM print
        # YoY: same month 1 year ago by exact date match
        target_yoy = last["date"] - pd.DateOffset(months=12)
        yoy_row    = df[df["date"] == target_yoy]
        yoy_val    = yoy_row.iloc[0]["value"] if not yoy_row.empty else None
        yoy_date   = yoy_row.iloc[0]["date"].strftime("%b %Y") if not yoy_row.empty else "—"

        if yoy_val is not None:
            yoy_diff     = last_val - yoy_val
            yoy_diff_s   = "+" if yoy_diff >= 0 else ""
            yoy_prev_s   = "+" if yoy_val  >= 0 else ""
            yoy_dlt_str  = f"{yoy_diff_s}{int(round(yoy_diff))}K vs {yoy_date}: {yoy_prev_s}{int(round(yoy_val))}K"
            yoy_dlt_up   = yoy_diff >= 0
        else:
            yoy_dlt_str = "—"
            yoy_dlt_up  = True

        # MoM badge: vs prior month
        prev_s   = "+" if prev1_val >= 0 else ""
        mom_str  = f"vs {prev1['date'].strftime('%b %Y')}: {prev_s}{int(round(prev1_val))}K"
        mom_up   = last_val >= prev1_val

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(stat_box_html(
                "Month-over-Month", fmt_k(last_val),
                mom_str, mom_up, date_str
            ), unsafe_allow_html=True)
        with c2:
            st.markdown(stat_box_html(
                "Year-over-Year", fmt_k(last_val),
                yoy_dlt_str, yoy_dlt_up, date_str
            ), unsafe_allow_html=True)

    # ── Michigan Sentiment ────────────────────────────────────────────────
    elif cfg["transform"] == "sentiment":
        mom_chg  = last_val - prev1_val
        mom_up   = mom_chg >= 0
        mom_sign = "+" if mom_chg >= 0 else ""
        mom_str  = f"{mom_sign}{mom_chg:.1f} vs {prev1['date'].strftime('%b %Y')}: {prev1_val:.1f}"

        # Previous box: just show prior print with no delta badge
        prev_date_str = prev1["date"].strftime("%b %Y")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(stat_box_html(
                "Latest Print", fmt_idx(last_val),
                mom_str, mom_up, date_str
            ), unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-period">Previous</div>
              <div class="stat-val">{fmt_idx(prev1_val)}</div>
              <div class="stat-date">{prev_date_str}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Chart — actual prints, no MoM/YoY toggle ─────────────────────────
    st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)

    # Build chart using raw value column
    plot_df = df.tail(104 if cfg["freq"] == "Weekly" else 60)
    r_c = int(color[1:3], 16)
    g_c = int(color[3:5], 16)
    b_c = int(color[5:7], 16)
    fill_color = f"rgba({r_c},{g_c},{b_c},0.1)"

    # ADP: bar chart (it's a change series, positive/negative)
    if cfg["transform"] == "adp":
        bar_colors  = ["rgba(15,214,138,.7)"  if v >= 0 else "rgba(240,72,90,.7)"  for v in plot_df["value"]]
        bar_borders = ["rgba(15,214,138,.95)" if v >= 0 else "rgba(240,72,90,.95)" for v in plot_df["value"]]
        fig = go.Figure(go.Bar(
            x=plot_df["date"], y=plot_df["value"],
            marker_color=bar_colors,
            marker_line_color=bar_borders,
            marker_line_width=1,
            hovertemplate="%{x|%b %Y}<br><b>%{y:+.0f}K</b><extra></extra>",
        ))
        fig.add_hline(y=0, line_color="rgba(0,0,0,.12)", line_width=1)
    else:
        hover_fmt = "%{x|%d %b '%y}<br><b>%{y:.0f}K</b>" if cfg["freq"] == "Weekly" else "%{x|%b %Y}<br><b>%{y:.1f}</b>"
        fig = go.Figure(go.Scatter(
            x=plot_df["date"], y=plot_df["value"],
            mode="lines",
            line=dict(color=color, width=1.8),
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate=hover_fmt + "<extra></extra>",
        ))
        # Floor y-axis so movements are visible
        y_min = max(0, plot_df["value"].min() * 0.9)
        y_max = plot_df["value"].max() * 1.05
        fig.update_yaxes(range=[y_min, y_max])

    fig.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#8898BB", size=10),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(size=10, color="#1A2540"),
                   tickformat="%b '%y", nticks=6),
        yaxis=dict(showgrid=True, gridcolor="rgba(120,140,200,.06)", zeroline=False,
                   tickfont=dict(size=10, color="#1A2540"), nticks=5),
        hoverlabel=dict(bgcolor="#F0F4FF", bordercolor="rgba(91,141,239,.3)",
                        font=dict(family="Inter, sans-serif", size=12, color="#1A2540")),
        showlegend=False,
    )

    col_chart, col_btn = st.columns([10, 1])
    with col_chart:
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False}, key=f"plt_fred_{key}")
    with col_btn:
        if st.button("⛶", key=f"exp_fred_{key}", help="Expand chart"):
            st.session_state["expanded"] = {
                "key": key, "which": "value",
                "title": cfg["name"],
                "cfg": cfg, "df_c": df.assign(mom=df["value"], yoy=df["value"])
            }
            st.rerun()
    st.caption(cfg["full"])
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MARKETS SCREENER — DATA
# ─────────────────────────────────────────────────────────────────────────────

_SP500_FALLBACK_DATA = [
    ("AAPL","Apple Inc.","Information Technology"),
    ("MSFT","Microsoft Corp.","Information Technology"),
    ("NVDA","NVIDIA Corp.","Information Technology"),
    ("AVGO","Broadcom Inc.","Information Technology"),
    ("ORCL","Oracle Corp.","Information Technology"),
    ("CRM","Salesforce Inc.","Information Technology"),
    ("ACN","Accenture plc","Information Technology"),
    ("CSCO","Cisco Systems","Information Technology"),
    ("IBM","IBM Corp.","Information Technology"),
    ("AMD","Advanced Micro Devices","Information Technology"),
    ("QCOM","Qualcomm Inc.","Information Technology"),
    ("TXN","Texas Instruments","Information Technology"),
    ("INTC","Intel Corp.","Information Technology"),
    ("AMAT","Applied Materials","Information Technology"),
    ("MU","Micron Technology","Information Technology"),
    ("ADI","Analog Devices","Information Technology"),
    ("KLAC","KLA Corp.","Information Technology"),
    ("LRCX","Lam Research","Information Technology"),
    ("NOW","ServiceNow Inc.","Information Technology"),
    ("PANW","Palo Alto Networks","Information Technology"),
    ("CDNS","Cadence Design Systems","Information Technology"),
    ("SNPS","Synopsys Inc.","Information Technology"),
    ("MSI","Motorola Solutions","Information Technology"),
    ("APH","Amphenol Corp.","Information Technology"),
    ("TEL","TE Connectivity","Information Technology"),
    ("FTNT","Fortinet Inc.","Information Technology"),
    ("HPQ","HP Inc.","Information Technology"),
    ("HPE","Hewlett Packard Enterprise","Information Technology"),
    ("KEYS","Keysight Technologies","Information Technology"),
    ("INTU","Intuit Inc.","Information Technology"),
    ("ADSK","Autodesk Inc.","Information Technology"),
    ("ANSS","ANSYS Inc.","Information Technology"),
    ("PTC","PTC Inc.","Information Technology"),
    ("GEN","Gen Digital","Information Technology"),
    ("FFIV","F5 Inc.","Information Technology"),
    ("JNPR","Juniper Networks","Information Technology"),
    ("WDC","Western Digital","Information Technology"),
    ("STX","Seagate Technology","Information Technology"),
    ("NTAP","NetApp Inc.","Information Technology"),
    ("ENPH","Enphase Energy","Information Technology"),
    ("JPM","JPMorgan Chase","Financials"),
    ("BAC","Bank of America","Financials"),
    ("WFC","Wells Fargo","Financials"),
    ("GS","Goldman Sachs","Financials"),
    ("MS","Morgan Stanley","Financials"),
    ("BLK","BlackRock Inc.","Financials"),
    ("SCHW","Charles Schwab","Financials"),
    ("AXP","American Express","Financials"),
    ("CB","Chubb Ltd.","Financials"),
    ("MMC","Marsh & McLennan","Financials"),
    ("PGR","Progressive Corp.","Financials"),
    ("USB","U.S. Bancorp","Financials"),
    ("TFC","Truist Financial","Financials"),
    ("COF","Capital One Financial","Financials"),
    ("PNC","PNC Financial Services","Financials"),
    ("ICE","Intercontinental Exchange","Financials"),
    ("CME","CME Group","Financials"),
    ("SPGI","S&P Global Inc.","Financials"),
    ("MCO","Moody's Corp.","Financials"),
    ("AON","Aon plc","Financials"),
    ("MET","MetLife Inc.","Financials"),
    ("PRU","Prudential Financial","Financials"),
    ("ALL","Allstate Corp.","Financials"),
    ("AFL","Aflac Inc.","Financials"),
    ("AIG","American International Group","Financials"),
    ("BK","Bank of New York Mellon","Financials"),
    ("STT","State Street Corp.","Financials"),
    ("MTB","M&T Bank Corp.","Financials"),
    ("FITB","Fifth Third Bancorp","Financials"),
    ("RF","Regions Financial","Financials"),
    ("HBAN","Huntington Bancshares","Financials"),
    ("CFG","Citizens Financial","Financials"),
    ("KEY","KeyCorp","Financials"),
    ("PYPL","PayPal Holdings","Financials"),
    ("V","Visa Inc.","Financials"),
    ("MA","Mastercard Inc.","Financials"),
    ("LLY","Eli Lilly and Co.","Health Care"),
    ("UNH","UnitedHealth Group","Health Care"),
    ("JNJ","Johnson & Johnson","Health Care"),
    ("ABBV","AbbVie Inc.","Health Care"),
    ("MRK","Merck & Co.","Health Care"),
    ("TMO","Thermo Fisher Scientific","Health Care"),
    ("ABT","Abbott Laboratories","Health Care"),
    ("DHR","Danaher Corp.","Health Care"),
    ("BMY","Bristol-Myers Squibb","Health Care"),
    ("AMGN","Amgen Inc.","Health Care"),
    ("PFE","Pfizer Inc.","Health Care"),
    ("GILD","Gilead Sciences","Health Care"),
    ("SYK","Stryker Corp.","Health Care"),
    ("MDT","Medtronic plc","Health Care"),
    ("ELV","Elevance Health","Health Care"),
    ("CI","Cigna Group","Health Care"),
    ("CVS","CVS Health Corp.","Health Care"),
    ("HUM","Humana Inc.","Health Care"),
    ("ISRG","Intuitive Surgical","Health Care"),
    ("BSX","Boston Scientific","Health Care"),
    ("BDX","Becton Dickinson","Health Care"),
    ("IQV","IQVIA Holdings","Health Care"),
    ("VRTX","Vertex Pharmaceuticals","Health Care"),
    ("REGN","Regeneron Pharmaceuticals","Health Care"),
    ("BIIB","Biogen Inc.","Health Care"),
    ("MRNA","Moderna Inc.","Health Care"),
    ("HCA","HCA Healthcare","Health Care"),
    ("MCK","McKesson Corp.","Health Care"),
    ("GEHC","GE HealthCare","Health Care"),
    ("IDXX","IDEXX Laboratories","Health Care"),
    ("ALGN","Align Technology","Health Care"),
    ("DXCM","DexCom Inc.","Health Care"),
    ("AMZN","Amazon.com Inc.","Consumer Discretionary"),
    ("TSLA","Tesla Inc.","Consumer Discretionary"),
    ("HD","Home Depot","Consumer Discretionary"),
    ("MCD","McDonald's Corp.","Consumer Discretionary"),
    ("NKE","Nike Inc.","Consumer Discretionary"),
    ("LOW","Lowe's Companies","Consumer Discretionary"),
    ("SBUX","Starbucks Corp.","Consumer Discretionary"),
    ("TJX","TJX Companies","Consumer Discretionary"),
    ("BKNG","Booking Holdings","Consumer Discretionary"),
    ("GM","General Motors","Consumer Discretionary"),
    ("F","Ford Motor Co.","Consumer Discretionary"),
    ("ORLY","O'Reilly Automotive","Consumer Discretionary"),
    ("AZO","AutoZone Inc.","Consumer Discretionary"),
    ("MAR","Marriott International","Consumer Discretionary"),
    ("HLT","Hilton Worldwide","Consumer Discretionary"),
    ("EXPE","Expedia Group","Consumer Discretionary"),
    ("RCL","Royal Caribbean","Consumer Discretionary"),
    ("CCL","Carnival Corp.","Consumer Discretionary"),
    ("DHI","D.R. Horton","Consumer Discretionary"),
    ("LEN","Lennar Corp.","Consumer Discretionary"),
    ("PHM","PulteGroup Inc.","Consumer Discretionary"),
    ("ROST","Ross Stores","Consumer Discretionary"),
    ("BBY","Best Buy Co.","Consumer Discretionary"),
    ("DRI","Darden Restaurants","Consumer Discretionary"),
    ("YUM","Yum! Brands","Consumer Discretionary"),
    ("CMG","Chipotle Mexican Grill","Consumer Discretionary"),
    ("EBAY","eBay Inc.","Consumer Discretionary"),
    ("ETSY","Etsy Inc.","Consumer Discretionary"),
    ("MELI","MercadoLibre","Consumer Discretionary"),
    ("LULU","Lululemon Athletica","Consumer Discretionary"),
    ("DASH","DoorDash Inc.","Consumer Discretionary"),
    ("ABNB","Airbnb Inc.","Consumer Discretionary"),
    ("DLTR","Dollar Tree","Consumer Discretionary"),
    ("META","Meta Platforms","Communication Services"),
    ("GOOGL","Alphabet Inc. Class A","Communication Services"),
    ("GOOG","Alphabet Inc. Class C","Communication Services"),
    ("NFLX","Netflix Inc.","Communication Services"),
    ("DIS","Walt Disney Co.","Communication Services"),
    ("CMCSA","Comcast Corp.","Communication Services"),
    ("T","AT&T Inc.","Communication Services"),
    ("VZ","Verizon Communications","Communication Services"),
    ("TMUS","T-Mobile US","Communication Services"),
    ("CHTR","Charter Communications","Communication Services"),
    ("EA","Electronic Arts","Communication Services"),
    ("TTWO","Take-Two Interactive","Communication Services"),
    ("OMC","Omnicom Group","Communication Services"),
    ("WBD","Warner Bros. Discovery","Communication Services"),
    ("PARA","Paramount Global","Communication Services"),
    ("FOX","Fox Corp. Class B","Communication Services"),
    ("FOXA","Fox Corp. Class A","Communication Services"),
    ("CAT","Caterpillar Inc.","Industrials"),
    ("RTX","RTX Corp.","Industrials"),
    ("HON","Honeywell International","Industrials"),
    ("UPS","United Parcel Service","Industrials"),
    ("BA","Boeing Co.","Industrials"),
    ("GE","GE Aerospace","Industrials"),
    ("LMT","Lockheed Martin","Industrials"),
    ("DE","Deere & Co.","Industrials"),
    ("MMM","3M Co.","Industrials"),
    ("EMR","Emerson Electric","Industrials"),
    ("ETN","Eaton Corp.","Industrials"),
    ("ITW","Illinois Tool Works","Industrials"),
    ("PH","Parker Hannifin","Industrials"),
    ("GD","General Dynamics","Industrials"),
    ("NOC","Northrop Grumman","Industrials"),
    ("TDG","TransDigm Group","Industrials"),
    ("FDX","FedEx Corp.","Industrials"),
    ("CSX","CSX Corp.","Industrials"),
    ("UNP","Union Pacific Corp.","Industrials"),
    ("NSC","Norfolk Southern","Industrials"),
    ("WM","Waste Management","Industrials"),
    ("RSG","Republic Services","Industrials"),
    ("CTAS","Cintas Corp.","Industrials"),
    ("FAST","Fastenal Co.","Industrials"),
    ("PWR","Quanta Services","Industrials"),
    ("VRSK","Verisk Analytics","Industrials"),
    ("DAL","Delta Air Lines","Industrials"),
    ("UAL","United Airlines","Industrials"),
    ("LUV","Southwest Airlines","Industrials"),
    ("AAL","American Airlines","Industrials"),
    ("PCAR","PACCAR Inc.","Industrials"),
    ("ODFL","Old Dominion Freight","Industrials"),
    ("CPRT","Copart Inc.","Industrials"),
    ("PAYX","Paychex Inc.","Industrials"),
    ("WMT","Walmart Inc.","Consumer Staples"),
    ("PG","Procter & Gamble","Consumer Staples"),
    ("COST","Costco Wholesale","Consumer Staples"),
    ("KO","Coca-Cola Co.","Consumer Staples"),
    ("PEP","PepsiCo Inc.","Consumer Staples"),
    ("PM","Philip Morris","Consumer Staples"),
    ("MO","Altria Group","Consumer Staples"),
    ("MDLZ","Mondelez International","Consumer Staples"),
    ("CL","Colgate-Palmolive","Consumer Staples"),
    ("KMB","Kimberly-Clark","Consumer Staples"),
    ("GIS","General Mills","Consumer Staples"),
    ("KR","Kroger Co.","Consumer Staples"),
    ("SYY","Sysco Corp.","Consumer Staples"),
    ("ADM","Archer-Daniels-Midland","Consumer Staples"),
    ("TSN","Tyson Foods","Consumer Staples"),
    ("MNST","Monster Beverage","Consumer Staples"),
    ("KDP","Keurig Dr Pepper","Consumer Staples"),
    ("WBA","Walgreens Boots Alliance","Consumer Staples"),
    ("XOM","ExxonMobil Corp.","Energy"),
    ("CVX","Chevron Corp.","Energy"),
    ("COP","ConocoPhillips","Energy"),
    ("EOG","EOG Resources","Energy"),
    ("SLB","SLB (Schlumberger)","Energy"),
    ("MPC","Marathon Petroleum","Energy"),
    ("PSX","Phillips 66","Energy"),
    ("VLO","Valero Energy","Energy"),
    ("DVN","Devon Energy","Energy"),
    ("HAL","Halliburton Co.","Energy"),
    ("BKR","Baker Hughes","Energy"),
    ("OXY","Occidental Petroleum","Energy"),
    ("HES","Hess Corp.","Energy"),
    ("FANG","Diamondback Energy","Energy"),
    ("MRO","Marathon Oil","Energy"),
    ("APA","APA Corp.","Energy"),
    ("CTRA","Coterra Energy","Energy"),
    ("EQT","EQT Corp.","Energy"),
    ("KMI","Kinder Morgan","Energy"),
    ("NEE","NextEra Energy","Utilities"),
    ("SO","Southern Co.","Utilities"),
    ("DUK","Duke Energy","Utilities"),
    ("SRE","Sempra","Utilities"),
    ("AEP","American Electric Power","Utilities"),
    ("D","Dominion Energy","Utilities"),
    ("EXC","Exelon Corp.","Utilities"),
    ("XEL","Xcel Energy","Utilities"),
    ("PCG","PG&E Corp.","Utilities"),
    ("ED","Consolidated Edison","Utilities"),
    ("ETR","Entergy Corp.","Utilities"),
    ("FE","FirstEnergy Corp.","Utilities"),
    ("PPL","PPL Corp.","Utilities"),
    ("AES","AES Corp.","Utilities"),
    ("AWK","American Water Works","Utilities"),
    ("WEC","WEC Energy Group","Utilities"),
    ("CMS","CMS Energy","Utilities"),
    ("CNP","CenterPoint Energy","Utilities"),
    ("CEG","Constellation Energy","Utilities"),
    ("PLD","Prologis Inc.","Real Estate"),
    ("AMT","American Tower","Real Estate"),
    ("EQIX","Equinix Inc.","Real Estate"),
    ("CCI","Crown Castle","Real Estate"),
    ("SPG","Simon Property Group","Real Estate"),
    ("O","Realty Income","Real Estate"),
    ("VICI","VICI Properties","Real Estate"),
    ("WELL","Welltower Inc.","Real Estate"),
    ("DLR","Digital Realty Trust","Real Estate"),
    ("PSA","Public Storage","Real Estate"),
    ("AVB","AvalonBay Communities","Real Estate"),
    ("EQR","Equity Residential","Real Estate"),
    ("INVH","Invitation Homes","Real Estate"),
    ("VTR","Ventas Inc.","Real Estate"),
    ("ARE","Alexandria Real Estate","Real Estate"),
    ("BXP","BXP Inc.","Real Estate"),
    ("KIM","Kimco Realty","Real Estate"),
    ("WY","Weyerhaeuser Co.","Real Estate"),
    ("HST","Host Hotels","Real Estate"),
    ("LIN","Linde plc","Materials"),
    ("APD","Air Products","Materials"),
    ("SHW","Sherwin-Williams","Materials"),
    ("FCX","Freeport-McMoRan","Materials"),
    ("NEM","Newmont Corp.","Materials"),
    ("ECL","Ecolab Inc.","Materials"),
    ("DD","DuPont de Nemours","Materials"),
    ("DOW","Dow Inc.","Materials"),
    ("LYB","LyondellBasell","Materials"),
    ("NUE","Nucor Corp.","Materials"),
    ("STLD","Steel Dynamics","Materials"),
    ("CF","CF Industries","Materials"),
    ("MOS","Mosaic Co.","Materials"),
    ("IP","International Paper","Materials"),
    ("PKG","Packaging Corp.","Materials"),
    ("ALB","Albemarle Corp.","Materials"),
    ("EMN","Eastman Chemical","Materials"),
    ("RPM","RPM International","Materials"),
]

_NDX100_DATA = [
    ("AAPL","Apple Inc.","Information Technology"),
    ("MSFT","Microsoft Corp.","Information Technology"),
    ("NVDA","NVIDIA Corp.","Information Technology"),
    ("AMZN","Amazon.com Inc.","Consumer Discretionary"),
    ("META","Meta Platforms","Communication Services"),
    ("GOOGL","Alphabet Inc. Class A","Communication Services"),
    ("GOOG","Alphabet Inc. Class C","Communication Services"),
    ("TSLA","Tesla Inc.","Consumer Discretionary"),
    ("AVGO","Broadcom Inc.","Information Technology"),
    ("COST","Costco Wholesale","Consumer Staples"),
    ("NFLX","Netflix Inc.","Communication Services"),
    ("AMD","Advanced Micro Devices","Information Technology"),
    ("QCOM","Qualcomm Inc.","Information Technology"),
    ("TMUS","T-Mobile US","Communication Services"),
    ("LIN","Linde plc","Materials"),
    ("AMAT","Applied Materials","Information Technology"),
    ("INTU","Intuit Inc.","Information Technology"),
    ("ISRG","Intuitive Surgical","Health Care"),
    ("TXN","Texas Instruments","Information Technology"),
    ("BKNG","Booking Holdings","Consumer Discretionary"),
    ("AMGN","Amgen Inc.","Health Care"),
    ("CMCSA","Comcast Corp.","Communication Services"),
    ("HON","Honeywell International","Industrials"),
    ("VRTX","Vertex Pharmaceuticals","Health Care"),
    ("REGN","Regeneron Pharmaceuticals","Health Care"),
    ("MU","Micron Technology","Information Technology"),
    ("PANW","Palo Alto Networks","Information Technology"),
    ("KLAC","KLA Corp.","Information Technology"),
    ("LRCX","Lam Research","Information Technology"),
    ("ADI","Analog Devices","Information Technology"),
    ("CDNS","Cadence Design Systems","Information Technology"),
    ("SNPS","Synopsys Inc.","Information Technology"),
    ("MELI","MercadoLibre","Consumer Discretionary"),
    ("CRWD","CrowdStrike Holdings","Information Technology"),
    ("CSX","CSX Corp.","Industrials"),
    ("ORLY","O'Reilly Automotive","Consumer Discretionary"),
    ("MAR","Marriott International","Consumer Discretionary"),
    ("MNST","Monster Beverage","Consumer Staples"),
    ("FTNT","Fortinet Inc.","Information Technology"),
    ("PCAR","PACCAR Inc.","Industrials"),
    ("ADSK","Autodesk Inc.","Information Technology"),
    ("MRVL","Marvell Technology","Information Technology"),
    ("ASML","ASML Holding","Information Technology"),
    ("AZN","AstraZeneca","Health Care"),
    ("TTD","The Trade Desk","Communication Services"),
    ("DXCM","DexCom Inc.","Health Care"),
    ("ON","ON Semiconductor","Information Technology"),
    ("NXPI","NXP Semiconductors","Information Technology"),
    ("WDAY","Workday Inc.","Information Technology"),
    ("FAST","Fastenal Co.","Industrials"),
    ("BIIB","Biogen Inc.","Health Care"),
    ("IDXX","IDEXX Laboratories","Health Care"),
    ("ROST","Ross Stores","Consumer Discretionary"),
    ("ODFL","Old Dominion Freight","Industrials"),
    ("CPRT","Copart Inc.","Industrials"),
    ("CTAS","Cintas Corp.","Industrials"),
    ("EA","Electronic Arts","Communication Services"),
    ("GEHC","GE HealthCare","Health Care"),
    ("AEP","American Electric Power","Utilities"),
    ("XEL","Xcel Energy","Utilities"),
    ("KDP","Keurig Dr Pepper","Consumer Staples"),
    ("PAYX","Paychex Inc.","Industrials"),
    ("VRSK","Verisk Analytics","Industrials"),
    ("EXC","Exelon Corp.","Utilities"),
    ("FANG","Diamondback Energy","Energy"),
    ("CTSH","Cognizant Technology","Information Technology"),
    ("TEAM","Atlassian Corp.","Information Technology"),
    ("ZS","Zscaler Inc.","Information Technology"),
    ("DASH","DoorDash Inc.","Consumer Discretionary"),
    ("ABNB","Airbnb Inc.","Consumer Discretionary"),
    ("CEG","Constellation Energy","Utilities"),
    ("ILMN","Illumina Inc.","Health Care"),
    ("MRNA","Moderna Inc.","Health Care"),
    ("DLTR","Dollar Tree","Consumer Discretionary"),
    ("SBUX","Starbucks Corp.","Consumer Discretionary"),
    ("PYPL","PayPal Holdings","Financials"),
    ("MCHP","Microchip Technology","Information Technology"),
    ("LULU","Lululemon Athletica","Consumer Discretionary"),
    ("TTWO","Take-Two Interactive","Communication Services"),
    ("DDOG","Datadog Inc.","Information Technology"),
    ("EBAY","eBay Inc.","Consumer Discretionary"),
    ("PDD","PDD Holdings","Consumer Discretionary"),
    ("ANSS","ANSYS Inc.","Information Technology"),
    ("ENPH","Enphase Energy","Information Technology"),
    ("SMCI","Super Micro Computer","Information Technology"),
    ("ALGN","Align Technology","Health Care"),
    ("ARM","Arm Holdings","Information Technology"),
    ("APP","Applovin Corp.","Information Technology"),
    ("V","Visa Inc.","Financials"),
    ("MA","Mastercard Inc.","Financials"),
    ("WBA","Walgreens Boots Alliance","Consumer Staples"),
    ("NTES","NetEase Inc.","Communication Services"),
    ("WBD","Warner Bros. Discovery","Communication Services"),
    ("NOW","ServiceNow Inc.","Information Technology"),
    ("GFS","GlobalFoundries","Information Technology"),
    ("SIRI","Sirius XM","Communication Services"),
    ("MDLZ","Mondelez International","Consumer Staples"),
    ("RIVN","Rivian Automotive","Consumer Discretionary"),
]

# ─────────────────────────────────────────────────────────────────────────────
# ETF HOLDINGS — constituent lists driven by SPY / QQQ holdings files
# ─────────────────────────────────────────────────────────────────────────────
# Holdings files (as of 27 May 2026) live alongside this script in ./data/.
# Weights are recomputed live as shares_i * price_i / Σ(shares * price); the
# Weight column in the files is only a fallback for display before prices load.
import os
import re as _re

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:                       # __file__ undefined in some runners
    _HERE = os.getcwd()


def _find_data_file(filename: str) -> str:
    """
    Locate a holdings file across the layouts the app might run under
    (script dir, ./data, ./markets_data, CWD, repo root). Returns the first
    existing path, or the primary ./data path (for a clear error message)
    if none are found.
    """
    candidates = [
        os.path.join(_HERE, "data", filename),
        os.path.join(_HERE, filename),
        os.path.join(_HERE, "markets_data", filename),
        os.path.join(os.getcwd(), "data", filename),
        os.path.join(os.getcwd(), filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]


_DATA_DIR  = os.path.join(_HERE, "data")
_SPY_FILE  = _find_data_file("SPY.xlsx")
_QQQ_FILE  = _find_data_file("QQQ.csv")

# Wikipedia pages — used as the fast primary source for the bulk of tickers.
# Results are remapped to Yahoo Finance's sector terminology so the sector
# filter in the screener is consistent with what yfinance returns for the
# edge-case tickers that Wikipedia misses.
_SP500_WIKI  = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
_NDX100_WIKI = "https://en.wikipedia.org/wiki/Nasdaq-100"

# GICS (Wikipedia) → Yahoo Finance sector name mapping.
# Yahoo Finance uses slightly different names for five sectors; the rest match.
_GICS_TO_YAHOO = {
    "Information Technology": "Technology",
    "Health Care":            "Healthcare",
    "Consumer Discretionary": "Consumer Cyclical",
    "Consumer Staples":       "Consumer Defensive",
    "Financials":             "Financial Services",
    "Materials":              "Basic Materials",
    # The remaining six are identical in both taxonomies:
    "Communication Services": "Communication Services",
    "Industrials":            "Industrials",
    "Energy":                 "Energy",
    "Real Estate":            "Real Estate",
    "Utilities":              "Utilities",
}


def _to_yf(t: str) -> str:
    """Yahoo Finance ticker convention: dots become dashes (BRK.B -> BRK-B)."""
    return str(t).strip().upper().replace(".", "-")


def _is_priceable(raw: str) -> bool:
    """
    True if the holding is a normal listed equity Yahoo can price.
    Filters out cash (USD, '--'), index futures (NQM6, NQM6_), and Bloomberg
    placeholder tickers containing digits (e.g. 2602335D). These are summed
    and reported as 'Cash & Other' instead.
    """
    t = _to_yf(raw)
    if t in ("USD", "--", "-", "", "NAN", "NONE"):
        return False
    if _re.search(r"\d", t):          # futures / placeholder codes
        return False
    return bool(_re.match(r"^[A-Z][A-Z\-]{0,6}$", t))


def _parse_shares(x) -> float:
    """Shares Held may be a comma-formatted string ('114,012,363.00') or a number."""
    if pd.isna(x):
        return float("nan")
    return float(str(x).replace(",", "").strip())


@st.cache_data(ttl=3600, show_spinner=False)
def _load_gics_map(version: str = "v4") -> dict:
    """
    Build {yf_ticker: Yahoo Finance sector name}.

    Three-pass approach, all returning Yahoo Finance sector terminology
    so the screener's sector filter is consistent across every ticker:

      Pass 1 — Wikipedia S&P 500 page (batched, ~503 tickers, fast).
               Covers the full SPY universe plus the majority of QQQ names
               dual-listed in the S&P 500. GICS names are remapped to Yahoo
               Finance equivalents via _GICS_TO_YAHOO.

      Pass 2 — Wikipedia Nasdaq-100 page (batched, fills QQQ-only gaps
               where the table carries sector data). Same remapping applied.

      Pass 3 — yfinance .info['sector'] for any ticker still missing after
               both Wikipedia passes (non-US names like ASML/SHOP/CCEP,
               recent IPOs like SPCX, any future edge cases). Yahoo Finance
               returns its native sector names directly — no mapping needed.
               Only called for the handful of tickers that fall through
               (~10-20), so the per-ticker overhead is negligible.

    Falls back to the hardcoded legacy lists (in GICS names, remapped) only
    if Wikipedia is completely unreachable. Cached for 24h.
    """
    from io import StringIO as _SIO
    from concurrent.futures import ThreadPoolExecutor, as_completed

    HDR = {"User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )}
    gmap = {}

    def _find_col(df, *keywords):
        for col in df.columns:
            if any(kw in col.lower() for kw in keywords):
                return col
        return None

    def _remap(sec: str) -> str:
        """Convert a GICS sector name to its Yahoo Finance equivalent."""
        return _GICS_TO_YAHOO.get(str(sec).strip(), str(sec).strip())

    # ── Pass 1: S&P 500 Wikipedia ────────────────────────────────────────
    try:
        r     = requests.get(_SP500_WIKI, headers=HDR, timeout=20)
        r.raise_for_status()
        sp500 = pd.read_html(_SIO(r.text), attrs={"id": "constituents"})[0]
        sym_col = _find_col(sp500, "symbol", "ticker")
        sec_col = _find_col(sp500, "gics sector", "sector")
        if sym_col and sec_col:
            for sym, sec in zip(sp500[sym_col], sp500[sec_col]):
                if pd.notna(sym) and pd.notna(sec):
                    gmap[_to_yf(str(sym))] = _remap(sec)
            print(f"Sectors: loaded {len(gmap)} S&P 500 entries from Wikipedia")
        else:
            raise ValueError(f"Expected columns not found: {sp500.columns.tolist()}")
    except Exception as e:
        print(f"Sectors: S&P 500 Wikipedia fetch failed: {e}")

    # ── Pass 2: Nasdaq-100 Wikipedia (QQQ-only gaps) ─────────────────────
    try:
        r2 = requests.get(_NDX100_WIKI, headers=HDR, timeout=20)
        r2.raise_for_status()
        ndx_df = None
        for tbl in pd.read_html(_SIO(r2.text)):
            cols_lower = [c.lower() for c in tbl.columns]
            has_ticker = any("ticker" in c or "symbol" in c for c in cols_lower)
            has_sector = any("sector" in c or "gics" in c for c in cols_lower)
            if has_ticker and has_sector and len(tbl) > 50:
                ndx_df = tbl
                break
        if ndx_df is not None:
            sym_col = _find_col(ndx_df, "ticker", "symbol")
            sec_col = _find_col(ndx_df, "gics sector", "sector")
            if sym_col and sec_col:
                added = 0
                for sym, sec in zip(ndx_df[sym_col], ndx_df[sec_col]):
                    if pd.notna(sym) and pd.notna(sec):
                        tk = _to_yf(str(sym))
                        if tk not in gmap:
                            gmap[tk] = _remap(sec)
                            added += 1
                print(f"Sectors: added {added} Nasdaq-100-only entries from Wikipedia")
    except Exception as e:
        print(f"Sectors: Nasdaq-100 Wikipedia fetch failed: {e}")

    # ── Fallback: hardcoded legacy lists if both Wikipedia fetches failed ─
    if not gmap:
        print("Sectors: Wikipedia unavailable — using built-in fallback")
        for tk, _co, sec in _SP500_FALLBACK_DATA + _NDX100_DATA:
            gmap[_to_yf(tk)] = _remap(sec)

    # ── Supplemental dict: reliable Yahoo Finance sector names for tickers
    # that consistently slip through Wikipedia (non-US names, very recent
    # IPOs, spin-offs) or where yf.Ticker().info is unreliable at cache time.
    # Uses setdefault so Wikipedia-sourced entries are never overwritten.
    # Sector names match Yahoo Finance taxonomy exactly.
    _SECTOR_SUPPLEMENT = {
        # Non-US Nasdaq-100 names (not in S&P 500 Wikipedia)
        "ARM":  "Technology",          # ARM Holdings PLC (UK)
        "ASML": "Technology",          # ASML Holding (Netherlands)
        "SHOP": "Technology",          # Shopify (Canada)
        "MELI": "Consumer Cyclical",   # MercadoLibre (Argentina)
        "PDD":  "Consumer Cyclical",   # PDD Holdings (China)
        "FER":  "Industrials",         # Ferrovial (Spain)
        "CCEP": "Consumer Defensive",  # Coca-Cola Europacific Partners (UK)
        "TRI":  "Industrials",         # Thomson Reuters (Canada)
        # Recent US IPOs / spin-offs (may not yet be stable on Wikipedia)
        "ALAB": "Technology",          # Astera Labs
        "SNDK": "Technology",          # SanDisk (WD spin-off)
        "RKLB": "Industrials",         # Rocket Lab USA
        "NBIS": "Technology",          # Nebius Group (formerly Yandex NV)
        "CRWV": "Technology",          # CoreWeave
        "HONA": "Industrials",         # Honeywell Automation (spin-off)
        "MSTR": "Technology",          # MicroStrategy
        "SPCX": "Industrials",         # SpaceX (recently listed)
    }
    for tk, sec in _SECTOR_SUPPLEMENT.items():
        gmap.setdefault(_to_yf(tk), sec)

    # ── Pass 3: yfinance for any ticker still missing ─────────────────────
    # Determine which tickers need a yfinance lookup by checking against the
    # combined priceable universe. Called lazily here so the map is already
    # populated before _load_holdings() runs (which calls _load_gics_map()).
    # We don't know the full universe yet at this point, so Pass 3 is deferred
    # to _fill_missing_sectors(), called from _load_holdings() after merge.
    return gmap


def _fill_missing_sectors(df: pd.DataFrame) -> pd.DataFrame:
    """
    For any priceable ticker whose sector is still '—' after the Wikipedia
    passes, fetch it from yfinance .info['sector']. Yahoo Finance returns its
    native sector names directly (Technology, Healthcare, Consumer Cyclical,
    etc.) so no remapping is needed.

    Uses a small thread pool to parallelise the per-ticker .info calls;
    typically only ~10-20 tickers need this so latency is low. Results are
    written back into the df in-place and also merged into the cached gmap
    so subsequent calls within the same session don't re-fetch.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    missing = df[(df["sector"] == "—") & df["priceable"]]["ticker"].unique().tolist()
    if not missing:
        return df

    print(f"Sectors: fetching {len(missing)} missing via yfinance: {missing}")

    def _fetch_one(tk):
        try:
            info = yf.Ticker(tk).info
            sec  = info.get("sector", "")
            return tk, sec if sec else "—"
        except Exception:
            return tk, "—"

    results = {}
    with ThreadPoolExecutor(max_workers=min(len(missing), 8)) as pool:
        futures = {pool.submit(_fetch_one, tk): tk for tk in missing}
        for fut in as_completed(futures):
            tk, sec = fut.result()
            results[tk] = sec

    df["sector"] = df.apply(
        lambda row: results.get(row["ticker"], row["sector"])
        if row["sector"] == "—" else row["sector"],
        axis=1,
    )
    print(f"Sectors: yfinance filled {sum(1 for s in results.values() if s != '—')} / {len(missing)}")
    return df


_COLUMN_ALIASES = {
    # Company/name field
    "name":            "company",
    "company":         "company",
    # Ticker field
    "ticker":          "ticker_raw",
    "ticker symbol":   "ticker_raw",
    "symbol":          "ticker_raw",
    # Weight field (loaded but currently unused — the screener recomputes
    # live weight itself from shares × price)
    "weight":          "weight_file",
    "% tna":           "weight_file",
    # Shares-held field — provider naming has changed release to release
    "shares held":     "shares_raw",
    "share/ par":      "shares_raw",
    "share / par":     "shares_raw",
    "shares/par":      "shares_raw",
    "shares outstanding": "shares_raw",
}


def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename whichever provider-specific column names are present to the
    canonical names _load_holdings expects, matched case/whitespace-insensitively."""
    rename_map = {}
    for col in df.columns:
        key = str(col).strip().lower()
        if key in _COLUMN_ALIASES:
            rename_map[col] = _COLUMN_ALIASES[key]
    return df.rename(columns=rename_map)


def _find_header_row(path: str, sheet_name: str, max_scan: int = 20) -> int:
    """
    Provider xlsx exports (e.g. State Street's SPY.xlsx) prepend a few
    metadata rows (fund name, ticker symbol, as-of date, blank line) above
    the real header. Scan the first `max_scan` rows for the one containing
    both a ticker-like and a name-like label, rather than hardcoding a fixed
    skip count that would silently break the next time the provider adds or
    removes a metadata line.
    """
    try:
        raw = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=max_scan)
    except Exception:
        return 0
    for i, row in raw.iterrows():
        cells = {str(c).strip().lower() for c in row.tolist()}
        has_ticker = bool(cells & {"ticker", "ticker symbol", "symbol"})
        has_name   = bool(cells & {"name", "company"})
        if has_ticker and has_name:
            return int(i)
    return 0  # fall back to the old assumption if nothing matches


def _load_holdings(path: str, index_name: str) -> pd.DataFrame:
    """
    Read a holdings file (SPY .xlsx or QQQ .csv) into a normalised frame:
      ticker (yf), company, shares, sector, index, priceable

    Provider exports change shape more than you'd like:
      - State Street's SPY.xlsx prepends a few metadata rows (fund name,
        ticker symbol, as-of date, blank line) above the real header, and
        appends legal-disclaimer paragraphs + blank rows below the holdings.
      - Invesco's QQQ.csv uses different column names release to release
        (e.g. 'Company'/'Share/ Par'/'% TNA' vs an older 'Name'/'Shares
        Held'/'Weight' convention), and appends a trailing '# as of <date>'
        comment line.

    Rather than hardcode either provider's current quirks, this:
      1. Locates the real header row by content (xlsx only — CSVs are
         assumed header-row-0, which has held for both providers so far).
      2. Canonicalizes whichever column names are found via _COLUMN_ALIASES.
      3. Drops any row without a ticker — the one thing every genuine
         holding has and every metadata/disclaimer/comment row lacks.
    """
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path, encoding="utf-8-sig")
    else:
        header_row = _find_header_row(path, "holdings")
        df = pd.read_excel(path, sheet_name="holdings", header=header_row)

    df = _canonicalize_columns(df)

    missing = {"ticker_raw", "company"} - set(df.columns)
    if missing:
        raise ValueError(
            f"{index_name} holdings file at {path} is missing expected "
            f"column(s) {missing} after alias mapping — got columns "
            f"{df.columns.tolist()}. Update _COLUMN_ALIASES if the provider "
            f"renamed a field again."
        )

    # Strip metadata/footer/comment rows. Every genuine holding has a ticker;
    # disclaimers, blank spacer rows, and "# as of ..." trailers do not.
    df = df[df["ticker_raw"].notna()].copy()
    df = df[~df["ticker_raw"].astype(str).str.strip().str.startswith("#")].copy()

    df["ticker_raw"] = df["ticker_raw"].astype(str)
    df["ticker"]     = df["ticker_raw"].apply(_to_yf)
    if "shares_raw" in df.columns:
        df["shares"] = df["shares_raw"].apply(_parse_shares)
    else:
        df["shares"] = float("nan")
    df["priceable"]  = df["ticker_raw"].apply(_is_priceable)
    df["index"]      = index_name

    gmap = _load_gics_map("v4")
    df["sector"] = df["ticker"].map(gmap).fillna("—")
    df["source"] = "file"

    # Pass 3: yfinance fallback for any ticker still missing a sector
    df = _fill_missing_sectors(df)

    keep = ["ticker", "ticker_raw", "company", "shares", "sector", "index", "priceable", "source"]
    return df[keep].reset_index(drop=True)


@st.cache_data(ttl=86400, show_spinner=False)
def _get_holdings_date() -> str:
    """
    Read the as-of date from SPY.xlsx and QQQ.csv and return a formatted
    string for the DATA hover bar, e.g. 'SPY / QQQ Holdings · 02 Jul 2026'.
    Uses the most recent date across both files so the label is always
    current after a holdings file swap.
    """
    from datetime import datetime
    dates = {}

    # SPY.xlsx: row 3 cell B = "As of 01-Jul-2026"
    if _SPY_FILE:
        try:
            raw = pd.read_excel(_SPY_FILE, sheet_name="holdings",
                                header=None, nrows=4)
            for _, row in raw.iterrows():
                for cell in row:
                    if isinstance(cell, str) and "as of" in cell.lower():
                        date_str = cell.lower().replace("as of", "").strip()
                        dates["SPY"] = datetime.strptime(date_str, "%d-%b-%Y")
                        break
        except Exception as e:
            print(f"SPY date read failed: {e}")

    # QQQ.csv: trailing line "# as of 2026-07-02"
    if _QQQ_FILE:
        try:
            with open(_QQQ_FILE, "r", encoding="utf-8-sig") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            for line in reversed(lines):
                if line.lower().startswith("# as of"):
                    date_str = line.lower().replace("# as of", "").strip()
                    dates["QQQ"] = datetime.strptime(date_str, "%Y-%m-%d")
                    break
        except Exception as e:
            print(f"QQQ date read failed: {e}")

    if not dates:
        return "SPY / QQQ Holdings"
    most_recent = max(dates.values())
    return f"SPY / QQQ Holdings · {most_recent.strftime('%d %b %Y')}"


@st.cache_data(ttl=3600, show_spinner=False)
def _load_sp500_cached() -> pd.DataFrame:
    """Cached file load only — raises on failure so the caller can fall back uncached."""
    return _load_holdings(_SPY_FILE, "S&P 500")


def fetch_sp500_constituents() -> pd.DataFrame:
    """SPY holdings as the S&P 500 constituent universe (priceable equities only)."""
    try:
        df = _load_sp500_cached()
        return df[df["priceable"]].reset_index(drop=True)
    except Exception as e:
        print(f"SPY holdings load failed: {e} — falling back to legacy list")
        return _sp500_fallback()


def fetch_sp500_holdings_full() -> pd.DataFrame:
    """Full SPY holdings incl. non-priceable rows (for cash bucketing)."""
    try:
        return _load_sp500_cached()
    except Exception as e:
        print(f"SPY full holdings load failed: {e}")
        return _sp500_fallback()


def _sp500_fallback() -> pd.DataFrame:
    """Fallback: legacy hardcoded S&P 500 names if the holdings file is unreachable."""
    df = pd.DataFrame(_SP500_FALLBACK_DATA, columns=["ticker", "company", "sector"])
    df["ticker"]    = df["ticker"].apply(_to_yf)
    df["ticker_raw"] = df["ticker"]
    df["index"]     = "S&P 500"
    df["shares"]    = float("nan")
    df["priceable"] = True
    df["source"]    = "fallback"
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def _load_ndx_cached() -> pd.DataFrame:
    """Cached file load only — raises on failure so the caller can fall back uncached."""
    return _load_holdings(_QQQ_FILE, "Nasdaq 100")


def fetch_ndx_constituents() -> pd.DataFrame:
    """QQQ holdings as the Nasdaq 100 constituent universe (priceable equities only)."""
    try:
        df = _load_ndx_cached()
        return df[df["priceable"]].reset_index(drop=True)
    except Exception as e:
        print(f"QQQ holdings load failed: {e} — falling back to legacy list")
        return _ndx_fallback()


def fetch_ndx_holdings_full() -> pd.DataFrame:
    """Full QQQ holdings incl. non-priceable rows (for cash bucketing)."""
    try:
        return _load_ndx_cached()
    except Exception as e:
        print(f"QQQ full holdings load failed: {e}")
        return _ndx_fallback()


def _ndx_fallback() -> pd.DataFrame:
    df = pd.DataFrame(_NDX100_DATA, columns=["ticker", "company", "sector"])
    df["ticker"]    = df["ticker"].apply(_to_yf)
    df["ticker_raw"] = df["ticker"]
    df["index"]     = "Nasdaq 100"
    df["shares"]    = float("nan")
    df["priceable"] = True
    df["source"]    = "fallback"
    return df


def get_market_state() -> str:
    """
    Returns the NYSE session state, determined entirely in US/Eastern time —
    the exchange's own timezone — rather than mapping onto SGT calendar days.

    The previous SGT-based version gated on `SGT weekday >= 5` *before*
    checking time-of-day. Since ET is 12h behind SGT, Friday's regular
    session (and its after-hours tail) actually lands in the first 8 hours
    of *Saturday* SGT — so that gate incorrectly forced "closed" during
    hours that should still read "open"/"after_hours". Doing this in ET
    avoids that entirely: NYSE's own hours never get sliced by an Eastern
    weekday boundary, since ET *is* the exchange's home timezone.

    Eastern schedule (weekdays only):
      00:00 – 04:00 ET  →  closed       (dead zone after after-hours)
      04:00 – 09:30 ET  →  pre          (pre-market)
      09:30 – 16:00 ET  →  open         (regular session)
      16:00 – 20:00 ET  →  after_hours
      20:00 – 24:00 ET  →  closed
    Saturday/Sunday (Eastern calendar day) → closed.
    """
    et   = timezone(timedelta(hours=-4))   # EDT — matches the rest of the module
    now  = datetime.now(et)
    if now.weekday() >= 5:        # Sat/Sun, Eastern calendar day
        return "closed"
    mins = now.hour * 60 + now.minute
    if mins < 240:                # 00:00–04:00 ET
        return "closed"
    elif mins < 570:              # 04:00–09:30 ET
        return "pre"
    elif mins < 960:              # 09:30–16:00 ET
        return "open"
    elif mins < 1200:             # 16:00–20:00 ET
        return "after_hours"
    else:                         # 20:00–24:00 ET
        return "closed"


def _fetch_prev_close(tickers: list) -> dict:
    """
    Previous COMPLETED session's official close for each ticker, used as the
    chg% baseline in all intraday/extended modes.

    Bug fix: do NOT use Close.iloc[-1] of a multi-day frame — during market
    hours the last daily row is the in-progress session, so iloc[-1] would be
    today's price and every chg% would collapse toward 0. We take each
    ticker's own last *completed* daily close instead (the row before today
    when a partial bar exists), via per-column last-valid logic.
    """
    try:
        raw = yf.download(
            tickers, period="7d", interval="1d",
            auto_adjust=True, progress=False, threads=True,
        )
        if raw.empty:
            return {}
        close = raw["Close"]
        # Identify whether the final row is today's (partial) session in ET.
        et       = timezone(timedelta(hours=-4))
        today_et = datetime.now(et).date()
        idx_dates = [ts.date() for ts in close.index]

        out = {}
        for tk in tickers:
            if tk not in close.columns:
                continue
            col = close[tk].dropna()
            if col.empty:
                continue
            # Drop today's in-progress bar if present, then take last close.
            completed = col[[d != today_et for d in
                             (col.index.map(lambda x: x.date()))]]
            series = completed if not completed.empty else col
            out[tk] = float(series.iloc[-1])
        return out
    except Exception as e:
        print(f"Prev close fetch failed: {e}")
        return {}


def _last_valid_per_ticker(frame: pd.DataFrame, tickers) -> dict:
    """
    For a wide intraday Close frame (index = timestamps, columns = tickers),
    return {ticker: last non-NaN price}.

    Bug fix: the previous code used frame.iloc[-1], a single shared timestamp
    row. Thinly-traded names have no print in that exact final 2-min bar, so
    their cell is NaN and they were dropped or computed to a stale 0.00%
    ('Unchanged'). Forward-filling per column and taking the last value gives
    each ticker its own genuine latest traded price during market hours.
    """
    if frame is None or frame.empty:
        return {}
    ff = frame.ffill()
    last_row = ff.iloc[-1]
    out = {}
    for tk in tickers:
        if tk in last_row.index:
            v = last_row[tk]
            if pd.notna(v):
                out[tk] = float(v)
    return out


@st.cache_data(ttl=300, show_spinner=False)
def fetch_price_data_live(tickers: tuple) -> pd.DataFrame:
    """
    Market hours: 2-min intraday bars (~15min delayed).
    Last price = each ticker's own last valid intraday print (forward-filled),
    NOT the shared final timestamp row — this fixes the spurious 'Unchanged'
    bucket for less-active names during live trading.
    Chg % vs previous completed session's close. Volume = cumulative intraday.
    """
    try:
        raw = yf.download(
            list(tickers), period="1d", interval="2m",
            auto_adjust=True, progress=False, threads=True,
        )
        if raw.empty or raw["Close"].empty:
            return fetch_price_data_eod(tickers)

        close  = raw["Close"]
        volume = raw["Volume"]
        if len(close) == 0:
            return fetch_price_data_eod(tickers)

        prev_close_map = _fetch_prev_close(list(tickers))
        if not prev_close_map:
            return fetch_price_data_eod(tickers)

        last_price_map = _last_valid_per_ticker(close, tickers)
        cum_volume     = volume.sum(axis=0)
        trade_date     = close.index[-1].date()

        rows = []
        for ticker in tickers:
            lp = last_price_map.get(ticker)
            pc = prev_close_map.get(ticker)
            if lp is None or pc is None or pc == 0:
                continue
            chg_pct = (lp / pc - 1) * 100
            chg_abs = lp - pc
            vol     = cum_volume[ticker] if ticker in cum_volume.index else 0
            rows.append({
                "ticker":     ticker,
                "price":      lp,            # full precision; rounded only at display
                "chg_pct":    chg_pct,       # full precision; weighted sum needs it
                "chg_abs":    chg_abs,
                "prev_close": pc,            # t-1 anchor for the weight base
                "volume":     int(vol) if not pd.isna(vol) else 0,
                "trade_date": str(trade_date),
            })
        if not rows:
            return fetch_price_data_eod(tickers)
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Live fetch failed: {e} — falling back to EOD")
        return fetch_price_data_eod(tickers)


def _pre_market_prev_close(tickers: list, ref_date) -> dict:
    """
    Baseline for PRE-MARKET ONLY.

    Pre-market chg% must be measured against the most recent COMPLETED
    regular-session close (yesterday's official close), NOT an earlier session.
    Daily bars can't be trusted for this: Yahoo sometimes stamps a completed
    session's daily bar with the *next* calendar date, so any date filter on the
    daily frame silently lands one session too far back and folds the prior day's
    full move into the "pre-market" change.

    So we derive the baseline from INTRADAY bars instead, where every bar is
    unambiguously timestamped inside the trading day (09:30–16:00 ET) on its real
    date. prepost=False → regular-session bars only; the last bar on the most
    recent session strictly BEFORE ref_date (today's ET date) is that session's
    close. This is immune to the daily-bar dating quirk.
    """
    ET = timezone(timedelta(hours=-4))   # EDT, matches the rest of the module

    def _et_date(ts):
        try:
            return ts.tz_convert(ET).date() if ts.tzinfo is not None else ts.date()
        except (TypeError, AttributeError):
            return ts.date()

    try:
        raw = yf.download(
            tickers, period="5d", interval="2m",
            auto_adjust=True, prepost=False, progress=False,
            threads=True, group_by="ticker",
        )
        if raw.empty:
            return {}
        out = {}
        lvl0 = raw.columns.get_level_values(0)
        for tk in tickers:
            if tk not in lvl0:
                continue
            col = raw[tk]["Close"].dropna()
            if col.empty:
                continue
            prior = col[[_et_date(ts) < ref_date for ts in col.index]]
            if prior.empty:
                continue
            out[tk] = float(prior.iloc[-1])
        return out
    except Exception as e:
        print(f"Pre-market prev close fetch failed: {e}")
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_price_data_extended(tickers: tuple, session: str) -> pd.DataFrame:
    """
    Pre-market and after-hours: 1-min bars with prepost=True (~15min delayed).
    Chg % vs previous completed session's close.
    session: 'pre' or 'after_hours'.
    """
    try:
        raw = yf.download(
            list(tickers), period="1d", interval="1m",
            auto_adjust=True, prepost=True, progress=False,
            threads=True, group_by="ticker",
        )
        if raw.empty:
            return fetch_price_data_eod(tickers)

        ticker_data = {}
        for tk in tickers:
            try:
                if tk in raw.columns.get_level_values(0):
                    tk_df = raw[tk][["Close", "Volume"]].copy()
                    tk_df.columns = ["close", "volume"]
                    ticker_data[tk] = tk_df
            except Exception:
                continue
        if not ticker_data:
            return fetch_price_data_eod(tickers)

        et       = timezone(timedelta(hours=-4))   # EDT
        now_et   = datetime.now(et)
        today_et = now_et.date()

        if session == "pre":
            day_start  = datetime(today_et.year, today_et.month, today_et.day, 0, 0, tzinfo=et)
            day_cutoff = datetime(today_et.year, today_et.month, today_et.day, 9, 30, tzinfo=et)
            def in_session(idx): return day_start <= idx < day_cutoff
        else:
            cutoff = datetime(today_et.year, today_et.month, today_et.day, 16, 0, tzinfo=et)
            def in_session(idx): return idx >= cutoff

        if session == "pre":
            prev_close_map = _pre_market_prev_close(list(tickers), today_et)
        else:
            prev_close_map = _fetch_prev_close(list(tickers))
        if not prev_close_map:
            return fetch_price_data_eod(tickers)

        rows = []
        for tk, df_tk in ticker_data.items():
            df_ext = df_tk[df_tk.index.map(in_session)].dropna(subset=["close"])
            if df_ext.empty:
                continue
            pc = prev_close_map.get(tk)
            if pc is None or pc == 0:
                continue
            lp      = float(df_ext["close"].iloc[-1])
            chg_pct = (lp / pc - 1) * 100
            chg_abs = lp - pc
            vol_raw = df_ext["volume"].sum()
            vol     = int(vol_raw) if not pd.isna(vol_raw) and vol_raw > 0 else None
            rows.append({
                "ticker":     tk,
                "price":      lp,            # full precision; rounded only at display
                "chg_pct":    chg_pct,       # full precision; weighted sum needs it
                "chg_abs":    chg_abs,
                "prev_close": pc,            # t-1 anchor for the weight base
                "volume":     vol,
                "trade_date": str(df_ext.index[-1].date()),
            })
        if not rows:
            return fetch_price_data_eod(tickers)
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Extended hours fetch failed [{session}]: {e} — falling back to EOD")
        return fetch_price_data_eod(tickers)


@st.cache_data(ttl=900, show_spinner=False)
def _fetch_eod_raw(tickers: tuple, et_date_str: str) -> pd.DataFrame:
    """
    Fetch daily bars with explicit ET-anchored start/end dates rather than
    period=, which yfinance anchors to the server (SGT) clock and can land
    during a window where Yahoo still considers the latest US session open —
    causing it to return the session BEFORE the one we want.  Explicit dates
    in ET eliminate that timezone ambiguity entirely.  et_date_str also pins
    the cache so it rebuilds at most once per ET calendar day; the ttl=900s
    backstop handles late Yahoo data posts within the same day.
    """
    try:
        target = datetime.strptime(et_date_str, "%Y-%m-%d").date()
        start  = target - timedelta(days=15)   # 15-day buffer covers long weekends
        end    = target + timedelta(days=1)    # yfinance end is exclusive
        return yf.download(
            list(tickers),
            start=str(start),
            end=str(end),
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        print(f"EOD fetch failed: {e}")
        return pd.DataFrame()


def fetch_price_data_eod(tickers: tuple) -> pd.DataFrame:
    """
    Always returns the MOST RECENT COMPLETED trading session's prices.

    Key insight: SGT is 12 h ahead of ET.  At 10 AM SGT July 29, ET is still
    July 28 -- so today_et = July 28.  Filtering close.index < July 28 would
    strip the July 28 session we actually want.  The partial-bar guard must
    run ONLY when the market is open (the sole moment a true intraday daily
    bar exists).  After-hours / closed / pre: the last daily bar is a
    completed official close and must not be stripped.
    """
    et          = timezone(timedelta(hours=-4))
    today_et    = datetime.now(et).date()
    et_date_str = str(today_et)

    raw = _fetch_eod_raw(tickers, et_date_str)
    if raw.empty or "Close" not in raw or raw["Close"].empty:
        return pd.DataFrame()

    close  = raw["Close"]
    volume = raw.get("Volume", pd.DataFrame())

    # Only strip today's partial bar during live market hours.
    if get_market_state() == "open":
        completed_idx = [d for d in close.index if d.date() < today_et]
        if not completed_idx:
            return pd.DataFrame()
        close = close.loc[completed_idx]
        if isinstance(volume, pd.DataFrame) and not volume.empty:
            vol_idx = [d for d in volume.index if d.date() < today_et]
            volume  = volume.loc[vol_idx] if vol_idx else pd.DataFrame()

    rows = []
    for ticker in tickers:
        if ticker not in close.columns:
            continue

        col = close[ticker].dropna()
        if len(col) < 2:
            continue

        # Last completed session
        lc = float(col.iloc[-1])
        pc = float(col.iloc[-2])   # Previous completed session

        if pc == 0:
            continue

        chg_pct = (lc / pc - 1) * 100
        chg_abs = lc - pc

        # Volume
        try:
            vol_col = volume[ticker].dropna() if isinstance(volume, pd.DataFrame) and ticker in volume.columns else pd.Series()
            vol = int(vol_col.iloc[-1]) if not vol_col.empty else 0
        except Exception:
            vol = 0

        rows.append({
            "ticker":     ticker,
            "price":      lc,            # full precision; rounded only at display
            "chg_pct":    chg_pct,       # full precision; weighted sum needs it
            "chg_abs":    chg_abs,
            "prev_close": pc,            # t-1 anchor for the weight base
            "volume":     vol,
            "trade_date": str(col.index[-1].date()),
        })

    return pd.DataFrame(rows)


@st.cache_data(ttl=21600, show_spinner=False)
def _fetch_historical_raw(tickers: tuple, target_date_str: str) -> pd.DataFrame:
    """
    Cached Yahoo pull of daily bars spanning a window around a past date.
    The 21-day lookback (vs. the 5-day window used for live/EOD) guards
    against long weekends and multi-day holiday clusters so there is always
    a valid prior trading day to diff against. Cached 6h — a backdated
    report for a fixed date never changes, so this is mostly a safety TTL.
    """
    target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    start  = target - timedelta(days=21)
    end    = target + timedelta(days=1)   # yfinance's `end` is exclusive
    try:
        return yf.download(
            list(tickers), start=start.isoformat(), end=end.isoformat(),
            interval="1d", auto_adjust=True, progress=False, threads=True,
        )
    except Exception as e:
        print(f"Historical fetch failed: {e}")
        return pd.DataFrame()


def fetch_price_data_historical(tickers: tuple, target_date) -> pd.DataFrame:
    """
    Historical / backdated: daily bars as of a specific past date.
    last_close = close on target_date, or the most recent trading day on or
    before it (so picking a weekend/holiday date snaps back to the last
    session that actually traded); prev_close = the session before that.
    """
    target_date_str = target_date.isoformat() if hasattr(target_date, "isoformat") else str(target_date)
    target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    raw = _fetch_historical_raw(tickers, target_date_str)
    if raw.empty:
        return pd.DataFrame()
    close  = raw["Close"]
    volume = raw["Volume"]

    rows = []
    for ticker in tickers:
        if ticker not in close.columns:
            continue
        col = close[ticker].dropna()
        col = col[col.index.date <= target]
        if len(col) < 2:
            continue
        lc = float(col.iloc[-1])
        pc = float(col.iloc[-2])
        if pc == 0:
            continue
        chg_pct = (lc / pc - 1) * 100
        chg_abs = lc - pc
        try:
            vcol = volume[ticker].dropna()
            vcol = vcol[vcol.index.date <= target]
            vol  = vcol.iloc[-1]
        except Exception:
            vol = 0
        rows.append({
            "ticker":     ticker,
            "price":      lc,
            "chg_pct":    chg_pct,
            "chg_abs":    chg_abs,
            "prev_close": pc,
            "volume":     int(vol) if not pd.isna(vol) else 0,
            "trade_date": str(col.index[-1].date()),
        })
    return pd.DataFrame(rows)


def fetch_price_data(tickers: tuple) -> tuple:
    """Router: picks correct fetch based on market state. Returns (DataFrame, state)."""
    state = get_market_state()
    if state == "open":
        return fetch_price_data_live(tickers), state
    elif state in ("pre", "after_hours"):
        return fetch_price_data_extended(tickers, state), state
    else:
        return fetch_price_data_eod(tickers), state


def fmt_volume(v) -> str:
    """Format volume; None → '—' for extended hours with no volume."""
    if v is None:
        return "—"
    v = int(v)
    if v >= 1_000_000_000: return f"{v/1_000_000_000:.1f}B"
    if v >= 1_000_000:     return f"{v/1_000_000:.1f}M"
    if v >= 1_000:         return f"{v/1_000:.0f}K"
    return str(v)


# ─────────────────────────────────────────────────────────────────────────────
# MARKETS SCREENER — RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def fmt_mktcap(v) -> str:
    """Format market cap value into readable string."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    if v >= 1_000_000_000_000:
        return f"${v/1_000_000_000_000:.2f}T"
    if v >= 1_000_000_000:
        return f"${v/1_000_000_000:.1f}B"
    if v >= 1_000_000:
        return f"${v/1_000_000:.0f}M"
    return f"${v:,.0f}"


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_market_caps(tickers: tuple, prev_prices: tuple) -> dict:
    """
    Previous-day market cap = shares_outstanding × prev_close.
    prev_prices: tuple of (ticker, price) pairs from EOD fetch.
    Cached 24hrs — shares outstanding barely changes day-to-day.
    """
    price_map = dict(prev_prices)
    result    = {}
    for tk in tickers:
        try:
            shares = yf.Ticker(tk).fast_info.shares
            pc     = price_map.get(tk)
            if shares and pc and not pd.isna(shares) and not pd.isna(pc):
                result[tk] = float(shares) * float(pc)
            else:
                result[tk] = None
        except Exception:
            result[tk] = None
    return result


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_recent_splits(tickers: tuple, cache_bucket: str, lookback_days: int = 3) -> dict:
    """
    Batched, near-zero-marginal-cost corporate-action check.

    A stock split mechanically moves a ticker's raw closing price by the
    split ratio (a 10-for-1 split drops the raw print ~90%) even though
    nothing economically happened. yfinance's auto_adjust=True is *supposed*
    to retroactively rebase historical closes so chg_pct nets this out — but
    Yahoo's backend can lag applying that rebase for a few hours right on the
    ex-date, which is exactly when a split-driven artifact would otherwise
    slip through as a bogus "top mover".

    This does ONE extra batched download (actions=True) across the whole
    universe — not one call per ticker — and returns any ticker with a split
    dated within `lookback_days`, so the screener can (a) tag it for
    transparency and (b) independently verify its chg_pct rather than
    trusting auto_adjust blindly.

    cache_bucket: caller passes a date-keyed string (ET) so this can't serve
    a stale "no splits today" result across a calendar-day boundary — same
    pattern as _fetch_eod_raw's cache_bucket.
    """
    try:
        raw = yf.download(
            list(tickers), period="10d", interval="1d",
            auto_adjust=True, actions=True, progress=False, threads=True,
        )
        if raw.empty or "Stock Splits" not in raw.columns.get_level_values(0):
            return {}
        splits = raw["Stock Splits"]
        et     = timezone(timedelta(hours=-4))
        cutoff = (datetime.now(et) - timedelta(days=lookback_days)).date()

        out = {}
        for tk in tickers:
            if tk not in splits.columns:
                continue
            col = splits[tk].dropna()
            col = col[col != 0]
            if col.empty:
                continue
            recent = col[[ts.date() >= cutoff for ts in col.index]]
            if not recent.empty:
                ts    = recent.index[-1]
                ratio = float(recent.iloc[-1])
                out[tk] = {"date": ts.date(), "ratio": ratio}
        return out
    except Exception as e:
        print(f"Split detection failed: {e}")
        return {}


def _verify_split_adjusted_chg(ticker: str, split_date, ratio: float,
                                current_price: float):
    """
    Independently re-derives chg_pct for a single flagged ticker using RAW
    (auto_adjust=False) closes, manually dividing the pre-split close by the
    split ratio (post-split price = pre-split price / ratio; e.g. a 4-for-1
    split: $400 -> $100, ratio=4.0). This sidesteps any Yahoo-side lag in
    applying the auto-adjust rebase and gives a trustworthy figure to
    cross-check the fast-path value against.

    Only called for the handful of tickers fetch_recent_splits flags — not
    the full universe — so the extra per-ticker call is cheap.

    Returns None if it can't be computed (missing data), in which case the
    caller leaves the original auto_adjust-derived chg_pct untouched.
    """
    try:
        raw = yf.download(
            ticker, period="10d", interval="1d",
            auto_adjust=False, progress=False, threads=False,
        )
        if raw.empty:
            return None
        close = raw["Close"].dropna()
        pre_split = close[close.index.date < split_date]
        if pre_split.empty or ratio == 0:
            return None
        raw_prev_close      = float(pre_split.iloc[-1])
        adjusted_prev_close = raw_prev_close / ratio
        if adjusted_prev_close == 0:
            return None
        return (current_price / adjusted_prev_close - 1) * 100
    except Exception as e:
        print(f"Split verification failed for {ticker}: {e}")
        return None


def _split_tag(ratio) -> str:
    """Human-readable split label, e.g. 4.0 -> '4:1 split', 0.1 -> '1:10 split'."""
    if ratio >= 1:
        return f"{ratio:.0f}:1 split"
    return f"1:{(1/ratio):.0f} split"


_SORTABLE_TABLE_TEMPLATE = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  html, body {
      margin: 0; background: #FFFFFF;
      font-family: 'Inter', sans-serif;
  }
  .table-wrap {
      background: #FFFFFF; border: 1px solid #D8E0F0;
      border-radius: 10px; overflow: hidden; overflow-x: auto;
  }
  table.stock-table { width: 100%; border-collapse: collapse; }
  .stock-table th {
      font-family: 'Inter', sans-serif;
      font-size: 10px; font-weight: 700; letter-spacing: .7px;
      text-transform: uppercase; color: #1A2540;
      padding: 8px 12px; border-bottom: 1px solid #D8E0F0;
      text-align: left; background: #EEF2FC;
      cursor: pointer; user-select: none; white-space: nowrap;
  }
  .stock-table th:hover { background: #E2E9F8; color: #3D6DD6; }
  .stock-table th .sort-arrow { font-size: 8px; color: #3D6DD6; margin-left: 4px; }
  .stock-table td {
      font-family: 'Inter', sans-serif;
      font-size: 12px; padding: 8px 12px;
      border-bottom: 1px solid #F0F4FC;
      color: #1A2540;
  }
  .stock-table tr:hover td { background: rgba(91,141,239,.05); }
  .chg-pos { color: #0CA86C !important; font-weight: 700; }
  .chg-neg { color: #C8303F !important; font-weight: 700; }
  .ticker-badge {
      font-weight: 700; color: #3D6DD6;
      background: rgba(91,141,239,.1);
      padding: 2px 6px; border-radius: 4px;
      font-size: 12px;
  }
  .sector-tag {
      font-size: 11px; padding: 2px 7px; border-radius: 3px;
      background: rgba(91,141,239,.08);
      border: 1px solid rgba(91,141,239,.2);
      color: #1A2540; white-space: nowrap;
  }
  ::-webkit-scrollbar { height: 8px; width: 8px; }
  ::-webkit-scrollbar-thumb { background: rgba(91,141,239,.2); border-radius: 4px; }
</style></head>
<body>
<div class="table-wrap">
  <table class="stock-table" id="stockTable">
    <thead>
      <tr>
        <th onclick="sortTable(0,true)">#<span class="sort-arrow"></span></th>
        <th onclick="sortTable(1,false)">Ticker<span class="sort-arrow"></span></th>
        <th onclick="sortTable(2,false)">Company<span class="sort-arrow"></span></th>
        <th onclick="sortTable(3,false)">Sector<span class="sort-arrow"></span></th>
        <th onclick="sortTable(4,true)" style="text-align:right">Price<span class="sort-arrow"></span></th>
        <th onclick="sortTable(5,true)" style="text-align:right">Chg %<span class="sort-arrow"></span></th>
        <th onclick="sortTable(6,true)" style="text-align:right">Chg $<span class="sort-arrow"></span></th>
        <th onclick="sortTable(7,true)" style="text-align:right">Weight<span class="sort-arrow"></span></th>
        <th onclick="sortTable(8,true)" style="text-align:right">Volume<span class="sort-arrow"></span></th>
        <th onclick="sortTable(9,true)" style="text-align:right">Mkt Cap<span class="sort-arrow"></span></th>
      </tr>
    </thead>
    <tbody>__ROWS__</tbody>
  </table>
</div>
<script>
function sortTable(colIdx, isNumeric) {
    var table = document.getElementById('stockTable');
    var tbody = table.tBodies[0];
    var rows  = Array.prototype.slice.call(tbody.rows);
    var ths   = table.tHead.rows[0].cells;
    var th    = ths[colIdx];
    var dir   = th.getAttribute('data-dir') === 'asc' ? 'desc' : 'asc';

    for (var k = 0; k < ths.length; k++) {
        ths[k].removeAttribute('data-dir');
        ths[k].querySelector('.sort-arrow').textContent = '';
    }
    th.setAttribute('data-dir', dir);
    th.querySelector('.sort-arrow').textContent = dir === 'asc' ? ' ▲' : ' ▼';

    rows.sort(function(a, b) {
        var va = a.children[colIdx].getAttribute('data-sort');
        var vb = b.children[colIdx].getAttribute('data-sort');
        if (isNumeric) {
            var na = parseFloat(va), nb = parseFloat(vb);
            var aNaN = isNaN(na), bNaN = isNaN(nb);
            if (aNaN && bNaN) return 0;
            if (aNaN) return 1;
            if (bNaN) return -1;
            return dir === 'asc' ? na - nb : nb - na;
        } else {
            va = (va || '').toLowerCase();
            vb = (vb || '').toLowerCase();
            if (va < vb) return dir === 'asc' ? -1 : 1;
            if (va > vb) return dir === 'asc' ? 1 : -1;
            return 0;
        }
    });
    rows.forEach(function(r) { tbody.appendChild(r); });
}
</script>
</body></html>
"""


def render_screener() -> None:
    sgt = timezone(timedelta(hours=8))
    now = datetime.now(sgt)

    # All controls (index, view, sector, top_n) live in the sidebar.
    # Read their current values from session_state here.
    if "idx_choice" not in st.session_state:
        st.session_state["idx_choice"] = "S&P 500"

    idx_choice  = st.session_state["idx_choice"]
    etf_label   = "SPY" if idx_choice == "S&P 500" else "QQQ"
    index_label = "S&P 500 Return" if idx_choice == "S&P 500" else "Nasdaq 100 Return"

    # ── Historical mode: set by the sidebar "Date" toggle ──────────────────
    hist_mode = st.session_state.get("hist_mode", False)
    hist_date = st.session_state.get("hist_date") if hist_mode else None

    # ── Page-scoped font bump ──────────────────────────────────────────────
    st.markdown("""
    <style>
    .screener-title { font-size: 20px !important; }
    .screener-meta  { font-size: 11px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Minimal main-content title ─────────────────────────────────────────
    _title_date_badge = (
        f"<span style='font-size:11px;font-weight:700;color:#5B8DEF;"
        f"background:rgba(91,141,239,.12);border-radius:4px;padding:2px 8px;"
        f"margin-left:10px'>📅 {hist_date.strftime('%d %b %Y')}</span>"
        if hist_mode and hist_date else ""
    )
    st.markdown(
        f"<div class='screener-title' style='font-weight:700;color:#1A2540;"
        f"padding:20px 0 12px;font-family:Inter,sans-serif;font-size:20px'>📈 Market Screener"
        f"<span style='font-size:12px;font-weight:400;color:#4D6080;"
        f"margin-left:12px'>{idx_choice}</span>{_title_date_badge}</div>",
        unsafe_allow_html=True,
    )

    # ── Load holdings (full, incl. non-priceable for cash bucketing) ───────
    with st.spinner("Loading constituent list…"):
        if idx_choice == "S&P 500":
            holdings_full = fetch_sp500_holdings_full()
        else:
            holdings_full = fetch_ndx_holdings_full()

    if holdings_full.empty:
        st.error("Failed to load constituent list. Check that the holdings file is present in ./data/.")
        return

    # ── Diagnostic: warn loudly if we silently fell back to the legacy list ─
    on_fallback = (holdings_full.get("source") == "fallback").any() \
        if "source" in holdings_full.columns else True
    if on_fallback:
        expected = _SPY_FILE if idx_choice == "S&P 500" else _QQQ_FILE
        st.warning(
            f"⚠️ Holdings file not found — showing the legacy built-in list "
            f"(~{len(holdings_full)} names, no live weights). "
            f"Expected file at: `{expected}`. "
            f"Place SPY.xlsx / QQQ.csv in a `data/` folder next to app.py."
        )

    constituents   = holdings_full[holdings_full["priceable"]].reset_index(drop=True)
    non_priceable  = holdings_full[~holdings_full["priceable"]].reset_index(drop=True)
    tickers_tuple  = tuple(constituents["ticker"].tolist())
    total_universe = len(tickers_tuple)

    # ── Load price data (market-state-aware, or historical if a date is set) ─
    if hist_mode and hist_date:
        with st.spinner(f"Fetching {total_universe} stocks as of {hist_date.strftime('%d %b %Y')}…"):
            prices = fetch_price_data_historical(tickers_tuple, hist_date)
        market_state = "historical"
    else:
        market_state = get_market_state()
        spinner_msgs = {
            "open":        f"Fetching live prices for {total_universe} stocks (~15min delay)…",
            "pre":         f"Fetching pre-market prices for {total_universe} stocks (~15min delay)…",
            "after_hours": f"Fetching after-hours prices for {total_universe} stocks (~15min delay)…",
            "closed":      f"Fetching EOD prices for {total_universe} stocks…",
        }
        with st.spinner(spinner_msgs.get(market_state, "Fetching prices…")):
            prices, market_state = fetch_price_data(tickers_tuple)

    if prices.empty:
        st.error(
            "Failed to fetch price data from Yahoo Finance."
            + (f" No trading data found on or before {hist_date.strftime('%d %b %Y')}."
               if hist_mode and hist_date else "")
        )
        return

    # ── Merge constituents + prices ───────────────────────────────────────
    # LEFT join keeps ALL constituents, including names with no current print
    # (common pre-market / after-hours, when only liquid names trade). Without
    # this, an inner join would drop them and the weight base would shrink to
    # only the names that traded — over-weighting them and pushing the index
    # return away from the ETF's true move.
    priced = constituents.merge(prices, on="ticker", how="left")
    if priced["price"].notna().sum() == 0:
        st.error("No matching price data found.")
        return

    # ── Corporate-action guard: flag & verify recent stock splits ──────────
    # See fetch_recent_splits / _verify_split_adjusted_chg docstrings. This
    # is one extra batched call across the whole universe, then a targeted
    # re-check only for whatever handful of tickers actually split.
    # Skipped in historical mode: this check reconciles TODAY's live print
    # against a split that happened in the last few days — not meaningful
    # for an arbitrary past date, whose split-adjustment is already handled
    # correctly by auto_adjust=True in the historical fetch itself.
    if not hist_mode:
        et_now       = timezone(timedelta(hours=-4))
        split_bucket = str(datetime.now(et_now).date())
        with st.spinner("Checking for recent stock splits…"):
            splits_map = fetch_recent_splits(tickers_tuple, split_bucket)

        priced["split_ratio"] = priced["ticker"].map(
            lambda t: splits_map.get(t, {}).get("ratio"))
        priced["split_date"] = priced["ticker"].map(
            lambda t: splits_map.get(t, {}).get("date"))
        priced["split_tag"] = priced["split_ratio"].apply(
            lambda r: _split_tag(r) if pd.notna(r) else None)

        for tk, info in splits_map.items():
            mask = priced["ticker"] == tk
            if not mask.any():
                continue
            px = priced.loc[mask, "price"].iloc[0]
            if pd.isna(px):
                continue
            verified = _verify_split_adjusted_chg(tk, info["date"], info["ratio"], float(px))
            if verified is None:
                continue
            existing = priced.loc[mask, "chg_pct"].iloc[0]
            # Only override if auto_adjust's figure materially disagrees with the
            # independently-verified one (>1pp) — otherwise auto_adjust already
            # did its job correctly and the split_tag badge alone is enough.
            if pd.isna(existing) or abs(verified - float(existing)) > 1.0:
                corrected_prev_close = float(px) / (1 + verified / 100)
                priced.loc[mask, "chg_pct"]    = verified
                priced.loc[mask, "chg_abs"]    = float(px) - corrected_prev_close
                priced.loc[mask, "prev_close"] = corrected_prev_close
    else:
        priced["split_ratio"] = None
        priced["split_date"]  = None
        priced["split_tag"]   = None

    # ── Stable weight base: shares × t-1 close over the FULL universe ──────
    # Use the prev_close column emitted by the price-fetch layer — which is
    # the close of the session BEFORE the one chg_pct is measured against.
    # This is the start-of-period market cap, the correct anchor for a
    # period-return weighting (using end-of-period market cap as the weight
    # base inflates the index return by ~2-3bps because winners gain weight
    # mid-period). For constituents missing a prev_close in the price frame
    # (e.g. unmatched names), fall back to the current price.
    priced["prev_close"] = priced["prev_close"].fillna(priced["price"])

    priced["mkt_val"] = priced["shares"] * priced["prev_close"]
    total_mkt_val     = priced["mkt_val"].sum()
    if total_mkt_val and total_mkt_val > 0:
        priced["weight"] = priced["mkt_val"] / total_mkt_val
    else:
        priced["weight"] = 0.0

    # ── Weighted index return (bottom-up estimate, used for Top-N Contrib) ──
    # Each name contributes weight_i × chg_pct_i over the FULL-universe weight
    # base. Names with no current print are treated as flat (0% change) — the
    # same way the ETF's own price treats a constituent that hasn't traded yet.
    # Non-priceable cash holdings contribute 0% and are excluded from the base,
    # so this tracks the priced-equity portion of the ETF. This bottom-up
    # figure can drift from the ETF's own live tape pre/post-market (thin,
    # unsynchronized constituent prints), so it is no longer used for the
    # headline Return badge below — only as the weight base for Top-N Contrib.
    priced["chg_for_idx"] = priced["chg_pct"].fillna(0.0)
    weighted_return = float((priced["weight"] * priced["chg_for_idx"]).sum())

    # ── Headline index return = SPY / QQQ's OWN price change ───────────────
    # The user wants the headline "S&P 500 Return" / "Nasdaq 100 Return" badge
    # to match the ETF's actual tape tick-for-tick, at any point in the
    # session — not a bottom-up constituent estimate. Re-use the exact same
    # session-aware routing (live 2-min bars / pre/after-hours / EOD /
    # historical) already used for the constituent universe above, just
    # pointed at the ETF ticker itself, so the same market-state branch and
    # hist_date apply consistently to both.
    try:
        if hist_mode and hist_date:
            etf_prices = fetch_price_data_historical((etf_label,), hist_date)
        elif market_state == "open":
            etf_prices = fetch_price_data_live((etf_label,))
        elif market_state in ("pre", "after_hours"):
            etf_prices = fetch_price_data_extended((etf_label,), market_state)
        else:
            etf_prices = fetch_price_data_eod((etf_label,))
    except Exception as e:
        print(f"ETF return fetch failed [{etf_label}]: {e}")
        etf_prices = pd.DataFrame()

    if not etf_prices.empty and etf_prices["chg_pct"].notna().any():
        etf_row      = etf_prices[etf_prices["ticker"] == etf_label]
        index_return = float(etf_row["chg_pct"].iloc[0]) if not etf_row.empty else weighted_return
        index_return_is_live = True
    else:
        # Fallback: if the ETF's own quote fails to fetch, fall back to the
        # bottom-up weighted estimate rather than showing nothing.
        index_return = weighted_return
        index_return_is_live = False

    # Count of names actually carrying a live print (for the status line).
    priced_with_quote = int(priced["price"].notna().sum())
    # Share of total index weight that is actually quoted right now. Pre-market
    # this is < 100% (illiquid names don't trade); the un-quoted remainder is
    # assumed flat, which is the main reason a bottom-up figure can differ from
    # the ETF's own live quote.
    quoted_weight = float(priced.loc[priced["price"].notna(), "weight"].sum()) * 100

    # ── Cash & Other exposure (non-priceable holdings) ────────────────────
    # Estimate notional from prev-close-based market value where shares exist;
    # fall back to reporting count when shares are unusable (e.g. futures).
    cash_names  = non_priceable["company"].tolist()
    cash_count  = len(non_priceable)

    # Names carrying an actual live/EOD quote — used for the table, the
    # gainers/losers counts, and the Top-N pool. The weighted index return
    # above still uses the full-universe weight base.
    quoted = priced[priced["price"].notna()].copy()

    # Bug fix: this used to take quoted["trade_date"].iloc[0] — whichever
    # ticker happened to land in the first row. If even one early-ordered
    # ticker's daily bar hadn't posted yet on Yahoo's side while the rest of
    # the market had already rolled to the new session, the page-wide date
    # badge would wrongly show yesterday's date even though the table itself
    # was mostly already showing the new session. Using the most common
    # trade_date across the full quoted universe is robust to a handful of
    # stale/late-posting outliers.
    if "trade_date" in quoted.columns and not quoted.empty:
        trade_date = quoted["trade_date"].value_counts().idxmax()
    else:
        trade_date = "—"
    active_count  = len(quoted)
    sgt           = timezone(timedelta(hours=8))
    now_sgt_str   = datetime.now(sgt).strftime("%H:%M SGT")

    # ── Market state status badge ─────────────────────────────────────────
    _txt = "#1A2540"   # dark text for white background
    if market_state == "open":
        state_html = (
            f"<span style='color:#0FD68A;font-weight:700'>● LIVE</span>"
            f"<span style='color:{_txt}'> (~15min delay) · "
            f"{active_count} of {total_universe} stocks active · "
            f"as of {now_sgt_str}</span>"
        )
    elif market_state == "pre":
        state_html = (
            f"<span style='color:#F59E0B;font-weight:700'>● PRE-MARKET</span>"
            f"<span style='color:{_txt}'> (~15min delay) · "
            f"{active_count} of {total_universe} stocks active · "
            f"as of {now_sgt_str}</span>"
        )
    elif market_state == "after_hours":
        state_html = (
            f"<span style='color:#A78BFA;font-weight:700'>● AFTER-HOURS</span>"
            f"<span style='color:{_txt}'> (~15min delay) · "
            f"{active_count} of {total_universe} stocks active · "
            f"as of {now_sgt_str}</span>"
        )
    elif market_state == "historical":
        _picked_str = hist_date.strftime("%d %b %Y") if hist_date else trade_date
        _snap_note = ""
        if hist_date and trade_date != "—" and str(hist_date) != trade_date:
            _snap_note = f" — {_picked_str} was non-trading, showing the nearest prior session"
        state_html = (
            f"<span style='color:#5B8DEF;font-weight:700'>📅 HISTORICAL</span>"
            f"<span style='color:{_txt}'> · showing {trade_date} official close{_snap_note} · "
            f"{active_count} stocks</span>"
        )
    else:
        state_html = (
            f"<span style='color:#F0485A;font-weight:700'>● CLOSED</span>"
            f"<span style='color:{_txt}'> · showing {trade_date} official close · "
            f"{active_count} stocks</span>"
        )

    st.markdown(
        f"<div style='font-family:'Inter',sans-serif;font-size:14px;margin-bottom:14px;color:{_txt}'>"
        f"✓ {state_html}"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── Read controls from session_state (all set by sidebar) ───────────────
    # Update the available sectors cache so the sidebar selectbox has the
    # correct options on the next rerun.
    sectors = ["All"] + sorted([s for s in quoted["sector"].dropna().unique().tolist() if s != "—"])
    if (quoted["sector"] == "—").any():
        sectors = sectors + ["—"]

    old_sectors = st.session_state.get("available_sectors", ["All"])
    st.session_state["available_sectors"] = sectors
    # First time data loads, trigger a rerun so the sidebar selectbox
    # immediately shows the full sector list rather than just "All".
    if len(old_sectors) <= 1 and len(sectors) > 1:
        st.rerun()

    sector_sel = st.session_state.get("sector_sel", "All")
    if sector_sel not in sectors:
        sector_sel = "All"
        st.session_state["sector_sel"] = "All"

    view = st.session_state.get("view_sel", "Gainers")

    # ── Build the directional pool (used for both the table and Top-N) ─────
    df = quoted.copy()
    if sector_sel != "All":
        df = df[df["sector"] == sector_sel]

    if view == "Gainers":
        direction_pool = df[df["chg_pct"] > 0].sort_values("chg_pct", ascending=False).reset_index(drop=True)
    else:
        direction_pool = df[df["chg_pct"] < 0].sort_values("chg_pct", ascending=True).reset_index(drop=True)

    pool_size = len(direction_pool)
    # Cache pool_size so the sidebar slider can set its max correctly next rerun
    st.session_state["pool_size"] = pool_size

    # Read Top N from sidebar slider (clamped to actual pool size)
    top_n = min(st.session_state.get("top_n_val", 10), pool_size) if pool_size >= 1 else 0

    top_n_slice  = direction_pool.head(top_n) if top_n > 0 else direction_pool.head(0)
    top_n_avg    = top_n_slice["chg_pct"].mean() if not top_n_slice.empty else 0.0
    top_n_label  = f"Top {top_n} {view} Avg"

    # Index-return contribution of those same Top N names: Σ(weightᵢ × chgᵢ).
    if not top_n_slice.empty:
        top_n_contrib_bps = float((top_n_slice["weight"] * top_n_slice["chg_pct"]).sum()) * 100
    else:
        top_n_contrib_bps = 0.0
    top_n_contrib_label = f"Top {top_n} {view} Contrib"

    # ── Summary stats: Gainers · Losers · Unchanged · Top-N Avg · Overall ──
    gainers   = (quoted["chg_pct"] > 0).sum()
    losers    = (quoted["chg_pct"] < 0).sum()
    unchanged = (quoted["chg_pct"] == 0).sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, label, val, color in [
        (c1, "Gainers",       f"{gainers}",               "#0CA86C"),
        (c2, "Losers",        f"{losers}",                "#C8303F"),
        (c3, "Unchanged",     f"{unchanged}",             "#4D6080"),
        (c4, top_n_label,     f"{top_n_avg:+.2f}%",       "#0CA86C" if top_n_avg          >= 0 else "#C8303F"),
        (c5, top_n_contrib_label, f"{top_n_contrib_bps:+.1f}bps", "#0CA86C" if top_n_contrib_bps >= 0 else "#C8303F"),
        (c6, index_label, f"{index_return:+.2f}%", "#0CA86C" if index_return    >= 0 else "#C8303F"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#F0F4FF;border:1px solid rgba(91,141,239,.2);
                border-radius:8px;padding:12px 16px;text-align:center;min-height:80px;
                display:flex;flex-direction:column;justify-content:center">
              <div style="font-family:'Inter', sans-serif;font-size:9px;font-weight:600;
                   color:#4D6080;letter-spacing:.5px;text-transform:uppercase;
                   margin-bottom:6px;white-space:nowrap;overflow:hidden;
                   text-overflow:ellipsis">{label}</div>
              <div style="font-family:'Inter', sans-serif;font-size:20px;
                   font-weight:700;color:{color};line-height:1">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Cache footnotes for sidebar "About" section ──────────────────────
    _etf_return_note = (
        f"ⓘ {index_label} = {etf_label}'s own live price change"
        if index_return_is_live else
        f"ⓘ {index_label} = bottom-up weighted estimate "
        f"({etf_label}'s own quote was unavailable)"
    )
    st.session_state["screener_about_main"] = (
        f"{_etf_return_note}. "
        f"Top {top_n} {view} Contrib = those same {top_n} names' index-weighted share of the "
        f"move, in basis points (Σ weightᵢ × chgᵢ over the full {total_universe}-name base; "
        f"{quoted_weight:.1f}% of index weight is currently quoted "
        f"({priced_with_quote}/{total_universe} names), the rest assumed flat)."
    )
    if cash_count > 0:
        names_str = ", ".join(cash_names[:6]) + ("…" if cash_count > 6 else "")
        st.session_state["screener_about_cash"] = (
            f"⊘ {cash_count} non-priceable holding(s) treated as Cash & Other "
            f"(excluded from weighted return): {names_str}"
        )
    else:
        st.session_state["screener_about_cash"] = ""

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── Market caps for the full displayed pool (prev-close × shares) ──────
    # Cached 24h; computed once per day across the whole universe.
    pool_tickers = tuple(direction_pool["ticker"].tolist())
    if pool_tickers:
        if hist_mode:
            # Reuse the prev_close already fetched for the picked historical
            # date — re-pulling "recent" bars here would silently give
            # today's market caps instead of the backdated ones.
            prev_prices = tuple(zip(direction_pool["ticker"], direction_pool["prev_close"]))
        else:
            try:
                raw_prev = yf.download(
                    list(pool_tickers), period="7d", interval="1d",
                    auto_adjust=True, progress=False, threads=True,
                )
                prev_prices = tuple()
                if not raw_prev.empty:
                    pc_close = raw_prev["Close"]
                    et       = timezone(timedelta(hours=-4))
                    today_et = datetime.now(et).date()
                    pp = []
                    for tk in pool_tickers:
                        if tk not in pc_close.columns:
                            continue
                        colp = pc_close[tk].dropna()
                        completed = colp[[d != today_et for d in colp.index.map(lambda x: x.date())]]
                        series = completed if not completed.empty else colp
                        if not series.empty:
                            pp.append((tk, float(series.iloc[-1])))
                    prev_prices = tuple(pp)
            except Exception:
                prev_prices = tuple()

        with st.spinner("Fetching market caps (prev close)…"):
            mktcap_map = fetch_market_caps(pool_tickers, prev_prices)
        direction_pool = direction_pool.copy()
        direction_pool["mkt_cap"] = direction_pool["ticker"].map(mktcap_map)
    else:
        direction_pool = direction_pool.copy()
        direction_pool["mkt_cap"] = None

    # ── Excel export — current view, plain data ────────────────────────────
    # Mirrors the on-screen table exactly: same column order, same row order,
    # same filtering (sector + Gainers/Losers). Built lazily and only when the
    # user clicks the download button (no cost on normal page renders).
    import io
    export_df = pd.DataFrame({
        "Rank":       range(1, len(direction_pool) + 1),
        "Ticker":     direction_pool["ticker"].values,
        "Company":    direction_pool["company"].values,
        "Sector":     direction_pool["sector"].values,
        "Price":      direction_pool["price"].values,
        "Chg %":      direction_pool["chg_pct"].values,
        "Chg $":      direction_pool["chg_abs"].values,
        "Weight %":   (direction_pool["weight"] * 100).values,
        "Volume":     direction_pool["volume"].values,
        "Market Cap": direction_pool["mkt_cap"].values,
    })
    xlsx_buf = io.BytesIO()
    with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
        export_df.to_excel(writer, sheet_name=f"{etf_label} {view}", index=False)
    xlsx_buf.seek(0)
    _fname_date = (
        f"asof_{trade_date.replace('-', '')}" if hist_mode and trade_date != "—"
        else datetime.now(sgt).strftime('%Y%m%d_%H%M')
    )
    fname = (
        f"{etf_label}_{view.lower()}_"
        f"{('all' if sector_sel == 'All' else sector_sel.replace(' ', '_'))}_"
        f"{_fname_date}.xlsx"
    )
    col_dl, col_pad = st.columns([2, 8])
    with col_dl:
        # Export button styled for white background
        st.markdown("""
        <style>
        div[data-testid="stDownloadButton"] button {
            background: #EEF2FC !important;
            border: 1px solid rgba(61,109,214,.4) !important;
            color: #1A2540 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            letter-spacing: .3px !important;
            padding: 8px 18px !important;
            border-radius: 6px !important;
            transition: all .15s !important;
        }
        div[data-testid="stDownloadButton"] button:hover {
            background: #dde5f7 !important;
            border-color: rgba(61,109,214,.7) !important;
            color: #1A2540 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.download_button(
            label="📊  Export to Excel",
            data=xlsx_buf.getvalue(),
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_{etf_label}_{view}",
            help=f"Download the current view ({len(export_df)} rows) as .xlsx",
        )

    # ── Stock table — ALL constituents in the directional pool, sortable ──
    rows_html = ""
    for i, row in direction_pool.iterrows():
        chg_cls   = "chg-pos" if row["chg_pct"] >= 0 else "chg-neg"
        chg_sign  = "▲" if row["chg_pct"] >= 0 else "▼"
        wt_pct    = row.get("weight", 0.0) * 100
        mkt_cap_v = row.get("mkt_cap")
        mkt_cap_sort = "" if (mkt_cap_v is None or pd.isna(mkt_cap_v)) else f"{mkt_cap_v}"
        ticker_e  = html.escape(str(row["ticker"]))
        company_e = html.escape(str(row["company"]))
        sector_e  = html.escape(str(row["sector"]))
        split_tag_v = row.get("split_tag")
        split_badge = ""
        if pd.notna(split_tag_v):
            split_badge = (
                f' <span title="Recent corporate action — chg% is normalized for this split" '
                f'style="font-size:10px;padding:1px 6px;border-radius:3px;'
                f'background:rgba(245,158,11,.15);color:#F59E0B;'
                f'border:1px solid rgba(245,158,11,.35);white-space:nowrap">'
                f'↺ {html.escape(str(split_tag_v))}</span>'
            )
        rows_html += f"""
        <tr>
          <td data-sort="{i+1}" style="color:#4D6080;width:36px">{i+1}</td>
          <td data-sort="{ticker_e}"><span class="ticker-badge">{ticker_e}</span>{split_badge}</td>
          <td data-sort="{company_e}" style="max-width:180px;overflow:hidden;text-overflow:ellipsis;
              white-space:nowrap">{company_e}</td>
          <td data-sort="{sector_e}"><span class="sector-tag">{sector_e}</span></td>
          <td data-sort="{row['price']}" style="text-align:right">${row['price']:,.2f}</td>
          <td data-sort="{row['chg_pct']}" class="{chg_cls}" style="text-align:right">
              {chg_sign} {abs(row['chg_pct']):.2f}%</td>
          <td data-sort="{row['chg_abs']}" class="{chg_cls}" style="text-align:right">
              {'+' if row['chg_abs']>=0 else ''}{row['chg_abs']:.2f}</td>
          <td data-sort="{wt_pct}" style="text-align:right;color:#1A2540">{wt_pct:.2f}%</td>
          <td data-sort="{row['volume']}" style="text-align:right;color:#1A2540">{fmt_volume(row['volume'])}</td>
          <td data-sort="{mkt_cap_sort}" style="text-align:right;color:#1A2540">{fmt_mktcap(row.get('mkt_cap'))}</td>
        </tr>"""

    table_doc    = _SORTABLE_TABLE_TEMPLATE.replace("__ROWS__", rows_html)
    table_height = min(70 + 38 * max(len(direction_pool), 1), 900)
    components.html(table_doc, height=table_height, scrolling=True)

    st.markdown(f"""
    <div style="font-family:'Inter', sans-serif;font-size:10px;color:#6B7A99;
        margin-top:8px;text-align:right">
      Data: Yahoo Finance · Weights: live shares × price · Market cap: prev-day close ·
      Showing all {len(direction_pool)} {view.lower()} of {active_count} priced · Click any column header to sort ↕ ·
      ↺ = recent stock split, chg% normalized for the split
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# EVENTS CALENDAR — CONFIG
# ─────────────────────────────────────────────────────────────────────────────
# FOMC meeting calendar, taken directly from the Federal Reserve's own
# published schedule (federalreserve.gov). 2026 dates are confirmed; 2027
# dates are the Fed's own "tentative" schedule (announced 05 Sep 2025),
# confirmed meeting-by-meeting as each one approaches — per the Fed's own
# disclosure this almost never moves. Each tuple is (decision date, whether
# the meeting carries a Summary of Economic Projections / dot plot).
FOMC_DATES = [
    (date(2026, 1, 28), False),
    (date(2026, 3, 18), True),
    (date(2026, 4, 29), False),
    (date(2026, 6, 17), True),
    (date(2026, 7, 29), False),
    (date(2026, 9, 16), True),
    (date(2026, 10, 28), False),
    (date(2026, 12, 9), True),
    (date(2027, 1, 27), False),
    (date(2027, 3, 17), True),
    (date(2027, 4, 28), False),
    (date(2027, 6, 9), True),
    (date(2027, 7, 28), False),
    (date(2027, 9, 15), True),
    (date(2027, 10, 27), False),
    (date(2027, 12, 8), True),
]

# FRED "release" IDs whose /fred/release/dates calendar mirrors the source
# agency's own official forward schedule (BLS/BEA/Census typically publish
# these 6-18 months ahead). Risk scoring is deferred for now — this is a
# pure forward-looking calendar (date + category only).
FRED_CALENDAR_RELEASES = {
    "nfp":     {"release_id": 50, "name": "Employment Situation (NFP + Unemployment)",
                "category": "Labor"},
    "cpi":     {"release_id": 10, "name": "CPI / Core CPI",
                "category": "Inflation"},
    "corepce": {"release_id": 54, "name": "Core PCE (Fed's Preferred Gauge)",
                "category": "Inflation"},
    "retail":  {"release_id": 9,  "name": "Retail Sales",
                "category": "Growth"},
    "ppi":     {"release_id": 46, "name": "PPI (Final Demand)",
                "category": "Inflation"},
}
UMICH_RELEASE_ID = 91   # "Surveys of Consumers" — posts 2 dates/month (prelim, final)

EVENT_CATEGORY_COLORS = {
    "Fed":       "#A78BFA",
    "Labor":     "#5B8DEF",
    "Inflation": "#F0485A",
    "Growth":    "#4D6080",
    "Sentiment": "#F59E0B",
}

BACKDROP_TICKERS = [
    ("Gold",          "GLD"),
    ("Dollar",        "UUP"),
    ("Long Duration", "TLT"),
    ("Russell 2000",  "IWM"),
    ("Nasdaq 100",    "QQQ"),
    ("S&P 500",       "SPY"),
]
BACKDROP_HORIZONS = [
    ("1D", pd.DateOffset(days=1)),
    ("1W", pd.DateOffset(days=7)),
    ("1M", pd.DateOffset(months=1)),
    ("3M", pd.DateOffset(months=3)),
    ("6M", pd.DateOffset(months=6)),
    ("1Y", pd.DateOffset(years=1)),
]

# ─────────────────────────────────────────────────────────────────────────────
# EVENTS CALENDAR — DATA FETCH
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=21600, show_spinner=False)
def _fetch_fred_release_dates_raw(release_id: int):
    """
    Scheduled/actual dates for a FRED release (fred/release/dates), most-
    recent-first. FRED mirrors each source agency's OWN published release
    calendar, so forward dates here are genuine official schedule entries,
    not an estimate. Cached 6h; callers key on today's date so this rebuilds
    at most once/day.

    include_release_dates_with_no_data=true is REQUIRED here — FRED's
    default (false) excludes any release date that doesn't have data
    attached yet, which by definition excludes every future/scheduled
    date. Without this flag every category except the hardcoded FOMC
    calendar silently returns zero forward dates.

    Returns (dates: list[str], diag: dict) — diag carries the HTTP status
    and either an error message or a snippet of the raw response, so a
    failure is visible in the UI instead of only a server-log print.
    """
    fred_key = st.secrets["FRED_API_KEY"]
    url = (
        f"https://api.stlouisfed.org/fred/release/dates"
        f"?release_id={release_id}&api_key={fred_key}"
        f"&file_type=json&sort_order=desc&limit=60"
        f"&include_release_dates_with_no_data=true"
    )
    try:
        resp = requests.get(url, timeout=20)
        diag = {"http_status": resp.status_code, "error": None}
        resp.raise_for_status()
        data = resp.json()
        dates = [d["date"] for d in data.get("release_dates", [])]
        diag["raw_count"] = len(dates)
        if not dates:
            diag["response_snippet"] = str(data)[:300]
        return dates, diag
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        print(f"FRED release-dates fetch failed [{release_id}]: {err}")
        return [], {"http_status": None, "error": err, "raw_count": 0}


def _next_release_dates(release_id: int, today: date, n: int = 3):
    """Next n scheduled dates on/after `today` for a release, ascending.
    Returns (dates, diag) — diag is enriched with the future-date count."""
    raw, diag = _fetch_fred_release_dates_raw(release_id)
    parsed = sorted(datetime.strptime(d, "%Y-%m-%d").date() for d in raw)
    future = [d for d in parsed if d >= today]
    diag["future_count"] = len(future)
    return future[:n], diag


@st.cache_data(ttl=21600, show_spinner=False)
def build_events_calendar(cache_bucket: str):
    """
    Builds the forward-looking US macro events calendar. cache_bucket is
    today's ET date string (rebuild-once-per-day cache key).

    Sources: FOMC = Federal Reserve's own published calendar (hardcoded
    above). CPI/PPI/Core PCE/Retail Sales/NFP = FRED's release-date
    calendar, which mirrors BLS/BEA/Census's own official schedules.
    ADP = derived — always the Wednesday 2 days before the Employment
    Situation release. Michigan Sentiment = FRED's Surveys of Consumers
    calendar, which posts 2 dates/month (prelim, then final) — split
    accordingly.

    Returns (df, diagnostics) — diagnostics is a list of per-source dicts
    (name, release_id, http_status, raw_count, future_count, error) so a
    silent fetch failure is visible in the UI rather than only server logs.
    """
    today = datetime.strptime(cache_bucket, "%Y-%m-%d").date()
    rows  = []
    diagnostics = [{
        "source": "FOMC Decision", "release_id": "hardcoded", "http_status": "n/a",
        "raw_count": len(FOMC_DATES), "future_count": sum(1 for d, _ in FOMC_DATES if d >= today),
        "error": None,
    }]

    for d, has_sep in FOMC_DATES:
        if d < today:
            continue
        name = "FOMC Decision" + (" (+ SEP / Dot Plot)" if has_sep else "")
        tentative = d.year >= 2027
        if tentative:
            name += " *"
        rows.append({"date": d, "name": name, "category": "Fed", "tentative": tentative})

    nfp_cfg = FRED_CALENDAR_RELEASES["nfp"]
    nfp_dates, nfp_diag = _next_release_dates(nfp_cfg["release_id"], today, n=3)
    diagnostics.append({"source": nfp_cfg["name"], "release_id": nfp_cfg["release_id"], **nfp_diag})
    for d in nfp_dates:
        rows.append({"date": d, "name": nfp_cfg["name"], "category": "Labor", "tentative": False})
        adp_d = d - timedelta(days=2)   # ADP's standing Wednesday-before-payrolls slot
        if adp_d >= today:
            rows.append({"date": adp_d, "name": "ADP Employment Report",
                          "category": "Labor", "tentative": False})

    for key in ("cpi", "corepce", "retail", "ppi"):
        cfg = FRED_CALENDAR_RELEASES[key]
        dates, diag = _next_release_dates(cfg["release_id"], today, n=3)
        diagnostics.append({"source": cfg["name"], "release_id": cfg["release_id"], **diag})
        for d in dates:
            rows.append({"date": d, "name": cfg["name"], "category": cfg["category"], "tentative": False})

    umich_dates_raw, umich_diag = _next_release_dates(UMICH_RELEASE_ID, today, n=8)
    diagnostics.append({"source": "Michigan Sentiment", "release_id": UMICH_RELEASE_ID, **umich_diag})
    umich_dates = sorted(set(umich_dates_raw))
    by_month = {}
    for d in umich_dates:
        by_month.setdefault((d.year, d.month), []).append(d)
    for _, ds in by_month.items():
        ds = sorted(ds)
        if len(ds) >= 1:
            rows.append({"date": ds[0], "name": "Michigan Sentiment (Prelim)",
                          "category": "Sentiment", "tentative": False})
        if len(ds) >= 2:
            rows.append({"date": ds[1], "name": "Michigan Sentiment (Final)",
                          "category": "Sentiment", "tentative": False})

    if not rows:
        empty = pd.DataFrame(columns=["date", "name", "category", "tentative", "days_away"])
        return empty, diagnostics

    df = (pd.DataFrame(rows)
          .drop_duplicates(subset=["date", "name"])
          .sort_values("date")
          .reset_index(drop=True))
    df["days_away"] = df["date"].apply(lambda d: (d - today).days)
    df["date"]      = pd.to_datetime(df["date"])
    return df, diagnostics


@st.cache_data(ttl=900, show_spinner=False)
def fetch_market_backdrop(cache_bucket: str):
    """
    Trailing returns for the backdrop tickers + VIX level/1D change.
    Horizons are anchored to the SAME calendar day-of-month, N months/years
    back (e.g. today 13 Jul 2026 → 1M target is 13 Jun 2026, 3M target is
    13 Apr 2026, 1Y target is 13 Jul 2025) via pd.DateOffset, not a fixed
    day-count. For each horizon we look up the price as of that target date
    via pandas' asof(): if the target lands on a weekend/holiday (a
    non-trading day), asof naturally resolves to the last trading day AT OR
    BEFORE it (walking back one day at a time until a trading day is found).
    YTD compares against the last trading close of the prior calendar year
    (i.e. as of 31 Dec, same asof logic). cache_bucket = today's ET date
    (rebuild-once-per-day); ttl=900s is just a backstop. Fetches 3y of
    history so even the 1Y/YTD lookups have safe buffer at the boundary.
    """
    tickers = [tk for _, tk in BACKDROP_TICKERS] + ["^VIX"]
    # Use explicit start/end instead of period="3y" — the period param
    # computes its epoch range from the local system clock, which on a
    # non-US-timezone host can land on or before the latest US close and
    # silently exclude the most recent trading day. Anchoring to the
    # ET-aware cache_bucket + 1 day (yfinance end is exclusive) guarantees
    # the latest US close is always captured.
    today_et   = datetime.strptime(cache_bucket, "%Y-%m-%d").date()
    end_date   = today_et + timedelta(days=1)
    start_date = today_et - timedelta(days=3 * 365 + 30)
    try:
        raw = yf.download(tickers, start=str(start_date), end=str(end_date),
                           interval="1d",
                           auto_adjust=True, progress=False, threads=True)
    except Exception as e:
        print(f"Market backdrop fetch failed: {e}")
        return pd.DataFrame(), None, None, None

    if raw.empty or "Close" not in raw:
        return pd.DataFrame(), None, None, None
    close = raw["Close"]

    # Strip today's partial bar ONLY when the US market is currently open.
    # At 10 AM SGT July 29 ET is still July 28; unconditionally filtering
    # < today_ET would exclude the July 28 session we want to show.
    # Outside open hours the last daily bar is always the completed close.
    et            = timezone(timedelta(hours=-4))
    today_date_et = datetime.now(et).date()
    if get_market_state() == "open":
        completed_idx = [d for d in close.index if d.date() < today_date_et]
        if completed_idx:
            close = close.loc[completed_idx]

    def _asof_pct(col: pd.Series, last_val: float, target: pd.Timestamp):
        base = col.asof(target)
        if base is None or (isinstance(base, float) and pd.isna(base)) or base == 0:
            return None
        return (last_val / float(base) - 1) * 100

    rows = []
    for label, tk in BACKDROP_TICKERS:
        if tk not in close.columns:
            continue
        col = close[tk].dropna()
        if col.empty:
            continue
        last_date = col.index[-1]
        last      = float(col.iloc[-1])
        row       = {"label": label, "ticker": tk, "last": last}
        for h_label, offset in BACKDROP_HORIZONS:
            target = last_date - offset
            row[h_label] = _asof_pct(col, last, target)
        ytd_target = pd.Timestamp(year=last_date.year - 1, month=12, day=31)
        row["YTD"] = _asof_pct(col, last, ytd_target)
        rows.append(row)
    backdrop_df = pd.DataFrame(rows)

    vix_last, vix_chg, vix_chg_pct = None, None, None
    if "^VIX" in close.columns:
        vix_col = close["^VIX"].dropna()
        if len(vix_col) >= 2:
            vix_last = float(vix_col.iloc[-1])
            vix_prev = float(vix_col.iloc[-2])
            vix_chg  = vix_last - vix_prev
            vix_chg_pct = (vix_last / vix_prev - 1) * 100 if vix_prev else None

    return backdrop_df, vix_last, vix_chg, vix_chg_pct

# ─────────────────────────────────────────────────────────────────────────────
# EVENTS CALENDAR — DISPLAY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _fmt_days_away(n: int) -> str:
    if n == 0: return "Today"
    if n == 1: return "Tomorrow"
    return f"in {n} days"


def _diverging_bg(v, vmax=20.0):
    """
    Background + text colour for a signed % cell, RdYlGn-style: deep red at
    -vmax, pale cream at 0, deep green at +vmax. `vmax` is typically computed
    per-column by the caller (see render_backdrop_table_html) so each
    horizon's own natural range of movement gets full color contrast.
    Returns (bg_css, text_css).
    """
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "#F4F6FA", "#8898BB"
    t = max(-1.0, min(1.0, v / vmax))
    stops = [
        (-1.00, (178, 24, 43)),
        (-0.50, (244, 165, 130)),
        (0.00,  (255, 247, 214)),
        (0.50,  (166, 217, 106)),
        (1.00,  (26, 152, 80)),
    ]
    r = g = b = 0
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 != t0 else 0
            r = int(c0[0] + f * (c1[0] - c0[0]))
            g = int(c0[1] + f * (c1[1] - c0[1]))
            b = int(c0[2] + f * (c1[2] - c0[2]))
            break
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    text = "#1A2540" if luminance > 140 else "#FFFFFF"
    return f"rgb({r},{g},{b})", text


def _event_card_html(label: str, value_html: str, sub_html: str, accent: str = "#1A2540") -> str:
    return f"""
    <div style="background:#F0F4FF;border:1px solid rgba(91,141,239,.2);
        border-radius:8px;padding:14px 16px;min-height:96px;
        display:flex;flex-direction:column;justify-content:center;gap:5px">
      <div style="font-family:'Inter',sans-serif;font-size:9px;font-weight:600;
           color:#4D6080;letter-spacing:.5px;text-transform:uppercase;
           white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{label}</div>
      <div style="font-family:'Inter',sans-serif;font-size:15px;font-weight:700;
           color:{accent};line-height:1.25">{value_html}</div>
      <div style="font-family:'Inter',sans-serif;font-size:10.5px;color:#8898BB;
           line-height:1.3">{sub_html}</div>
    </div>
    """


def render_backdrop_table_html(df: pd.DataFrame) -> str:
    if df.empty:
        return "<div class='sb-footnote'>Backdrop data unavailable.</div>"
    horizon_labels = [h for h, _ in BACKDROP_HORIZONS] + ["YTD"]
    header_cells   = "".join(f"<th>{h}</th>" for h in horizon_labels)

    # Colour scale is ONE consistent scale across the whole table (not
    # per-column) so intensity always tracks absolute magnitude the same way
    # everywhere. It's fixed at a sensible clamp (±15%) rather than derived
    # from the single largest move present — using the literal data max as
    # vmax meant one outlier (e.g. a +30%+ 1Y move) stretched the whole
    # scale so that genuinely large moves like -15.67% still looked pale.
    # Anything at or beyond ±15% simply renders as the deepest red/green.
    vmax = 15.0

    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for h in horizon_labels:
            v = row.get(h)
            bg, txt = _diverging_bg(v, vmax=vmax)
            disp = f"{v:+.2f}%" if v is not None and not pd.isna(v) else "—"
            cells += f"<td style='background:{bg};color:{txt};border-radius:3px'>{disp}</td>"
        rows_html += f"""
        <tr>
          <td>{row['label']}<span class="backdrop-ticker-chip">{row['ticker']}</span></td>
          {cells}
        </tr>"""
    return f"""
    <table class="backdrop-table">
      <thead><tr><th>Asset</th>{header_cells}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table>"""


CATEGORY_ORDER = ["Fed", "Labor", "Inflation", "Growth", "Sentiment"]
CATEGORY_Y     = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}


def make_catalyst_tape(df: pd.DataFrame, today: date, window_days: int = 180) -> go.Figure:
    window_df = df[df["days_away"].between(0, window_days)].copy()
    fig = go.Figure()
    for cat, color in EVENT_CATEGORY_COLORS.items():
        cat_df = window_df[window_df["category"] == cat]
        if cat_df.empty:
            continue
        fig.add_trace(go.Scatter(
            x=cat_df["date"], y=[CATEGORY_Y[cat]] * len(cat_df),
            mode="markers", name=cat,
            marker=dict(size=13, color=color, line=dict(width=1, color="rgba(255,255,255,.7)")),
            customdata=cat_df["name"],
            hovertemplate="<b>%{customdata}</b><br>%{x|%d %b %Y}<extra></extra>",
        ))
    today_ts = pd.Timestamp(today)
    fig.add_shape(
        type="line", xref="x", yref="paper",
        x0=today_ts, x1=today_ts, y0=0, y1=1,
        line=dict(dash="dot", width=1.5, color="rgba(26,37,64,.45)"),
    )
    fig.add_annotation(
        x=today_ts, y=1, yref="paper", yanchor="bottom",
        text="Today", showarrow=False,
        font=dict(color="#1A2540", size=11),
    )
    fig.update_layout(
        height=380,
        margin=dict(l=0, r=0, t=34, b=0),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#4D6080", size=11),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11, color="#1A2540")),
        yaxis=dict(range=[-0.6, len(CATEGORY_ORDER) - 0.4], showgrid=True,
                    gridcolor="rgba(0,0,0,.06)", zeroline=False,
                    tickvals=list(CATEGORY_Y.values()), ticktext=CATEGORY_ORDER,
                    tickfont=dict(size=11, color="#1A2540")),
        showlegend=False,
        hoverlabel=dict(bgcolor="#F0F4FF", bordercolor="rgba(91,141,239,.3)",
                         font=dict(family="Inter, sans-serif", size=12, color="#1A2540")),
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# EVENTS CALENDAR — PAGE RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_events_calendar() -> None:
    sgt      = timezone(timedelta(hours=8))
    today_et = datetime.now(sgt).date()
    cache_bucket = str(today_et)

    st.markdown(
        f"<div style='font-weight:700;color:#1A2540;padding:20px 0 4px;"
        f"font-family:Inter,sans-serif;font-size:20px'>🗓️ Events Calendar"
        f"<span style='font-size:12px;font-weight:400;color:#4D6080;margin-left:12px'>"
        f"US Macro &amp; Fed Catalysts</span></div>"
        f"<div style='font-family:Inter,sans-serif;font-size:12px;color:#4D6080;"
        f"margin-bottom:18px'>A forward-looking calendar of the next US macro catalysts worth watching.</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("Loading events calendar…"):
        events_df, _events_diag = build_events_calendar(cache_bucket)
    with st.spinner("Loading market backdrop…"):
        backdrop_df, vix_last, vix_chg, vix_chg_pct = fetch_market_backdrop(cache_bucket)

    if events_df.empty:
        st.error("Could not load the events calendar (FRED release-calendar fetch failed). Try refreshing.")
        return

    # ── Summary cards ───────────────────────────────────────────────────────
    next_row  = events_df.iloc[0]
    fed_df    = events_df[events_df["category"] == "Fed"]
    next_fomc = fed_df.iloc[0] if not fed_df.empty else None
    next7     = events_df[events_df["days_away"] <= 7]

    # Level tag is purely descriptive (where VIX sits in absolute terms).
    # Colour tracks the DIRECTION of the 1D move: VIX rising means
    # volatility is increasing (bad news for risk assets) → red; VIX
    # falling → green. This is the opposite convention from an equity
    # index card, which is intentional — a rising vol gauge is the
    # negative signal here.
    if vix_chg is None:
        vix_dir_color = "#4D6080"
    elif vix_chg > 0:
        vix_dir_color = "#C8303F"   # VIX up → more volatile → red
    elif vix_chg < 0:
        vix_dir_color = "#0CA86C"   # VIX down → calmer → green
    else:
        vix_dir_color = "#4D6080"

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        st.markdown(_event_card_html(
            "Next Catalyst", next_row["name"],
            f"{_fmt_days_away(int(next_row['days_away']))} · {next_row['date'].strftime('%d %b %Y')}",
        ), unsafe_allow_html=True)
    with c2:
        if next_fomc is not None:
            st.markdown(_event_card_html(
                "Next FOMC", next_fomc["name"],
                f"{_fmt_days_away(int(next_fomc['days_away']))} · {next_fomc['date'].strftime('%d %b %Y')}",
            ), unsafe_allow_html=True)
        else:
            st.markdown(_event_card_html("Next FOMC", "—", "None scheduled in range"), unsafe_allow_html=True)
    with c3:
        st.markdown(_event_card_html(
            "Next 7 Days", str(len(next7)),
            "upcoming event(s)",
        ), unsafe_allow_html=True)
    with c4:
        vix_val = f"VIX {vix_last:.1f}" if vix_last is not None else "VIX —"
        vix_sub = (f"<span style='font-weight:700;color:#1A2540'>{vix_chg_pct:+.1f}% 1D</span>"
                   if vix_chg_pct is not None else "1D change unavailable")
        st.markdown(_event_card_html("Vol Backdrop", vix_val, vix_sub, accent=vix_dir_color), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)

    # ── Catalyst tape ────────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Inter,sans-serif;font-size:14px;font-weight:700;"
        "color:#1A2540;margin-bottom:2px'>Economic Calendar</div>"
        "<div style='font-family:Inter,sans-serif;font-size:10.5px;color:#8898BB;"
        "margin-bottom:6px'>* 2026 FOMC dates are confirmed; 2027 dates are the "
        "Fed's own tentative schedule.</div>",
        unsafe_allow_html=True,
    )
    fig = make_catalyst_tape(events_df, today_et)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="catalyst_tape")

    # ── Market backdrop ──────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Inter,sans-serif;font-size:14px;font-weight:700;"
        "color:#1A2540;margin:14px 0 8px'>Market Backdrop (% Δ)</div>",
        unsafe_allow_html=True,
    )
    st.markdown("""
    <style>
    .backdrop-table { width:100%; border-collapse:collapse; font-family:'Inter',sans-serif; font-size:14px; }
    .backdrop-table th { text-align:center; padding:11px 10px; font-size:11.5px; font-weight:700;
        letter-spacing:.6px; text-transform:uppercase; color:#4D6080; background:#EEF2FC;
        font-family:'Inter',sans-serif;
        border-bottom:1px solid rgba(91,141,239,.25); border-right:1px solid rgba(91,141,239,.10); }
    .backdrop-table th:first-child { text-align:left; font-family:'Inter',sans-serif; }
    .backdrop-table th:last-child { border-right:none; }
    .backdrop-table td { padding:10px 10px; text-align:center; font-weight:700;
        font-family:'Inter',sans-serif;
        font-variant-numeric: tabular-nums; letter-spacing:.2px;
        border-bottom:1px solid rgba(91,141,239,.07); border-right:1px solid rgba(91,141,239,.05); }
    .backdrop-table td:last-child { border-right:none; }
    .backdrop-table td:first-child { text-align:left; font-weight:600; color:#1A2540;
        font-family:'Inter',sans-serif; }
    .backdrop-ticker-chip {
        font-family:'Inter',sans-serif;
        font-size:10.5px; font-weight:700; color:#5B8DEF; background:rgba(91,141,239,.10);
        padding:1px 6px; border-radius:3px; letter-spacing:.2px; margin-left:6px; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(render_backdrop_table_html(backdrop_df), unsafe_allow_html=True)

    st.markdown(
        "<div style='font-family:Inter,sans-serif;font-size:10px;color:#8898BB;margin-top:6px'>"
        "Colour scale is one consistent scale across the whole table, fixed at ±15% — a -12% cell "
        "is always darker than a -2% cell, and any move at or beyond ±15% renders as the deepest "
        "red/green.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style="font-family:'Inter', sans-serif;font-size:10px;color:#6B7A99;
        margin-top:8px;text-align:right">
      Prices: Yahoo Finance (auto-adjusted daily close) · Horizons anchor to the same
      day-of-month N months/years back (1M/3M/6M/1Y; 1D/1W = 1/7 calendar days) —
      a non-trading anchor date resolves to the last trading day at or before it ·
      YTD = vs. last close of the prior calendar year
    </div>
    """, unsafe_allow_html=True)

    # ── Cache sidebar About footnote ─────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def _on_top_n_slider():
    """Slider moved → push new value into number input and shared state."""
    pool_max = st.session_state.get("pool_max", 50)
    val = min(max(int(st.session_state.get("sb_top_n", 10)), 1), pool_max)
    st.session_state["top_n_val"]    = val
    st.session_state["sb_top_n_num"] = val   # forces number input to update


def _on_top_n_input():
    """Number typed → push new value into slider and shared state."""
    pool_max = st.session_state.get("pool_max", 50)
    raw = st.session_state.get("sb_top_n_num", 10)
    val = min(max(int(raw), 1), pool_max)
    st.session_state["top_n_val"] = val
    st.session_state["sb_top_n"]  = val      # forces slider to update
    st.session_state["sb_top_n_num"] = val   # clamp in case user typed out-of-range


def main():
    sgt = timezone(timedelta(hours=8))
    now_str = datetime.now(sgt).strftime("%d %b %Y · %H:%M SGT")

    # ── Initialise session state ───────────────────────────────────────────
    if "page"               not in st.session_state: st.session_state["page"]               = "MACRO"
    if "idx_choice"         not in st.session_state: st.session_state["idx_choice"]         = "S&P 500"
    if "view_sel"           not in st.session_state: st.session_state["view_sel"]           = "Gainers"
    if "top_n_val"          not in st.session_state: st.session_state["top_n_val"]          = 10
    if "sector_sel"         not in st.session_state: st.session_state["sector_sel"]         = "All"
    if "available_sectors"  not in st.session_state: st.session_state["available_sectors"]  = ["All"]
    if "pool_size"          not in st.session_state: st.session_state["pool_size"]          = 50

    # ── Sidebar ────────────────────────────────────────────────────────────
    # All navigation and Markets controls live here. Streamlit re-runs the
    # whole script on every interaction, so sidebar widgets simply write to
    # session_state and the main content area reads from it.

    page_cur   = st.session_state["page"]
    is_macro   = page_cur == "MACRO"
    is_markets = page_cur == "MARKETS"
    is_events  = page_cur == "EVENTS"

    # ── White background for all pages ────────────────────────────────────
    st.markdown("""
    <style>
    [data-testid="stMain"]                  { background: #FFFFFF !important; }
    [data-testid="stMain"] .block-container { background: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Active-state CSS for all sidebar + legacy nav buttons ─────────────
    # Sidebar buttons are targeted by aria-label. All colour tokens are
    # injected here in one block so the dynamic f-string logic is centralised.
    idx_choice_css = st.session_state.get("idx_choice", "S&P 500")
    view_css       = st.session_state.get("view_sel", "Gainers")

    sp_active  = idx_choice_css == "S&P 500"
    ndx_active = not sp_active
    g_active   = view_css == "Gainers"
    l_active   = not g_active

    # ── Active/inactive colours — light sidebar ───────────────────────────
    # Active: blue-tinted background + white text (blue bg → white readable)
    # Inactive: transparent + dark text (light sidebar bg → dark readable)
    _act_col = "#FFFFFF"   # text on active (blue-bg) button
    _ina_col = "#1A2540"   # text on inactive (transparent) button

    sp_bg  = "rgba(91,141,239,.22)" if sp_active  else "transparent"
    sp_bd  = "rgba(91,141,239,.7)"  if sp_active  else "rgba(91,141,239,.2)"
    sp_fw  = "700"                  if sp_active  else "400"
    sp_col = _act_col               if sp_active  else _ina_col
    ndx_bg  = "rgba(91,141,239,.22)" if ndx_active else "transparent"
    ndx_bd  = "rgba(91,141,239,.7)"  if ndx_active else "rgba(91,141,239,.2)"
    ndx_fw  = "700"                  if ndx_active else "400"
    ndx_col = _act_col               if ndx_active else _ina_col
    g_bg   = "rgba(12,168,108,.15)"  if g_active else "transparent"
    g_bd   = "rgba(12,168,108,.5)"   if g_active else "rgba(12,168,108,.25)"
    g_fw   = "700"                   if g_active else "400"
    g_col  = "#0CA86C"
    l_bg   = "rgba(200,48,63,.15)"   if l_active else "transparent"
    l_bd   = "rgba(200,48,63,.5)"    if l_active else "rgba(200,48,63,.25)"
    l_fw   = "700"                   if l_active else "400"
    l_col  = "#C8303F"
    m_bg   = "rgba(91,141,239,.22)"  if is_macro   else "transparent"
    m_bd   = "rgba(91,141,239,.7)"   if is_macro   else "rgba(91,141,239,.2)"
    m_fw   = "700"                   if is_macro   else "400"
    m_col  = _act_col                if is_macro   else _ina_col
    mk_bg  = "rgba(91,141,239,.22)"  if is_markets else "transparent"
    mk_bd  = "rgba(91,141,239,.7)"   if is_markets else "rgba(91,141,239,.2)"
    mk_fw  = "700"                   if is_markets else "400"
    mk_col = _act_col                if is_markets else _ina_col
    ev_bg  = "rgba(91,141,239,.22)"  if is_events  else "transparent"
    ev_bd  = "rgba(91,141,239,.7)"   if is_events  else "rgba(91,141,239,.2)"
    ev_fw  = "700"                   if is_events  else "400"
    ev_col = _act_col                if is_events  else _ina_col

    st.markdown(f"""
    <style>
    button[aria-label="📊  Macro"]     {{ background:{m_bg}!important;  border-color:{m_bd}!important;  font-weight:{m_fw}!important; color:{m_col}!important; }}
    button[aria-label="📈  Market Screener"]   {{ background:{mk_bg}!important; border-color:{mk_bd}!important; font-weight:{mk_fw}!important; color:{mk_col}!important; }}
    button[aria-label="🗓️  Events Calendar"]   {{ background:{ev_bg}!important; border-color:{ev_bd}!important; font-weight:{ev_fw}!important; color:{ev_col}!important; }}
    button[aria-label="S&P 500"]       {{ background:{sp_bg}!important; border-color:{sp_bd}!important; font-weight:{sp_fw}!important; color:{sp_col}!important; }}
    button[aria-label="Nasdaq 100"]    {{ background:{ndx_bg}!important;border-color:{ndx_bd}!important;font-weight:{ndx_fw}!important;color:{ndx_col}!important;}}
    button[aria-label="Gainers"]       {{ background:{g_bg}!important;  border-color:{g_bd}!important;  font-weight:{g_fw}!important;  color:{g_col}!important; }}
    button[aria-label="Losers"]        {{ background:{l_bg}!important;  border-color:{l_bd}!important;  font-weight:{l_fw}!important;  color:{l_col}!important; }}
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # ── Identity ──────────────────────────────────────────────────────
        st.markdown("""
        <div class="sb-logo">
          <div class="sb-logo-title">📊 US Markets</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────────────────────────
        st.markdown('<div class="sb-section-label">Navigation</div>', unsafe_allow_html=True)
        if st.button("📊  Macro", key="btn_macro", use_container_width=True):
            st.session_state["page"] = "MACRO"
            st.rerun()
        if st.button("📈  Market Screener", key="btn_markets", use_container_width=True):
            st.session_state["page"] = "MARKETS"
            st.rerun()
        if st.button("🗓️  Events Calendar", key="btn_events", use_container_width=True):
            st.session_state["page"] = "EVENTS"
            st.rerun()

        # ── Macro section navigation (only when on Macro tab) ─────────────
        if is_macro:
            if "macro_section" not in st.session_state:
                st.session_state["macro_section"] = "Inflation"

            ms = st.session_state["macro_section"]
            inf_active = ms == "Inflation"
            lab_active = ms == "Labour Markets"
            inf_bg = "rgba(91,141,239,.22)" if inf_active else "transparent"
            inf_bd = "rgba(91,141,239,.7)"  if inf_active else "rgba(91,141,239,.2)"
            inf_fw = "700"                  if inf_active else "400"
            inf_col = "#FFFFFF"             if inf_active else "#1A2540"
            lab_bg = "rgba(91,141,239,.22)" if lab_active else "transparent"
            lab_bd = "rgba(91,141,239,.7)"  if lab_active else "rgba(91,141,239,.2)"
            lab_fw = "700"                  if lab_active else "400"
            lab_col = "#FFFFFF"             if lab_active else "#1A2540"

            st.markdown(f"""
            <style>
            button[aria-label="Inflation"]       {{ background:{inf_bg}!important; border-color:{inf_bd}!important; font-weight:{inf_fw}!important; color:{inf_col}!important; }}
            button[aria-label="Labour Markets"]  {{ background:{lab_bg}!important; border-color:{lab_bd}!important; font-weight:{lab_fw}!important; color:{lab_col}!important; }}
            </style>
            """, unsafe_allow_html=True)

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
            st.markdown('<div class="sb-section-label">Section</div>', unsafe_allow_html=True)
            if st.button("Inflation", key="sb_inflation", use_container_width=True):
                st.session_state["macro_section"] = "Inflation"
                st.rerun()
            if st.button("Labour Markets", key="sb_labour", use_container_width=True):
                st.session_state["macro_section"] = "Labour Markets"
                st.rerun()

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
            st.markdown('<div class="sb-section-label">Data</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="sb-footnote">
              <b style="color:#1A2540">Source</b><br>BLS (Official) · FRED (BEA/DOL)<br><br>
              <b style="color:#1A2540">Series</b><br>CPI · Core CPI · PPI · Core PCE · Unemp · NFP · Claims<br><br>
              <b style="color:#1A2540">Frequency</b><br>Monthly · Weekly (Claims) · 10yr History<br><br>
              <b style="color:#1A2540">Cache</b><br>Refreshes Every Hour<br><br>
              <b style="color:#1A2540">API</b><br>BLS Public Data API v2
            </div>
            """, unsafe_allow_html=True)

        # ── Markets controls (only when on Markets tab) ───────────────────
        if is_markets:
            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            # Index
            st.markdown('<div class="sb-section-label">Index</div>', unsafe_allow_html=True)
            col_sp, col_ndx = st.columns(2)
            with col_sp:
                if st.button("S&P 500", key="btn_sp500", use_container_width=True):
                    st.session_state["idx_choice"] = "S&P 500"
                    st.rerun()
            with col_ndx:
                if st.button("Nasdaq 100", key="btn_ndx100", use_container_width=True):
                    st.session_state["idx_choice"] = "Nasdaq 100"
                    st.rerun()

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            # Date — backdate the entire report to a specific past trading
            # day. Off by default (live/EOD data as before). Picking a
            # weekend/holiday date snaps to the last session that traded.
            st.markdown('<div class="sb-section-label">Date</div>', unsafe_allow_html=True)
            _et_now   = timezone(timedelta(hours=-4))
            _today_et = datetime.now(_et_now).date()

            hist_mode = st.checkbox(
                "View a past date",
                value=st.session_state.get("hist_mode", False),
                key="sb_hist_mode",
            )
            st.session_state["hist_mode"] = hist_mode

            if hist_mode:
                _default_date = st.session_state.get("hist_date", _today_et - timedelta(days=1))
                if _default_date > _today_et:
                    _default_date = _today_et
                picked_date = st.date_input(
                    "Date",
                    value=_default_date,
                    max_value=_today_et,
                    key="sb_hist_date",
                    label_visibility="collapsed",
                )
                st.session_state["hist_date"] = picked_date

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            # View
            st.markdown('<div class="sb-section-label">View</div>', unsafe_allow_html=True)
            col_g, col_l = st.columns(2)
            with col_g:
                if st.button("Gainers", key="btn_gainers", use_container_width=True):
                    st.session_state["view_sel"] = "Gainers"
                    st.rerun()
            with col_l:
                if st.button("Losers", key="btn_losers", use_container_width=True):
                    st.session_state["view_sel"] = "Losers"
                    st.rerun()

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            # Top N — slider + number input, fully bidirectional.
            # _on_top_n_slider / _on_top_n_input (defined at module level)
            # write to the OTHER widget's session_state key so both always
            # reflect the same value after any interaction.
            st.markdown('<div class="sb-section-label">Top N</div>', unsafe_allow_html=True)
            pool_max = max(1, st.session_state.get("pool_size", 50))
            st.session_state["pool_max"] = pool_max   # makes pool_max accessible inside callbacks
            current  = min(st.session_state.get("top_n_val", 10), pool_max)

            st.slider(
                "Top N",
                min_value=1, max_value=pool_max,
                value=current, step=1,
                key="sb_top_n",
                on_change=_on_top_n_slider,
                label_visibility="collapsed",
            )
            st.number_input(
                "Type exact number",
                min_value=1, max_value=pool_max,
                value=current, step=1,
                key="sb_top_n_num",
                on_change=_on_top_n_input,
                label_visibility="collapsed",
                help="Type an exact value — slider will move to match",
            )
            st.session_state["top_n_val"] = st.session_state.get("sb_top_n", current)

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            # Sector filter — populated with sectors cached from last render.
            # Shows only "All" on very first load, full list from second load onward.
            st.markdown('<div class="sb-section-label">Sector</div>', unsafe_allow_html=True)
            available_sectors = st.session_state.get("available_sectors", ["All"])
            prev_sel = st.session_state.get("sector_sel", "All")
            sec_idx  = available_sectors.index(prev_sel) if prev_sel in available_sectors else 0
            sector_sel = st.selectbox(
                "Sector",
                available_sectors,
                index=sec_idx,
                key="sb_sector",
                label_visibility="collapsed",
            )
            st.session_state["sector_sel"] = sector_sel

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            # About — methodology footnotes cached from last render_screener() call
            st.markdown('<div class="sb-section-label">About</div>', unsafe_allow_html=True)
            about_main = st.session_state.get("screener_about_main", "")
            about_cash = st.session_state.get("screener_about_cash", "")
            if about_main:
                st.markdown(
                    f'<div class="sb-footnote">{about_main}</div>',
                    unsafe_allow_html=True,
                )
                if about_cash:
                    st.markdown(
                        f'<div class="sb-footnote" style="margin-top:8px">{about_cash}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="sb-footnote">Load the screener to see methodology details.</div>',
                    unsafe_allow_html=True,
                )
            holdings_date = _get_holdings_date()
            st.markdown(f"""
            <div class="sb-footnote">
              <b style="color:#1A2540">Universe</b><br>{holdings_date}<br><br>
              <b style="color:#1A2540">Prices</b><br>Yahoo Finance · Market-state aware<br><br>
              <b style="color:#1A2540">Weights</b><br>Live shares × price<br><br>
              <b style="color:#1A2540">Cache</b><br>Prices 5 min · Sectors 24 h<br><br>
              <b style="color:#1A2540">Corp Actions</b><br>Splits auto-detected · chg% normalised
            </div>
            """, unsafe_allow_html=True)

        # ── Events Calendar controls (only when on Events tab) ────────────
        if is_events:
            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
            st.markdown('<div class="sb-section-label">About</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="sb-footnote">
              <b style="color:#1A2540">Sources</b><br>Federal Reserve · FRED Release Calendar · Yahoo Finance<br><br>
              <b style="color:#1A2540">Coverage</b><br>FOMC · NFP · ADP · CPI · Core PCE · PPI · Retail Sales · Michigan Sentiment<br><br>
              <b style="color:#1A2540">Cache</b><br>Calendar refreshes daily · Backdrop prices 15 min
            </div>
            """, unsafe_allow_html=True)

    # ── Route to page ──────────────────────────────────────────────────────
    if st.session_state["page"] == "MARKETS":
        render_screener()
        return

    if st.session_state["page"] == "EVENTS":
        render_events_calendar()
        return

    # ── Expanded chart view ────────────────────────────────────────────────
    # If an expand button was clicked, show ONLY the expanded chart +
    # a Back button. Nothing else renders until Back is pressed.
    if "expanded" in st.session_state:
        exp     = st.session_state["expanded"]
        cfg_e   = exp["cfg"]
        df_e    = exp["df_c"]
        which_e = exp["which"]
        title_e = exp["title"]

        # Back button — top left
        st.markdown("<div style='margin-bottom:20px'>", unsafe_allow_html=True)
        if st.button("← Back to Dashboard", key="back_btn"):
            del st.session_state["expanded"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Chart title
        st.markdown(f"""
        <div style="
            font-family:'Inter', sans-serif;font-size:22px;font-weight:700;
            color:#1A2540;margin-bottom:6px;letter-spacing:-.3px
        ">{title_e}</div>
        <div style="
            font-family:'Inter', sans-serif;font-size:11px;
            color:#4D6080;margin-bottom:24px;letter-spacing:.3px
        ">{cfg_e['full']}</div>
        """, unsafe_allow_html=True)

        # Full-height expanded chart
        # FRED cards store transform in cfg — use raw value column directly
        is_fred = cfg_e.get("transform") in ("claims", "adp", "sentiment")

        if is_fred:
            # Rebuild expanded chart from raw df using same logic as render_fred_card
            plot_df = df_e.tail(104 if cfg_e.get("freq") == "Weekly" else 60)
            color_e = cfg_e["color"]
            r_e = int(color_e[1:3], 16)
            g_e = int(color_e[3:5], 16)
            b_e = int(color_e[5:7], 16)
            fill_e = f"rgba({r_e},{g_e},{b_e},0.1)"

            if cfg_e["transform"] == "adp":
                bar_colors  = ["rgba(15,214,138,.7)"  if v >= 0 else "rgba(240,72,90,.7)"  for v in plot_df["value"]]
                bar_borders = ["rgba(15,214,138,.95)" if v >= 0 else "rgba(240,72,90,.95)" for v in plot_df["value"]]
                fig_exp = go.Figure(go.Bar(
                    x=plot_df["date"], y=plot_df["value"],
                    marker_color=bar_colors, marker_line_color=bar_borders,
                    marker_line_width=1,
                    hovertemplate="%{x|%b %Y}<br><b>%{y:+.0f}K</b><extra></extra>",
                ))
                fig_exp.add_hline(y=0, line_color="rgba(0,0,0,.12)", line_width=1)
            else:
                hover_fmt = "%{x|%d %b '%y}<br><b>%{y:.0f}K</b>" if cfg_e.get("freq") == "Weekly" else "%{x|%b %Y}<br><b>%{y:.1f}</b>"
                fig_exp = go.Figure(go.Scatter(
                    x=plot_df["date"], y=plot_df["value"],
                    mode="lines", line=dict(color=color_e, width=2),
                    fill="tozeroy", fillcolor=fill_e,
                    hovertemplate=hover_fmt + "<extra></extra>",
                ))
                y_min = max(0, plot_df["value"].min() * 0.9)
                y_max = plot_df["value"].max() * 1.05
                fig_exp.update_yaxes(range=[y_min, y_max])

            fig_exp.update_layout(
                height=550,
                margin=dict(l=0, r=0, t=8, b=0),
                paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                font=dict(family="Inter, sans-serif", color="#8898BB", size=11),
                xaxis=dict(showgrid=False, zeroline=False,
                           tickfont=dict(size=11, color="#1A2540"),
                           tickformat="%b '%y", nticks=8),
                yaxis=dict(showgrid=True, gridcolor="rgba(120,140,200,.06)", zeroline=False,
                           tickfont=dict(size=11, color="#1A2540"), nticks=6),
                hoverlabel=dict(bgcolor="#F0F4FF", bordercolor="rgba(91,141,239,.3)",
                                font=dict(family="Inter, sans-serif", size=13, color="#1A2540")),
                showlegend=False,
            )
        else:
            fig_exp = make_chart(df_e, cfg_e, which_e, height=550)

        st.plotly_chart(
            fig_exp, use_container_width=True,
            config={
                "displayModeBar": True,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                "displaylogo": False
            },
            key="expanded_chart"
        )
        return  # Stop here — don't render the rest of the dashboard

    # ── Hero banner ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-banner">
      <div class="hero-top">
        <div class="hero-left">
          <div class="hero-title"><span>US Macro Dashboard</span></div>
          <div class="hero-sub">OFFICIAL BLS DATA · {now_str}</div>
        </div>
        <div class="hero-right">
          <span class="bls-tag">BLS · OFFICIAL</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch BLS data ─────────────────────────────────────────────────────
    with st.spinner("Fetching data from BLS & FRED…"):
        try:
            all_data = fetch_bls_data()
        except Exception as e:
            st.error(f"❌ BLS API error: {e}")
            st.stop()
        try:
            fred_data = fetch_fred_data()
        except Exception as e:
            st.error(f"❌ FRED API error: {e}")
            fred_data = {}

    # ── Status + refresh row ───────────────────────────────────────────────
    bls_loaded  = len(all_data)
    fred_loaded = len([v for v in fred_data.values() if not v.empty])
    total_loaded = bls_loaded + fred_loaded
    total_series = len(SERIES) + len(FRED_SERIES)

    c_status, c_spacer, c_btn = st.columns([4, 6, 1])
    with c_status:
        cls = "status-ok" if total_loaded == total_series else "status-warn"
        st.markdown(
            f"<span class='{cls}'>✓ {total_loaded}/{total_series} series loaded "
            f"(BLS: {bls_loaded}/{len(SERIES)} · FRED: {fred_loaded}/{len(FRED_SERIES)})</span>",
            unsafe_allow_html=True
        )
    with c_btn:
        if st.button("↻", help="Refresh data", key="refresh_main"):
            st.cache_data.clear()
            st.rerun()

    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

    macro_section = st.session_state.get("macro_section", "Inflation")

    # ── INFLATION: CPI · Core CPI · PPI · Core PCE ───────────────────────
    if macro_section == "Inflation":
        # Row 1: CPI · Core CPI · PPI (BLS)
        cols_price = st.columns(3, gap="medium")
        for col, key in zip(cols_price, ["cpi", "corecpi", "ppi"]):
            with col:
                with st.container(border=True):
                    render_card(key, SERIES[key], all_data.get(key))
        st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
        # Row 2: Core PCE (BEA via FRED) — Fed's preferred inflation measure
        cols_pce = st.columns(3, gap="medium")
        with cols_pce[0]:
            with st.container(border=True):
                render_fred_card("corepce", FRED_SERIES["corepce"], fred_data.get("corepce"))

    # ── LABOR: Unemployment · NFP · Initial Claims ────────────────────────
    elif macro_section == "Labour Markets":
        # Row 1: Unemployment + NFP (BLS)
        cols_labor = st.columns(2, gap="medium")
        for col, key in zip(cols_labor, ["unemp", "nfp"]):
            with col:
                with st.container(border=True):
                    render_card(key, SERIES[key], all_data.get(key))
        st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
        # Row 2: Initial Claims (FRED)
        cols_labor2 = st.columns(2, gap="medium")
        with cols_labor2[0]:
            with st.container(border=True):
                render_fred_card("claims", FRED_SERIES["claims"], fred_data.get("claims"))



    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown("<hr style='margin-top:32px'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:11px;color:#4D6080;font-family:'Inter',sans-serif;text-align:center'>"
        "BLS data: CUSR0000SA0 · CUSR0000SA0L1E · WPSFD4 · LNS14000000 · CES0000000001 &nbsp;·&nbsp; "
        "FRED data: PCEPILFE (BEA) · ICSA (DOL)"
        "</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

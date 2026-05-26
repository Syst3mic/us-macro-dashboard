"""
US Macro Dashboard — Streamlit
Data: BLS Official API v2 + FRED API + Yahoo Finance
Indicators: CPI · Core CPI · PPI · Unemployment · NFP · Initial Claims
Markets: S&P 500 · Nasdaq 100 screener with weights
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import yfinance as yf

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="US Macro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600;700&display=swap');

html, body, [data-testid="stApp"] {
    background-color: #06080F;
    color: #FFFFFF;
    font-family: 'Sora', 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stAppViewContainer"] { background-color: #06080F; }
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #080C16; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 4rem; max-width: 1400px; }
hr { border-color: rgba(120,140,200,.1) !important; margin: 0.5rem 0 !important; }

.hero-banner {
    background: #06080F;
    border-bottom: 1px solid rgba(91,141,239,.2);
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
    display: flex; align-items: center;
    justify-content: space-between;
    flex-wrap: wrap; gap: 12px;
}
.hero-left { display: flex; flex-direction: column; gap: 6px; }
.hero-title {
    font-size: 28px; font-weight: 800; color: #FFFFFF;
    letter-spacing: -.5px; line-height: 1; font-family: 'Sora', sans-serif;
}
.hero-title span {
    background: linear-gradient(90deg, #5B8DEF, #22D3EE);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #FFFFFF; letter-spacing: .5px; }
.hero-right { display: flex; align-items: center; gap: 10px; }
.bls-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; font-weight: 700; letter-spacing: .7px;
    padding: 6px 14px; border-radius: 5px;
    background: rgba(91,141,239,.1); border: 1px solid rgba(91,141,239,.3); color: #7BA4F5;
}
.section-header {
    font-size: 20px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.5px; color: #FFFFFF;
    padding: 6px 0 14px; border-bottom: 1px solid rgba(120,140,200,.1);
    margin-bottom: 16px; font-family: 'Sora', sans-serif;
}
.section-header .section-icon { color: #5B8DEF; margin-right: 8px; }
.ind-name {
    font-size: 20px !important; font-weight: 700 !important; letter-spacing: .3px !important;
    text-transform: uppercase !important; color: #FFFFFF !important; font-family: 'Sora', sans-serif !important;
}
.ind-src {
    font-size: 9px; font-weight: 700; letter-spacing: .5px; padding: 3px 8px; border-radius: 3px;
    background: rgba(91,141,239,.07); border: 1px solid rgba(91,141,239,.15);
    color: #7BA4F5; font-family: 'IBM Plex Mono', monospace;
}
.ind-freq {
    font-size: 9px; color: #FFFFFF; padding: 3px 8px; border-radius: 3px;
    background: rgba(255,255,255,.06); border: 1px solid rgba(120,140,200,.12);
    font-family: 'IBM Plex Mono', monospace;
}
.stat-box {
    background: #0D1628; border: 1px solid rgba(120,140,200,.12);
    border-radius: 10px; padding: 18px 20px 14px; transition: border-color .2s;
}
.stat-box:hover { border-color: rgba(120,140,200,.25); }
.stat-period {
    font-size: 14px; font-weight: 700; letter-spacing: .5px;
    text-transform: uppercase; color: #FFFFFF; margin-bottom: 10px; font-family: 'Sora', sans-serif;
}
.stat-val {
    font-size: 30px; font-weight: 700; color: #FFFFFF;
    font-family: 'IBM Plex Mono', monospace; letter-spacing: -1px; line-height: 1;
}
.stat-delta {
    font-size: 11px; font-weight: 600; font-family: 'IBM Plex Mono', monospace;
    margin-top: 8px; display: inline-block; padding: 3px 9px; border-radius: 4px;
}
.stat-up { color: #0FD68A; background: rgba(15,214,138,.08); border: 1px solid rgba(15,214,138,.22); }
.stat-dn { color: #F0485A; background: rgba(240,72,90,.08);  border: 1px solid rgba(240,72,90,.22); }
.stat-date { font-size: 10px; color: #FFFFFF; margin-top: 5px; font-family: 'IBM Plex Mono', monospace; opacity: .7; }

.data-hover-wrap {
    margin-top: 16px; padding-top: 14px; border-top: 1px solid rgba(120,140,200,.08);
    position: relative; display: flex; flex-direction: row; align-items: center;
}
.data-hover-trigger {
    font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 700;
    letter-spacing: .8px; color: #7BA4F5; cursor: default; user-select: none;
    display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px;
    border-radius: 5px; background: rgba(91,141,239,.08); border: 1px solid rgba(91,141,239,.2);
    transition: background .15s, border-color .15s;
}
.data-hover-wrap:hover .data-hover-trigger { background: rgba(91,141,239,.16); border-color: rgba(91,141,239,.4); }
.data-q {
    display: inline-flex; align-items: center; justify-content: center;
    width: 14px; height: 14px; border-radius: 50%;
    background: rgba(91,141,239,.25); border: 1px solid rgba(91,141,239,.4);
    font-size: 9px; color: #FFFFFF; font-weight: 700;
}
.data-hover-bar {
    display: none; position: relative; z-index: 999;
    background: rgba(13,22,40,.92); border: 1px solid rgba(91,141,239,.2);
    border-radius: 8px; padding: 8px 18px; white-space: nowrap;
    flex-direction: row; align-items: center; gap: 0;
    box-shadow: 0 4px 20px rgba(0,0,0,.4); margin-left: 10px;
}
.data-hover-wrap:hover .data-hover-bar { display: flex; }
.data-hover-item { display: flex; flex-direction: column; gap: 3px; padding: 0 18px; }
.data-hover-item:first-child { padding-left: 0; }
.data-hover-item:last-child  { padding-right: 0; }
.data-hover-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 8px; font-weight: 700;
    letter-spacing: .7px; text-transform: uppercase; color: #4D6080;
}
.data-hover-val { font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600; color: #FFFFFF; }
.data-hover-divider { width: 1px; height: 32px; background: rgba(120,140,200,.12); flex-shrink: 0; }

[data-testid="stButton"] button {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(120,140,200,.15) !important;
    color: #FFFFFF !important; font-size: 14px !important;
    padding: 6px 14px !important; border-radius: 6px !important;
    font-family: 'Sora', sans-serif !important; min-height: 36px !important; line-height: 1 !important;
}
[data-testid="stButton"] button:hover {
    background: rgba(91,141,239,.15) !important; border-color: rgba(91,141,239,.4) !important;
}
.status-ok  { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #0FD68A; }
.status-warn{ font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #F59E0B; }

/* ── Tab labels ── */
[data-testid="stTab"] p {
    color: rgba(255,255,255,.4) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important; font-weight: 600 !important;
}
[data-testid="stTab"][aria-selected="true"] p { color: #FFFFFF !important; }

.screener-header {
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 12px; margin-bottom: 16px;
}
.screener-title { font-family: 'Sora', sans-serif; font-size: 20px; font-weight: 700; color: #FFFFFF; letter-spacing: -.2px; }
.stock-table { width: 100%; border-collapse: collapse; }
.stock-table th {
    font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 700;
    letter-spacing: .7px; text-transform: uppercase; color: #FFFFFF;
    padding: 8px 12px; border-bottom: 1px solid rgba(120,140,200,.1);
    text-align: left; background: #080C16;
}
.stock-table td {
    font-family: 'IBM Plex Mono', monospace; font-size: 12px;
    padding: 9px 12px; border-bottom: 1px solid rgba(120,140,200,.05); color: #FFFFFF;
}
.stock-table tr:hover td { background: rgba(91,141,239,.04); }
.chg-pos { color: #0FD68A !important; font-weight: 700; }
.chg-neg { color: #F0485A !important; font-weight: 700; }
.ticker-badge {
    font-weight: 700; color: #7BA4F5; background: rgba(91,141,239,.08);
    padding: 2px 7px; border-radius: 4px; font-size: 11px;
}
.sector-tag {
    font-size: 9px; padding: 2px 7px; border-radius: 3px;
    background: rgba(255,255,255,.05); border: 1px solid rgba(120,140,200,.1);
    color: #FFFFFF; white-space: nowrap;
}

/* ── Doc page ── */
.doc-h1 {
    font-family: 'Sora', sans-serif; font-size: 26px; font-weight: 800;
    color: #FFFFFF; letter-spacing: -.5px; margin: 32px 0 6px;
    padding-bottom: 10px; border-bottom: 2px solid rgba(91,141,239,.4);
}
.doc-h2 {
    font-family: 'Sora', sans-serif; font-size: 16px; font-weight: 700;
    color: #FFFFFF; letter-spacing: .3px; text-transform: uppercase;
    margin: 28px 0 10px; padding-bottom: 6px; border-bottom: 1px solid rgba(120,140,200,.15);
}
.doc-h3 { font-family: 'Sora', sans-serif; font-size: 13px; font-weight: 700; color: #7BA4F5; letter-spacing: .3px; margin: 20px 0 6px; }
.doc-body { font-family: 'Sora', sans-serif; font-size: 13px; line-height: 1.75; color: rgba(255,255,255,.75); max-width: 900px; }
.doc-body ul { padding-left: 20px; margin: 8px 0; }
.doc-body li { margin-bottom: 5px; }
.doc-body b  { color: #FFFFFF; font-weight: 600; }
.doc-tag {
    display: inline-block; font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px;
    background: rgba(91,141,239,.1); border: 1px solid rgba(91,141,239,.25); color: #7BA4F5; margin: 0 2px;
}
.doc-disclaimer {
    background: rgba(91,141,239,.06); border: 1px solid rgba(91,141,239,.2);
    border-radius: 8px; padding: 14px 18px; font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; color: rgba(255,255,255,.6); margin: 16px 0 24px; line-height: 1.6;
}
.doc-table { width: 100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 11px; margin: 12px 0 20px; }
.doc-table th {
    text-align: left; padding: 8px 12px; font-size: 9px; font-weight: 700;
    letter-spacing: .6px; text-transform: uppercase; color: #FFFFFF;
    background: #0D1628; border-bottom: 1px solid rgba(120,140,200,.15); opacity: .7;
}
.doc-table td { padding: 8px 12px; color: rgba(255,255,255,.75); border-bottom: 1px solid rgba(120,140,200,.06); vertical-align: top; }
.doc-table tr:hover td { background: rgba(91,141,239,.04); }
</style>

<div class="modal-overlay" id="chartModal" onclick="if(event.target===this)closeModal()">
  <div class="modal-box" style="background:#0B1020;border:1px solid rgba(91,141,239,.25);border-radius:14px;padding:24px;width:90vw;max-width:1100px;position:relative;box-shadow:0 24px 80px rgba(0,0,0,.7)">
    <button onclick="closeModal()" style="position:absolute;top:16px;right:16px;background:rgba(255,255,255,.06);border:1px solid rgba(120,140,200,.15);color:#FFFFFF;font-size:18px;width:32px;height:32px;border-radius:6px;cursor:pointer">✕</button>
    <div id="modalTitle" style="font-family:'Sora',sans-serif;font-size:16px;font-weight:700;color:#FFFFFF;margin-bottom:16px"></div>
    <div id="modalChart"></div>
  </div>
</div>
<script>
function closeModal() {
    document.getElementById('chartModal').style.display='none';
    document.body.style.overflow='';
    document.getElementById('modalChart').innerHTML='';
}
document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeModal(); });
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BLS SERIES CONFIG
# ─────────────────────────────────────────────────────────────────────────────
SERIES = {
    "cpi":     {"id":"CUSR0000SA0",    "name":"CPI",              "full":"Consumer Price Index — All Items SA",       "transform":"price_index","color":"#5B8DEF","unit_mom":"%","unit_yoy":"%","dp":2},
    "corecpi": {"id":"CUSR0000SA0L1E", "name":"Core CPI",         "full":"CPI ex Food & Energy SA",                  "transform":"price_index","color":"#22D3EE","unit_mom":"%","unit_yoy":"%","dp":2},
    "ppi":     {"id":"WPSFD4",         "name":"PPI",              "full":"PPI Final Demand",                          "transform":"price_index","color":"#A78BFA","unit_mom":"%","unit_yoy":"%","dp":2},
    "unemp":   {"id":"LNS14000000",    "name":"Unemployment Rate","full":"Civilian Unemployment Rate (U-3) SA",       "transform":"rate",       "color":"#F59E0B","unit_mom":"pp","unit_yoy":"pp","dp":1},
    "nfp":     {"id":"CES0000000001",  "name":"Nonfarm Payrolls", "full":"Total Nonfarm Payrolls SA",                 "transform":"nfp",        "color":"#0FD68A","unit_mom":"K","unit_yoy":"K","dp":0},
}

FRED_SERIES = {
    "corepce": {"id":"PCEPILFE","name":"Core PCE","full":"PCE Excluding Food & Energy — BEA","transform":"price_index","color":"#F472B6","unit_mom":"%","unit_yoy":"%","dp":2,"freq":"Monthly","source":"BEA via FRED"},
    "claims":  {"id":"ICSA",    "name":"Initial Jobless Claims","full":"Initial Unemployment Insurance Claims (Weekly SA)","transform":"claims","color":"#F97316","unit":"K","dp":0,"freq":"Weekly","source":"DOL via FRED"},
}

# ─────────────────────────────────────────────────────────────────────────────
# BLS API FETCH
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bls_data() -> dict:
    api_key    = st.secrets["BLS_API_KEY"]
    series_ids = [cfg["id"] for cfg in SERIES.values()]
    id_to_key  = {cfg["id"]: k for k, cfg in SERIES.items()}
    end_year   = datetime.now().year
    start_year = end_year - 10
    payload = {"seriesid": series_ids, "startyear": str(start_year), "endyear": str(end_year), "registrationkey": api_key}
    resp = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError("BLS API error: " + "; ".join(data.get("message", ["Unknown"])))
    result = {}
    for series in data["Results"]["series"]:
        key = id_to_key.get(series["seriesID"])
        if not key: continue
        rows = []
        for obs in series["data"]:
            if obs["period"] == "M13" or obs["value"] in ("-", ""): continue
            rows.append({"date": pd.Timestamp(year=int(obs["year"]), month=int(obs["period"][1:]), day=1), "value": float(obs["value"])})
        result[key] = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return result

# ─────────────────────────────────────────────────────────────────────────────
# FRED API FETCH
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fred_data() -> dict:
    fred_key = "bc1f32b397114934e95d879ec2646074"
    result   = {}
    for key, cfg in FRED_SERIES.items():
        limit = 156 if cfg["freq"] == "Weekly" else 120
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={cfg['id']}&api_key={fred_key}&file_type=json&sort_order=desc&limit={limit}")
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            rows = [{"date": pd.Timestamp(o["date"]), "value": float(o["value"])}
                    for o in resp.json().get("observations", []) if o["value"] not in (".", "")]
            df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
            if key == "claims": df["value"] = df["value"] / 1000
            result[key] = df
        except Exception as e:
            print(f"FRED fetch failed [{key}]: {e}")
            result[key] = pd.DataFrame(columns=["date", "value"])
    return result

# ─────────────────────────────────────────────────────────────────────────────
# TRANSFORMATIONS & HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def compute_series(df: pd.DataFrame, transform: str) -> pd.DataFrame:
    df = df.copy()
    if transform == "price_index":
        df["mom"] = df["value"].pct_change(1)  * 100
        df["yoy"] = df["value"].pct_change(12) * 100
    elif transform in ("rate", "nfp"):
        df["mom"] = df["value"].diff(1)
        df["yoy"] = df["value"].diff(12)
    return df

def fmt_val(v: float, cfg: dict, which: str) -> str:
    sign = "+" if v >= 0 else ""
    if cfg["transform"] == "nfp": return f"{sign}{int(round(v))}K"
    return f"{sign}{v:.{cfg['dp']}f}{cfg[f'unit_{which}']}"

def is_positive_signal(v: float, key: str) -> bool:
    if key == "nfp": return v >= 0
    return v <= 0

def stat_box_html(label, value_str, delta_str, is_up, date_str):
    arrow = "▲" if is_up else "▼"
    cls   = "stat-up" if is_up else "stat-dn"
    return f"""<div class="stat-box">
      <div class="stat-period">{label}</div>
      <div class="stat-val">{value_str}</div>
      <span class="stat-delta {cls}">{arrow} {delta_str}</span>
      <div class="stat-date">{date_str}</div>
    </div>"""

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART
# ─────────────────────────────────────────────────────────────────────────────
CHART_BG  = "#0B1020"
GRID_COL  = "rgba(120,140,200,.06)"
AXIS_COL  = "#8898BB"
FONT_MONO = "IBM Plex Mono, Courier New, monospace"

def make_chart(df: pd.DataFrame, cfg: dict, which: str = "yoy", height: int = 200) -> go.Figure:
    color = cfg["color"]
    fig   = go.Figure()
    yaxis_opts = {}

    def hex_fill(hex_col, alpha=0.1):
        r,g,b = int(hex_col[1:3],16), int(hex_col[3:5],16), int(hex_col[5:7],16)
        return f"rgba({r},{g},{b},{alpha})"

    if cfg["transform"] == "rate":
        plot_df = df.dropna(subset=["value"]).tail(60)
        fig.add_trace(go.Scatter(x=plot_df["date"], y=plot_df["value"], mode="lines",
            line=dict(color=color, width=1.8), fill="tozeroy", fillcolor=hex_fill(color, 0.1),
            hovertemplate="%{x|%b %Y}<br><b>%{y:.1f}%</b><extra></extra>"))
        yaxis_opts["range"] = [max(0, plot_df["value"].min()-0.5), plot_df["value"].max()+0.5]
    elif cfg["transform"] == "nfp":
        plot_df = df.dropna(subset=[which]).tail(60)
        bar_colors  = ["rgba(15,214,138,.7)"  if v >= 0 else "rgba(240,72,90,.7)"  for v in plot_df[which]]
        bar_borders = ["rgba(15,214,138,.95)" if v >= 0 else "rgba(240,72,90,.95)" for v in plot_df[which]]
        fig.add_trace(go.Bar(x=plot_df["date"], y=plot_df[which],
            marker_color=bar_colors, marker_line_color=bar_borders, marker_line_width=1,
            hovertemplate="%{x|%b %Y}<br><b>%{y:+.0f}K</b><extra></extra>"))
        fig.add_hline(y=0, line_color="rgba(120,140,200,.2)", line_width=1)
    else:
        plot_df = df.dropna(subset=[which]).tail(60)
        unit = cfg[f"unit_{which}"]
        fig.add_trace(go.Scatter(x=plot_df["date"], y=plot_df[which], mode="lines",
            line=dict(color=color, width=1.8), fill="tozeroy", fillcolor=hex_fill(color, 0.1),
            hovertemplate=f"%{{x|%b %Y}}<br><b>%{{y:+.2f}}{unit}</b><extra></extra>"))
        fig.add_hline(y=0, line_color="rgba(120,140,200,.2)", line_width=1)

    fig.update_layout(height=height, margin=dict(l=0,r=0,t=8,b=0),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(family=FONT_MONO, color=AXIS_COL, size=10),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10,color="#FFFFFF"), tickformat="%b '%y", nticks=6),
        yaxis=dict(showgrid=True, gridcolor=GRID_COL, zeroline=False, tickfont=dict(size=10,color="#FFFFFF"), nticks=5, **yaxis_opts),
        hoverlabel=dict(bgcolor="#0E1428", bordercolor="rgba(91,141,239,.3)", font=dict(family=FONT_MONO,size=12,color="#FFFFFF")),
        showlegend=False)
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# RENDER INDICATOR CARD
# ─────────────────────────────────────────────────────────────────────────────
def render_card(key: str, cfg: dict, df) -> None:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="width:9px;height:9px;border-radius:50%;background:{cfg['color']};box-shadow:0 0 10px {cfg['color']}70;display:inline-block;flex-shrink:0"></span>
        <span class="ind-name">{cfg['name']}</span>
      </div>
      <div style="display:flex;gap:6px;align-items:center">
        <span class="ind-src">BLS</span><span class="ind-freq">MONTHLY</span>
      </div>
    </div>""", unsafe_allow_html=True)

    if df is None or df.empty: st.warning("Data unavailable", icon="⚠️"); return
    df_c  = compute_series(df, cfg["transform"])
    valid = df_c.dropna(subset=["mom","yoy"])
    if len(valid) < 2: st.warning("Insufficient data", icon="⚠️"); return

    last, prev = valid.iloc[-1], valid.iloc[-2]
    date_str   = last["date"].strftime("%b %Y")
    mom_val, yoy_val, level = last["mom"], last["yoy"], last["value"]

    df_raw    = df.sort_values("date").reset_index(drop=True)
    last_date = last["date"]
    prev1_row  = df_raw[df_raw["date"] == last_date - pd.DateOffset(months=1)]
    prev12_row = df_raw[df_raw["date"] == last_date - pd.DateOffset(months=12)]
    prev1_val  = prev1_row.iloc[0]["value"]  if not prev1_row.empty  else None
    prev12_val = prev12_row.iloc[0]["value"] if not prev12_row.empty else None
    prev1_date  = prev1_row.iloc[0]["date"].strftime("%b %Y")  if not prev1_row.empty  else "—"
    prev12_date = prev12_row.iloc[0]["date"].strftime("%b %Y") if not prev12_row.empty else "—"

    if cfg["transform"] == "price_index":
        mom_headline, yoy_headline = fmt_val(mom_val,cfg,"mom"), fmt_val(yoy_val,cfg,"yoy")
    elif cfg["transform"] == "rate":
        mom_headline = yoy_headline = f"{level:.1f}%"
    else:
        mom_headline = yoy_headline = fmt_val(mom_val,cfg,"mom")

    if cfg["transform"] == "rate":
        mom_dlt_str = f"vs {prev1_date}: {prev1_val:.1f}%"  if prev1_val  is not None else "—"
        yoy_dlt_str = f"vs {prev12_date}: {prev12_val:.1f}%" if prev12_val is not None else "—"
        delta_up    = is_positive_signal(mom_val, key)
        yoy_dlt_up  = is_positive_signal(yoy_val, key)
    elif cfg["transform"] == "nfp":
        p1  = df_c[df_c["date"] == last["date"] - pd.DateOffset(months=1)]
        p12 = df_c[df_c["date"] == last["date"] - pd.DateOffset(months=12)]
        p1_mom  = p1.iloc[0]["mom"]  if not p1.empty  else None
        p12_mom = p12.iloc[0]["mom"] if not p12.empty else None
        p1_date  = p1.iloc[0]["date"].strftime("%b %Y")  if not p1.empty  else "—"
        p12_date = p12.iloc[0]["date"].strftime("%b %Y") if not p12.empty else "—"
        mom_dlt_str = (f"vs {p1_date}: {'+'if(p1_mom or 0)>=0 else ''}{int(round(p1_mom))}K" if p1_mom is not None else "—")
        if p12_mom is not None:
            yd = mom_val - p12_mom
            yoy_dlt_str = f"{'+'if yd>=0 else ''}{int(round(yd))}K vs {p12_date}: {'+'if p12_mom>=0 else ''}{int(round(p12_mom))}K"
        else: yoy_dlt_str = "—"
        delta_up   = is_positive_signal(mom_val - (p1_mom  or 0), key)
        yoy_dlt_up = is_positive_signal(mom_val - (p12_mom or 0), key)
    else:
        mom_delta, yoy_delta = mom_val - prev["mom"], yoy_val - prev["yoy"]
        mom_dlt_str = fmt_val(mom_delta,cfg,"mom") + " vs prior"
        yoy_dlt_str = fmt_val(yoy_delta,cfg,"yoy") + " vs prior"
        delta_up    = is_positive_signal(mom_delta, key)
        yoy_dlt_up  = is_positive_signal(yoy_delta, key)

    c1, c2 = st.columns(2)
    with c1: st.markdown(stat_box_html("Month-over-Month", mom_headline, mom_dlt_str, delta_up, date_str), unsafe_allow_html=True)
    with c2: st.markdown(stat_box_html("Year-over-Year",   yoy_headline, yoy_dlt_str, yoy_dlt_up, date_str), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)
    if cfg["transform"] in ("rate","nfp"):
        fig = make_chart(df_c, cfg, "mom", height=200)
        cc, cb = st.columns([10,1])
        with cc: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}, key=f"plt_direct_{key}")
        with cb:
            if st.button("⛶", key=f"exp_direct_{key}", help="Expand chart"):
                st.session_state["expanded"] = {"key":key,"which":"mom","title":f"{cfg['name']} — Actual Prints","cfg":cfg,"df_c":df_c}; st.rerun()
        st.caption(cfg["full"])
    else:
        tab_mom, tab_yoy = st.tabs(["  MoM  ","  YoY  "])
        with tab_mom:
            fig = make_chart(df_c, cfg, "mom", height=200)
            cc, cb = st.columns([10,1])
            with cc: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}, key=f"plt_mom_{key}")
            with cb:
                if st.button("⛶", key=f"exp_mom_{key}", help="Expand chart"):
                    st.session_state["expanded"] = {"key":key,"which":"mom","title":f"{cfg['name']} — Month-over-Month","cfg":cfg,"df_c":df_c}; st.rerun()
            st.caption(cfg["full"])
        with tab_yoy:
            fig = make_chart(df_c, cfg, "yoy", height=200)
            cc, cb = st.columns([10,1])
            with cc: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}, key=f"plt_yoy_{key}")
            with cb:
                if st.button("⛶", key=f"exp_yoy_{key}", help="Expand chart"):
                    st.session_state["expanded"] = {"key":key,"which":"yoy","title":f"{cfg['name']} — Year-over-Year","cfg":cfg,"df_c":df_c}; st.rerun()
            st.caption(cfg["full"])
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FRED CARD RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_fred_card(key: str, cfg: dict, df) -> None:
    color = cfg["color"]
    if cfg.get("transform") == "price_index":
        st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
          <div style="display:flex;align-items:center;gap:10px">
            <span style="width:9px;height:9px;border-radius:50%;background:{color};box-shadow:0 0 10px {color}70;display:inline-block;flex-shrink:0"></span>
            <span class="ind-name">{cfg['name']}</span>
          </div>
          <div style="display:flex;gap:6px;align-items:center">
            <span class="ind-src" style="background:rgba(251,191,36,.07);border-color:rgba(251,191,36,.2);color:#FCD34D">FRED</span>
            <span class="ind-freq">{cfg['freq'].upper()}</span>
          </div>
        </div>""", unsafe_allow_html=True)
        if df is None or df.empty: st.warning("Data unavailable", icon="⚠️"); return
        df_c  = compute_series(df, "price_index")
        valid = df_c.dropna(subset=["mom","yoy"])
        if len(valid) < 2: st.warning("Insufficient data", icon="⚠️"); return
        last, prev = valid.iloc[-1], valid.iloc[-2]
        date_str = last["date"].strftime("%b %Y")
        mom_val, yoy_val = last["mom"], last["yoy"]
        mom_delta, yoy_delta = mom_val-prev["mom"], yoy_val-prev["yoy"]
        c1, c2 = st.columns(2)
        with c1: st.markdown(stat_box_html("Month-over-Month", fmt_val(mom_val,cfg,"mom"), fmt_val(mom_delta,cfg,"mom")+" vs prior", is_positive_signal(mom_delta,key), date_str), unsafe_allow_html=True)
        with c2: st.markdown(stat_box_html("Year-over-Year",   fmt_val(yoy_val,cfg,"yoy"), fmt_val(yoy_delta,cfg,"yoy")+" vs prior", is_positive_signal(yoy_delta,key), date_str), unsafe_allow_html=True)
        st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)
        tab_mom, tab_yoy = st.tabs(["  MoM  ","  YoY  "])
        with tab_mom:
            fig = make_chart(df_c, cfg, "mom", height=200)
            cc, cb = st.columns([10,1])
            with cc: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}, key=f"plt_mom_{key}")
            with cb:
                if st.button("⛶", key=f"exp_mom_{key}", help="Expand chart"):
                    st.session_state["expanded"] = {"key":key,"which":"mom","title":f"{cfg['name']} — Month-over-Month","cfg":cfg,"df_c":df_c}; st.rerun()
            st.caption(cfg["full"])
        with tab_yoy:
            fig = make_chart(df_c, cfg, "yoy", height=200)
            cc, cb = st.columns([10,1])
            with cc: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}, key=f"plt_yoy_{key}")
            with cb:
                if st.button("⛶", key=f"exp_yoy_{key}", help="Expand chart"):
                    st.session_state["expanded"] = {"key":key,"which":"yoy","title":f"{cfg['name']} — Year-over-Year","cfg":cfg,"df_c":df_c}; st.rerun()
            st.caption(cfg["full"])
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="width:9px;height:9px;border-radius:50%;background:{color};box-shadow:0 0 10px {color}70;display:inline-block;flex-shrink:0"></span>
        <span class="ind-name">{cfg['name']}</span>
      </div>
      <div style="display:flex;gap:6px;align-items:center">
        <span class="ind-src" style="background:rgba(251,191,36,.07);border-color:rgba(251,191,36,.2);color:#FCD34D">FRED</span>
        <span class="ind-freq">{cfg['freq'].upper()}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    if df is None or df.empty or len(df) < 2: st.warning("Data unavailable", icon="⚠️"); return
    df = df.sort_values("date").reset_index(drop=True)
    last, prev1 = df.iloc[-1], df.iloc[-2]
    last_val, prev1_val = last["value"], prev1["value"]
    date_str = last["date"].strftime("%d %b %Y") if cfg["freq"] == "Weekly" else last["date"].strftime("%b %Y")

    def fmt_k(v, sign=True):
        s = "+" if (v >= 0 and sign) else ""
        return f"{s}{int(round(v))}K"

    if cfg["transform"] == "claims":
        wow = last_val - prev1_val
        c1, c2 = st.columns(2)
        with c1: st.markdown(stat_box_html("Latest Print", fmt_k(last_val,sign=False), f"{'+'if wow>=0 else ''}{int(round(wow))}K vs prior week", wow<=0, date_str), unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="stat-box"><div class="stat-period">Prior Week</div><div class="stat-val">{fmt_k(prev1_val,sign=False)}</div><div class="stat-date">{prev1['date'].strftime('%d %b %Y')}</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)
    plot_df = df.tail(104 if cfg["freq"]=="Weekly" else 60)
    r_c,g_c,b_c = int(color[1:3],16),int(color[3:5],16),int(color[5:7],16)
    fig = go.Figure(go.Scatter(x=plot_df["date"], y=plot_df["value"], mode="lines",
        line=dict(color=color,width=1.8), fill="tozeroy", fillcolor=f"rgba({r_c},{g_c},{b_c},0.1)",
        hovertemplate=("%{x|%d %b '%y}<br><b>%{y:.0f}K</b>" if cfg["freq"]=="Weekly" else "%{x|%b %Y}<br><b>%{y:.1f}</b>")+"<extra></extra>"))
    y_min = max(0, plot_df["value"].min()*0.9)
    fig.update_yaxes(range=[y_min, plot_df["value"].max()*1.05])
    fig.update_layout(height=200, margin=dict(l=0,r=0,t=8,b=0),
        paper_bgcolor="#0B1020", plot_bgcolor="#0B1020",
        font=dict(family="IBM Plex Mono, monospace",color="#8898BB",size=10),
        xaxis=dict(showgrid=False,zeroline=False,tickfont=dict(size=10,color="#FFFFFF"),tickformat="%b '%y",nticks=6),
        yaxis=dict(showgrid=True,gridcolor="rgba(120,140,200,.06)",zeroline=False,tickfont=dict(size=10,color="#FFFFFF"),nticks=5),
        hoverlabel=dict(bgcolor="#0E1428",bordercolor="rgba(91,141,239,.3)",font=dict(family="IBM Plex Mono, monospace",size=12,color="#FFFFFF")),
        showlegend=False)
    cc, cb = st.columns([10,1])
    with cc: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}, key=f"plt_fred_{key}")
    with cb:
        if st.button("⛶", key=f"exp_fred_{key}", help="Expand chart"):
            st.session_state["expanded"] = {"key":key,"which":"value","title":cfg["name"],"cfg":cfg,"df_c":df.assign(mom=df["value"],yoy=df["value"])}; st.rerun()
    st.caption(cfg["full"])
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MARKETS — CONSTITUENT DATA SOURCES
# ─────────────────────────────────────────────────────────────────────────────
_IVV_URL = (
    "https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax"
    "?fileType=csv&fileName=IVV_holdings&dataType=fund"
)
_QQQ_URL = (
    "https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0?audienceType=Institutional"
    "&action=download&ticker=QQQ"
)
_SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
_NDX_WIKI_URL   = "https://en.wikipedia.org/wiki/Nasdaq-100"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MacroDashboard/1.0)"}

# ── S&P 500 hardcoded fallback (used only if IVV + Wikipedia both fail) ───────
_SP500_FALLBACK_DATA = [
    ("AAPL","Apple Inc.","Information Technology"),("MSFT","Microsoft Corp.","Information Technology"),
    ("NVDA","NVIDIA Corp.","Information Technology"),("AVGO","Broadcom Inc.","Information Technology"),
    ("ORCL","Oracle Corp.","Information Technology"),("CRM","Salesforce Inc.","Information Technology"),
    ("ACN","Accenture plc","Information Technology"),("CSCO","Cisco Systems","Information Technology"),
    ("IBM","IBM Corp.","Information Technology"),("AMD","Advanced Micro Devices","Information Technology"),
    ("QCOM","Qualcomm Inc.","Information Technology"),("TXN","Texas Instruments","Information Technology"),
    ("INTC","Intel Corp.","Information Technology"),("AMAT","Applied Materials","Information Technology"),
    ("MU","Micron Technology","Information Technology"),("ADI","Analog Devices","Information Technology"),
    ("KLAC","KLA Corp.","Information Technology"),("LRCX","Lam Research","Information Technology"),
    ("NOW","ServiceNow Inc.","Information Technology"),("PANW","Palo Alto Networks","Information Technology"),
    ("INTU","Intuit Inc.","Information Technology"),("ADSK","Autodesk Inc.","Information Technology"),
    ("FTNT","Fortinet Inc.","Information Technology"),("HPQ","HP Inc.","Information Technology"),
    ("HPE","Hewlett Packard Enterprise","Information Technology"),
    ("JPM","JPMorgan Chase","Financials"),("BAC","Bank of America","Financials"),
    ("WFC","Wells Fargo","Financials"),("GS","Goldman Sachs","Financials"),
    ("MS","Morgan Stanley","Financials"),("BLK","BlackRock Inc.","Financials"),
    ("AXP","American Express","Financials"),("V","Visa Inc.","Financials"),("MA","Mastercard Inc.","Financials"),
    ("SPGI","S&P Global Inc.","Financials"),("MCO","Moody's Corp.","Financials"),
    ("LLY","Eli Lilly and Co.","Health Care"),("UNH","UnitedHealth Group","Health Care"),
    ("JNJ","Johnson & Johnson","Health Care"),("ABBV","AbbVie Inc.","Health Care"),
    ("MRK","Merck & Co.","Health Care"),("TMO","Thermo Fisher Scientific","Health Care"),
    ("ABT","Abbott Laboratories","Health Care"),("AMGN","Amgen Inc.","Health Care"),
    ("PFE","Pfizer Inc.","Health Care"),("ISRG","Intuitive Surgical","Health Care"),
    ("AMZN","Amazon.com Inc.","Consumer Discretionary"),("TSLA","Tesla Inc.","Consumer Discretionary"),
    ("HD","Home Depot","Consumer Discretionary"),("MCD","McDonald's Corp.","Consumer Discretionary"),
    ("NKE","Nike Inc.","Consumer Discretionary"),("LOW","Lowe's Companies","Consumer Discretionary"),
    ("BKNG","Booking Holdings","Consumer Discretionary"),
    ("META","Meta Platforms","Communication Services"),("GOOGL","Alphabet Inc. Class A","Communication Services"),
    ("GOOG","Alphabet Inc. Class C","Communication Services"),("NFLX","Netflix Inc.","Communication Services"),
    ("DIS","Walt Disney Co.","Communication Services"),("CMCSA","Comcast Corp.","Communication Services"),
    ("T","AT&T Inc.","Communication Services"),("VZ","Verizon Communications","Communication Services"),
    ("TMUS","T-Mobile US","Communication Services"),
    ("CAT","Caterpillar Inc.","Industrials"),("RTX","RTX Corp.","Industrials"),
    ("HON","Honeywell International","Industrials"),("UPS","United Parcel Service","Industrials"),
    ("BA","Boeing Co.","Industrials"),("GE","GE Aerospace","Industrials"),
    ("LMT","Lockheed Martin","Industrials"),("DE","Deere & Co.","Industrials"),
    ("WMT","Walmart Inc.","Consumer Staples"),("PG","Procter & Gamble","Consumer Staples"),
    ("COST","Costco Wholesale","Consumer Staples"),("KO","Coca-Cola Co.","Consumer Staples"),
    ("PEP","PepsiCo Inc.","Consumer Staples"),("PM","Philip Morris","Consumer Staples"),
    ("XOM","ExxonMobil Corp.","Energy"),("CVX","Chevron Corp.","Energy"),
    ("COP","ConocoPhillips","Energy"),("EOG","EOG Resources","Energy"),
    ("NEE","NextEra Energy","Utilities"),("SO","Southern Co.","Utilities"),
    ("DUK","Duke Energy","Utilities"),("AEP","American Electric Power","Utilities"),
    ("PLD","Prologis Inc.","Real Estate"),("AMT","American Tower","Real Estate"),
    ("EQIX","Equinix Inc.","Real Estate"),("SPG","Simon Property Group","Real Estate"),
    ("LIN","Linde plc","Materials"),("APD","Air Products","Materials"),
    ("SHW","Sherwin-Williams","Materials"),("FCX","Freeport-McMoRan","Materials"),
]

# ── Nasdaq 100 hardcoded fallback ─────────────────────────────────────────────
_NDX100_DATA = [
    ("AAPL","Apple Inc.","Information Technology"),("MSFT","Microsoft Corp.","Information Technology"),
    ("NVDA","NVIDIA Corp.","Information Technology"),("AMZN","Amazon.com Inc.","Consumer Discretionary"),
    ("META","Meta Platforms","Communication Services"),("GOOGL","Alphabet Inc. Class A","Communication Services"),
    ("GOOG","Alphabet Inc. Class C","Communication Services"),("TSLA","Tesla Inc.","Consumer Discretionary"),
    ("AVGO","Broadcom Inc.","Information Technology"),("COST","Costco Wholesale","Consumer Staples"),
    ("NFLX","Netflix Inc.","Communication Services"),("AMD","Advanced Micro Devices","Information Technology"),
    ("QCOM","Qualcomm Inc.","Information Technology"),("TMUS","T-Mobile US","Communication Services"),
    ("LIN","Linde plc","Materials"),("AMAT","Applied Materials","Information Technology"),
    ("INTU","Intuit Inc.","Information Technology"),("ISRG","Intuitive Surgical","Health Care"),
    ("TXN","Texas Instruments","Information Technology"),("BKNG","Booking Holdings","Consumer Discretionary"),
    ("AMGN","Amgen Inc.","Health Care"),("CMCSA","Comcast Corp.","Communication Services"),
    ("HON","Honeywell International","Industrials"),("VRTX","Vertex Pharmaceuticals","Health Care"),
    ("REGN","Regeneron Pharmaceuticals","Health Care"),("MU","Micron Technology","Information Technology"),
    ("PANW","Palo Alto Networks","Information Technology"),("KLAC","KLA Corp.","Information Technology"),
    ("LRCX","Lam Research","Information Technology"),("ADI","Analog Devices","Information Technology"),
    ("CDNS","Cadence Design Systems","Information Technology"),("SNPS","Synopsys Inc.","Information Technology"),
    ("MELI","MercadoLibre","Consumer Discretionary"),("CRWD","CrowdStrike Holdings","Information Technology"),
    ("CSX","CSX Corp.","Industrials"),("ORLY","O'Reilly Automotive","Consumer Discretionary"),
    ("MAR","Marriott International","Consumer Discretionary"),("MNST","Monster Beverage","Consumer Staples"),
    ("FTNT","Fortinet Inc.","Information Technology"),("PCAR","PACCAR Inc.","Industrials"),
    ("ADSK","Autodesk Inc.","Information Technology"),("MRVL","Marvell Technology","Information Technology"),
    ("ASML","ASML Holding","Information Technology"),("AZN","AstraZeneca","Health Care"),
    ("TTD","The Trade Desk","Communication Services"),("DXCM","DexCom Inc.","Health Care"),
    ("ON","ON Semiconductor","Information Technology"),("NXPI","NXP Semiconductors","Information Technology"),
    ("WDAY","Workday Inc.","Information Technology"),("FAST","Fastenal Co.","Industrials"),
    ("BIIB","Biogen Inc.","Health Care"),("IDXX","IDEXX Laboratories","Health Care"),
    ("ROST","Ross Stores","Consumer Discretionary"),("ODFL","Old Dominion Freight","Industrials"),
    ("CPRT","Copart Inc.","Industrials"),("CTAS","Cintas Corp.","Industrials"),
    ("EA","Electronic Arts","Communication Services"),("GEHC","GE HealthCare","Health Care"),
    ("AEP","American Electric Power","Utilities"),("XEL","Xcel Energy","Utilities"),
    ("KDP","Keurig Dr Pepper","Consumer Staples"),("PAYX","Paychex Inc.","Industrials"),
    ("VRSK","Verisk Analytics","Industrials"),("EXC","Exelon Corp.","Utilities"),
    ("FANG","Diamondback Energy","Energy"),("CTSH","Cognizant Technology","Information Technology"),
    ("TEAM","Atlassian Corp.","Information Technology"),("ZS","Zscaler Inc.","Information Technology"),
    ("DASH","DoorDash Inc.","Consumer Discretionary"),("ABNB","Airbnb Inc.","Consumer Discretionary"),
    ("CEG","Constellation Energy","Utilities"),("ILMN","Illumina Inc.","Health Care"),
    ("MRNA","Moderna Inc.","Health Care"),("DLTR","Dollar Tree","Consumer Discretionary"),
    ("SBUX","Starbucks Corp.","Consumer Discretionary"),("PYPL","PayPal Holdings","Financials"),
    ("MCHP","Microchip Technology","Information Technology"),("LULU","Lululemon Athletica","Consumer Discretionary"),
    ("TTWO","Take-Two Interactive","Communication Services"),("DDOG","Datadog Inc.","Information Technology"),
    ("EBAY","eBay Inc.","Consumer Discretionary"),("PDD","PDD Holdings","Consumer Discretionary"),
    ("ANSS","ANSYS Inc.","Information Technology"),("ENPH","Enphase Energy","Information Technology"),
    ("SMCI","Super Micro Computer","Information Technology"),("ALGN","Align Technology","Health Care"),
    ("ARM","Arm Holdings","Information Technology"),("APP","Applovin Corp.","Information Technology"),
    ("V","Visa Inc.","Financials"),("MA","Mastercard Inc.","Financials"),
    ("WBA","Walgreens Boots Alliance","Consumer Staples"),("NTES","NetEase Inc.","Communication Services"),
    ("WBD","Warner Bros. Discovery","Communication Services"),("NOW","ServiceNow Inc.","Information Technology"),
    ("GFS","GlobalFoundries","Information Technology"),("SIRI","Sirius XM","Communication Services"),
    ("MDLZ","Mondelez International","Consumer Staples"),("RIVN","Rivian Automotive","Consumer Discretionary"),
]

# ─────────────────────────────────────────────────────────────────────────────
# CONSTITUENT FETCH HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _find_csv_header(lines: list, required: list) -> int | None:
    for i, line in enumerate(lines):
        low = line.lower()
        if all(r in low for r in required):
            return i
    return None

def _normalise_cols(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        cl = str(c).lower().strip()
        if cl in ("ticker","symbol"):          rename[c] = "ticker"
        elif cl in ("name","security","holding name","holdings name"): rename[c] = "company"
        elif "weight" in cl:                   rename[c] = "weight"
        elif "sector" in cl:                   rename[c] = "sector"
    return df.rename(columns=rename)

def _clean_tickers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ticker"] = df["ticker"].astype(str).str.strip().str.replace(".", "-", regex=False)
    df = df[df["ticker"].str.match(r'^[A-Z0-9\-]{1,6}$', na=False)]
    return df.drop_duplicates(subset=["ticker"]).reset_index(drop=True)

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_sp500_constituents() -> pd.DataFrame:
    # Tier 1: iShares IVV holdings CSV (exact weights)
    try:
        r = requests.get(_IVV_URL, headers=_HEADERS, timeout=25)
        r.raise_for_status()
        lines = r.text.splitlines()
        hi = _find_csv_header(lines, ["ticker", "weight"])
        if hi is not None:
            df = pd.read_csv(pd.io.common.StringIO("\n".join(lines[hi:])), low_memory=False)
            df = _normalise_cols(df)
            if "asset class" in [c.lower() for c in df.columns]:
                ac = next(c for c in df.columns if c.lower() == "asset class")
                df = df[df[ac].astype(str).str.strip() == "Equity"]
            needed = [c for c in ("ticker","company","weight","sector") if c in df.columns]
            df = df[needed].copy()
            if "weight" in df.columns:
                df["weight"] = pd.to_numeric(df["weight"], errors="coerce") / 100.0
            if "sector"  not in df.columns: df["sector"]  = "Unknown"
            if "company" not in df.columns: df["company"] = df["ticker"]
            df = _clean_tickers(df)
            df["index"] = "S&P 500"
            if len(df) >= 400:
                return df.reset_index(drop=True)
    except Exception as e:
        print(f"IVV fetch failed: {e}")

    # Tier 2: Wikipedia (no weights)
    try:
        r = requests.get(_SP500_WIKI_URL, headers=_HEADERS, timeout=20)
        r.raise_for_status()
        tables = pd.read_html(pd.io.common.StringIO(r.text))
        for t in tables:
            cols_l = [str(c).lower() for c in t.columns]
            if any("symbol" in c for c in cols_l) and any("sector" in c for c in cols_l):
                col_map = {}
                for c in t.columns:
                    cl = str(c).lower()
                    if "symbol" in cl:             col_map[c] = "ticker"
                    elif "security" in cl or "name" in cl: col_map[c] = "company"
                    elif "sector" in cl:           col_map[c] = "sector"
                df = t.rename(columns=col_map)
                needed = [c for c in ("ticker","company","sector") if c in df.columns]
                df = df[needed].copy()
                df["weight"] = None
                df["index"]  = "S&P 500"
                df = _clean_tickers(df)
                if len(df) >= 400:
                    return df.reset_index(drop=True)
    except Exception as e:
        print(f"Wikipedia S&P 500 fetch failed: {e}")

    # Tier 3: hardcoded fallback
    print("SP500: using hardcoded fallback")
    df = pd.DataFrame(_SP500_FALLBACK_DATA, columns=["ticker","company","sector"])
    df["weight"] = None
    df["index"]  = "S&P 500"
    return df.reset_index(drop=True)


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_ndx_constituents() -> pd.DataFrame:
    # Tier 1: Invesco QQQ holdings CSV (exact weights)
    try:
        r = requests.get(_QQQ_URL, headers=_HEADERS, timeout=25)
        r.raise_for_status()
        lines = r.text.splitlines()
        hi = _find_csv_header(lines, ["ticker", "weight"])
        if hi is not None:
            df = pd.read_csv(pd.io.common.StringIO("\n".join(lines[hi:])), low_memory=False)
            df = _normalise_cols(df)
            needed = [c for c in ("ticker","company","weight","sector") if c in df.columns]
            df = df[needed].copy()
            if "weight" in df.columns:
                df["weight"] = pd.to_numeric(df["weight"], errors="coerce") / 100.0
            if "sector"  not in df.columns: df["sector"]  = "Unknown"
            if "company" not in df.columns: df["company"] = df["ticker"]
            df = _clean_tickers(df)
            df["index"] = "Nasdaq 100"
            if len(df) >= 90:
                return df.reset_index(drop=True)
    except Exception as e:
        print(f"QQQ fetch failed: {e}")

    # Tier 2: Wikipedia (no weights)
    try:
        r = requests.get(_NDX_WIKI_URL, headers=_HEADERS, timeout=20)
        r.raise_for_status()
        tables = pd.read_html(pd.io.common.StringIO(r.text))
        for t in tables:
            cols_l = [str(c).lower() for c in t.columns]
            if any("ticker" in c or "symbol" in c for c in cols_l):
                col_map = {}
                for c in t.columns:
                    cl = str(c).lower()
                    if "ticker" in cl or "symbol" in cl: col_map[c] = "ticker"
                    elif "company" in cl or "name" in cl: col_map[c] = "company"
                    elif "sector" in cl:                  col_map[c] = "sector"
                df = t.rename(columns=col_map)
                needed = [c for c in ("ticker","company","sector") if c in df.columns]
                df = df[needed].copy()
                df["weight"] = None
                df["index"]  = "Nasdaq 100"
                df = _clean_tickers(df)
                if len(df) >= 90:
                    return df.reset_index(drop=True)
    except Exception as e:
        print(f"Wikipedia Nasdaq 100 fetch failed: {e}")

    # Tier 3: hardcoded fallback
    print("NDX: using hardcoded fallback")
    df = pd.DataFrame(_NDX100_DATA, columns=["ticker","company","sector"])
    df["weight"] = None
    df["index"]  = "Nasdaq 100"
    return df.reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────────────────
# MARKET STATE DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def get_market_state() -> str:
    sgt  = timezone(timedelta(hours=8))
    now  = datetime.now(sgt)
    if now.weekday() >= 5: return "closed"
    mins = now.hour * 60 + now.minute
    if   mins < 240:  return "open"
    elif mins < 480:  return "after_hours"
    elif mins < 960:  return "closed"
    elif mins < 1290: return "pre"
    else:             return "open"

# ─────────────────────────────────────────────────────────────────────────────
# PRICE FETCHING
# ─────────────────────────────────────────────────────────────────────────────
def _fetch_prev_close(tickers: list) -> dict:
    try:
        raw = yf.download(tickers, period="5d", interval="1d", auto_adjust=True, progress=False, threads=True)
        if raw.empty or len(raw["Close"]) < 1: return {}
        pc = raw["Close"].iloc[-1]
        return {tk: float(pc[tk]) for tk in tickers if tk in pc.index and not pd.isna(pc[tk])}
    except Exception as e:
        print(f"Prev close fetch failed: {e}"); return {}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_price_data_live(tickers: tuple) -> pd.DataFrame:
    try:
        raw = yf.download(list(tickers), period="1d", interval="2m", auto_adjust=True, progress=False, threads=True)
        if raw.empty or raw["Close"].empty: return fetch_price_data_eod(tickers)
        close, volume = raw["Close"], raw["Volume"]
        if len(close) == 0: return fetch_price_data_eod(tickers)
        prev_close_map = _fetch_prev_close(list(tickers))
        if not prev_close_map: return fetch_price_data_eod(tickers)
        last_price = close.iloc[-1]
        cum_volume = volume.sum(axis=0)
        trade_date = close.index[-1].date()
        rows = []
        for ticker in tickers:
            if ticker not in close.columns: continue
            lp = last_price[ticker]; pc = prev_close_map.get(ticker)
            if lp is None or pd.isna(lp) or pc is None or pc == 0: continue
            vol = cum_volume[ticker] if ticker in cum_volume.index else 0
            rows.append({"ticker":ticker,"price":round(float(lp),2),"chg_pct":round((float(lp)/pc-1)*100,2),
                         "chg_abs":round(float(lp)-pc,2),"volume":int(vol) if not pd.isna(vol) else 0,"trade_date":str(trade_date)})
        return pd.DataFrame(rows) if rows else fetch_price_data_eod(tickers)
    except Exception as e:
        print(f"Live fetch failed: {e}"); return fetch_price_data_eod(tickers)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_price_data_extended(tickers: tuple, session: str) -> pd.DataFrame:
    try:
        raw = yf.download(list(tickers), period="1d", interval="1m", auto_adjust=True,
                          prepost=True, progress=False, threads=True, group_by="ticker")
        if raw.empty: return fetch_price_data_eod(tickers)
        ticker_data = {}
        for tk in tickers:
            try:
                if tk in raw.columns.get_level_values(0):
                    tk_df = raw[tk][["Close","Volume"]].copy()
                    tk_df.columns = ["close","volume"]
                    ticker_data[tk] = tk_df
            except Exception: continue
        if not ticker_data: return fetch_price_data_eod(tickers)

        et      = timezone(timedelta(hours=-4))
        utc     = timezone.utc
        now_et  = datetime.now(et)
        today   = now_et.date()
        if session == "pre":
            s_utc = datetime(today.year,today.month,today.day,0,0,tzinfo=et).astimezone(utc)
            e_utc = datetime(today.year,today.month,today.day,9,30,tzinfo=et).astimezone(utc)
            def in_session(idx):
                ts = (idx if idx.tzinfo else idx.replace(tzinfo=utc)).astimezone(utc)
                return s_utc <= ts < e_utc
        else:
            c_utc = datetime(today.year,today.month,today.day,16,0,tzinfo=et).astimezone(utc)
            def in_session(idx):
                ts = (idx if idx.tzinfo else idx.replace(tzinfo=utc)).astimezone(utc)
                return ts >= c_utc

        prev_close_map = _fetch_prev_close(list(tickers))
        if not prev_close_map: return fetch_price_data_eod(tickers)

        rows = []
        for tk, df_tk in ticker_data.items():
            df_ext = df_tk[df_tk.index.map(in_session)].dropna(subset=["close"])
            if df_ext.empty: continue
            pc = prev_close_map.get(tk)
            if pc is None or pc == 0: continue
            lp = float(df_ext["close"].iloc[-1])
            vol_raw = df_ext["volume"].sum()
            rows.append({"ticker":tk,"price":round(lp,2),"chg_pct":round((lp/pc-1)*100,2),
                         "chg_abs":round(lp-pc,2),"volume":int(vol_raw) if not pd.isna(vol_raw) and vol_raw>0 else None,
                         "trade_date":str(df_ext.index[-1].date())})
        return pd.DataFrame(rows) if rows else fetch_price_data_eod(tickers)
    except Exception as e:
        print(f"Extended hours fetch failed [{session}]: {e}"); return fetch_price_data_eod(tickers)

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_price_data_eod(tickers: tuple) -> pd.DataFrame:
    try:
        raw = yf.download(list(tickers), period="5d", interval="1d", auto_adjust=True, progress=False, threads=True)
        if raw.empty: return pd.DataFrame()
        close, volume = raw["Close"], raw["Volume"]
        if len(close) < 2: return pd.DataFrame()
        lc, pc = close.iloc[-1], close.iloc[-2]
        lv, ld = volume.iloc[-1], close.index[-1].date()
        rows = []
        for ticker in tickers:
            if ticker not in close.columns: continue
            l, p = lc[ticker], pc[ticker]
            if pd.isna(l) or pd.isna(p) or p == 0: continue
            v = lv[ticker] if ticker in lv.index else 0
            rows.append({"ticker":ticker,"price":round(float(l),2),"chg_pct":round((float(l)/float(p)-1)*100,2),
                         "chg_abs":round(float(l)-float(p),2),"volume":int(v) if not pd.isna(v) else 0,"trade_date":str(ld)})
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"EOD fetch failed: {e}"); return pd.DataFrame()

def fetch_price_data(tickers: tuple) -> tuple:
    state = get_market_state()
    if state == "open":                    return fetch_price_data_live(tickers), state
    elif state in ("pre","after_hours"):   return fetch_price_data_extended(tickers, state), state
    else:                                  return fetch_price_data_eod(tickers), state

def fmt_volume(v) -> str:
    if v is None: return "—"
    v = int(v)
    if v >= 1_000_000_000: return f"{v/1_000_000_000:.1f}B"
    if v >= 1_000_000:     return f"{v/1_000_000:.1f}M"
    if v >= 1_000:         return f"{v/1_000:.0f}K"
    return str(v)

def fmt_mktcap(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)): return "—"
    if v >= 1_000_000_000_000: return f"${v/1_000_000_000_000:.2f}T"
    if v >= 1_000_000_000:     return f"${v/1_000_000_000:.1f}B"
    if v >= 1_000_000:         return f"${v/1_000_000:.0f}M"
    return f"${v:,.0f}"

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_market_caps(tickers: tuple, prev_prices: tuple) -> dict:
    price_map = dict(prev_prices)
    result    = {}
    for tk in tickers:
        try:
            shares = yf.Ticker(tk).fast_info.shares
            pc     = price_map.get(tk)
            if shares and pc and not pd.isna(shares) and not pd.isna(pc):
                result[tk] = float(shares) * float(pc)
            else: result[tk] = None
        except Exception: result[tk] = None
    return result

# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENTATION PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_docs() -> None:
    st.markdown("""
    <div class="doc-body">
    <div class="doc-h1">US Macro Dashboard — Documentation</div>

    <div class="doc-h2">Overview</div>
    <p>The US Macro Dashboard is a personal project built for idea generation and to stay better informed
    on macroeconomic conditions and market movements. It is not intended for institutional or commercial use.
    Built on <b>Streamlit (Python)</b> and hosted on <b>Streamlit Community Cloud</b>, the dashboard
    consists of two tabs — <b>Macro</b> and <b>Markets</b> — pulling from official government data sources
    and market data providers to present a consolidated view of key US economic indicators and equity market activity.</p>

    <div class="doc-disclaimer">
        <b>Data Freshness</b><br>
        &middot; <b>Macro tab</b> — indicators are as current as the underlying source publishes them.
        BLS and FRED series are updated whenever the respective agency releases new data (typically monthly).
        The dashboard reflects the latest available release at any given time.<br>
        &middot; <b>Markets tab</b> — all price data (price, chg %, chg $, volume) carries an approximate
        <b>15-minute delay</b> sourced from Yahoo Finance's free data feed. This applies during market hours,
        pre-market, and after-hours sessions. Market cap is based on the previous session's official closing
        price and is updated once daily.<br><br>
        This dashboard is intended solely for personal informational purposes and idea generation.
    </div>

    <div class="doc-h1">Macro Tab</div>

    <div class="doc-h2">Data Sources</div>
    <table class="doc-table">
        <thead><tr><th>Indicator</th><th>Source</th><th>Series ID</th><th>Frequency</th></tr></thead>
        <tbody>
            <tr><td>CPI All Items SA</td><td>BLS Official API v2</td><td>CUSR0000SA0</td><td>Monthly</td></tr>
            <tr><td>Core CPI (ex Food &amp; Energy SA)</td><td>BLS Official API v2</td><td>CUSR0000SA0L1E</td><td>Monthly</td></tr>
            <tr><td>PPI Final Demand</td><td>BLS Official API v2</td><td>WPSFD4</td><td>Monthly</td></tr>
            <tr><td>Core PCE (ex Food &amp; Energy)</td><td>FRED API (BEA)</td><td>PCEPILFE</td><td>Monthly</td></tr>
            <tr><td>Unemployment Rate U-3 SA</td><td>BLS Official API v2</td><td>LNS14000000</td><td>Monthly</td></tr>
            <tr><td>Nonfarm Payrolls SA</td><td>BLS Official API v2</td><td>CES0000000001</td><td>Monthly</td></tr>
            <tr><td>Initial Jobless Claims SA</td><td>FRED API (DOL)</td><td>ICSA</td><td>Weekly</td></tr>
        </tbody>
    </table>

    <div class="doc-h2">Indicator Methodology</div>

    <div class="doc-h3">CPI / Core CPI / PPI / Core PCE</div>
    <ul>
        <li>Raw data is a monthly index level (e.g. 314.87).</li>
        <li><b>MoM%</b> = (current index level / prior month index level &minus; 1) &times; 100</li>
        <li><b>YoY%</b> = (current index level / index level 12 months prior &minus; 1) &times; 100</li>
        <li>YoY uses <b>exact date matching</b> (e.g. Apr 2026 vs Apr 2025), not a fixed index offset.</li>
        <li>Delta badge on MoM = current MoM print minus prior month's MoM print.</li>
        <li>Delta badge on YoY = current YoY print minus prior month's YoY print.</li>
        <li>Core PCE is the <b>Federal Reserve's preferred inflation measure</b>.</li>
    </ul>

    <div class="doc-h3">Unemployment Rate</div>
    <ul>
        <li>Headline = <b>actual rate level</b> (e.g. 4.2%), not a period-over-period change.</li>
        <li>MoM badge = current rate vs prior month's actual rate.</li>
        <li>YoY badge = current rate vs same month last year.</li>
        <li>Chart shows actual monthly rate prints. A <b>declining rate</b> = positive signal (green).</li>
    </ul>

    <div class="doc-h3">Nonfarm Payrolls</div>
    <ul>
        <li>Headline = <b>net jobs added month-over-month</b> (e.g. +177K).</li>
        <li>Computed client-side: <span class="doc-tag">PAYEMS[n] &minus; PAYEMS[n&minus;1]</span>.</li>
        <li>FRED's server-side <span class="doc-tag">ch1</span> transformation is not used — unreliable via proxy.</li>
        <li>MoM badge = current print vs prior month. YoY badge = current vs same month last year.</li>
        <li>Chart = bar chart of monthly net jobs — <b>green positive, red negative</b>.</li>
    </ul>

    <div class="doc-h3">Initial Jobless Claims</div>
    <ul>
        <li>Weekly FRED series (ICSA), converted from persons to thousands (&divide;1000).</li>
        <li>WoW badge = current week minus prior week. Lower = positive (green).</li>
    </ul>

    <div class="doc-h2">Caching</div>
    <ul>
        <li>BLS and FRED data: <b>1-hour TTL</b>.</li>
        <li>Manual refresh button (&circlearrowleft;) clears cache on demand — useful on data release days.</li>
    </ul>

    <div class="doc-h2">Excluded Indicators</div>
    <ul>
        <li><b>Michigan Consumer Sentiment</b> — FRED imposes a 1-month lag due to UMich licensing. Always one month stale.</li>
        <li><b>ADP Employment</b> — Methodology changed post-2022; historical series discontinued. Excluded on reliability grounds.</li>
    </ul>

    <div class="doc-h1">Markets Tab</div>

    <div class="doc-h2">Overview</div>
    <p>An equity screener covering the <b>S&amp;P 500</b> and <b>Nasdaq 100</b>, displaying gainers or losers
    ranked by percentage change. All price data carries an approximate <b>15-minute delay</b>.
    Users can filter by sector and control how many stocks to display (top N).</p>

    <div class="doc-h2">Data Sources</div>
    <table class="doc-table">
        <thead><tr><th>Data</th><th>Primary Source</th><th>Fallback</th><th>Cache TTL</th></tr></thead>
        <tbody>
            <tr><td>S&amp;P 500 constituents + weights</td><td>iShares IVV holdings CSV (BlackRock)</td><td>Wikipedia &rarr; hardcoded list</td><td>24 hours</td></tr>
            <tr><td>Nasdaq 100 constituents + weights</td><td>Invesco QQQ holdings CSV</td><td>Wikipedia &rarr; hardcoded list</td><td>24 hours</td></tr>
            <tr><td>Price / Chg % / Chg $ / Volume</td><td>Yahoo Finance (yfinance batch)</td><td>EOD fallback</td><td>5 min (live/extended) · 1 hr (EOD)</td></tr>
            <tr><td>Market Cap (displayed N stocks)</td><td>Yahoo Finance fast_info.shares &times; prev close</td><td>&mdash;</td><td>24 hours</td></tr>
        </tbody>
    </table>

    <div class="doc-h2">Market State Detection</div>
    <p>Automatically detects state based on <b>Singapore Time (SGT, UTC+8)</b>.</p>
    <table class="doc-table">
        <thead><tr><th>SGT Time</th><th>ET Equivalent</th><th>State</th><th>Data Method</th></tr></thead>
        <tbody>
            <tr><td>00:00 &ndash; 04:00</td><td>12:00pm &ndash; 4:00pm ET</td><td>&#x1F7E2; LIVE</td><td>2-min intraday bars, ~15min delay</td></tr>
            <tr><td>04:00 &ndash; 08:00</td><td>4:00pm &ndash; 8:00pm ET</td><td>&#x1F7E3; AFTER-HOURS</td><td>1-min bars with prepost=True, ~15min delay</td></tr>
            <tr><td>08:00 &ndash; 16:00</td><td>8:00pm &ndash; 4:00am ET</td><td>&#x1F534; CLOSED</td><td>Previous session's official closing prices</td></tr>
            <tr><td>16:00 &ndash; 21:30</td><td>4:00am &ndash; 9:30am ET</td><td>&#x1F7E1; PRE-MARKET</td><td>1-min bars with prepost=True, ~15min delay</td></tr>
            <tr><td>21:30 &ndash; 24:00</td><td>9:30am &ndash; 12:00pm ET</td><td>&#x1F7E2; LIVE</td><td>2-min intraday bars, ~15min delay</td></tr>
        </tbody>
    </table>
    <ul>
        <li>Weekends &rarr; CLOSED. US holidays &rarr; falls back to CLOSED (yfinance returns no intraday bars).</li>
        <li>Pre-market data available from ~4:15pm SGT (4:00pm open + 15min delay).</li>
    </ul>

    <div class="doc-h2">Price &amp; Change Calculation</div>

    <div class="doc-h3">LIVE (Market Hours)</div>
    <ul>
        <li>Price = latest 2-min bar close (~15min delay).</li>
        <li><b>Chg %</b> = (current price / previous session's official close &minus; 1) &times; 100</li>
        <li>Volume = cumulative intraday volume from open to current bar.</li>
    </ul>

    <div class="doc-h3">PRE-MARKET</div>
    <ul>
        <li>Price = latest 1-min pre-market bar close (~15min delay).</li>
        <li>Window = <b>midnight ET &rarr; 9:30am ET today only</b>. Yesterday's after-hours bars explicitly excluded.</li>
        <li><b>Chg %</b> = (pre-market price / previous session's official close &minus; 1) &times; 100</li>
        <li>Volume shown as <b>&mdash;</b> if zero or unavailable.</li>
        <li>Only stocks with actual pre-market activity included. Status bar shows active count.</li>
    </ul>

    <div class="doc-h3">AFTER-HOURS</div>
    <ul>
        <li>Same methodology as pre-market, filtered to bars from 4:00pm ET onwards.</li>
        <li>Volume shown as <b>&mdash;</b> if unavailable.</li>
    </ul>

    <div class="doc-h3">CLOSED / EOD</div>
    <ul>
        <li>Price = most recent session's official closing price.</li>
        <li><b>Chg %</b> = (last close / prior session's close &minus; 1) &times; 100</li>
    </ul>

    <div class="doc-h2">Index Weights &amp; Weighted Averages</div>
    <ul>
        <li>Weights sourced from ETF holdings CSVs (IVV for S&amp;P 500, QQQ for Nasdaq 100) — the same fetch that provides the constituent list. No extra API calls.</li>
        <li>When weights are available: <b>Overall Avg</b> = &Sigma;(weight &times; chg %) across all active stocks — a true index-level return estimate.</li>
        <li>When weights are unavailable (Wikipedia/hardcoded fallback): simple equal-weighted mean is used instead.</li>
        <li><b>Top N Avg</b> = &Sigma;(weight &times; chg %) / &Sigma;(weight) for the N displayed stocks. Also falls back to simple mean if weights unavailable.</li>
    </ul>

    <div class="doc-h2">Market Cap Methodology</div>
    <ul>
        <li>Market cap = <b>shares outstanding &times; previous session's official closing price</b>.</li>
        <li>Previous-day static metric — does not update intraday.</li>
        <li>Computed for the <b>displayed N stocks only</b> to keep response times practical.</li>
        <li>Cached 24 hours.</li>
    </ul>

    <div class="doc-h2">Ranking &amp; Display</div>
    <ul>
        <li>All stocks fetched in a <b>single batch call</b> — ranking and display are always consistent (apple-to-apple).</li>
        <li>Full universe sorted by chg %. User controls displayed count via the <b>Show top N</b> input (default 50).</li>
    </ul>

    <div class="doc-h2">Summary Bar</div>
    <table class="doc-table">
        <thead><tr><th>Metric</th><th>Definition</th></tr></thead>
        <tbody>
            <tr><td>Gainers</td><td>Count of active stocks with chg % &gt; 0</td></tr>
            <tr><td>Losers</td><td>Count of active stocks with chg % &lt; 0</td></tr>
            <tr><td>Unchanged</td><td>Count of active stocks with chg % = 0</td></tr>
            <tr><td>Top N Gainers/Losers Avg</td><td>Weighted mean chg % of displayed N stocks (equal-weighted if no weights)</td></tr>
            <tr><td>Overall Avg</td><td>Weighted mean chg % of all active stocks (equal-weighted if no weights)</td></tr>
        </tbody>
    </table>

    <div class="doc-h2">Known Limitations</div>
    <ul>
        <li>Pre-market and after-hours data only covers stocks with actual extended-hours activity. Thinly traded stocks may not appear.</li>
        <li>Volume during pre-market and after-hours often zero or unavailable — shown as <b>&mdash;</b>.</li>
        <li>Market cap computed for displayed N stocks only.</li>
        <li>All price data carries an approximate 15-minute delay.</li>
    </ul>

    <div style="margin-top:48px;padding-top:16px;border-top:1px solid rgba(120,140,200,.1);
        font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4D6080;">
        US Macro Dashboard &middot; Personal Project &middot; Built with Streamlit + BLS API + FRED API + Yahoo Finance
    </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MARKETS SCREENER RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_screener() -> None:
    sgt = timezone(timedelta(hours=8))

    st.markdown("""
    <div class="screener-header">
      <div>
        <div class="screener-title">📈 Markets Screener</div>
        <div class="data-hover-wrap" style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(120,140,200,.08)">
          <div class="data-hover-trigger">DATA <span class="data-q">?</span></div>
          <div class="data-hover-bar">
            <div class="data-hover-item"><span class="data-hover-label">Source</span><span class="data-hover-val">Yahoo Finance (~15min delay)</span></div>
            <div class="data-hover-divider"></div>
            <div class="data-hover-item"><span class="data-hover-label">Constituents</span><span class="data-hover-val">iShares IVV · Invesco QQQ · Wikipedia fallback</span></div>
            <div class="data-hover-divider"></div>
            <div class="data-hover-item"><span class="data-hover-label">Weights</span><span class="data-hover-val">ETF holdings (24hr cache)</span></div>
            <div class="data-hover-divider"></div>
            <div class="data-hover-item"><span class="data-hover-label">Market Cap</span><span class="data-hover-val">shares × prev close · displayed N only</span></div>
            <div class="data-hover-divider"></div>
            <div class="data-hover-item"><span class="data-hover-label">Cache</span><span class="data-hover-val">Prices: 5min live · 1hr EOD</span></div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Index selector ────────────────────────────────────────────────────
    if "idx_choice" not in st.session_state:
        st.session_state["idx_choice"] = "S&P 500"
    is_sp  = st.session_state["idx_choice"] == "S&P 500"
    is_ndx = not is_sp

    sp_bg  = "rgba(255,255,255,.14)" if is_sp  else "transparent"
    sp_bd  = "rgba(255,255,255,.55)" if is_sp  else "rgba(120,140,200,.18)"
    sp_col = "#FFFFFF"               if is_sp  else "rgba(255,255,255,.3)"
    sp_fw  = "700"                   if is_sp  else "400"
    ndx_bg  = "rgba(255,255,255,.14)" if is_ndx else "transparent"
    ndx_bd  = "rgba(255,255,255,.55)" if is_ndx else "rgba(120,140,200,.18)"
    ndx_col = "#FFFFFF"               if is_ndx else "rgba(255,255,255,.3)"
    ndx_fw  = "700"                   if is_ndx else "400"

    st.markdown(f"""<style>
    button[aria-label="S&P 500"]   {{ background:{sp_bg}!important;  border-color:{sp_bd}!important;  color:{sp_col}!important;  font-weight:{sp_fw}!important; }}
    button[aria-label="Nasdaq 100"]{{ background:{ndx_bg}!important; border-color:{ndx_bd}!important; color:{ndx_col}!important; font-weight:{ndx_fw}!important; }}
    </style>""", unsafe_allow_html=True)

    col_sp, col_ndx, col_rest = st.columns([1,1,8])
    with col_sp:
        if st.button("S&P 500", key="btn_sp500", use_container_width=True):
            st.session_state["idx_choice"] = "S&P 500"; st.rerun()
    with col_ndx:
        if st.button("Nasdaq 100", key="btn_ndx100", use_container_width=True):
            st.session_state["idx_choice"] = "Nasdaq 100"; st.rerun()
    idx_choice = st.session_state["idx_choice"]

    # ── Load constituents ─────────────────────────────────────────────────
    with st.spinner("Loading constituent list…"):
        constituents = fetch_sp500_constituents() if idx_choice == "S&P 500" else fetch_ndx_constituents()

    if constituents.empty:
        st.error("Failed to load constituent list."); return

    has_weights   = "weight" in constituents.columns and constituents["weight"].notna().any()
    tickers_tuple = tuple(constituents["ticker"].tolist())
    total_universe = len(tickers_tuple)

    # ── Load price data ───────────────────────────────────────────────────
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
        st.error("Failed to fetch price data from Yahoo Finance."); return

    df = constituents.merge(prices, on="ticker", how="inner")
    if df.empty:
        st.error("No matching price data found."); return

    trade_date    = df["trade_date"].iloc[0] if "trade_date" in df.columns else "—"
    active_count  = len(df)
    now_sgt_str   = datetime.now(timezone(timedelta(hours=8))).strftime("%H:%M SGT")

    # ── Status badge ──────────────────────────────────────────────────────
    if market_state == "open":
        state_html = (f"<span style='color:#0FD68A;font-weight:700'>● LIVE</span>"
                      f"<span style='color:#4D6080'> (~15min delay) · {active_count} of {total_universe} stocks active · as of {now_sgt_str}</span>")
    elif market_state == "pre":
        state_html = (f"<span style='color:#F59E0B;font-weight:700'>● PRE-MARKET</span>"
                      f"<span style='color:#4D6080'> (~15min delay) · {active_count} of {total_universe} stocks active · as of {now_sgt_str}</span>")
    elif market_state == "after_hours":
        state_html = (f"<span style='color:#A78BFA;font-weight:700'>● AFTER-HOURS</span>"
                      f"<span style='color:#4D6080'> (~15min delay) · {active_count} of {total_universe} stocks active · as of {now_sgt_str}</span>")
    else:
        state_html = (f"<span style='color:#F0485A;font-weight:700'>● CLOSED</span>"
                      f"<span style='color:#4D6080'> · showing {trade_date} official close · {active_count} stocks</span>")

    st.markdown(f"<div style='font-family:IBM Plex Mono,monospace;font-size:11px;margin-bottom:14px'>✓ {state_html}</div>", unsafe_allow_html=True)

    # ── Sector filter ─────────────────────────────────────────────────────
    sectors    = ["All"] + sorted(df["sector"].dropna().unique().tolist())
    sector_sel = st.selectbox("Filter by Sector", sectors, key="sector_sel", label_visibility="collapsed")
    if sector_sel != "All":
        df = df[df["sector"] == sector_sel]

    # ── View toggle: Gainers / Losers ─────────────────────────────────────
    if "view_sel" not in st.session_state:
        st.session_state["view_sel"] = "Gainers"
    is_gainers = st.session_state["view_sel"] == "Gainers"
    is_losers  = not is_gainers

    g_bg = "rgba(15,214,138,.15)"  if is_gainers else "transparent"
    g_bd = "rgba(15,214,138,.5)"   if is_gainers else "rgba(15,214,138,.2)"
    l_bg = "rgba(240,72,90,.15)"   if is_losers  else "transparent"
    l_bd = "rgba(240,72,90,.5)"    if is_losers  else "rgba(240,72,90,.2)"

    st.markdown(f"""<style>
    button[aria-label="Gainers"] {{ background:{g_bg}!important; border-color:{g_bd}!important; color:#0FD68A!important; font-weight:{'700' if is_gainers else '400'}!important; }}
    button[aria-label="Losers"]  {{ background:{l_bg}!important; border-color:{l_bd}!important; color:#F0485A!important; font-weight:{'700' if is_losers  else '400'}!important; }}
    </style>""", unsafe_allow_html=True)

    col_g, col_l, col_n, col_rest2 = st.columns([1, 1, 1.5, 6.5])
    with col_g:
        if st.button("Gainers", key="btn_gainers", use_container_width=True):
            st.session_state["view_sel"] = "Gainers"; st.rerun()
    with col_l:
        if st.button("Losers", key="btn_losers", use_container_width=True):
            st.session_state["view_sel"] = "Losers"; st.rerun()
    with col_n:
        top_n_input = st.text_input("Show top N", value="50", key="top_n_input", label_visibility="collapsed",
                                    placeholder="Show top N (e.g. 50)")

    # Parse top N
    try:
        top_n = int(top_n_input.strip())
        top_n = max(1, min(top_n, active_count))
    except (ValueError, AttributeError):
        top_n = 50

    view = st.session_state["view_sel"]
    if view == "Gainers":
        df_sorted = df[df["chg_pct"] > 0].sort_values("chg_pct", ascending=False)
    else:
        df_sorted = df[df["chg_pct"] < 0].sort_values("chg_pct", ascending=True)

    # ── Weighted average calculations ─────────────────────────────────────
    # Overall: weighted avg across all active stocks in current view direction
    all_active = constituents.merge(prices, on="ticker", how="inner")
    gainers_all = all_active[all_active["chg_pct"] > 0]
    losers_all  = all_active[all_active["chg_pct"] < 0]
    unchanged   = (all_active["chg_pct"] == 0).sum()

    if has_weights:
        w_col = constituents[["ticker","weight"]]
        all_w  = all_active.merge(w_col, on="ticker", how="left")
        w_sum  = all_w["weight"].sum()
        overall_avg = (all_w["chg_pct"] * all_w["weight"]).sum() / w_sum if w_sum > 0 else all_active["chg_pct"].mean()
    else:
        overall_avg = all_active["chg_pct"].mean()

    # Slice to top N after sorting
    df_display = df_sorted.head(top_n).reset_index(drop=True)

    # Top N weighted avg
    if has_weights and "weight" in df_display.columns and df_display["weight"].notna().any():
        w_sum_n = df_display["weight"].sum()
        topn_avg = (df_display["chg_pct"] * df_display["weight"]).sum() / w_sum_n if w_sum_n > 0 else df_display["chg_pct"].mean()
    else:
        topn_avg = df_display["chg_pct"].mean() if not df_display.empty else 0.0

    topn_label = f"Top {top_n} {'Gainers' if view=='Gainers' else 'Losers'} Avg"

    # ── Fetch market cap for displayed N stocks ───────────────────────────
    display_tickers = tuple(df_display["ticker"].tolist())
    try:
        raw_prev = yf.download(list(display_tickers), period="5d", interval="1d",
                               auto_adjust=True, progress=False, threads=True)
        if not raw_prev.empty and len(raw_prev["Close"]) >= 2:
            pc_row      = raw_prev["Close"].iloc[-2]
            prev_prices = tuple((tk, float(pc_row[tk])) for tk in display_tickers
                                if tk in pc_row.index and not pd.isna(pc_row[tk]))
        else:
            prev_prices = tuple()
    except Exception:
        prev_prices = tuple()

    with st.spinner(f"Fetching market caps for top {top_n}…"):
        mktcap_map = fetch_market_caps(display_tickers, prev_prices)
    df_display["mkt_cap"] = df_display["ticker"].map(mktcap_map)

    # ── Summary stats row ─────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, color in [
        (c1, "Gainers",    f"{len(gainers_all)}",         "#0FD68A"),
        (c2, "Losers",     f"{len(losers_all)}",          "#F0485A"),
        (c3, "Unchanged",  f"{unchanged}",                "#8898BB"),
        (c4, topn_label,   f"{topn_avg:+.2f}%",  "#0FD68A" if topn_avg   >= 0 else "#F0485A"),
        (c5, "Overall Avg",f"{overall_avg:+.2f}%","#0FD68A" if overall_avg >= 0 else "#F0485A"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#0D1628;border:1px solid rgba(120,140,200,.1);
                border-radius:8px;padding:12px 16px;text-align:center">
              <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#FFFFFF;
                   letter-spacing:.6px;text-transform:uppercase;margin-bottom:4px">{label}</div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:{color}">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── Stock table ───────────────────────────────────────────────────────
    weight_col_html = "<th style='text-align:right'>Weight</th>" if has_weights else ""
    rows_html = ""
    for i, row in df_display.iterrows():
        chg_cls  = "chg-pos" if row["chg_pct"] >= 0 else "chg-neg"
        chg_sign = "▲" if row["chg_pct"] >= 0 else "▼"
        weight_td = ""
        if has_weights:
            w = row.get("weight")
            weight_td = f"<td style='text-align:right;color:#8898BB'>{f'{w*100:.3f}%' if w is not None and not pd.isna(w) else '—'}</td>"
        rows_html += f"""<tr>
          <td style="color:#4D6080;width:36px">{i+1}</td>
          <td><span class="ticker-badge">{row['ticker']}</span></td>
          <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{row['company']}</td>
          <td><span class="sector-tag">{row['sector']}</span></td>
          {weight_td}
          <td style="text-align:right">${row['price']:,.2f}</td>
          <td class="{chg_cls}" style="text-align:right">{chg_sign} {abs(row['chg_pct']):.2f}%</td>
          <td class="{chg_cls}" style="text-align:right">{'+' if row['chg_abs']>=0 else ''}{row['chg_abs']:.2f}</td>
          <td style="text-align:right;color:#FFFFFF">{fmt_volume(row['volume'])}</td>
          <td style="text-align:right;color:#FFFFFF">{fmt_mktcap(row.get('mkt_cap'))}</td>
        </tr>"""

    st.markdown(f"""
    <div style="background:#0B1020;border:1px solid rgba(120,140,200,.1);border-radius:10px;overflow:hidden;overflow-x:auto">
      <table class="stock-table">
        <thead><tr>
          <th>#</th><th>Ticker</th><th>Company</th><th>Sector</th>
          {weight_col_html}
          <th style="text-align:right">Price</th>
          <th style="text-align:right">Chg %</th>
          <th style="text-align:right">Chg $</th>
          <th style="text-align:right">Volume</th>
          <th style="text-align:right">Mkt Cap</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#4D6080;margin-top:8px;text-align:right">
      Data: Yahoo Finance · Weights: {'ETF holdings' if has_weights else 'unavailable (equal-weight avg used)'} · Mkt cap: prev-day close · Showing {len(df_display)} of {active_count}
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    sgt     = timezone(timedelta(hours=8))
    now_str = datetime.now(sgt).strftime("%d %b %Y · %H:%M SGT")

    # ── Page toggle: MACRO / MARKETS / DOCUMENTATION ─────────────────────
    if "page" not in st.session_state:
        st.session_state["page"] = "MACRO"

    is_macro = st.session_state["page"] == "MACRO"
    is_mkt   = st.session_state["page"] == "MARKETS"
    is_docs  = st.session_state["page"] == "DOCUMENTATION"

    def _s(active):
        return {"bg":  "rgba(91,141,239,.22)" if active else "transparent",
                "bd":  "rgba(91,141,239,.7)"  if active else "rgba(120,140,200,.2)",
                "col": "#FFFFFF"              if active else "rgba(255,255,255,.35)",
                "fw":  "700"                  if active else "400"}

    ms, mks, ds = _s(is_macro), _s(is_mkt), _s(is_docs)

    st.markdown(f"""<style>
    button[aria-label="📊  MACRO"]         {{ background:{ms['bg']}!important;  border-color:{ms['bd']}!important;  color:{ms['col']}!important;  font-weight:{ms['fw']}!important; }}
    button[aria-label="📈  MARKETS"]       {{ background:{mks['bg']}!important; border-color:{mks['bd']}!important; color:{mks['col']}!important; font-weight:{mks['fw']}!important; }}
    button[aria-label="📋  DOCUMENTATION"] {{ background:{ds['bg']}!important;  border-color:{ds['bd']}!important;  color:{ds['col']}!important;  font-weight:{ds['fw']}!important; }}
    </style>""", unsafe_allow_html=True)

    st.markdown("<div style='padding:20px 0 0'>", unsafe_allow_html=True)
    col_macro, col_markets, col_docs, col_spacer = st.columns([1, 1, 1.5, 6.5])
    with col_macro:
        if st.button("📊  MACRO", key="btn_macro", use_container_width=True):
            st.session_state["page"] = "MACRO"; st.rerun()
    with col_markets:
        if st.button("📈  MARKETS", key="btn_markets", use_container_width=True):
            st.session_state["page"] = "MARKETS"; st.rerun()
    with col_docs:
        if st.button("📋  DOCUMENTATION", key="btn_docs", use_container_width=True):
            st.session_state["page"] = "DOCUMENTATION"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["page"] == "MARKETS":
        render_screener(); return

    if st.session_state["page"] == "DOCUMENTATION":
        render_docs(); return

    # ── Expanded chart view ────────────────────────────────────────────────
    if "expanded" in st.session_state:
        exp = st.session_state["expanded"]
        cfg_e, df_e, which_e, title_e = exp["cfg"], exp["df_c"], exp["which"], exp["title"]
        st.markdown("<div style='margin-bottom:20px'>", unsafe_allow_html=True)
        if st.button("← Back to Dashboard", key="back_btn"):
            del st.session_state["expanded"]; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"""<div style="font-family:'Sora',sans-serif;font-size:22px;font-weight:700;color:#FFFFFF;margin-bottom:6px;letter-spacing:-.3px">{title_e}</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#4D6080;margin-bottom:24px;letter-spacing:.3px">{cfg_e['full']}</div>""", unsafe_allow_html=True)

        is_fred = cfg_e.get("transform") in ("claims","adp","sentiment")
        if is_fred:
            plot_df = df_e.tail(104 if cfg_e.get("freq")=="Weekly" else 60)
            color_e = cfg_e["color"]
            r_e,g_e,b_e = int(color_e[1:3],16),int(color_e[3:5],16),int(color_e[5:7],16)
            hover_fmt = "%{x|%d %b '%y}<br><b>%{y:.0f}K</b>" if cfg_e.get("freq")=="Weekly" else "%{x|%b %Y}<br><b>%{y:.1f}</b>"
            fig_exp = go.Figure(go.Scatter(x=plot_df["date"],y=plot_df["value"],mode="lines",
                line=dict(color=color_e,width=2),fill="tozeroy",fillcolor=f"rgba({r_e},{g_e},{b_e},0.1)",
                hovertemplate=hover_fmt+"<extra></extra>"))
            y_min = max(0, plot_df["value"].min()*0.9)
            fig_exp.update_yaxes(range=[y_min, plot_df["value"].max()*1.05])
            fig_exp.update_layout(height=550,margin=dict(l=0,r=0,t=8,b=0),
                paper_bgcolor="#0B1020",plot_bgcolor="#0B1020",
                font=dict(family="IBM Plex Mono, monospace",color="#8898BB",size=11),
                xaxis=dict(showgrid=False,zeroline=False,tickfont=dict(size=11,color="#FFFFFF"),tickformat="%b '%y",nticks=8),
                yaxis=dict(showgrid=True,gridcolor="rgba(120,140,200,.06)",zeroline=False,tickfont=dict(size=11,color="#FFFFFF"),nticks=6),
                hoverlabel=dict(bgcolor="#0E1428",bordercolor="rgba(91,141,239,.3)",font=dict(family="IBM Plex Mono, monospace",size=13,color="#FFFFFF")),
                showlegend=False)
        else:
            fig_exp = make_chart(df_e, cfg_e, which_e, height=550)

        st.plotly_chart(fig_exp, use_container_width=True,
            config={"displayModeBar":True,"modeBarButtonsToRemove":["lasso2d","select2d"],"displaylogo":False},
            key="expanded_chart")
        return

    # ── Hero banner ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-banner">
      <div class="hero-top">
        <div class="hero-left">
          <div class="hero-title"><span>US Macro Dashboard</span></div>
          <div class="hero-sub">OFFICIAL BLS DATA · {now_str}</div>
        </div>
        <div class="hero-right"><span class="bls-tag">BLS · OFFICIAL</span></div>
      </div>
      <div class="data-hover-wrap">
        <div class="data-hover-trigger">DATA <span class="data-q">?</span></div>
        <div class="data-hover-bar">
          <div class="data-hover-item"><span class="data-hover-label">Source</span><span class="data-hover-val">BLS (Official) · FRED (BEA/DOL)</span></div>
          <div class="data-hover-divider"></div>
          <div class="data-hover-item"><span class="data-hover-label">Series</span><span class="data-hover-val">CPI · Core CPI · PPI · Core PCE · Unemp · NFP · Claims</span></div>
          <div class="data-hover-divider"></div>
          <div class="data-hover-item"><span class="data-hover-label">Frequency</span><span class="data-hover-val">Monthly · Weekly (Claims) · 10yr History</span></div>
          <div class="data-hover-divider"></div>
          <div class="data-hover-item"><span class="data-hover-label">Cache</span><span class="data-hover-val">Refreshes Every Hour</span></div>
          <div class="data-hover-divider"></div>
          <div class="data-hover-item"><span class="data-hover-label">API</span><span class="data-hover-val">BLS Public Data API v2</span></div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Fetch data ─────────────────────────────────────────────────────────
    with st.spinner("Fetching data from BLS & FRED…"):
        try:
            all_data = fetch_bls_data()
        except Exception as e:
            st.error(f"❌ BLS API error: {e}"); st.stop()
        try:
            fred_data = fetch_fred_data()
        except Exception as e:
            st.error(f"❌ FRED API error: {e}"); fred_data = {}

    bls_loaded   = len(all_data)
    fred_loaded  = len([v for v in fred_data.values() if not v.empty])
    total_loaded = bls_loaded + fred_loaded
    total_series = len(SERIES) + len(FRED_SERIES)

    c_status, c_spacer, c_btn = st.columns([4,6,1])
    with c_status:
        cls = "status-ok" if total_loaded == total_series else "status-warn"
        st.markdown(f"<span class='{cls}'>✓ {total_loaded}/{total_series} series loaded (BLS: {bls_loaded}/{len(SERIES)} · FRED: {fred_loaded}/{len(FRED_SERIES)})</span>", unsafe_allow_html=True)
    with c_btn:
        if st.button("↻", help="Refresh data", key="refresh_main"):
            st.cache_data.clear(); st.rerun()

    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

    # ── INFLATION ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">▲</span>INFLATION</div>', unsafe_allow_html=True)
    cols_price = st.columns(3, gap="medium")
    for col, key in zip(cols_price, ["cpi","corecpi","ppi"]):
        with col:
            with st.container(border=True): render_card(key, SERIES[key], all_data.get(key))
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    cols_pce = st.columns(3, gap="medium")
    with cols_pce[0]:
        with st.container(border=True): render_fred_card("corepce", FRED_SERIES["corepce"], fred_data.get("corepce"))

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── LABOR MARKET ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">●</span>LABOR MARKET</div>', unsafe_allow_html=True)
    cols_labor = st.columns(2, gap="medium")
    for col, key in zip(cols_labor, ["unemp","nfp"]):
        with col:
            with st.container(border=True): render_card(key, SERIES[key], all_data.get(key))
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    cols_labor2 = st.columns(2, gap="medium")
    with cols_labor2[0]:
        with st.container(border=True): render_fred_card("claims", FRED_SERIES["claims"], fred_data.get("claims"))

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown("<hr style='margin-top:32px'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:11px;color:#4D6080;font-family:IBM Plex Mono,monospace;text-align:center'>"
                "BLS data: CUSR0000SA0 · CUSR0000SA0L1E · WPSFD4 · LNS14000000 · CES0000000001 &nbsp;·&nbsp; "
                "FRED data: PCEPILFE (BEA) · ICSA (DOL)</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

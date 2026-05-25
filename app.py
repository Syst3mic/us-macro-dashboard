"""
US Macro Dashboard — Streamlit
Data: U.S. Bureau of Labor Statistics (BLS) Official API v2
Indicators: CPI · Core CPI · PPI · Unemployment · Nonfarm Payrolls
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

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

/* ── Global ── */
html, body, [data-testid="stApp"] {
    background-color: #06080F;
    color: #FFFFFF;
    font-family: 'Sora', 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stAppViewContainer"] { background-color: #06080F; }
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #080C16; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 4rem; max-width: 1400px; }

/* ── Divider ── */
hr { border-color: rgba(120,140,200,.1) !important; margin: 0.5rem 0 !important; }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #080E20 0%, #0D1530 40%, #071018 100%);
    border-bottom: 1px solid rgba(91,141,239,.2);
    padding: 28px 32px 24px;
    margin: 0 -2rem 28px;
    position: relative;
    overflow: hidden;
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
    color: #FFFFFF;
    letter-spacing: -.5px;
    line-height: 1;
    font-family: 'Sora', sans-serif;
}
.hero-title span {
    background: linear-gradient(90deg, #5B8DEF, #22D3EE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #8898BB;
    letter-spacing: .5px;
}
.hero-right { display: flex; align-items: center; gap: 10px; }
.bls-tag {
    font-family: 'IBM Plex Mono', monospace;
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
.hero-stats {
    display: flex; gap: 28px; margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid rgba(120,140,200,.08);
    flex-wrap: wrap;
}
.hero-stat-item { display: flex; flex-direction: column; gap: 2px; }
.hero-stat-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px; color: #4D6080; letter-spacing: .6px; text-transform: uppercase;
}
.hero-stat-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; color: #FFFFFF; font-weight: 600;
}

/* ── Section headers ── */
.section-header {
    font-size: 20px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #FFFFFF;
    padding: 6px 0 14px;
    border-bottom: 1px solid rgba(120,140,200,.1);
    margin-bottom: 16px;
    font-family: 'Sora', sans-serif;
}
.section-header .section-icon {
    color: #5B8DEF;
    margin-right: 8px;
}

/* ── Indicator name ── */
.ind-name {
    font-size: 20px !important;
    font-weight: 700 !important;
    letter-spacing: .3px !important;
    text-transform: uppercase !important;
    color: #FFFFFF !important;
    font-family: 'Sora', sans-serif !important;
}
.ind-src {
    font-size: 9px; font-weight: 700; letter-spacing: .5px;
    padding: 3px 8px; border-radius: 3px;
    background: rgba(91,141,239,.07);
    border: 1px solid rgba(91,141,239,.15);
    color: #7BA4F5;
    font-family: 'IBM Plex Mono', monospace;
}
.ind-freq {
    font-size: 9px; color: #FFFFFF;
    padding: 3px 8px; border-radius: 3px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(120,140,200,.12);
    font-family: 'IBM Plex Mono', monospace;
}

/* ── Stat boxes ── */
.stat-box {
    background: #0D1628;
    border: 1px solid rgba(120,140,200,.12);
    border-radius: 10px;
    padding: 18px 20px 14px;
    transition: border-color .2s;
}
.stat-box:hover { border-color: rgba(120,140,200,.25); }
.stat-period {
    font-size: 14px; font-weight: 700; letter-spacing: .5px;
    text-transform: uppercase; color: #FFFFFF;
    margin-bottom: 10px;
    font-family: 'Sora', sans-serif;
}
.stat-val {
    font-size: 30px; font-weight: 700; color: #FFFFFF;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: -1px; line-height: 1;
}
.stat-delta {
    font-size: 11px; font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 8px; display: inline-block;
    padding: 3px 9px; border-radius: 4px;
}
.stat-up { color: #0FD68A; background: rgba(15,214,138,.08); border: 1px solid rgba(15,214,138,.22); }
.stat-dn { color: #F0485A; background: rgba(240,72,90,.08);  border: 1px solid rgba(240,72,90,.22); }
.stat-date {
    font-size: 10px; color: #FFFFFF;
    margin-top: 5px; font-family: 'IBM Plex Mono', monospace;
    opacity: .7;
}

/* ── Release table ── */
.rel-table { width: 100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 12px; }
.rel-table th {
    text-align: left; padding: 8px 12px;
    font-size: 10px; font-weight: 700; letter-spacing: .6px; text-transform: uppercase;
    color: #FFFFFF; background: #111827;
    border-bottom: 1px solid rgba(120,140,200,.1);
    opacity: .7;
}
.rel-table td {
    padding: 8px 12px; color: #FFFFFF;
    border-bottom: 1px solid rgba(120,140,200,.06);
    opacity: .8;
}
.rel-table tr:first-child td { opacity: 1; font-weight: 600; }
.pos { color: #0FD68A !important; opacity: 1 !important; }
.neg { color: #F0485A !important; opacity: 1 !important; }

/* ── Chart expand button ── */
.chart-expand-btn {
    font-family: 'IBM Plex Mono', monospace;
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
    color: #FFFFFF;
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
    font-family: 'Sora', sans-serif;
    font-size: 16px; font-weight: 700; color: #FFFFFF;
    margin-bottom: 16px; letter-spacing: -.2px;
}

/* ── Streamlit button overrides (refresh) ── */
[data-testid="stButton"] button {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(120,140,200,.15) !important;
    color: #FFFFFF !important;
    font-size: 18px !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    font-family: 'Sora', sans-serif !important;
    min-height: 34px !important;
    line-height: 1 !important;
}
[data-testid="stButton"] button:hover {
    background: rgba(91,141,239,.15) !important;
    border-color: rgba(91,141,239,.4) !important;
}

/* ── Status text ── */
.status-ok  { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #0FD68A; }
.status-warn{ font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #F59E0B; }
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
        "id": "CUSR0000SA0",
        "name": "CPI",
        "full": "Consumer Price Index — All Items SA",
        "transform": "price_index",
        "color": "#5B8DEF",
        "unit_mom": "%", "unit_yoy": "%", "dp": 2,
    },
    "corecpi": {
        "id": "CUSR0000SA0L1E",
        "name": "Core CPI",
        "full": "CPI ex Food & Energy SA",
        "transform": "price_index",
        "color": "#22D3EE",
        "unit_mom": "%", "unit_yoy": "%", "dp": 2,
    },
    "ppi": {
        "id": "WPSFD4",
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
# BLS API FETCH
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bls_data() -> dict:
    api_key    = st.secrets["BLS_API_KEY"]
    series_ids = [cfg["id"] for cfg in SERIES.values()]
    id_to_key  = {cfg["id"]: k for k, cfg in SERIES.items()}
    end_year   = datetime.now().year
    start_year = end_year - 10

    payload = {
        "seriesid":        series_ids,
        "startyear":       str(start_year),
        "endyear":         str(end_year),
        "registrationkey": api_key,
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
            rows.append({
                "date":  pd.Timestamp(year=int(obs["year"]), month=month, day=1),
                "value": float(obs["value"]),
            })
        df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
        result[key] = df
    return result

# ─────────────────────────────────────────────────────────────────────────────
# TRANSFORMATIONS
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
CHART_BG  = "#0B1020"
GRID_COL  = "rgba(120,140,200,.06)"
AXIS_COL  = "#8898BB"
FONT_MONO = "IBM Plex Mono, Courier New, monospace"

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
        fig.add_hline(y=0, line_color="rgba(120,140,200,.2)", line_width=1)

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
        fig.add_hline(y=0, line_color="rgba(120,140,200,.2)", line_width=1)

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_MONO, color=AXIS_COL, size=10),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=10, color="#FFFFFF"),
            tickformat="%b '%y", nticks=6,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID_COL, zeroline=False,
            tickfont=dict(size=10, color="#FFFFFF"), nticks=5,
            **yaxis_opts,
        ),
        hoverlabel=dict(
            bgcolor="#0E1428",
            bordercolor="rgba(91,141,239,.3)",
            font=dict(family=FONT_MONO, size=12, color="#FFFFFF"),
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
    else:  # nfp
        mom_headline = fmt_val(mom_val, cfg, "mom")
        yoy_headline = fmt_val(yoy_val, cfg, "yoy")

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
        # MoM badge: show prior month's actual rate
        mom_dlt_str = f"vs {prev1_date}: {prev1_val:.1f}%" if prev1_val is not None else "—"
        yoy_dlt_str = f"vs {prev12_date}: {prev12_val:.1f}%" if prev12_val is not None else "—"
        # Colour: green if rate went down (or stayed same), red if it went up
        delta_up   = is_positive_signal(mom_val, key)   # mom_val = diff(1) = change in rate
        yoy_dlt_up = is_positive_signal(yoy_val, key)   # yoy_val = diff(12)
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

    # ── NFP release table ─────────────────────────────────────────────────
    if cfg["transform"] == "nfp":
        st.markdown("<div style='margin-top:14px'>", unsafe_allow_html=True)
        st.markdown(nfp_release_table(df_c), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Chart section ─────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)

    # Rate (unemployment): no tab toggle — both tabs show identical chart,
    # so just render the chart directly with no heading.
    if cfg["transform"] == "rate":
        fig_rate = make_chart(df_c, cfg, "mom", height=200)
        col_chart, col_btn = st.columns([10, 1])
        with col_chart:
            st.plotly_chart(
                fig_rate, use_container_width=True,
                config={"displayModeBar": False},
                key=f"plt_rate_{key}"
            )
        with col_btn:
            if st.button("⛶", key=f"exp_rate_{key}", help="Expand chart"):
                st.session_state[f"modal_{key}"] = ("mom", f"{cfg['name']} — Historical Rate")
        st.caption(cfg["full"])

    # All other indicators: MoM / YoY tab toggle
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
                    st.session_state[f"modal_{key}"] = ("mom", f"{cfg['name']} — Month-over-Month")
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
                    st.session_state[f"modal_{key}"] = ("yoy", f"{cfg['name']} — Year-over-Year")
            st.caption(cfg["full"])

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Modal (expanded chart) ─────────────────────────────────────────────
    modal_state = st.session_state.get(f"modal_{key}")
    if modal_state:
        which_modal, modal_title = modal_state
        fig_modal = make_chart(df_c, cfg, which_modal, height=480)
        with st.container():
            st.markdown(f"""
            <div style="
                position:fixed;top:0;left:0;right:0;bottom:0;
                background:rgba(0,0,0,.88);z-index:9999;
                display:flex;align-items:center;justify-content:center;
                backdrop-filter:blur(6px);
            ">
              <div style="
                  background:#0B1020;
                  border:1px solid rgba(91,141,239,.3);
                  border-radius:14px;padding:28px;
                  width:92vw;max-width:1100px;
                  box-shadow:0 24px 80px rgba(0,0,0,.8);
                  position:relative;
              ">
                <div style="font-family:'Sora',sans-serif;font-size:17px;font-weight:700;
                     color:#FFFFFF;margin-bottom:18px">{modal_title}</div>
            """, unsafe_allow_html=True)
            st.plotly_chart(
                fig_modal, use_container_width=True,
                config={"displayModeBar": True},
                key=f"modal_chart_{key}_{which_modal}"
            )
            if st.button("✕  Close", key=f"close_modal_{key}"):
                del st.session_state[f"modal_{key}"]
                st.rerun()
            st.markdown("</div></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    now_str = datetime.now().strftime("%d %b %Y · %H:%M UTC")

    # ── Hero banner ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-banner">
      <div class="hero-top">
        <div class="hero-left">
          <div class="hero-title">US <span>Macro</span> Dashboard</div>
          <div class="hero-sub">OFFICIAL BLS DATA · {now_str}</div>
        </div>
        <div class="hero-right">
          <span class="bls-tag">BLS · OFFICIAL</span>
        </div>
      </div>
      <div class="hero-stats">
        <div class="hero-stat-item">
          <div class="hero-stat-label">Data Source</div>
          <div class="hero-stat-val">Bureau of Labor Statistics</div>
        </div>
        <div class="hero-stat-item">
          <div class="hero-stat-label">Series</div>
          <div class="hero-stat-val">CPI · Core CPI · PPI · UNEMP · NFP</div>
        </div>
        <div class="hero-stat-item">
          <div class="hero-stat-label">Frequency</div>
          <div class="hero-stat-val">Monthly · 10yr History</div>
        </div>
        <div class="hero-stat-item">
          <div class="hero-stat-label">Cache</div>
          <div class="hero-stat-val">Refreshes Every Hour</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch data ─────────────────────────────────────────────────────────
    with st.spinner("Fetching data from BLS…"):
        try:
            all_data = fetch_bls_data()
        except Exception as e:
            st.error(f"❌ BLS API error: {e}")
            st.stop()

    # ── Status + refresh row ───────────────────────────────────────────────
    loaded = len(all_data)
    total  = len(SERIES)
    c_status, c_spacer, c_btn = st.columns([4, 6, 1])
    with c_status:
        color = "#0FD68A" if loaded == total else "#F59E0B"
        cls   = "status-ok" if loaded == total else "status-warn"
        st.markdown(
            f"<span class='{cls}'>✓ {loaded}/{total} series loaded from BLS</span>",
            unsafe_allow_html=True
        )
    with c_btn:
        if st.button("↻", help="Refresh data", key="refresh_main"):
            st.cache_data.clear()
            st.rerun()

    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

    # ── INFLATION: CPI · Core CPI · PPI ───────────────────────────────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">▲</span>INFLATION</div>',
        unsafe_allow_html=True
    )
    cols_price = st.columns(3, gap="medium")
    for col, key in zip(cols_price, ["cpi", "corecpi", "ppi"]):
        with col:
            with st.container(border=True):
                render_card(key, SERIES[key], all_data.get(key))

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── LABOR: Unemployment · NFP ──────────────────────────────────────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">●</span>LABOR MARKET</div>',
        unsafe_allow_html=True
    )
    cols_labor = st.columns(2, gap="medium")
    for col, key in zip(cols_labor, ["unemp", "nfp"]):
        with col:
            with st.container(border=True):
                render_card(key, SERIES[key], all_data.get(key))

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown("<hr style='margin-top:32px'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:11px;color:#4D6080;font-family:IBM Plex Mono,monospace;text-align:center'>"
        "Data: <b style='color:#7BA4F5'>U.S. Bureau of Labor Statistics</b> · API v2 · "
        "CUSR0000SA0 · CUSR0000SA0L1E · WPSFD4 · LNS14000000 · CES0000000001"
        "</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

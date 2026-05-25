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
# CUSTOM CSS  — dark enterprise theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [data-testid="stApp"] {
    background-color: #06080F;
    color: #EEF2FF;
    font-family: 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stAppViewContainer"] { background-color: #06080F; }
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #080C16; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 4rem; max-width: 1400px; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #0B1020;
    border: 1px solid rgba(120,140,200,.1);
    border-radius: 10px;
    padding: 16px 20px;
    transition: border-color .2s;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(120,140,200,.22);
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: .8px !important;
    text-transform: uppercase !important;
    color: #8898BB !important;
}
[data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 700 !important;
    font-family: 'Courier New', monospace !important;
    color: #EEF2FF !important;
}
[data-testid="stMetricDelta"] svg { display: none; }
[data-testid="stMetricDelta"] > div {
    font-family: 'Courier New', monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
}

/* ── Divider ── */
hr { border-color: rgba(120,140,200,.08) !important; margin: 0.5rem 0 !important; }

/* ── Section headers ── */
.section-header {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #3D5070;
    padding: 4px 0 10px;
    border-bottom: 1px solid rgba(120,140,200,.07);
    margin-bottom: 12px;
}

/* ── Top header bar ── */
.dash-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 18px;
    border-bottom: 1px solid rgba(120,140,200,.08);
    margin-bottom: 20px;
}
.dash-title { font-size: 18px; font-weight: 700; color: #EEF2FF; letter-spacing: -.3px; }
.dash-sub   { font-size: 10px; color: #3D5070; letter-spacing: .4px; margin-top: 3px; font-family: 'Courier New', monospace; }
.bls-tag {
    font-size: 9px; font-weight: 700; letter-spacing: .6px;
    padding: 4px 10px; border-radius: 4px;
    background: rgba(91,141,239,.08); border: 1px solid rgba(91,141,239,.2); color: #7BA4F5;
    font-family: 'Courier New', monospace;
}

/* ── Release table ── */
.rel-table { width: 100%; border-collapse: collapse; font-family: 'Courier New', monospace; font-size: 11px; }
.rel-table th {
    text-align: left; padding: 6px 10px;
    font-size: 8px; font-weight: 700; letter-spacing: .6px; text-transform: uppercase;
    color: #3D5070; background: #111827; border-bottom: 1px solid rgba(120,140,200,.08);
}
.rel-table td { padding: 7px 10px; color: #8898BB; border-bottom: 1px solid rgba(120,140,200,.05); }
.rel-table tr:first-child td { color: #EEF2FF; font-weight: 600; }
.pos { color: #0FD68A !important; }
.neg { color: #F0485A !important; }

/* ── Stat pair box ── */
.stat-box {
    background: #0B1020;
    border: 1px solid rgba(120,140,200,.1);
    border-radius: 10px;
    padding: 16px 20px 12px;
}
.stat-box:hover { border-color: rgba(120,140,200,.2); }
.stat-period { font-size: 8px; font-weight: 700; letter-spacing: .7px; text-transform: uppercase; color: #3D5070; margin-bottom: 6px; font-family: 'Courier New', monospace; }
.stat-val    { font-size: 24px; font-weight: 700; color: #EEF2FF; font-family: 'Courier New', monospace; letter-spacing: -1px; line-height: 1; }
.stat-delta  { font-size: 10px; font-weight: 600; font-family: 'Courier New', monospace; margin-top: 6px; display: inline-block; padding: 2px 8px; border-radius: 4px; }
.stat-up     { color: #0FD68A; background: rgba(15,214,138,.08); border: 1px solid rgba(15,214,138,.2); }
.stat-dn     { color: #F0485A; background: rgba(240,72,90,.08);  border: 1px solid rgba(240,72,90,.2); }
.stat-date   { font-size: 9px; color: #3D5070; margin-top: 4px; font-family: 'Courier New', monospace; }
.ind-src     { font-size: 8px; font-weight: 700; letter-spacing: .5px; padding: 2px 6px; border-radius: 3px; background: rgba(91,141,239,.07); border: 1px solid rgba(91,141,239,.15); color: #5E7AAA; font-family: 'Courier New', monospace; }
.ind-freq    { font-size: 8px; color: #3D5070; padding: 2px 6px; border-radius: 3px; background: #111827; border: 1px solid rgba(120,140,200,.08); font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BLS SERIES CONFIG
# ─────────────────────────────────────────────────────────────────────────────
SERIES = {
    "cpi": {
        "id": "CUSR0000SA0",
        "name": "CPI",
        "full": "Consumer Price Index — All Items SA",
        "transform": "price_index",   # MoM% and YoY% via pct_change
        "color": "#5B8DEF",
        "unit_mom": "%",
        "unit_yoy": "%",
        "dp": 2,                      # decimal places
    },
    "corecpi": {
        "id": "CUSR0000SA0L1E",
        "name": "Core CPI",
        "full": "CPI ex Food & Energy SA",
        "transform": "price_index",
        "color": "#22D3EE",
        "unit_mom": "%",
        "unit_yoy": "%",
        "dp": 2,
    },
    "ppi": {
        "id": "WPSFD4",
        "name": "PPI",
        "full": "PPI Final Demand",
        "transform": "price_index",
        "color": "#A78BFA",
        "unit_mom": "%",
        "unit_yoy": "%",
        "dp": 2,
    },
    "unemp": {
        "id": "LNS14000000",
        "name": "Unemployment Rate",
        "full": "Civilian Unemployment Rate (U-3) SA",
        "transform": "rate",          # already in %, report pp change
        "color": "#F59E0B",
        "unit_mom": "pp",
        "unit_yoy": "pp",
        "dp": 1,
    },
    "nfp": {
        "id": "CES0000000001",
        "name": "Nonfarm Payrolls",
        "full": "Total Nonfarm Payrolls SA",
        "transform": "nfp",           # level in thousands, diff = net jobs
        "color": "#0FD68A",
        "unit_mom": "K",
        "unit_yoy": "K",
        "dp": 0,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# BLS API  — server-side, no CORS, no proxy needed
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)  # cache 1 hour
def fetch_bls_data() -> dict[str, pd.DataFrame]:
    """
    Single BLS v2 POST fetching all 5 series at once.
    Returns dict of {key: DataFrame} with columns [date, value]
    sorted oldest → newest.
    """
    api_key = st.secrets["BLS_API_KEY"]
    series_ids = [cfg["id"] for cfg in SERIES.values()]
    keys       = list(SERIES.keys())
    id_to_key  = {cfg["id"]: k for k, cfg in SERIES.items()}

    end_year   = datetime.now().year
    start_year = end_year - 10  # 10 years of history

    payload = {
        "seriesid":       series_ids,
        "startyear":      str(start_year),
        "endyear":        str(end_year),
        "registrationkey": api_key,
    }

    resp = requests.post(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        json=payload,
        timeout=30,
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
            # Skip annual averages (M13) and missing values
            if obs["period"] == "M13":
                continue
            if obs["value"] in ("-", ""):
                continue
            month = int(obs["period"][1:])  # "M01" → 1
            rows.append({
                "date":  pd.Timestamp(year=int(obs["year"]), month=month, day=1),
                "value": float(obs["value"]),
            })
        df = (
            pd.DataFrame(rows)
            .sort_values("date")
            .reset_index(drop=True)
        )
        result[key] = df

    return result

# ─────────────────────────────────────────────────────────────────────────────
# TRANSFORMATIONS
# ─────────────────────────────────────────────────────────────────────────────
def compute_series(df: pd.DataFrame, transform: str) -> pd.DataFrame:
    """
    Add mom and yoy columns to dataframe.
      price_index : MoM% = pct_change(1)*100,  YoY% = pct_change(12)*100
      rate        : MoM pp = diff(1),            YoY pp = diff(12)
      nfp         : MoM K  = diff(1),            YoY K  = diff(12)
    """
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
    """
    Inflation (cpi/corecpi/ppi): lower = better (green when negative)
    Unemployment: lower = better (green when negative)
    NFP: higher = better (green when positive)
    """
    if key == "nfp":
        return v >= 0
    return v <= 0  # lower inflation / lower unemployment = positive signal

def delta_color(v: float, key: str) -> str:
    return "normal" if is_positive_signal(v, key) else "inverse"

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART  — dark theme, consistent with dashboard aesthetic
# ─────────────────────────────────────────────────────────────────────────────
CHART_BG    = "#0B1020"
CHART_PAPER = "#0B1020"
GRID_COLOR  = "rgba(120,140,200,.06)"
AXIS_COLOR  = "#3D5070"
FONT_MONO   = "Courier New, monospace"

def make_chart(df: pd.DataFrame, cfg: dict, which: str = "yoy") -> go.Figure:
    col_name = which  # "mom" or "yoy"
    plot_df  = df.dropna(subset=[col_name]).tail(60)  # last 5 years

    color    = cfg["color"]
    fig      = go.Figure()

    if cfg["transform"] == "nfp":
        # Bar chart with green/red coloring
        bar_colors = [
            "rgba(15,214,138,.7)" if v >= 0 else "rgba(240,72,90,.7)"
            for v in plot_df[col_name]
        ]
        bar_borders = [
            "rgba(15,214,138,.9)" if v >= 0 else "rgba(240,72,90,.9)"
            for v in plot_df[col_name]
        ]
        fig.add_trace(go.Bar(
            x=plot_df["date"],
            y=plot_df[col_name],
            marker_color=bar_colors,
            marker_line_color=bar_borders,
            marker_line_width=1,
            hovertemplate="%{x|%b %Y}<br><b>%{y:+.0f}K</b><extra></extra>",
        ))
    else:
        # Area chart with gradient fill
        unit = cfg[f"unit_{which}"]
        hover_fmt = f"%{{y:+.2f}}{unit}"
        # Fill: use zero baseline for spread/change series
        fig.add_trace(go.Scatter(
            x=plot_df["date"],
            y=plot_df[col_name],
            mode="lines",
            line=dict(color=color, width=1.5),
            fill="tozeroy",
            fillcolor=color.replace("#", "rgba(").rstrip(")") + ",0.08)"
                if color.startswith("#") else color,
            hovertemplate=f"%{{x|%b %Y}}<br><b>{hover_fmt}</b><extra></extra>",
        ))
        # Patch: rebuild fillcolor properly from hex
        r = int(color[1:3], 16)
        g_c = int(color[3:5], 16)
        b = int(color[5:7], 16)
        fig.data[0].fillcolor = f"rgba({r},{g_c},{b},0.09)"

    # Zero line
    fig.add_hline(y=0, line_color="rgba(120,140,200,.18)", line_width=1)

    fig.update_layout(
        height=160,
        margin=dict(l=0, r=0, t=4, b=0),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_MONO, color=AXIS_COLOR, size=9),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=9, color=AXIS_COLOR),
            tickformat="%b '%y",
            nticks=6,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=False,
            tickfont=dict(size=9, color=AXIS_COLOR),
            nticks=4,
        ),
        hoverlabel=dict(
            bgcolor="#0E1428",
            bordercolor="rgba(91,141,239,.25)",
            font=dict(family=FONT_MONO, size=11, color="#EEF2FF"),
        ),
        showlegend=False,
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# STAT BOX HTML helper
# ─────────────────────────────────────────────────────────────────────────────
def stat_box_html(label: str, value_str: str, delta_str: str,
                  is_up: bool, date_str: str) -> str:
    arrow      = "▲" if is_up else "▼"
    delta_cls  = "stat-up" if is_up else "stat-dn"
    return f"""
    <div class="stat-box">
      <div class="stat-period">{label}</div>
      <div class="stat-val">{value_str}</div>
      <span class="stat-delta {delta_cls}">{arrow} {delta_str}</span>
      <div class="stat-date">{date_str}</div>
    </div>
    """

# ─────────────────────────────────────────────────────────────────────────────
# NFP RELEASE TABLE  — last 6 prints
# ─────────────────────────────────────────────────────────────────────────────
def nfp_release_table(df: pd.DataFrame) -> str:
    recent = df.dropna(subset=["mom"]).tail(6).iloc[::-1]
    rows   = ""
    for i, (_, row) in enumerate(recent.iterrows()):
        mom   = row["mom"]
        cls   = "pos" if mom >= 0 else "neg"
        sign  = "+" if mom >= 0 else ""
        bold  = "font-weight:700;color:#EEF2FF;" if i == 0 else ""
        rows += f"""
        <tr>
          <td style="{bold}">{row['date'].strftime('%b %Y')}</td>
          <td class="{cls}" style="{bold}">{sign}{int(round(mom))}K</td>
          <td style="color:#3D5070">—</td>
        </tr>"""
    return f"""
    <table class="rel-table">
      <thead>
        <tr><th>Release</th><th>Actual</th><th>Consensus</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>"""

# ─────────────────────────────────────────────────────────────────────────────
# RENDER ONE INDICATOR CARD
# ─────────────────────────────────────────────────────────────────────────────
def render_card(key: str, cfg: dict, df: pd.DataFrame | None) -> None:
    """Renders a full indicator card: stat pair + chart with MoM/YoY toggle."""

    # ── Header row ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
      <div style="display:flex;align-items:center;gap:8px">
        <span style="width:7px;height:7px;border-radius:50%;background:{cfg['color']};
               box-shadow:0 0 8px {cfg['color']}60;display:inline-block"></span>
        <span style="font-size:10px;font-weight:700;letter-spacing:.8px;
               text-transform:uppercase;color:#8898BB">{cfg['name']}</span>
      </div>
      <div style="display:flex;gap:5px">
        <span class="ind-src">BLS</span>
        <span class="ind-freq">MONTHLY</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Data unavailable", icon="⚠️")
        return

    # ── Compute transforms ────────────────────────────────────────────────
    df_c = compute_series(df, cfg["transform"])
    last = df_c.dropna(subset=["mom", "yoy"]).iloc[-1]
    prev = df_c.dropna(subset=["mom"]).iloc[-2]

    mom_val    = last["mom"]
    yoy_val    = last["yoy"]
    mom_prev   = prev["mom"]
    date_str   = last["date"].strftime("%b %Y")

    # Delta vs prior MoM
    mom_delta  = mom_val - mom_prev
    mom_up     = is_positive_signal(mom_val,   key)
    yoy_up     = is_positive_signal(yoy_val,   key)
    delta_up   = is_positive_signal(mom_delta, key)

    mom_str    = fmt_val(mom_val,   cfg, "mom")
    yoy_str    = fmt_val(yoy_val,   cfg, "yoy")
    delta_str  = fmt_val(mom_delta, cfg, "mom") + " vs prior"

    # ── Stat pair ─────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(stat_box_html(
            "Month-over-Month", mom_str,
            delta_str, delta_up, date_str
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_box_html(
            "Year-over-Year", yoy_str,
            yoy_str + " YoY", yoy_up, date_str
        ), unsafe_allow_html=True)

    # ── NFP release table ─────────────────────────────────────────────────
    if cfg["transform"] == "nfp":
        st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
        st.markdown(nfp_release_table(df_c), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Chart with MoM / YoY toggle ───────────────────────────────────────
    st.markdown("<div style='margin-top:14px;margin-bottom:4px'>", unsafe_allow_html=True)
    tab_mom, tab_yoy = st.tabs(["MoM", "YoY"])
    with tab_mom:
        st.plotly_chart(
            make_chart(df_c, cfg, "mom"),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.caption(cfg["full"])
    with tab_yoy:
        st.plotly_chart(
            make_chart(df_c, cfg, "yoy"),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.caption(cfg["full"])
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── Header ────────────────────────────────────────────────────────────
    now_str = datetime.now().strftime("%d %b %Y · %H:%M UTC")
    st.markdown(f"""
    <div class="dash-header">
      <div>
        <div class="dash-title">📊 US Macro Dashboard</div>
        <div class="dash-sub">OFFICIAL BLS DATA · {now_str}</div>
      </div>
      <span class="bls-tag">BLS · OFFICIAL</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch data ─────────────────────────────────────────────────────────
    with st.spinner("Fetching data from BLS…"):
        try:
            all_data = fetch_bls_data()
        except Exception as e:
            st.error(f"❌ BLS API error: {e}")
            st.stop()

    # ── Refresh button + last-updated ─────────────────────────────────────
    col_info, col_btn = st.columns([5, 1])
    with col_info:
        loaded = len(all_data)
        total  = len(SERIES)
        color  = "#0FD68A" if loaded == total else "#F59E0B"
        st.markdown(
            f"<span style='font-family:Courier New,monospace;font-size:10px;color:{color}'>"
            f"✓ {loaded}/{total} series loaded from BLS</span>",
            unsafe_allow_html=True
        )
    with col_btn:
        if st.button("↻ Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Price Indicators row: CPI · Core CPI · PPI ────────────────────────
    st.markdown('<div class="section-header">▲ &nbsp;INFLATION</div>', unsafe_allow_html=True)
    cols_price = st.columns(3, gap="medium")
    price_keys = ["cpi", "corecpi", "ppi"]
    for col, key in zip(cols_price, price_keys):
        with col:
            with st.container(border=True):
                render_card(key, SERIES[key], all_data.get(key))

    st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)

    # ── Labor Indicators row: Unemployment · NFP ──────────────────────────
    st.markdown('<div class="section-header" style="margin-top:8px">● &nbsp;LABOR MARKET</div>',
                unsafe_allow_html=True)
    cols_labor = st.columns(2, gap="medium")
    labor_keys = ["unemp", "nfp"]
    for col, key in zip(cols_labor, labor_keys):
        with col:
            with st.container(border=True):
                render_card(key, SERIES[key], all_data.get(key))

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:10px;color:#3D5070;font-family:Courier New,monospace'>"
        "Data sourced from <b style='color:#5E7AAA'>U.S. Bureau of Labor Statistics (BLS)</b> "
        "via official API v2 &nbsp;·&nbsp; "
        "CPI series: CUSR0000SA0 &nbsp;·&nbsp; "
        "Core CPI: CUSR0000SA0L1E &nbsp;·&nbsp; "
        "PPI: WPSFD4 &nbsp;·&nbsp; "
        "Unemployment: LNS14000000 &nbsp;·&nbsp; "
        "NFP: CES0000000001"
        "</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

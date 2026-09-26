"""FinBytes | Alert Behaviour Research — redesigned EDA dashboard.

All narrative text, callouts, metrics, and chart content from the original
14-section report is preserved. Design is inspired by the three uploaded
analytics dashboard reference images.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── constants ────────────────────────────────────────────────────────────────
SUMMARY = Path(__file__).parent / "assets" / "eda_summary.json"

PAGES = [
    ("🏠",  "Overview"),
    ("📋",  "Dataset Structure"),
    ("🛡️",  "Data Quality"),
    ("🎯",  "Target Distribution"),
    ("📈",  "Transaction Activity"),
    ("↔️",  "Direction & Type"),
    ("💰",  "Amount Distributions"),
    ("🕒",  "Recent Activity"),
    ("⚖️",  "Escalated vs Dismissed"),
    ("🔬",  "Key EDA Findings"),
    ("🔧",  "Feature Engineering"),
    ("🤖",  "Modeling & Validation"),
    ("✅",  "Conclusion"),
]

ACCENT  = "#183E31"
ACCENT2 = "#2D7459"
COLORS  = ["#2D7459", "#4FAE9A", "#B6D86A", "#E49A63", "#67857B", "#A9C8B8"]

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinBytes · Alert Behaviour Research",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* base */
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
.stApp { background: #F4F6F5; color: #1D3029; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1240px; padding: 1.4rem 2rem 4rem; }

/* sidebar */
[data-testid="stSidebar"] { background: #0E2B22; border-right: none; }
[data-testid="stSidebar"] * { color: #C8DDD4 !important; }
[data-testid="stSidebarUserContent"] { padding: 1rem 0.65rem 1rem; }

.sb-brand {
    display: flex; align-items: center; gap: .55rem;
    padding: .4rem .5rem 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,.08); margin-bottom: .9rem;
}
.sb-logo {
    width: 32px; height: 32px; border-radius: 7px;
    background: #2D7459; display: grid; place-items: center;
    font-size: .9rem; font-weight: 800; color: #fff !important; flex-shrink: 0;
}
.sb-name  { font-size: .84rem; font-weight: 800; color: #E8F3EE !important; letter-spacing:-.01em; }
.sb-sub   { font-size: .6rem; color: #7CA898 !important; letter-spacing: .1em; text-transform:uppercase; }

.nav-group { font-size:.58rem; letter-spacing:.14em; text-transform:uppercase;
    color: #5A8070 !important; font-weight:700; padding:.8rem .7rem .25rem; margin-top:.2rem; }

.nav-item {
    display: flex; align-items: center; gap: .55rem;
    padding: .44rem .7rem; border-radius: 7px; margin-bottom: .13rem;
    font-size: .8rem; font-weight: 600; color: #9DBDB3 !important; transition: all .14s;
}
.nav-item:hover { background: rgba(255,255,255,.07); color: #E8F3EE !important; }
.nav-item.active { background: #2D7459 !important; color:#fff !important;
    box-shadow: 0 4px 12px rgba(45,116,89,.35); }
.nav-icon { font-size:.88rem; width:18px; text-align:center; }

/* KPI strip */
.kpi-strip { display:grid; gap:.85rem; grid-template-columns:repeat(4,1fr); margin-bottom:1.4rem; }
.kpi-card {
    background:#fff; border:1px solid #DDE5DC; border-radius:13px;
    padding:1rem 1.15rem; box-shadow:0 2px 10px rgba(19,50,38,.04);
    transition:transform .15s, box-shadow .15s; position:relative; overflow:hidden;
}
.kpi-card:hover { transform:translateY(-2px); box-shadow:0 7px 20px rgba(19,50,38,.08); }
.kpi-card::before {
    content:''; position:absolute; top:0; left:0; width:4px; height:100%;
    background:linear-gradient(180deg,#2D7459,#4FAE9A); border-radius:13px 0 0 13px;
}
.kpi-label { font-size:.67rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
    color:#7A8D83; margin-bottom:.35rem; }
.kpi-value { font-size:1.85rem; font-weight:780; color:#0E2B22;
    letter-spacing:-.04em; line-height:1; margin-bottom:.2rem; }
.kpi-sub   { font-size:.69rem; color:#9AABA3; }

/* page header */
.page-header {
    display:flex; align-items:flex-start; justify-content:space-between;
    padding:.1rem 0 1rem; margin-bottom:.6rem; border-bottom:2px solid #DDE5DC;
}
.page-eyebrow { font-size:.63rem; font-weight:800; letter-spacing:.16em;
    text-transform:uppercase; color:#2D7459; margin-bottom:.3rem; }
.page-title { font-size:1.65rem; font-weight:760; color:#0E2B22;
    letter-spacing:-.04em; margin:0 0 .3rem; line-height:1.12; }
.page-desc { font-size:.86rem; color:#62766C; line-height:1.65; margin:0; max-width:660px; }
.page-badge {
    flex-shrink:0; background:#EBF5F0; border:1px solid #C4DCCE;
    border-radius:7px; padding:.38rem .8rem;
    font-size:.66rem; font-weight:700; color:#2D7459;
    letter-spacing:.08em; text-transform:uppercase; align-self:flex-start; margin-left:1rem;
}

/* callouts */
.callout {
    background:#EBF5F0; border:1px solid #C4DCCE; border-left:4px solid #2D7459;
    border-radius:0 9px 9px 0; padding:.85rem 1.05rem; margin:.75rem 0 1rem;
    font-size:.84rem; color:#2B5041; line-height:1.65;
}
.callout-warn {
    background:#FFF8EE; border-color:#F0C87E; border-left-color:#D4870D; color:#6B4B10;
}
.callout-info {
    background:#EEF5FF; border-color:#C0D4F0; border-left-color:#3A6CB0; color:#2B4070;
}
.callout b { font-weight:720; }

/* section card */
.s-card {
    background:#fff; border:1px solid #DDE5DC; border-radius:13px;
    padding:1.2rem 1.4rem; margin-bottom:.85rem;
    box-shadow:0 2px 9px rgba(19,50,38,.03);
}
.s-card h3 { font-size:.95rem; font-weight:720; color:#0E2B22;
    margin:0 0 .45rem; letter-spacing:-.02em; }
.s-card p  { font-size:.84rem; color:#62766C; line-height:1.65; margin:0; }

/* comparison / fold tables */
.data-table { width:100%; border-collapse:collapse; font-size:.83rem; }
.data-table th {
    background:#F0F5F2; color:#2B5041; font-size:.66rem; font-weight:800;
    letter-spacing:.1em; text-transform:uppercase; padding:.65rem .9rem;
    text-align:left; border-bottom:2px solid #DDE5DC;
}
.data-table td { padding:.68rem .9rem; border-bottom:1px solid #EEF2EE; color:#1D3029; }
.data-table tr:last-child td { border-bottom:none; }
.data-table tr:hover td { background:#F9FBF9; }
.badge      { display:inline-block; background:#2D7459; color:#fff;
    border-radius:999px; padding:.1rem .5rem; font-size:.63rem; font-weight:700; }
.badge.dim  { background:#C5D5CE; color:#3D5A50; }
.badge.warn { background:#F5C842; color:#5A3C00; }

/* metrics */
[data-testid="stMetric"] {
    background:#fff; border:1px solid #DDE5DC; border-radius:12px;
    padding:.85rem .95rem; box-shadow:0 2px 8px rgba(19,50,38,.03);
}
[data-testid="stMetricLabel"] { color:#7A8D83; font-size:.7rem; letter-spacing:.04em; }
[data-testid="stMetricValue"] { color:#0E2B22; font-size:1.6rem; font-weight:700; letter-spacing:-.04em; }

/* plotly containers */
[data-testid="stPlotlyChart"] {
    background:#fff; border:1px solid #DDE5DC; border-radius:13px;
    padding:.4rem; box-shadow:0 2px 9px rgba(19,50,38,.03);
}

/* tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background:#EEF3F0; border-radius:9px; padding:.2rem; gap:.15rem; border-bottom:none;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background:transparent; border-radius:7px; font-size:.79rem; font-weight:650;
    color:#62766C; padding:.36rem .85rem; border:none;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background:#fff !important; color:#0E2B22 !important;
    box-shadow:0 2px 7px rgba(19,50,38,.07);
}

/* dataframe */
[data-testid="stDataFrame"] { border:1px solid #DDE5DC; border-radius:9px; overflow:hidden; }

/* radio */
[data-testid="stRadio"] [role="radiogroup"] { gap:.35rem; }
[data-testid="stRadio"] label {
    background:#fff; border:1px solid #DDE5DC; border-radius:7px;
    padding:.34rem .7rem; color:#62766C; font-size:.78rem; font-weight:650; transition:all .14s;
}
[data-testid="stRadio"] label:has(input:checked) { background:#183E31; border-color:#183E31; color:#fff; }

/* chart subtitle */
.chart-head { margin:.05rem .1rem .45rem; }
.chart-head strong { font-size:.9rem; color:#0E2B22; font-weight:720; }
.chart-head span   { font-size:.68rem; color:#9AABA3; letter-spacing:.07em;
    text-transform:uppercase; display:block; margin-top:.1rem; }

/* finding bullets */
.finding-list { list-style:none; padding:0; margin:.4rem 0; }
.finding-list li {
    display:flex; gap:.6rem; align-items:flex-start;
    padding:.5rem 0; border-bottom:1px solid #F0F4F2;
    font-size:.86rem; color:#2B4036; line-height:1.62;
}
.finding-list li:last-child { border-bottom:none; }
.finding-list li::before {
    content:''; width:7px; height:7px; border-radius:50%;
    background:#2D7459; flex-shrink:0; margin-top:.45rem;
}

/* AUC bar in fold table */
.auc-wrap { display:flex; align-items:center; gap:.5rem; }
.auc-bar  { height:8px; border-radius:99px; background:#2D7459; min-width:4px; }

/* inline progress bar for quality / direction cards */
.mini-bar-wrap { margin-top:.3rem; height:5px; border-radius:99px;
    background:#EEF2EE; overflow:hidden; }
.mini-bar { height:100%; border-radius:99px; background:#2D7459; }

/* insight chips */
.chip-row { display:flex; flex-wrap:wrap; gap:.5rem; margin:.5rem 0 1rem; }
.chip {
    display:inline-flex; align-items:center; gap:.35rem;
    background:#EBF5F0; border:1px solid #C4DCCE;
    border-radius:999px; padding:.24rem .68rem;
    font-size:.71rem; font-weight:650; color:#2B5041;
}
.chip-dot { width:5px; height:5px; border-radius:50%; background:#2D7459; flex-shrink:0; }

/* dashboard shell */
.stApp { background:#F3F5F5; color:#202A29; }
.block-container { max-width:1440px; padding:1rem clamp(1rem,3vw,2.6rem) 3rem; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #E5E9E8; }
[data-testid="stSidebar"] * { color:#475350 !important; }
[data-testid="stSidebarUserContent"] { padding:1rem .8rem; }
.sb-brand { border-bottom:1px solid #E5E9E8; }
.sb-logo { background:#087E75; }
.sb-name { color:#202A29 !important; }
.sb-sub { color:#87918E !important; }
.nav-group { color:#65716E !important; }
.nav-item { color:#475350 !important; }
.nav-item:hover { background:#F2F7F6; color:#086E67 !important; }
.nav-item.active { background:#064B47 !important; color:#fff !important; }
.nav-item.active * { color:#fff !important; }
.app-topbar { min-height:66px; display:flex; align-items:center; justify-content:space-between; gap:1rem; border-bottom:1px solid #E5E9E8; margin:0 0 1.4rem; }
.app-welcome { color:#202A29; font-size:.98rem; font-weight:650; letter-spacing:-.025em; }
.app-subtitle { color:#78837F; font-size:.72rem; margin-top:.15rem; }
.app-avatar { display:grid; place-items:center; width:32px; height:32px; border:1px solid #DBE7E4; border-radius:50%; background:#EFF6F4; color:#07544F; font-size:.72rem; font-weight:750; }
.app-pagebar { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin:0 0 1rem; }
.app-page-title { color:#202A29; font-size:1.4rem; font-weight:580; letter-spacing:-.045em; }
.app-page-tag { padding:.25rem .55rem; border:1px solid #E1E7E5; border-radius:5px; background:#fff; color:#687571; font-size:.66rem; }
.stApp [data-testid="stMetric"] { border-radius:8px; border-color:#E5E9E8; box-shadow:none; }
.stApp [data-testid="stPlotlyChart"] { border-radius:8px; border-color:#E5E9E8; box-shadow:none; }
.stApp .s-card { border-radius:8px; border-color:#E5E9E8; box-shadow:none; }
.stApp .callout { border-left-color:#087E75; }
.stApp [data-testid="stRadio"] label:has(input:checked) { background:#064B47; border-color:#064B47; }
.stApp [data-testid="stTabs"] [aria-selected="true"] { color:#07544F !important; }
@media(max-width:720px) {
    .app-topbar { min-height:54px; margin-bottom:1rem; }
    .app-subtitle { display:none; }
    .app-pagebar { align-items:flex-start; }
    .app-page-title { font-size:1.13rem; }
}

/* responsive */
@media(max-width:920px) {
    .kpi-strip { grid-template-columns:repeat(2,1fr); }
    .block-container { padding:1rem 1rem 3rem; }
}
@media(max-width:580px) {
    .kpi-strip { grid-template-columns:1fr; }
    .page-header { flex-direction:column; gap:.4rem; }
    .page-badge { margin-left:0; }
}
</style>
""", unsafe_allow_html=True)


# ── helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_summary():
    if not SUMMARY.exists():
        return None
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def chart(data, x, y, *, kind="bar", title=None, xlabel=None, ylabel=None,
          color=None, height=340):
    df = pd.DataFrame(data)
    if df.empty:
        st.info("Chart data unavailable for this view.")
        return
    if kind == "line":
        fig = px.line(df, x=x, y=y, markers=True, title=title,
                      color=color, color_discrete_sequence=COLORS)
        fig.update_traces(line=dict(width=2.5), marker=dict(size=6, line=dict(width=0)))
    else:
        fig = px.bar(df, x=x, y=y, title=title,
                     color=color, color_discrete_sequence=COLORS)
        fig.update_traces(marker_line_width=0, opacity=.92, marker_color=COLORS[0])
    fig.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=18, r=18, t=44 if title else 12, b=22),
        xaxis_title=xlabel, yaxis_title=ylabel, legend_title_text="",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#627269", size=12),
        title_font=dict(size=14, color="#0E2B22", family="Inter, Segoe UI, sans-serif"),
        colorway=COLORS,
    )
    fig.update_xaxes(showgrid=False, linecolor="#D8E2DC",
                     tickfont_color="#7A8D83", title_font_color="#62766C")
    fig.update_yaxes(gridcolor="#EEF2EE", gridwidth=1, zerolinecolor="#D8E2DC",
                     tickfont_color="#7A8D83", title_font_color="#62766C")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displaylogo": False, "displayModeBar": False, "scrollZoom": False})


def kpi_strip(d, t, method=None):
    positive = next((r["count"] for r in t["counts"] if r["class"] == 1), 0)
    esc_rate = positive / max(d["train_signals"], 1)
    auc = (method or {}).get("oof_roc_auc")
    auc_text = f"{auc:.4f}" if auc is not None else "—"
    st.markdown(f"""
    <div class="kpi-strip">
      <div class="kpi-card">
        <div class="kpi-label">Labeled Alerts</div>
        <div class="kpi-value">{d['train_signals']:,}</div>
        <div class="kpi-sub">Training dataset</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Test Alerts</div>
        <div class="kpi-value">{d['test_signals']:,}</div>
        <div class="kpi-sub">Labels withheld</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Escalation Rate</div>
        <div class="kpi-value">{esc_rate:.1%}</div>
        <div class="kpi-sub">{positive:,} of {d['train_signals']:,} escalated</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">OOF ROC-AUC</div>
        <div class="kpi-value">{auc_text}</div>
        <div class="kpi-sub">Forward-only validation</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def page_header(eyebrow, title, desc, badge=None):
    badge_html = f'<div class="page-badge">{badge}</div>' if badge else ""
    st.markdown(f"""
    <div class="page-header">
      <div>
        <div class="page-eyebrow">{eyebrow}</div>
        <div class="page-title">{title}</div>
        <p  class="page-desc">{desc}</p>
      </div>
      {badge_html}
    </div>
    """, unsafe_allow_html=True)


# ── sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar(active_page: str) -> str:
    groups = [
        ("Introduction",  PAGES[:3]),   # Overview, Dataset Structure, Data Quality
        ("EDA Analysis",  PAGES[3:9]),  # Target → Escalated vs Dismissed
        ("Conclusions",   PAGES[9:]),   # Findings, Features, Modeling, Conclusion
    ]
    with st.sidebar:
        st.markdown("""
        <div class="sb-brand">
          <div class="sb-logo">F</div>
          <div>
            <div class="sb-name">FinBytes</div>
            <div class="sb-sub">EDA Report</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        for group_label, group_pages in groups:
            st.markdown(f'<div class="nav-group">{group_label}</div>', unsafe_allow_html=True)
            for icon, label in group_pages:
                cls = "active" if label == active_page else ""
                st.markdown(
                    f'<div class="nav-item {cls}">'
                    f'<span class="nav-icon">{icon}</span>{label}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        page_labels = [p[1] for p in PAGES]
        choice = st.radio(
            "Navigate",
            page_labels,
            index=page_labels.index(active_page),
            label_visibility="collapsed",
        )
        st.markdown("""
        <div style="margin-top:1.2rem; padding:.55rem .7rem;
             background:rgba(255,255,255,.04); border-radius:7px;
             border:1px solid rgba(255,255,255,.06);">
          <div style="font-size:.59rem; color:#5A8070; letter-spacing:.1em;
               text-transform:uppercase; margin-bottom:.22rem;">Data scope</div>
          <div style="font-size:.73rem; color:#9DBDB3; line-height:1.55;">
            Aggregate summaries only<br>No individual records exposed
          </div>
        </div>
        """, unsafe_allow_html=True)
    return choice


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 · OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
def page_overview(s):
    d, t, act, q = s["dataset"], s["target"], s["activity"], s["quality"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    page_header(
        "REPORT OVERVIEW · PROBLEM STATEMENT",
        "What activity comes before an alert?",
        "We studied whether transaction history can help distinguish alerts that were escalated "
        "for review from those that were dismissed. This report presents the data, the patterns we "
        "observed, and how they shaped our analysis. It does not score alerts or serve a model.",
        badge="Synthetic · Hackathon data",
    )

    st.markdown("""
    <div class="callout">
      <b>Data provenance:</b> these competition records are synthetic and localized for the hackathon.
      They do not represent real customers or transactions from the Central Bank of Uzbekistan or a
      commercial bank.
    </div>
    <div class="callout callout-warn">
      <b>How to interpret the analysis:</b> these comparisons describe this dataset. They do not explain
      why an alert was escalated or guarantee that a pattern will hold for new data.
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        f"Training alerts run from {d['train_date_min']} to {d['train_date_max']}. "
        "Transaction summaries use the alert-date cutoff."
    )
    st.markdown("**Navigate the report using the sidebar** — start with Dataset Structure to "
                "understand the data, then work through the EDA pages, and finish with Findings "
                "and Modeling for the conclusions.")

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="chart-head"><strong>Outcome Mix</strong>'
                    '<span>Training labels · 14,000 alerts</span></div>', unsafe_allow_html=True)
        chart(t["counts"], "label", "count", ylabel="Alerts")
    with right:
        st.markdown('<div class="chart-head"><strong>Eligible Transaction Activity</strong>'
                    '<span>Monthly totals · signal-date cutoff</span></div>', unsafe_allow_html=True)
        chart(act["transactions_by_month"], "month", "count", kind="line", ylabel="Transactions")

    stats = act["transactions_per_signal"]
    auc   = method.get("oof_roc_auc")
    c1, c2, c3 = st.columns(3)
    c1.metric("Median Tx / alert",      f"{stats['median']:.0f}")
    c2.metric("Future Tx excluded",     f"{q['future_transaction_percent']:.3f}%")
    c3.metric("Forward-only OOF AUC",   f"{auc:.4f}" if auc else "—")
    st.caption("Outcome comparisons are descriptive, not causal. "
               "The OOF score is an internal forward-validation estimate, not a hidden-test result.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 · DATASET STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════
def page_dataset(s):
    d, t = s["dataset"], s["target"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    page_header(
        "DATASET STRUCTURE · SCHEMA",
        "How is the data organised?",
        "Each alert is one training example, linked to its transaction history by "
        "<code>signal_id</code>. Test alerts have the same fields, but their outcomes are withheld.",
        badge="3 tables · linked by signal_id",
    )

    fc1, fc2 = st.columns(2, gap="large")
    with fc1:
        st.markdown("""
        <div class="s-card">
          <h3>Signal tables (alerts)</h3>
          <p>Each row is one alert with a date (<code>signal_sanasi</code>).
             Training alerts also carry the outcome label (<code>eskalatsiya</code>).
             Test alerts have no label.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Training alert fields:** " +
                    ", ".join(f"`{c}`" for c in d["train_signal_columns"]))
        st.markdown("**Test alert fields:** " +
                    ", ".join(f"`{c}`" for c in d["test_signal_columns"]))

    with fc2:
        st.markdown("""
        <div class="s-card">
          <h3>Transaction table</h3>
          <p>Each row is one transaction linked to an alert. Transactions without a valid date
             or matched <code>signal_id</code> are excluded from analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Transaction fields:** " +
                    ", ".join(f"`{c}`" for c in d["transaction_columns"]))

    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Training transactions", f"{d['train_transaction_rows']:,}")
    c2.metric("Test transactions",      f"{d['test_transaction_rows']:,}")

    st.markdown(f"""
    <div class="callout">
      Training alerts: <b>{d['train_date_min']}</b> → <b>{d['train_date_max']}</b>.<br>
      Test alerts: <b>{d['test_date_min']}</b> → <b>{d['test_date_max']}</b>.
      Dates overlap substantially — a random split would not test performance on later dates.
    </div>
    """, unsafe_allow_html=True)
    st.caption("This site shows aggregate summaries only. "
               "It does not expose individual alert records or identifiers.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 · DATA QUALITY
# ═══════════════════════════════════════════════════════════════════════════════
def page_quality(s):
    d, t, q = s["dataset"], s["target"], s["quality"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    page_header(
        "DATA QUALITY · TEMPORAL RELATIONSHIP",
        "What did quality checks reveal?",
        "We checked for duplicate alert IDs, missing transaction dates, unmatched transaction links, "
        "and transactions dated after their alert. All of these affect which transactions can be "
        "safely used as features.",
        badge=f"{q['future_transaction_percent']:.3f}% future Tx",
    )

    # top-level quality metrics
    a1, a2, a3 = st.columns(3)
    a1.metric("Duplicate training IDs",         f"{q['train_signal_duplicate_ids']:,}")
    a2.metric("Duplicate test IDs",              f"{q['test_signal_duplicate_ids']:,}")
    a3.metric("Transactions with unmatched IDs", f"{q['transaction_signal_ids_unmatched']:,}")

    b1, b2, b3 = st.columns(3)
    b1.metric("Transactions missing date",       f"{q['transaction_missing_date']:,}")
    b2.metric("Dated & linked transactions",     f"{q['linked_dated_transactions']:,}")
    b3.metric("After signal date (excluded)",
              f"{q['future_transactions']:,}  ({q['future_transaction_percent']}%)")

    st.markdown("""
    <div class="callout">
      <b>Signal-time cutoff:</b> behaviour summaries include dated transactions on or before the
      alert date. Later transactions are excluded because they would not have been available when
      the alert was reviewed. This is the central leakage-prevention rule applied throughout the
      analysis.
    </div>
    """, unsafe_allow_html=True)

    # per-column quality table
    st.markdown("### Transaction field quality")
    st.write("Null counts, null percentages, and distinct value counts for every transaction field.")

    quality_rows = [
        {
            "Field": k,
            "Nulls": v["nulls"],
            "Null (%)": v["null_percent"],
            "Distinct values": v["distinct"],
        }
        for k, v in q["transaction_column_quality"].items()
    ]
    quality_df = pd.DataFrame(quality_rows)
    st.dataframe(quality_df, hide_index=True, use_container_width=True)

    st.markdown(f"""
    <div class="callout callout-info">
      <b>Observation:</b> all fields are fully populated (0% nulls). The transaction dataset is
      clean by construction — a common property of synthetic hackathon data. The only data-quality
      concern is the small fraction of transactions that post-date their linked alert
      (<b>{q['future_transaction_percent']}%</b>), which affects 21 alerts.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 · TARGET DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
def page_target(s):
    d, t = s["dataset"], s["target"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)

    positive = next((r["count"] for r in t["counts"] if r["class"] == 1), 0)
    negative = next((r["count"] for r in t["counts"] if r["class"] == 0), 0)
    total    = d["train_signals"]

    page_header(
        "TARGET DISTRIBUTION · ESCALATION RATES",
        "How often are alerts escalated?",
        "Label 0 means dismissed and label 1 means escalated. Monthly rates describe the "
        "observed data and may vary when a month has fewer alerts.",
        badge=f"~{positive/total:.1%} escalation rate",
    )

    st.markdown(f"""
    <div class="chip-row">
      <div class="chip"><div class="chip-dot"></div>{positive:,} escalated alerts ({positive/total:.1%})</div>
      <div class="chip"><div class="chip-dot"></div>{negative:,} dismissed alerts ({negative/total:.1%})</div>
      <div class="chip"><div class="chip-dot"></div>Class ratio ≈ 1 : {negative // max(positive,1)}</div>
    </div>
    """, unsafe_allow_html=True)

    tab_dist, tab_trend = st.tabs(["📊 Outcome Distribution", "📈 Monthly Escalation Rate"])

    with tab_dist:
        col_bar, col_donut = st.columns(2, gap="large")
        with col_bar:
            st.markdown('<div class="chart-head"><strong>Alert Counts by Outcome</strong>'
                        '<span>Training set labels</span></div>', unsafe_allow_html=True)
            chart(t["counts"], "label", "count", ylabel="Alerts")
        with col_donut:
            fig_d = go.Figure(go.Pie(
                labels=["Dismissed", "Escalated"],
                values=[negative, positive],
                hole=.60,
                marker=dict(colors=["#C5D5CE", "#2D7459"]),
                textinfo="label+percent",
                textfont=dict(size=12, color="#0E2B22"),
                hovertemplate="%{label}: %{value:,}<extra></extra>",
            ))
            fig_d.update_layout(
                height=310, margin=dict(l=10, r=10, t=28, b=10),
                paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                annotations=[dict(
                    text=f"<b>{positive/total:.0%}</b><br>escalated",
                    x=.5, y=.5, showarrow=False,
                    font=dict(size=14, color="#0E2B22"),
                )],
            )
            st.markdown('<div class="chart-head"><strong>Class Balance</strong>'
                        '<span>Proportion of each outcome</span></div>', unsafe_allow_html=True)
            st.plotly_chart(fig_d, use_container_width=True,
                            config={"displaylogo": False, "displayModeBar": False})
        st.markdown("""
        <div class="callout">
          <b>Class imbalance note:</b> the training set is heavily skewed toward dismissed alerts.
          ROC-AUC is the recommended metric because it evaluates ranking quality independently of
          the decision threshold and is robust to class imbalance.
        </div>
        """, unsafe_allow_html=True)

    with tab_trend:
        st.write("Monthly escalation rates describe the observed data. "
                 "Rates may fluctuate in months with fewer alerts.")
        st.markdown('<div class="chart-head"><strong>Escalation Rate by Alert Month</strong>'
                    '<span>Proportion of escalated alerts per calendar month</span></div>',
                    unsafe_allow_html=True)
        chart(t["monthly"], "month", "escalation_rate", kind="line",
              ylabel="Escalation rate", xlabel="Month")
        monthly_df = pd.DataFrame(t["monthly"])
        if not monthly_df.empty:
            peak = monthly_df.loc[monthly_df["escalation_rate"].idxmax()]
            low  = monthly_df.loc[monthly_df["escalation_rate"].idxmin()]
            c1, c2, c3 = st.columns(3)
            c1.metric("Average monthly rate", f"{monthly_df['escalation_rate'].mean():.1%}")
            c2.metric(f"Peak month ({peak['month']})", f"{peak['escalation_rate']:.1%}")
            c3.metric(f"Lowest month ({low['month']})", f"{low['escalation_rate']:.1%}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 · TRANSACTION ACTIVITY
# ═══════════════════════════════════════════════════════════════════════════════
def page_activity(s):
    d, t, act = s["dataset"], s["target"], s["activity"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    stats = act["transactions_per_signal"]
    page_header(
        "TRANSACTION ACTIVITY OVER TIME",
        "How much history does each alert carry?",
        "These monthly totals include only transactions dated on or before their linked alert. "
        "The amount of history available varies from one alert to another.",
        badge=f"{d['train_transaction_rows']:,} eligible transactions",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean Tx / alert",      f"{stats['mean']:.2f}")
    c2.metric("Median Tx / alert",    f"{stats['median']:.0f}")
    c3.metric("90th percentile",      f"{stats['p90']:.0f}")
    c4.metric("Alerts: zero history", f"{stats['zero_signal_percent']:.1f}%")

    tab_time, tab_hist = st.tabs(["📅 Activity Over Time", "📊 Tx per Alert Distribution"])

    with tab_time:
        st.write("Eligible transaction counts by month across all training alerts. "
                 "Only transactions on or before the alert date are included.")
        st.markdown('<div class="chart-head"><strong>Eligible Transactions by Month</strong>'
                    '<span>Signal-date–cutoff transactions · all training alerts</span></div>',
                    unsafe_allow_html=True)
        chart(act["transactions_by_month"], "month", "count",
              kind="line", ylabel="Transactions", xlabel="Month")

    with tab_hist:
        st.write(f"Across {d['train_signals']:,} training alerts, the mean history contains "
                 f"**{stats['mean']:.2f}** transactions and the median **{stats['median']:.0f}**. "
                 f"The 90th percentile is **{stats['p90']:.0f}**; "
                 f"**{stats['zero_signal_percent']:.1f}%** have no eligible transactions.")
        st.markdown('<div class="chart-head"><strong>Transactions per Alert</strong>'
                    '<span>Distribution of history size (upper tail clipped)</span></div>',
                    unsafe_allow_html=True)
        chart(act["transaction_count_distribution"], "bin", "count", ylabel="Alerts")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 · DIRECTION & TYPE
# ═══════════════════════════════════════════════════════════════════════════════
def page_direction_type(s):
    d, t, act = s["dataset"], s["target"], s["activity"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    page_header(
        "INCOMING VS OUTGOING · TRANSACTION TYPES",
        "What kinds of transactions appear in alert histories?",
        "Direction (kirim = incoming, chiqim = outgoing) and transaction type show the "
        "composition of each alert's history. Counts motivated categorical-mix features in the model.",
        badge="2 directions · 4 types",
    )

    tab_dir, tab_type = st.tabs(["↔️ Incoming vs Outgoing (kirim / chiqim)",
                                  "🏷️ Transaction Type Breakdown"])

    with tab_dir:
        st.write("This chart counts eligible transactions by recorded direction. "
                 "It shows how often each direction appears, not the net flow of money.")
        col_bar, col_cards = st.columns([1.3, 1], gap="large")
        total_dir = sum(r["count"] for r in act["directions"])
        with col_bar:
            st.markdown('<div class="chart-head"><strong>Transaction Frequency by Direction</strong>'
                        '<span>All eligible training transactions</span></div>',
                        unsafe_allow_html=True)
            chart(act["directions"], "category", "count", ylabel="Transactions")
        with col_cards:
            for row in act["directions"]:
                pct = row["count"] / max(total_dir, 1)
                st.markdown(f"""
                <div class="s-card" style="padding:.85rem 1.05rem; margin-bottom:.55rem;">
                  <h3>{row['category']}</h3>
                  <p style="font-size:1.3rem; font-weight:720; color:#0E2B22;
                       letter-spacing:-.03em; margin-bottom:.3rem;">{row['count']:,}</p>
                  <div class="mini-bar-wrap">
                    <div class="mini-bar" style="width:{pct:.0%};"></div>
                  </div>
                  <p style="margin-top:.28rem; font-size:.72rem; color:#9AABA3;">
                    {pct:.1%} of eligible transactions</p>
                </div>
                """, unsafe_allow_html=True)

    with tab_type:
        st.write("These counts show which transaction types appear most often in the histories. "
                 "They also motivated category-count features in the model.")
        col_bar2, col_cards2 = st.columns([1.3, 1], gap="large")
        total_type = sum(r["count"] for r in act["types"])
        with col_bar2:
            st.markdown('<div class="chart-head"><strong>Transaction Frequency by Type</strong>'
                        '<span>All eligible training transactions</span></div>',
                        unsafe_allow_html=True)
            chart(act["types"], "category", "count", ylabel="Transactions")
        with col_cards2:
            bar_colors = ["#2D7459", "#4FAE9A", "#B6D86A", "#E49A63"]
            for i, row in enumerate(act["types"]):
                pct = row["count"] / max(total_type, 1)
                st.markdown(f"""
                <div class="s-card" style="padding:.85rem 1.05rem; margin-bottom:.55rem;">
                  <h3 style="font-family:monospace;">{row['category']}</h3>
                  <p style="font-size:1.3rem; font-weight:720; color:#0E2B22;
                       letter-spacing:-.03em; margin-bottom:.3rem;">{row['count']:,}</p>
                  <div class="mini-bar-wrap">
                    <div class="mini-bar" style="width:{pct:.0%};
                         background:{bar_colors[i % len(bar_colors)]};"></div>
                  </div>
                  <p style="margin-top:.28rem; font-size:.72rem; color:#9AABA3;">{pct:.1%} share</p>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 · AMOUNT DISTRIBUTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def page_amounts(s):
    d, t, a = s["dataset"], s["target"], s["amounts"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    page_header(
        "AMOUNT DISTRIBUTIONS · miqdor_indeksi",
        "How are standardized amounts distributed?",
        "Amounts are standardized index values, not currency. To keep the charts readable, the "
        "plotted range is capped at the 99th percentile; summary statistics include all observed values.",
        badge="miqdor_indeksi · index scale",
    )

    if not a.get("column"):
        st.info("An amount field was not identified in the transaction schema.")
        return

    suffix = " index units" if a.get("is_index") else ""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean amount index",   f"{a['mean']:,.3f}{suffix}")
    c2.metric("Median amount index", f"{a['median']:,.3f}{suffix}")
    c3.metric("95th percentile",     f"{a['p95']:,.3f}{suffix}")
    c4.metric("Transactions",        f"{a['count']:,}")

    tab_all, tab_per = st.tabs(["📊 All Transactions", "📦 Per-Alert Totals"])

    with tab_all:
        st.markdown('<div class="chart-head"><strong>Amount Index Distribution</strong>'
                    '<span>Upper tail clipped at 99th percentile</span></div>', unsafe_allow_html=True)
        chart(a["distribution"], "bin", "count", ylabel="Transactions")
        st.markdown("""
        <div class="callout">
          The distribution is centred just below zero (median ≈ −0.24) with a long right tail.
          These values represent standardized transaction magnitudes — not absolute currency amounts.
        </div>
        """, unsafe_allow_html=True)

    with tab_per:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown('<div class="chart-head"><strong>Total Eligible Amount per Alert</strong>'
                        '<span>Sum of eligible amounts by signal</span></div>', unsafe_allow_html=True)
            chart(a["amount_per_signal_distribution"], "bin", "count", ylabel="Alerts")
        with right:
            st.markdown('<div class="chart-head"><strong>Mean Transaction Amount per Alert</strong>'
                        '<span>Average eligible transaction value by signal</span></div>',
                        unsafe_allow_html=True)
            chart(a["mean_per_signal_distribution"], "bin", "count", ylabel="Alerts")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8 · RECENT ACTIVITY
# ═══════════════════════════════════════════════════════════════════════════════
def page_recent(s):
    d, t, recent = s["dataset"], s["target"], s["recent"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    page_header(
        "RECENT ACTIVITY · TEMPORAL BEHAVIOUR",
        "When do alerts arrive?",
        "This chart shows alert arrivals across the latest 90 dates with activity in the training "
        "data. The model also summarises transactions from fixed lookback periods (7, 30, 90 days).",
        badge=f"{recent['date_range_days']:,}-day date span",
    )

    c1, c2 = st.columns(2)
    c1.metric("Date range (days)",        f"{recent['date_range_days']:,}")
    c2.metric("Alerts in latest month",   f"{recent['latest_month_signals']:,}")

    st.markdown('<div class="chart-head"><strong>Daily Alert Arrivals</strong>'
                '<span>Latest 90 active dates in training data</span></div>', unsafe_allow_html=True)
    chart(recent["daily"], "date", "signals", kind="line",
          ylabel="Alerts", xlabel="Date")
    st.caption(f"Training alert dates span {recent['date_range_days']:,} days. "
               f"The most recent month shown contains {recent['latest_month_signals']:,} alerts.")

    st.markdown(f"""
    <div class="callout">
      Training and test alert dates overlap substantially
      ({d['train_date_min']}–{d['train_date_max']} and {d['test_date_min']}–{d['test_date_max']}).
      A random split alone would not test performance on later dates — motivating the use of
      expanding chronological folds in validation.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 9 · ESCALATED VS DISMISSED
# ═══════════════════════════════════════════════════════════════════════════════
def page_comparison(s):
    d, t, cmp = s["dataset"], s["target"], s["target_comparison"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    dismissed, escalated = cmp["dismissed"], cmp["escalated"]
    page_header(
        "ESCALATED VS DISMISSED COMPARISONS",
        "How do the two outcome groups differ?",
        "These unadjusted averages compare dismissed and escalated alerts. They show associations "
        "in the training data, not causes or guaranteed predictive signals.",
        badge="Descriptive · not causal",
    )

    # comparison table
    rows_html = ""
    table_data = [
        ("0", "dim",  "Dismissed (0)", dismissed),
        ("1", "",     "Escalated (1)", escalated),
    ]
    for badge_lbl, badge_cls, label, grp in table_data:
        rows_html += (
            f"<tr><td><span class='badge {badge_cls}'>{badge_lbl}</span> {label}</td>"
            f"<td>{grp['signals']:,}</td>"
            f"<td>{grp['transactions_per_signal_mean']:.1f}</td>"
            f"<td>{grp['transactions_per_signal_median']:.1f}</td>"
            f"<td>{grp['amount_per_signal_mean']:.2f}</td></tr>"
        )
    st.markdown(f"""
    <div class="s-card" style="padding:0; overflow:hidden;">
    <table class="data-table">
      <thead><tr>
        <th>Group</th><th>Signals</th>
        <th>Mean Tx / Signal</th><th>Median Tx / Signal</th>
        <th>Mean Amount Index / Signal</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="chart-head"><strong>Mean Transaction Count by Label</strong>'
                    '<span>Eligible transactions · unadjusted average</span></div>',
                    unsafe_allow_html=True)
        chart(
            [{"Group": "Dismissed", "Mean transactions": dismissed["transactions_per_signal_mean"]},
             {"Group": "Escalated", "Mean transactions": escalated["transactions_per_signal_mean"]}],
            "Group", "Mean transactions", ylabel="Mean eligible transactions",
        )
    with right:
        st.markdown('<div class="chart-head"><strong>Mean Total Amount Index by Label</strong>'
                    '<span>Sum of eligible amounts per signal · unadjusted</span></div>',
                    unsafe_allow_html=True)
        chart(
            [{"Group": "Dismissed", "Mean amount": dismissed["amount_per_signal_mean"]},
             {"Group": "Escalated", "Mean amount": escalated["amount_per_signal_mean"]}],
            "Group", "Mean amount", ylabel="Mean total amount index",
        )

    diff = escalated["transactions_per_signal_mean"] - dismissed["transactions_per_signal_mean"]
    direction = "more" if diff > 0 else "fewer"
    st.markdown(f"""
    <div class="callout">
      Dismissed alerts average <b>{dismissed['transactions_per_signal_mean']:.1f}</b> eligible
      transactions, compared with <b>{escalated['transactions_per_signal_mean']:.1f}</b> for
      escalated alerts — a difference of <b>{abs(diff):.1f} {direction}</b> transactions.
      This is a descriptive difference, not evidence of cause.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 10 · KEY EDA FINDINGS
# ═══════════════════════════════════════════════════════════════════════════════
def page_findings(s):
    d, t, act, q = s["dataset"], s["target"], s["activity"], s["quality"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    page_header(
        "KEY EDA OBSERVATIONS",
        "What patterns did we observe?",
        "These observations come from the training data and its precomputed aggregate summaries. "
        "They informed feature engineering and validation design.",
        badge="11 key observations",
    )

    stats   = act["transactions_per_signal"]
    positive = next((r["count"] for r in t["counts"] if r["class"] == 1), 0)
    cmp     = s["target_comparison"]

    items = [
        f"The training set contains <b>{d['train_signals']:,}</b> labeled alerts; "
        f"the test set contains <b>{d['test_signals']:,}</b> alerts without labels.",

        f"Each alert has a median of <b>{stats['median']:.0f}</b> eligible transactions. "
        f"<b>{stats['zero_signal_percent']:.1f}%</b> have no eligible history.",

        f"<b>{q['future_transaction_percent']:.3f}%</b> of linked, dated training transactions "
        f"occur after the alert date, so they are excluded from all historical summaries.",

        f"Training and test alert dates overlap substantially "
        f"({d['train_date_min']}–{d['train_date_max']} and {d['test_date_min']}–{d['test_date_max']}). "
        f"A random split alone would not test performance on later dates.",

        f"<b>{positive:,} of {d['train_signals']:,}</b> training alerts were escalated "
        f"({positive / max(d['train_signals'], 1):.1%}). Given this imbalance, ROC-AUC is a "
        f"useful metric for comparing rankings.",

        f"Dismissed alerts average <b>{cmp['dismissed']['transactions_per_signal_mean']:.1f}</b> "
        f"eligible transactions, compared with "
        f"<b>{cmp['escalated']['transactions_per_signal_mean']:.1f}</b> for escalated alerts. "
        f"This is a descriptive difference, not evidence of cause.",
    ]
    if method.get("oof_roc_auc") is not None:
        items.append(
            f"The final reproducible model, <b>{method['model']}</b>, achieved an "
            f"out-of-fold (OOF) ROC-AUC of <b>{method['oof_roc_auc']:.4f}</b> across "
            f"{method['oof_rows']:,} forward-validation alerts."
        )

    bullets = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(f'<ul class="finding-list">{bullets}</ul>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 11 · FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════
def page_features(s):
    d, t = s["dataset"], s["target"]
    method = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, method)
    page_header(
        "FEATURE ENGINEERING DECISIONS",
        "How did the EDA shape our features?",
        "The EDA led us to summarise each alert's history using features built without labels "
        "and only from transactions available by the alert date.",
        badge="28 final features",
    )

    groups = [
        ("History & transaction mix",
         "Transaction counts, active days, incoming and outgoing counts and shares, "
         "and counts by transaction type."),
        ("Amounts",
         "Sum, mean, standard deviation, median, minimum, maximum, and the 75th and 90th "
         "percentiles of the standardized amount index."),
        ("Recency",
         "Transaction counts and amount totals over 7-, 30-, and 90-day windows, "
         "time since the latest eligible transaction, and history span."),
        ("Calendar context",
         "Month and weekday features, evaluated with forward-only date blocks."),
        ("Feature selection outcome",
         "We tested longer windows, velocity ratios, transaction gaps, sequence summaries, "
         "feature subsets, model settings, and blends. The added feature groups did not "
         "outperform the simpler 28-feature shallow XGBoost model."),
        ("Leakage safeguards",
         "Later transactions are excluded; missing histories and zero denominators are handled "
         "explicitly; alert IDs are not used as target-encoded features."),
    ]

    for name, desc in groups:
        st.markdown(f"""
        <div class="s-card" style="margin-bottom:.6rem;">
          <h3>{name}</h3>
          <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.caption("Outcome comparisons helped guide the analysis, but were not used to create the features.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 12 · MODELING & VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════
def page_modeling(s):
    d, t = s["dataset"], s["target"]
    model = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, model)
    page_header(
        "MODELING APPROACH · VALIDATION METHODOLOGY",
        "How did we build and validate the model?",
        "We compared candidate models on the same five expanding, chronological folds. Each fold "
        "trains on earlier alerts and validates on a later date block; the initial warm-up period "
        "is not scored.",
        badge=f"OOF AUC {model.get('oof_roc_auc', 0):.4f}" if model.get("oof_roc_auc") else "Validation results",
    )

    tab_method, tab_folds, tab_base = st.tabs(
        ["⚙️ Model & Methodology", "📊 Fold-by-Fold Results", "📋 Baseline Comparison"]
    )

    with tab_method:
        st.markdown("""
        <ul class="finding-list">
          <li><b>Selected model:</b> shallow XGBoost with 500 trees, depth 2, learning rate 0.025,
              minimum child weight 15, 0.8 row and column subsampling, L2 regularisation of 5,
              and random seed 42.</li>
          <li><b>Validation strategy:</b> 5 forward-only folds producing out-of-fold predictions.
              Each fold trains on earlier alerts and validates on a non-overlapping later date block.</li>
          <li><b>Feature count:</b> 28 features covering count, amount, mix, recency, and calendar.</li>
          <li><b>Selection discipline:</b> we selected features and models using training data and
              OOF results only. Hidden test labels and leaderboard scores were not used.</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="callout callout-warn">
          <b>Scope note:</b> this OOF score is an internal forward-validation estimate.
          It is not a hidden-test or public leaderboard result.
        </div>
        """, unsafe_allow_html=True)
        if model.get("oof_roc_auc"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("OOF ROC-AUC",   f"{model['oof_roc_auc']:.4f}")
            c2.metric("Folds",         str(model.get("fold_count", "—")))
            c3.metric("OOF rows",      f"{model.get('oof_rows', 0):,}")
            c4.metric("Features used", str(model.get("feature_count", "—")))
        st.caption("This OOF score is an internal estimate. "
                   "It is not a hidden-test or leaderboard result.")

    with tab_folds:
        if model.get("fold_auc"):
            folds   = model["fold_auc"]
            max_auc = max(r["roc_auc"] for r in folds)
            fold_rows = ""
            for row in folds:
                bar_w = int(row["roc_auc"] / max_auc * 130)
                fold_rows += (
                    f"<tr><td><b>Fold {row['fold']}</b></td>"
                    f"<td><div class='auc-wrap'>"
                    f"<div class='auc-bar' style='width:{bar_w}px;'></div>"
                    f"<span>{row['roc_auc']:.4f}</span></div></td></tr>"
                )
            st.markdown(f"""
            <div class="s-card" style="padding:0; overflow:hidden;">
            <table class="data-table">
              <thead><tr><th>Fold</th><th>ROC-AUC</th></tr></thead>
              <tbody>{fold_rows}</tbody>
            </table>
            </div>
            """, unsafe_allow_html=True)

            fold_text = ", ".join(
                f"fold {r['fold']}: {r['roc_auc']:.4f}" for r in folds
            )
            st.markdown(f"**ROC-AUC by fold:** {fold_text}.")

            fig = go.Figure(go.Bar(
                x=[f"Fold {r['fold']}" for r in folds],
                y=[r["roc_auc"] for r in folds],
                marker_color=COLORS[0], marker_line_width=0,
                text=[f"{r['roc_auc']:.4f}" for r in folds],
                textposition="outside",
            ))
            fig.update_layout(
                template="plotly_white", height=300,
                margin=dict(l=18, r=18, t=16, b=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0, max_auc * 1.12], gridcolor="#EEF2EE"),
                xaxis=dict(showgrid=False),
                font=dict(family="Inter, Segoe UI, sans-serif", color="#627269"),
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displaylogo": False, "displayModeBar": False})
        else:
            st.info("Fold-level AUC breakdown not available in the summary.")

    with tab_base:
        if model.get("baseline_models"):
            baselines = model["baseline_models"]
            st.markdown("- **Baseline models:** " +
                        ", ".join(f"{r['model']}: {r['oof_roc_auc']:.4f}"
                                  for r in baselines) + ".")
            all_models = [
                {"model": model.get("model", "XGBoost (selected)"),
                 "oof_roc_auc": model["oof_roc_auc"], "selected": True},
            ] + [{"model": r["model"], "oof_roc_auc": r["oof_roc_auc"],
                  "selected": False} for r in baselines]
            all_models.sort(key=lambda x: x["oof_roc_auc"], reverse=True)
            max_auc_all = max(r["oof_roc_auc"] for r in all_models)

            brows = ""
            for r in all_models:
                bar_w = int(r["oof_roc_auc"] / max_auc_all * 130)
                star  = " ★" if r["selected"] else ""
                color = "#2D7459" if r["selected"] else "#4FAE9A"
                brows += (
                    f"<tr><td><b>{r['model']}{star}</b></td>"
                    f"<td><div class='auc-wrap'>"
                    f"<div class='auc-bar' style='width:{bar_w}px; background:{color};'></div>"
                    f"<span>{r['oof_roc_auc']:.4f}</span></div></td></tr>"
                )
            st.markdown(f"""
            <div class="s-card" style="padding:0; overflow:hidden;">
            <table class="data-table">
              <thead><tr><th>Model</th><th>OOF ROC-AUC</th></tr></thead>
              <tbody>{brows}</tbody>
            </table>
            </div>
            """, unsafe_allow_html=True)
            st.caption("★ = selected model. All models evaluated on the same 5 chronological folds.")
        else:
            st.info("Baseline model comparison not available in the summary.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 13 · CONCLUSION
# ═══════════════════════════════════════════════════════════════════════════════
def page_conclusion(s):
    d, t = s["dataset"], s["target"]
    model = s["method"].get("model_evaluation", {})
    kpi_strip(d, t, model)
    score_text = (
        f" Its forward-only OOF ROC-AUC was **{model['oof_roc_auc']:.4f}**."
        if model.get("oof_roc_auc") is not None else ""
    )
    page_header(
        "FINAL CONCLUSION",
        "What did we learn, and what does it mean?",
        "Our strongest validated approach applies a strict alert-date cutoff and uses a compact "
        "set of transaction count, amount, mix, recency, and calendar features." + score_text,
        badge="End of report",
    )

    st.write(
        "In our controlled experiments, shallow XGBoost with 28 features outperformed the "
        "more complex feature sets and blends we tested. "
        "This is a validation result, not a promise of hidden-test performance."
    )

    st.markdown("""
    <div class="callout">
      <b>In summary:</b> this report presents aggregate EDA and the modelling choices it
      informed. The synthetic competition data are shown only in aggregate; the site does not
      expose individual records or serve predictions.
    </div>
    """, unsafe_allow_html=True)

    # recap metrics grid
    positive = next((r["count"] for r in t["counts"] if r["class"] == 1), 0)
    esc_rate = positive / max(d["train_signals"], 1)
    act_stats = s["activity"]["transactions_per_signal"]
    auc = model.get("oof_roc_auc")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Labeled alerts",        f"{d['train_signals']:,}")
    c2.metric("Escalation rate",        f"{esc_rate:.1%}")
    c3.metric("Median Tx / alert",     f"{act_stats['median']:.0f}")
    c4.metric("Final OOF ROC-AUC",     f"{auc:.4f}" if auc else "—")

    st.markdown("---")
    st.markdown("""
    #### Report structure recap

    | Page | Content |
    |------|---------|
    | Dataset Structure | Tables, field definitions, transaction counts |
    | Data Quality | Duplicate IDs, future-transaction exclusion, per-column quality |
    | Target Distribution | Label counts, escalation rate, monthly trends |
    | Transaction Activity | Monthly volumes, history-size distribution |
    | Direction & Type | Incoming/outgoing split, transaction-type mix |
    | Amount Distributions | Index distribution, per-alert totals |
    | Recent Activity | Daily arrivals, temporal coverage |
    | Escalated vs Dismissed | Group-level descriptive comparisons |
    | Key EDA Findings | Consolidated bullet-point observations |
    | Feature Engineering | Feature groups and selection rationale |
    | Modeling & Validation | XGBoost details, fold results, baseline comparison |
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
summary = load_summary()
if summary is None:
    st.error("Precomputed summary is missing. "
             "Run: python eda_site/build_summary.py")
    st.stop()

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Overview"

active = render_sidebar(st.session_state["current_page"])
st.session_state["current_page"] = active

st.markdown(f"""
<header class="app-topbar">
  <div>
    <div class="app-welcome">Welcome to FinBytes</div>
    <div class="app-subtitle">Clear, time-aware insights into alert activity</div>
  </div>
  <div class="app-avatar" title="FinBytes analysis">F</div>
</header>
<div class="app-pagebar">
  <div class="app-page-title">{active}</div>
  <span class="app-page-tag">Synthetic data · Aggregate only</span>
</div>
""", unsafe_allow_html=True)

dispatch = {
    "Overview":               page_overview,
    "Dataset Structure":      page_dataset,
    "Data Quality":           page_quality,
    "Target Distribution":    page_target,
    "Transaction Activity":   page_activity,
    "Direction & Type":       page_direction_type,
    "Amount Distributions":   page_amounts,
    "Recent Activity":        page_recent,
    "Escalated vs Dismissed": page_comparison,
    "Key EDA Findings":       page_findings,
    "Feature Engineering":    page_features,
    "Modeling & Validation":  page_modeling,
    "Conclusion":             page_conclusion,
}
dispatch[active](summary)

st.markdown("---")
st.markdown(
    '<p style="font-size:.73rem; color:#9AABA3; text-align:center;">'
    'FinBytes · WIUT FinTech Hackathon · Exploratory analysis only · '
    'Aggregate summaries · No individual records exposed · No predictions served</p>',
    unsafe_allow_html=True,
)

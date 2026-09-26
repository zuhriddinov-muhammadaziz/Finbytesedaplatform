"""Public-facing, aggregate-only EDA website for FinBytes."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

SUMMARY = Path(__file__).parent / "assets" / "eda_summary.json"
SECTIONS = [
    "1. Problem overview", "2. Dataset structure", "3. Data quality and temporal relationship",
    "4. Target distribution", "5. Transaction activity over time", "6. Incoming vs outgoing behavior",
    "7. Transaction-type behavior", "8. Amount distributions", "9. Recent activity / temporal behavior",
    "10. Escalated vs dismissed comparisons", "11. Key EDA observations",
    "12. Feature engineering decisions motivated by EDA", "13. Modeling approach and validation methodology",
    "14. Final conclusion",
]
COLORS = ["#2D7459", "#B6D86A", "#4FAE9A", "#E49A63", "#67857B", "#A9C8B8"]

st.set_page_config(page_title="FinBytes | Exploratory Data Analysis", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.stApp {background:#F3F5F1;color:#1D3029}
[data-testid="stHeader"] {background:transparent}
.block-container {max-width:1360px;padding:1.25rem clamp(1rem,4vw,3.4rem) 4rem}
section[data-testid="stSidebar"] {display:none!important}
[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] {display:none!important}
.masthead {display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #D9E0D9;padding:.5rem 0 .9rem;margin-bottom:1.5rem}
.wordmark {font-size:.91rem;font-weight:800;letter-spacing:.07em;color:#153B2F}
.wordmark span {font-size:.65rem;font-weight:650;letter-spacing:.16em;color:#718078;margin-left:.8rem}
.synthetic-mark {font-size:.65rem;color:#65776E;letter-spacing:.08em;text-transform:uppercase}
.hero {position:relative;isolation:isolate;overflow:hidden;background:radial-gradient(ellipse at 94% 2%,rgba(79,174,154,.34),transparent 33%),linear-gradient(118deg,#102F28 0%,#174438 60%,#1D5847 100%);border-radius:18px;padding:clamp(1.45rem,4vw,3.1rem);margin:.4rem 0 1.35rem;box-shadow:0 18px 42px rgba(19,57,43,.12)}
.hero:after {content:"";position:absolute;z-index:-1;width:250px;height:250px;border:1px solid rgba(222,244,225,.16);border-radius:50%;right:7%;top:50%;transform:translateY(-50%);box-shadow:0 0 0 30px rgba(222,244,225,.035),0 0 0 62px rgba(222,244,225,.025)}
.hero-timeline {position:absolute;right:8%;top:50%;transform:translateY(-50%);width:220px;color:#D8E8DE}
.hero-timeline .timeline-labels {display:flex;justify-content:space-between;font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;color:#B9D1C3;margin-bottom:.8rem}
.hero-timeline .timeline-line {height:2px;position:relative;background:linear-gradient(90deg,rgba(168,214,181,.25),#A8D6B5);border-radius:2px}
.hero-timeline .timeline-line:before {content:"";position:absolute;left:18%;top:-4px;width:8px;height:8px;background:#A8D6B5;border:2px solid #225442;border-radius:50%;box-shadow:0 0 0 4px rgba(168,214,181,.12)}
.hero-timeline .timeline-line:after {content:"";position:absolute;right:0;top:-5px;width:2px;height:12px;background:#E3F2E8;box-shadow:0 0 0 4px rgba(227,242,232,.1)}
.hero-timeline .timeline-caption {display:flex;justify-content:space-between;font-size:.65rem;color:#B9D1C3;margin-top:.65rem}
.page-intro {position:relative;max-width:800px;margin:0}
.page-kicker {font-size:.67rem;letter-spacing:.16em;text-transform:uppercase;color:#A8D6B5;font-weight:800;margin-bottom:.85rem}
.page-intro h1 {font-size:clamp(2.2rem,5vw,4rem);line-height:1.01;margin:0;color:#F5F8F4;font-weight:760;letter-spacing:-.06em;max-width:720px}
.page-intro p {font-size:1rem;line-height:1.7;color:#D0DED5;max-width:650px;margin:.9rem 0 0}
[data-testid="stRadio"] {margin:.35rem 0 1.25rem}
[data-testid="stRadio"] [role="radiogroup"] {gap:.5rem}
[data-testid="stRadio"] label {background:#fff;border:1px solid #E1E7E0;border-radius:8px;padding:.48rem .9rem;color:#47594F;box-shadow:0 2px 8px rgba(25,54,38,.025);transition:all .18s ease}
[data-testid="stRadio"] label:has(input:checked) {background:#183E31;border-color:#183E31;color:#fff}
[data-testid="stRadio"] label p {font-size:.82rem;font-weight:650}
.view-title {display:flex;align-items:baseline;gap:.65rem;border-bottom:1px solid #D8E0D8;padding:1.2rem 0 .7rem;margin:1.1rem 0 .75rem}
.view-title .index {font-size:.68rem;letter-spacing:.12em;font-weight:800;color:#4B8D66}
.view-title h2 {font-size:1.55rem;letter-spacing:-.035em;margin:0;color:#1B3329}
[data-testid="stSelectbox"] [data-baseweb="select"] div {background:#fff!important;color:#1D3029!important}
[data-testid="stSelectbox"] [data-baseweb="select"] {background:#fff!important}
[data-testid="stSelectbox"] [data-baseweb="select"] * {color:#1D3029!important}
.section-heading-wrap {padding:.35rem 0 .75rem;margin:1.25rem 0 .2rem;border-bottom:1px solid #D8E0D8}
.section-heading {display:block;margin:.1rem 0 .25rem}
.chapter-label {font-size:.66rem;letter-spacing:.13em;text-transform:uppercase;color:#43805C;font-weight:800;margin-bottom:.4rem}
.section-heading h2 {margin:0;font-size:clamp(1.55rem,3vw,2rem);line-height:1.16;color:#1B3329;font-weight:720;letter-spacing:-.045em}
.callout {background:#fff;border:1px solid #E0E5DE;border-left:3px solid #73A458;padding:.95rem 1.1rem;border-radius:8px;margin:.75rem 0 1rem;color:#40554A;line-height:1.62}
.provenance {background:#EDF3E7;border-color:#DBE6D4;color:#426147}
.small-note {color:#78847D;font-size:.81rem}
h1,h2,h3 {letter-spacing:-.03em}
[data-testid="stMetric"] {position:relative;background:#fff;border:1px solid #E1E6DE;border-radius:12px;padding:1rem 1.05rem;min-height:102px;box-shadow:0 5px 18px rgba(32,51,39,.035);transition:transform .18s ease,box-shadow .18s ease}
[data-testid="stMetric"]:hover {transform:translateY(-2px);box-shadow:0 10px 24px rgba(32,51,39,.075)}
[data-testid="stMetricLabel"] {color:#758078;font-size:.76rem;letter-spacing:.015em}
[data-testid="stMetricValue"] {color:#1D3029;font-size:1.85rem;font-weight:680;letter-spacing:-.045em}
[data-testid="stPlotlyChart"] {background:#fff;border:1px solid #E1E6DE;border-radius:12px;padding:.5rem;box-shadow:0 5px 18px rgba(32,51,39,.035)}
[data-testid="stDataFrame"] {border:1px solid #E1E6DE;border-radius:9px;overflow:hidden}
[data-testid="stAlert"] {border-radius:8px;border-color:#DBE6D4;background:#EDF3E7}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {color:#426147;line-height:1.6}
.progress-meta {display:flex;justify-content:space-between;align-items:center;margin:.2rem 0 .4rem;color:#78847D;font-size:.72rem}
.progress-track {height:3px;border-radius:99px;background:#DDE5DC;overflow:hidden;margin:.1rem 0 1.3rem}
.progress-track span {display:block;height:100%;border-radius:99px;background:#69994D}
.fact-card {background:#fff;border:1px solid #E1E6DE;border-radius:9px;padding:.9rem 1rem;height:100%;color:#67766D;font-size:.77rem;line-height:1.5}
.fact-card b {display:block;color:#1D3029;font-size:1.25rem;letter-spacing:-.02em;margin-bottom:.35rem}
.overview-note {display:flex;align-items:center;gap:.75rem;background:#E7EEE7;border:1px solid #D9E4D8;border-radius:10px;padding:.85rem 1rem;margin:.5rem 0 1rem;color:#496052;font-size:.83rem;line-height:1.55}
.overview-note strong {color:#214B38;white-space:nowrap;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase}
.overview-chart-head {display:flex;align-items:baseline;justify-content:space-between;gap:1rem;margin:.2rem .2rem .5rem}
.overview-chart-head strong {font-size:.92rem;color:#233C30;letter-spacing:-.02em}
.overview-chart-head span {font-size:.7rem;color:#879188;letter-spacing:.08em;text-transform:uppercase}
.chart-insight {display:flex;align-items:flex-start;gap:.55rem;margin:.55rem .3rem .1rem;color:#64746B;font-size:.76rem;line-height:1.5}
.chart-insight b {color:#367454;font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap}
.explorer-intro {display:flex;justify-content:space-between;align-items:flex-end;gap:1.4rem;padding:.35rem 0 .85rem;color:#69776F}
.explorer-intro p {max-width:660px;margin:0;font-size:.9rem;line-height:1.6}
.explorer-count {flex:0 0 auto;border:1px solid #DDE5DC;background:#E9EFE8;border-radius:8px;padding:.55rem .75rem;color:#52705D;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase}
.topic-note {padding:.85rem 1rem;margin:.1rem 0 .7rem;background:#E7EEE7;border:1px solid #D9E4D8;border-radius:9px;color:#53665A;font-size:.8rem;line-height:1.5}
.topic-note strong {color:#244C38}
.journey-track {position:relative;display:grid;grid-template-columns:repeat(3,1fr);align-items:center;margin:.4rem 0 -.2rem;padding:0 1rem}
.journey-track:before {content:"";position:absolute;left:16.5%;right:16.5%;top:50%;height:2px;background:#C9D8CD;z-index:0}
.journey-stop {position:relative;z-index:1;justify-self:center;width:42px;height:42px;display:grid;place-items:center;border-radius:50%;background:#fff;border:2px solid #B8C8BC;color:#456653;font-size:.78rem;font-weight:800;box-shadow:0 0 0 5px #F3F5F1}
.journey-stop.active {background:#183E31;border-color:#183E31;color:#fff}
.journey-card {height:100%;min-height:176px;box-sizing:border-box;padding:1.05rem 1.1rem .9rem;margin-bottom:.45rem;border:1px solid #DDE5DC;border-radius:12px;background:#fff;transition:transform .18s ease,box-shadow .18s ease}
.journey-card.active {background:#183E31;border-color:#183E31;color:#fff;box-shadow:0 10px 25px rgba(24,62,49,.12)}
.journey-card:hover {transform:translateY(-2px);box-shadow:0 8px 22px rgba(32,51,39,.07)}
.journey-card .stage-kicker {font-size:.62rem;letter-spacing:.12em;font-weight:800;color:#4B8D66;text-transform:uppercase}
.journey-card.active .stage-kicker {color:#A8D6B5}
.journey-card h3 {font-size:1.08rem;line-height:1.25;margin:.5rem 0 .35rem;color:#1D3029}
.journey-card.active h3 {color:#fff}
.journey-card h3 a {display:none!important}
.journey-card p {font-size:.77rem;line-height:1.5;margin:0;color:#708078}
.journey-card.active p {color:#D2E2D8}
.journey-card .stage-chapters {margin-top:.75rem;padding-top:.65rem;border-top:1px solid #E5EBE4;color:#52675B;font-size:.68rem;font-weight:650}
.journey-card.active .stage-chapters {border-color:#47705D;color:#D2E2D8}
.journey-state {display:flex;justify-content:space-between;align-items:center;margin:1.35rem 0 .4rem}
.journey-state strong {font-size:.78rem;color:#284B39}
.journey-state span {font-size:.69rem;color:#829087;letter-spacing:.08em;text-transform:uppercase}
div[data-testid="stButton"] button {width:100%;border-radius:8px!important;min-height:40px;border:1px solid #D9E3DA;font-size:.78rem;font-weight:700;transition:transform .16s ease,box-shadow .16s ease}
div[data-testid="stButton"] button:hover {transform:translateY(-1px);box-shadow:0 5px 13px rgba(32,51,39,.08)}
div[data-testid="stButton"] button[kind="primary"] {background:#183E31;border-color:#183E31;color:#fff}
div[data-testid="stButton"] button[kind="secondary"] {background:#fff;color:#456653}
.chapter-choice-title {font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:#4B8D66;font-weight:800;margin:.3rem 0 .45rem}
@media(max-width:700px){.journey-track{padding:0}.journey-track:before{left:18%;right:18%}.journey-card{min-height:158px;padding:.85rem}.journey-card h3{font-size:.93rem}.journey-card .stage-chapters{font-size:.62rem}}
div[data-testid="stSelectbox"] label {font-size:.76rem;font-weight:650;color:#64746B}
div[data-testid="stSelectbox"] [data-baseweb="select"] {border-radius:8px}
hr {border-color:#DFE5DE!important;margin:1.8rem 0 1rem!important}
@media(max-width:900px){.hero-timeline{display:none}}
@media(max-width:900px){.block-container{padding:1rem 1rem 2.2rem}[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]){flex-wrap:wrap}[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"])>div{flex:1 1 calc(50% - .5rem);min-width:calc(50% - .5rem)!important}}
@media(max-width:600px){.masthead{align-items:flex-start;gap:.4rem;flex-direction:column}.wordmark span{display:block;margin:.2rem 0 0}.view-title{align-items:flex-start;flex-direction:column;gap:.25rem}}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_summary():
    if not SUMMARY.exists():
        return None
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def chart(data, x, y, *, kind="bar", title=None, xlabel=None, ylabel=None, color=None):
    df = pd.DataFrame(data)
    if df.empty:
        st.info("This view is not available because the source data did not include the required field.")
        return
    if kind == "line":
        fig = px.line(df, x=x, y=y, markers=True, title=title, color=color, color_discrete_sequence=COLORS)
    elif kind == "hist":
        fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=COLORS)
    else:
        fig = px.bar(df, x=x, y=y, title=title, color=color, color_discrete_sequence=COLORS)
    fig.update_layout(template="plotly_white", height=350, margin=dict(l=18, r=18, t=58, b=22),
                      xaxis_title=xlabel, yaxis_title=ylabel, legend_title_text="",
                      paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor="rgba(255,255,255,0)",
                      font=dict(family="Inter, sans-serif", color="#52645A"),
                      title_font=dict(size=16, color="#315C43"),
                      colorway=COLORS)
    if kind == "line":
        fig.update_traces(line=dict(width=2.6), marker=dict(size=6))
    else:
        fig.update_traces(marker_line_width=0, opacity=.92)
    fig.update_xaxes(showgrid=False, linecolor="#DCE3D9", tickfont_color="#748078", title_font_color="#52645A")
    fig.update_yaxes(gridcolor="#E9EDE6", zerolinecolor="#DCE3D9", tickfont_color="#748078", title_font_color="#52645A")
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "displayModeBar": False, "scrollZoom": False})


def chapter_progress(current: int, total: int, label: str) -> None:
    """Render an accessible, palette-aligned reading progress indicator."""
    percent = max(0, min(100, round(current / total * 100)))
    st.markdown(
        f'<div class="progress-meta"><span>{label} {current:02d} of {total:02d}</span>'
        f'<span>{percent}%</span></div><div class="progress-track" role="progressbar" '
        f'aria-valuemin="0" aria-valuemax="100" aria-valuenow="{percent}">'
        f'<span style="width:{percent}%"></span></div>',
        unsafe_allow_html=True,
    )


def show(s, selected=None, *, include_heading=True, explorer_chapter=False):
    d, q, t, a, act, recent = s["dataset"], s["quality"], s["target"], s["amounts"], s["activity"], s["recent"]
    selected = selected or st.session_state.section
    section_index = SECTIONS.index(selected)
    section_number, _, section_title = selected.partition(". ")
    if include_heading:
        if explorer_chapter:
            chapter_number = section_index
            chapter_label = f"CHAPTER {chapter_number:02d} / 09 · EDA EXPLORER"
        else:
            chapter_number = section_index + 1
            chapter_label = f"SECTION {int(section_number):02d} / {len(SECTIONS):02d} · EXPLORATORY ANALYSIS"
        st.markdown(
            f'<div class="section-heading-wrap"><div class="section-heading"><div class="chapter-label">{chapter_label}</div>'
            f'<h2>{section_title}</h2></div></div>',
            unsafe_allow_html=True,
        )
        if explorer_chapter:
            chapter_progress(chapter_number, 9, "Chapter")
        else:
            chapter_progress(chapter_number, len(SECTIONS), "Section")
    if selected.startswith("1."):
        st.write("We studied whether transaction history can help distinguish alerts that were escalated for review from those that were dismissed. This report presents the data, the patterns we observed, and how they shaped our analysis. It does not score alerts or serve a model.")
        st.markdown('<div class="callout provenance"><b>Data provenance:</b> these competition records are synthetic and localized for the hackathon. They do not represent real customers or transactions from the Central Bank of Uzbekistan or a commercial bank.</div>', unsafe_allow_html=True)
        st.markdown('<div class="callout"><b>How to interpret the analysis:</b> these comparisons describe this dataset. They do not explain why an alert was escalated or guarantee that a pattern will hold for new data.</div>', unsafe_allow_html=True)
        st.caption(f"Training alerts run from {d['train_date_min']} to {d['train_date_max']}. Transaction summaries use the alert-date cutoff.")
    elif selected.startswith("2."):
        st.write("Each alert is one training example, linked to its transaction history by `signal_id`. Test alerts have the same fields, but their outcomes are withheld.")
        st.markdown("**Training alert fields:** " + ", ".join(f"`{x}`" for x in d["train_signal_columns"]))
        st.markdown("**Test alert fields:** " + ", ".join(f"`{x}`" for x in d["test_signal_columns"]))
        st.markdown("**Transaction fields:** " + ", ".join(f"`{x}`" for x in d["transaction_columns"]))
        c1, c2 = st.columns(2)
        c1.metric("Training transactions", f"{d['train_transaction_rows']:,}")
        c2.metric("Test transactions", f"{d['test_transaction_rows']:,}")
        st.caption("This site shows aggregate summaries only. It does not expose individual alert records or identifiers.")
    elif selected.startswith("3."):
        st.write("We checked for duplicate alert IDs, missing transaction dates, unmatched transaction links, and transactions dated after their alert.")
        a1, a2, a3 = st.columns(3)
        a1.metric("Duplicate training IDs", f"{q['train_signal_duplicate_ids']:,}")
        a2.metric("Duplicate test IDs", f"{q['test_signal_duplicate_ids']:,}")
        a3.metric("Transactions with unmatched IDs", f"{q['transaction_signal_ids_unmatched']:,}")
        b1, b2, b3 = st.columns(3)
        b1.metric("Transactions missing date", f"{q['transaction_missing_date']:,}")
        b2.metric("Dated and linked transactions", f"{q['linked_dated_transactions']:,}")
        b3.metric("After signal date", f"{q['future_transactions']:,} ({q['future_transaction_percent']}%)")
        st.markdown('<div class="callout"><b>Signal-time cutoff:</b> behavior summaries include dated transactions on or before the alert date. Later transactions are excluded because they would not have been available when the alert was reviewed.</div>', unsafe_allow_html=True)
        quality = pd.DataFrame([{"Field": k, "Missing": v["nulls"], "Missing (%)": v["null_percent"], "Distinct values": v["distinct"]} for k, v in q["transaction_column_quality"].items()])
        st.dataframe(quality, hide_index=True, width="stretch")
    elif selected.startswith("4."):
        st.write("Label 0 means dismissed and label 1 means escalated. Monthly rates describe the observed data and may vary when a month has fewer alerts.")
        chart(t["counts"], "label", "count", title="Training alert outcomes", ylabel="Alerts")
        chart(t["monthly"], "month", "escalation_rate", kind="line", title="Escalation rate by alert month", ylabel="Escalation rate")
    elif selected.startswith("5."):
        st.write("These monthly totals include only transactions dated on or before their linked alert. The amount of history available varies from one alert to another.")
        chart(act["transactions_by_month"], "month", "count", title="Eligible transactions by month", ylabel="Transactions")
        stats = act["transactions_per_signal"]
        st.write(f"Across {d['train_signals']:,} training alerts, the mean history contains **{stats['mean']:.2f}** transactions and the median **{stats['median']:.0f}**. The 90th percentile is **{stats['p90']:.0f}**; **{stats['zero_signal_percent']:.1f}%** have no eligible transactions.")
        chart(act["transaction_count_distribution"], "bin", "count", title="Transactions per alert (upper tail clipped)", ylabel="Alerts")
    elif selected.startswith("6."):
        st.write("This chart counts eligible transactions by recorded direction. It shows how often each direction appears, not the net flow of money.")
        chart(act["directions"], "category", "count", title="Transaction frequency by direction", ylabel="Transactions")
    elif selected.startswith("7."):
        st.write("These counts show which transaction types appear most often in the histories. They also motivated category-count features in the model.")
        chart(act["types"], "category", "count", title="Transaction frequency by type", ylabel="Transactions")
    elif selected.startswith("8."):
        st.write("Amounts are standardized index values, not currency. To keep the charts readable, the plotted range is capped at the 99th percentile; summary statistics include all observed values.")
        if a["column"]:
            c1, c2, c3 = st.columns(3)
            suffix = " index units" if a.get("is_index") else ""
            c1.metric("Mean amount index", f"{a['mean']:,.2f}{suffix}")
            c2.metric("Median amount index", f"{a['median']:,.2f}{suffix}")
            c3.metric("95th percentile", f"{a['p95']:,.2f}{suffix}")
            chart(a["distribution"], "bin", "count", title="Amount index distribution (upper tail clipped)", ylabel="Transactions")
            col1, col2 = st.columns(2)
            with col1: chart(a["amount_per_signal_distribution"], "bin", "count", title="Total eligible amount per signal", ylabel="Signals")
            with col2: chart(a["mean_per_signal_distribution"], "bin", "count", title="Mean eligible transaction amount per signal", ylabel="Signals")
        else:
            st.info("An amount field was not identified in the transaction schema.")
    elif selected.startswith("9."):
        st.write("This chart shows alert arrivals across the latest 90 dates with activity in the training data. The model also summarizes transactions from fixed lookback periods.")
        chart(recent["daily"], "date", "signals", kind="line", title="Daily alert arrivals (latest 90 active dates)", ylabel="Alerts")
        st.caption(f"Training alert dates span {recent['date_range_days']:,} days. The most recent month shown contains {recent['latest_month_signals']:,} alerts.")
    elif selected.startswith("10."):
        st.write("These unadjusted averages compare dismissed and escalated alerts. They show associations in the training data, not causes or guaranteed predictive signals.")
        rows = []
        for key, label in (("dismissed", "Dismissed (0)"), ("escalated", "Escalated (1)")):
            v = s["target_comparison"][key]
            rows.append({"Group": label, "Signals": v["signals"], "Mean transactions / signal": v["transactions_per_signal_mean"], "Median transactions / signal": v["transactions_per_signal_median"], "Mean total amount index / signal": v["amount_per_signal_mean"]})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        chart([{"Group": "Dismissed", "Mean transactions": s["target_comparison"]["dismissed"]["transactions_per_signal_mean"]}, {"Group": "Escalated", "Mean transactions": s["target_comparison"]["escalated"]["transactions_per_signal_mean"]}], "Group", "Mean transactions", title="Mean eligible transaction count by label")
    elif selected.startswith("11."):
        st.write("These observations come from the training data and its precomputed aggregate summaries.")
        stats = act["transactions_per_signal"]
        st.markdown(f"- The training set contains **{d['train_signals']:,}** labeled alerts; the test set contains **{d['test_signals']:,}** alerts without labels.")
        st.markdown(f"- Each alert has a median of **{stats['median']:.0f}** eligible transactions. **{stats['zero_signal_percent']:.1f}%** have no eligible history.")
        st.markdown(f"- **{q['future_transaction_percent']:.2f}%** of linked, dated training transactions occur after the alert date, so they are excluded from historical summaries.")
        st.markdown(f"- Training and test alert dates overlap substantially ({d['train_date_min']}–{d['train_date_max']} and {d['test_date_min']}–{d['test_date_max']}). A random split alone would not test performance on later dates.")
        positive = next((x for x in t["counts"] if x["class"] == 1), {"count": 0})
        st.markdown(f"- **{positive['count']:,} of {d['train_signals']:,}** training alerts were escalated ({positive['count'] / max(d['train_signals'], 1):.1%}). Given this imbalance, ROC-AUC is a useful metric for comparing rankings.")
        compare = s["target_comparison"]
        st.markdown(f"- Dismissed alerts average **{compare['dismissed']['transactions_per_signal_mean']:.1f}** eligible transactions, compared with **{compare['escalated']['transactions_per_signal_mean']:.1f}** for escalated alerts. This is a descriptive difference, not evidence of cause.")
        model = s["method"].get("model_evaluation", {})
        if model.get("oof_roc_auc") is not None:
            st.markdown(f"- The final reproducible model, **{model['model']}**, achieved an out-of-fold (OOF) ROC-AUC of **{model['oof_roc_auc']:.4f}** across {model['oof_rows']:,} forward-validation alerts.")
    elif selected.startswith("12."):
        st.write("The EDA led us to summarize each alert’s history using features built without labels and only from transactions available by the alert date.")
        st.markdown("- **History and transaction mix:** transaction counts, active days, incoming and outgoing counts and shares, and counts by transaction type.")
        st.markdown("- **Amounts:** sum, mean, standard deviation, median, minimum, maximum, and the 75th and 90th percentiles of the standardized amount index.")
        st.markdown("- **Recency:** transaction counts and amount totals over 7-, 30-, and 90-day windows, time since the latest eligible transaction, and history span.")
        st.markdown("- **Calendar context:** month and weekday features, evaluated with forward-only date blocks.")
        st.markdown("- **Feature selection:** we tested longer windows, velocity ratios, transaction gaps, sequence summaries, feature subsets, model settings, and blends. The added feature groups did not outperform the simpler 28-feature shallow XGBoost model.")
        st.markdown("- **Leakage safeguards:** later transactions are excluded; missing histories and zero denominators are handled explicitly; alert IDs are not used as target-encoded features.")
        st.caption("Outcome comparisons helped guide the analysis, but were not used to create the features.")
    elif selected.startswith("13."):
        model = s["method"].get("model_evaluation", {})
        st.write("We compared candidate models on the same five expanding, chronological folds. Each fold trains on earlier alerts and validates on a later date block; the initial warm-up period is not scored.")
        st.markdown("- **Selected model:** shallow XGBoost with 500 trees, depth 2, learning rate 0.025, minimum child weight 15, 0.8 row and column subsampling, L2 regularization of 5, and random seed 42.")
        st.markdown(f"- **Validation result:** {model.get('fold_count', 0)} forward-only folds produced {model.get('oof_rows', 0):,} out-of-fold predictions. OOF ROC-AUC was **{model.get('oof_roc_auc', 0):.4f}** across {model.get('feature_count', 0)} features.")
        if model.get("fold_auc"):
            st.markdown("- **ROC-AUC by fold:** " + ", ".join(f"fold {row['fold']}: {row['roc_auc']:.4f}" for row in model["fold_auc"]) + ".")
        if model.get("baseline_models"):
            comparison = ", ".join(f"{row['model']}: {row['oof_roc_auc']:.4f}" for row in model["baseline_models"])
            st.markdown("- **Baseline models:** " + comparison + ".")
        st.markdown("- We selected features and models using training data and OOF results only. Hidden test labels and leaderboard scores were not used.")
        st.caption("This OOF score is an internal estimate. It is not a hidden-test or leaderboard result.")
    else:
        model = s["method"].get("model_evaluation", {})
        score_text = f" Its forward-only OOF ROC-AUC was {model['oof_roc_auc']:.4f}." if model.get("oof_roc_auc") is not None else ""
        st.write("Our strongest validated approach applies a strict alert-date cutoff and uses a compact set of transaction count, amount, mix, recency, and calendar features." + score_text)
        st.markdown("In our controlled experiments, shallow XGBoost with 28 features outperformed the more complex feature sets and blends we tested. This is a validation result, not a promise of hidden-test performance.")
        st.markdown('<div class="callout"><b>In summary:</b> this report presents aggregate EDA and the modeling choices it informed. The synthetic competition data are shown only in aggregate; the site does not expose individual records or serve predictions.</div>', unsafe_allow_html=True)


@st.fragment
def render_eda_explorer(summary_data):
    """Isolate chapter navigation so it doesn't rerun the rest of the report."""
    st.markdown('<div class="view-title"><span class="index">02 / 03</span><h2>Explore the data</h2></div>', unsafe_allow_html=True)
    stages = [
        {"name": "Foundations", "title": "Data foundation", "description": "Review the linked tables, field definitions, data quality, and alert-time cutoff.", "chapters": "01 Dataset structure  ·  02 Data quality", "sections": SECTIONS[1:3]},
        {"name": "Outcomes & activity", "title": "Activity & outcomes", "description": "Explore escalation rates, transaction volume, direction, and transaction type.", "chapters": "03–06  ·  4 chapters", "sections": SECTIONS[3:7]},
        {"name": "Transaction profiles", "title": "History profiles", "description": "Compare amount distributions, recent activity, and dismissed versus escalated alerts.", "chapters": "07–09  ·  3 chapters", "sections": SECTIONS[7:10]},
    ]
    st.session_state.setdefault("eda_topic", "Foundations")
    topic = st.session_state.eda_topic
    active_stage = next((stage for stage in stages if stage["name"] == topic), stages[0])
    topic = active_stage["name"]
    st.markdown('<div class="explorer-intro"><p>Move from data checks to behavioral patterns. All comparisons use aggregate transaction history available by the alert date.</p><span class="explorer-count">9 chapters · 3 stages</span></div>', unsafe_allow_html=True)
    track = ''.join(f'<div class="journey-stop{" active" if stage["name"] == topic else ""}">{index:02d}</div>' for index, stage in enumerate(stages, 1))
    st.markdown(f'<div class="journey-track" aria-label="Three-stage EDA path">{track}</div>', unsafe_allow_html=True)
    stage_columns = st.columns(3, gap="medium")
    stage_changed = False
    for column, stage in zip(stage_columns, stages):
        active = stage["name"] == topic
        with column:
            st.markdown(
                f'<div class="journey-card{" active" if active else ""}"><div class="stage-kicker">{stages.index(stage) + 1:02d} / EDA JOURNEY</div>'
                f'<h3>{stage["title"]}</h3><p>{stage["description"]}</p><div class="stage-chapters">{stage["chapters"]}</div></div>',
                unsafe_allow_html=True,
            )
            if not active and st.button("View stage →", key=f"eda-stage-{stages.index(stage)}",
                                        type="secondary", use_container_width=True):
                st.session_state.eda_topic = stage["name"]
                stage_changed = True
    if stage_changed:
        st.rerun(scope="fragment")

    topic_sections = active_stage["sections"]
    chapter = st.session_state.get("eda_chapter_selection", st.session_state.get("section", topic_sections[0]))
    if chapter not in topic_sections:
        chapter = topic_sections[0]
        st.session_state.eda_chapter_selection = chapter
    st.markdown(f'<div class="journey-state"><strong>Chapters · {active_stage["title"]}</strong><span>Choose one to open its analysis</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="chapter-choice-title">Select a chapter</div>', unsafe_allow_html=True)
    chapter_nav_titles = {3: "Data quality & timing", 5: "Activity over time", 6: "Incoming vs outgoing", 7: "Transaction types", 9: "Recent activity", 10: "Outcome comparison"}
    for row_start in range(0, len(topic_sections), 2):
        chapter_columns = st.columns(2, gap="small")
        for column, chapter_option in zip(chapter_columns, topic_sections[row_start:row_start + 2]):
            number, _, title = chapter_option.partition(". ")
            nav_title = chapter_nav_titles.get(int(number), title)
            explorer_number = SECTIONS.index(chapter_option)
            with column:
                if st.button(f"{explorer_number:02d}  ·  {nav_title}", key=f"eda-chapter-{number}",
                             type="primary" if chapter_option == chapter else "secondary", use_container_width=True):
                    chapter = chapter_option
                    st.session_state.eda_chapter_selection = chapter_option
    st.session_state.section = chapter
    _ = show(summary_data, chapter, explorer_chapter=True)


summary = load_summary()
if summary is None:
    st.error("The precomputed aggregate summary is missing. From the project root, run: python eda_site/build_summary.py")
    st.stop()
d, t = summary["dataset"], summary["target"]
positive = next((row["count"] for row in t["counts"] if row["class"] == 1), 0)
escalation_rate = positive / max(d["train_signals"], 1)
st.markdown('<div class="masthead"><div class="wordmark">FINBYTES <span>ALERT BEHAVIOR RESEARCH</span></div><div class="synthetic-mark">Synthetic hackathon data · Aggregate analysis</div></div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="page-intro"><div class="page-kicker">A TRANSACTION HISTORY STUDY&nbsp;&nbsp; / &nbsp;&nbsp; RESEARCH REPORT</div><h1>What activity comes before an alert?</h1><p>We studied synthetic transaction histories linked to past alerts to find useful patterns and guide our features and time-aware validation.</p></div><div class="hero-timeline" aria-label="Only activity before an alert is included"><div class="timeline-labels"><span>History</span><span>Signal time</span></div><div class="timeline-line"></div><div class="timeline-caption"><span>Earlier activity</span><span>Alert arrives</span></div></div></div>', unsafe_allow_html=True)
active_view = st.radio("Report view", ["Overview", "EDA explorer", "Findings & model"], horizontal=True, label_visibility="collapsed", key="active_view")
if active_view != "EDA explorer":
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Labeled alerts", f"{d['train_signals']:,}")
    kpi2.metric("Test alerts", f"{d['test_signals']:,}")
    kpi3.metric("Training transactions", f"{d['train_transaction_rows'] / 1_000_000:.2f}M")
    kpi4.metric("Escalation rate", f"{escalation_rate:.1%}")
if active_view == "Overview":
    st.markdown('<div class="view-title"><span class="index">01 / 03</span><h2>At a glance</h2></div>', unsafe_allow_html=True)
    show(summary, SECTIONS[0], include_heading=False)
    st.markdown('<div class="overview-note"><strong>Reading the report</strong><span>Start with the outcome mix, then explore transaction behavior and the time-aware validation choices it informed.</span></div>', unsafe_allow_html=True)
    activity = summary["activity"]
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="overview-chart-head"><strong>Outcome mix</strong><span>Training labels</span></div>', unsafe_allow_html=True)
        chart(t["counts"], "label", "count", title="Training alert outcomes", ylabel="Alerts")
    with right:
        st.markdown('<div class="overview-chart-head"><strong>Transaction activity</strong><span>Signal-time eligible</span></div>', unsafe_allow_html=True)
        activity_lens = st.radio("Activity view", ["Over time", "By direction", "By type"], horizontal=True,
                                 label_visibility="collapsed", key="overview_activity_lens")
        if activity_lens == "Over time":
            chart(activity["transactions_by_month"], "month", "count", title="Eligible activity by month", ylabel="Transactions")
            lens_detail = "Monthly totals show when eligible transaction activity was recorded."
        elif activity_lens == "By direction":
            chart(activity["directions"], "category", "count", title="Eligible activity by direction", ylabel="Transactions")
            lens_detail = "Direction counts describe recorded incoming and outgoing transaction frequency."
        else:
            chart(activity["types"], "category", "count", title="Eligible activity by transaction type", ylabel="Transactions")
            lens_detail = "Type counts show the most common transaction categories in the histories."
        st.markdown(f'<div class="chart-insight"><b>How to read</b><span>{lens_detail}</span></div>', unsafe_allow_html=True)
    quality = summary["quality"]
    method = summary["method"].get("model_evaluation", {})
    facts = st.columns(3)
    facts[0].markdown(f'<div class="fact-card"><b>{activity["transactions_per_signal"]["median"]:.0f}</b>Median eligible transactions per signal</div>', unsafe_allow_html=True)
    facts[1].markdown(f'<div class="fact-card"><b>{quality["future_transaction_percent"]:.2f}%</b>Linked, dated training transactions fall after the signal date and are excluded</div>', unsafe_allow_html=True)
    auc = method.get("oof_roc_auc")
    facts[2].markdown(f'<div class="fact-card"><b>{auc:.4f}</b>Forward-only OOF ROC-AUC</div>' if auc is not None else '<div class="fact-card"><b>—</b>Forward-only OOF ROC-AUC</div>', unsafe_allow_html=True)
    st.caption("Outcome comparisons are descriptive, not causal. The OOF score is an internal forward-validation estimate, not a hidden-test result.")
elif active_view == "EDA explorer":
    render_eda_explorer(summary)
else:
    st.markdown('<div class="view-title"><span class="index">03 / 03</span><h2>Findings & modeling</h2></div>', unsafe_allow_html=True)
    selected = st.selectbox("Choose a findings section", SECTIONS[10:], key="model_section")
    st.session_state.section = selected
    show(summary, selected)
st.markdown("---")
st.markdown('<p class="small-note">Exploratory analysis only · Aggregate data · No predictions are served</p>', unsafe_allow_html=True)

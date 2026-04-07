import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Returns Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        text-align: center;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1f3a5f;
        margin-bottom: 0.2rem;
    }
    .section-sub {
        font-size: 0.82rem;
        color: #6c757d;
        margin-bottom: 1rem;
    }
    h1 { color: #1f3a5f; }
    hr { border-color: #dee2e6; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Colour palette (consistent across all charts) ─────────────────────────────
PALETTE = px.colors.qualitative.Plotly  # 10 distinct colours

# ── Load & cache data ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    prices  = pd.read_csv("prices.csv",  index_col="Date", parse_dates=True)
    returns = pd.read_csv("returns.csv", index_col="Date", parse_dates=True)
    return prices, returns

prices, returns = load_data()
TICKERS   = prices.columns.tolist()
COLOR_MAP = {t: PALETTE[i % len(PALETTE)] for i, t in enumerate(TICKERS)}

# ── Pre-compute metrics ────────────────────────────────────────────────────────
ann_ret  = returns.mean() * 252 * 100
ann_vol  = returns.std()  * np.sqrt(252) * 100
sharpe   = ann_ret / ann_vol
total_ret = (prices.iloc[-1] / prices.iloc[0] - 1) * 100

max_dd = {}
for t in TICKERS:
    cum = (1 + returns[t]).cumprod()
    max_dd[t] = ((cum - cum.cummax()) / cum.cummax()).min() * 100

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/combo-chart--v1.png", width=60)
    st.title("Controls")
    st.markdown("---")

    selected = st.multiselect(
        "Select tickers",
        options=TICKERS,
        default=TICKERS,
    )
    if not selected:
        st.warning("Select at least one ticker.")
        st.stop()

    st.markdown("---")
    st.markdown("**Period**")
    min_date = prices.index.min().date()
    max_date = prices.index.max().date()
    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    else:
        start, end = pd.Timestamp(min_date), pd.Timestamp(max_date)

    st.markdown("---")
    st.markdown(
        "<small>**Data:** Yahoo Finance via yfinance<br>"
        "**Universe:** 10 tickers across equities, fixed income & commodities<br>"
        "**Period:** 2022–2024</small>",
        unsafe_allow_html=True,
    )

# ── Filter by sidebar selections ──────────────────────────────────────────────
p = prices.loc[start:end, selected]
r = returns.loc[start:end, selected]

ar  = r.mean() * 252 * 100
av  = r.std()  * np.sqrt(252) * 100
sh  = ar / av
tr  = (p.iloc[-1] / p.iloc[0] - 1) * 100
mdd = {}
for t in selected:
    cum = (1 + r[t]).cumprod()
    mdd[t] = ((cum - cum.cummax()) / cum.cummax()).min() * 100

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📈 Stock Returns Dashboard")
st.markdown(
    f"**Period:** {start.date()} → {end.date()} &nbsp;|&nbsp; "
    f"**Tickers:** {', '.join(selected)} &nbsp;|&nbsp; "
    f"**Trading days:** {len(r)}"
)
st.markdown("---")

# ── KPI cards ─────────────────────────────────────────────────────────────────
best_ticker  = ar.idxmax()
worst_ticker = ar.idxmin()
most_vol     = av.idxmax()
best_sharpe  = sh.idxmax()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Best Return",     f"{ar[best_ticker]:+.1f}%",  best_ticker)
k2.metric("Worst Return",    f"{ar[worst_ticker]:+.1f}%", worst_ticker)
k3.metric("Most Volatile",   f"{av[most_vol]:.1f}%",      most_vol)
k4.metric("Best Sharpe",     f"{sh[best_sharpe]:.2f}",    best_sharpe)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 · CORRELATION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">Section 1 · Correlation Heatmap</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Pairwise Pearson correlation of daily returns. Values near +1 = move together; near 0 = uncorrelated; negative = hedge.</p>', unsafe_allow_html=True)

corr = r.corr().round(2)
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
corr_masked = corr.where(~mask)

fig_corr = go.Figure(go.Heatmap(
    z=corr_masked.values,
    x=corr.columns.tolist(),
    y=corr.index.tolist(),
    colorscale="RdBu",
    reversescale=True,
    zmid=0, zmin=-1, zmax=1,
    text=corr_masked.round(2).astype(str).replace("nan", ""),
    texttemplate="%{text}",
    textfont={"size": 11, "color": "black"},
    hoverongaps=False,
    colorbar=dict(title="Correlation", thickness=14),
))
fig_corr.update_layout(
    title="Return Correlation Matrix",
    height=480,
    margin=dict(l=10, r=10, t=45, b=10),
    xaxis=dict(side="bottom"),
    paper_bgcolor="white",
    plot_bgcolor="white",
)
st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 & 3 · ANNUALIZED RETURNS + VOLATILITY
# ══════════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<p class="section-title">Section 2 · Annualized Returns</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Average daily return scaled to annual (×252). Green = positive, red = negative.</p>', unsafe_allow_html=True)

    sorted_ret = ar.sort_values()
    bar_colors = ["#2ca02c" if v >= 0 else "#d62728" for v in sorted_ret]

    fig_ret = go.Figure(go.Bar(
        x=sorted_ret.values,
        y=sorted_ret.index,
        orientation="h",
        marker_color=bar_colors,
        text=[f"{v:+.1f}%" for v in sorted_ret.values],
        textposition="outside",
        hovertemplate="%{y}: %{x:.2f}%<extra></extra>",
    ))
    fig_ret.add_vline(x=0, line_width=1.5, line_color="black")
    fig_ret.update_layout(
        title="Annualized Return (%)",
        xaxis_title="Return (%)",
        height=400,
        margin=dict(l=10, r=60, t=45, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(ticksuffix="%", gridcolor="#e9ecef"),
    )
    st.plotly_chart(fig_ret, use_container_width=True)

with col_right:
    st.markdown('<p class="section-title">Section 3 · Annualized Volatility</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Std dev of daily returns scaled to annual (×√252). Higher = wider outcome distribution = more risk.</p>', unsafe_allow_html=True)

    sorted_vol = av.sort_values()
    vol_colors = [COLOR_MAP[t] for t in sorted_vol.index]

    fig_vol = go.Figure(go.Bar(
        x=sorted_vol.values,
        y=sorted_vol.index,
        orientation="h",
        marker_color=vol_colors,
        text=[f"{v:.1f}%" for v in sorted_vol.values],
        textposition="outside",
        hovertemplate="%{y}: %{x:.2f}%<extra></extra>",
    ))
    fig_vol.update_layout(
        title="Annualized Volatility (%)",
        xaxis_title="Volatility (%)",
        height=400,
        margin=dict(l=10, r=60, t=45, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(ticksuffix="%", gridcolor="#e9ecef"),
    )
    st.plotly_chart(fig_vol, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 · CUMULATIVE RETURNS ($1 INVESTED)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">Section 4 · Cumulative Returns ($1 Invested)</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Tracks the growth of $1 invested at the start of the period — buy-and-hold, no transaction costs.</p>', unsafe_allow_html=True)

growth = (1 + r).cumprod()

fig_cum = go.Figure()
for ticker in selected:
    final = growth[ticker].iloc[-1]
    fig_cum.add_trace(go.Scatter(
        x=growth.index,
        y=growth[ticker],
        name=f"{ticker}  (${final:.2f})",
        line=dict(color=COLOR_MAP[ticker], width=2),
        hovertemplate=f"{ticker}<br>Date: %{{x|%d %b %Y}}<br>Value: $%{{y:.3f}}<extra></extra>",
    ))

fig_cum.add_hline(y=1.0, line_dash="dash", line_color="black",
                  line_width=1.2, annotation_text="Break-even ($1.00)",
                  annotation_position="bottom right")
fig_cum.update_layout(
    title="Growth of $1 Invested",
    yaxis_title="Portfolio Value ($)",
    yaxis_tickprefix="$",
    height=480,
    hovermode="x unified",
    legend=dict(orientation="v", x=1.01, y=1, bgcolor="rgba(255,255,255,0.85)",
                bordercolor="#dee2e6", borderwidth=1),
    margin=dict(l=10, r=160, t=45, b=10),
    paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis=dict(gridcolor="#e9ecef"),
    yaxis=dict(gridcolor="#e9ecef"),
)
st.plotly_chart(fig_cum, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 · SUMMARY STATISTICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">Section 5 · Summary Statistics</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Consolidated performance table sorted by annualized return. Sharpe = Ann. Return / Ann. Volatility (risk-free rate = 0).</p>', unsafe_allow_html=True)

summary = pd.DataFrame({
    "Total Return":     tr.map(lambda x: f"{x:+.1f}%"),
    "Ann. Return":      ar.map(lambda x: f"{x:+.1f}%"),
    "Ann. Volatility":  av.map(lambda x: f"{x:.1f}%"),
    "Sharpe Ratio":     sh.map(lambda x: f"{x:.2f}"),
    "Max Drawdown":     pd.Series(mdd).map(lambda x: f"{x:.1f}%"),
})
summary.index.name = "Ticker"
summary = summary.loc[ar.sort_values(ascending=False).index]

# Color rows by return value
def color_row(row):
    ticker = row.name
    val = ar[ticker]
    if val >= 15:
        bg = "background-color: #d4edda;"
    elif val >= 0:
        bg = "background-color: #f8f9fa;"
    else:
        bg = "background-color: #f8d7da;"
    return [bg] * len(row)

st.dataframe(
    summary.style.apply(color_row, axis=1),
    use_container_width=True,
    height=420,
)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# BONUS · RISK–RETURN SCATTER + DRAWDOWN
# ══════════════════════════════════════════════════════════════════════════════
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<p class="section-title">Risk–Return Scatter</p>', unsafe_allow_html=True)

    fig_rr = go.Figure()
    for ticker in selected:
        fig_rr.add_trace(go.Scatter(
            x=[av[ticker]], y=[ar[ticker]],
            mode="markers+text",
            name=ticker,
            text=[ticker],
            textposition="top right",
            textfont=dict(size=10),
            marker=dict(size=12, color=COLOR_MAP[ticker],
                        line=dict(width=1, color="white")),
            hovertemplate=(
                f"<b>{ticker}</b><br>"
                f"Volatility: {av[ticker]:.1f}%<br>"
                f"Return: {ar[ticker]:+.1f}%<br>"
                f"Sharpe: {sh[ticker]:.2f}<extra></extra>"
            ),
        ))
    fig_rr.add_hline(y=0, line_dash="dash", line_color="grey", line_width=1)
    fig_rr.update_layout(
        title="Risk–Return Profile",
        xaxis_title="Volatility (%)", yaxis_title="Return (%)",
        showlegend=False, height=400,
        xaxis=dict(ticksuffix="%", gridcolor="#e9ecef"),
        yaxis=dict(ticksuffix="%", gridcolor="#e9ecef"),
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=10, r=10, t=45, b=10),
    )
    st.plotly_chart(fig_rr, use_container_width=True)

with col_b:
    st.markdown('<p class="section-title">Drawdown from Peak</p>', unsafe_allow_html=True)

    fig_dd = go.Figure()
    for ticker in selected:
        cum = (1 + r[ticker]).cumprod()
        dd  = (cum - cum.cummax()) / cum.cummax() * 100
        fig_dd.add_trace(go.Scatter(
            x=dd.index, y=dd,
            name=ticker,
            line=dict(color=COLOR_MAP[ticker], width=1.6),
            hovertemplate=f"{ticker}<br>%{{x|%d %b %Y}}: %{{y:.2f}}%<extra></extra>",
        ))
    fig_dd.update_layout(
        title="Drawdown from Peak (%)",
        yaxis_title="Drawdown (%)",
        yaxis_ticksuffix="%",
        height=400,
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(gridcolor="#e9ecef"),
        yaxis=dict(gridcolor="#e9ecef"),
        margin=dict(l=10, r=10, t=45, b=10),
    )
    st.plotly_chart(fig_dd, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#6c757d;'>Data: Yahoo Finance · Built with Streamlit & Plotly · "
    "Sharpe ratio assumes risk-free rate = 0</small>",
    unsafe_allow_html=True,
)

"""
3_Position_Analysis.py — Average stats by position and squad composition breakdown.

NOTE: All data is SYNTHETIC — not based on real players or real-world results.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils import (
    load_data,
    render_sidebar,
    apply_theme,
    chart_layout,
    PRIMARY_GREEN,
    ACCENT,
    CHART_COLORS,
    POSITION_COLORS,
    POSITION_ORDER,
    CARD_BG,
)

st.set_page_config(
    page_title="Position Analysis | Football Analytics",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

df_full = load_data()
df = render_sidebar(df_full)

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("## 🗺️ Position Analysis")
st.markdown(
    "<span style='color:#f9c74f;font-size:13px;'>"
    "⚠ SYNTHETIC DATA — all statistics are artificially generated and do not "
    "represent real players or real-world results."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Average stats by position ──────────────────────────────────────────────
st.markdown("### Average Stats by Position")

AVG_COLS = ["goals", "assists", "shots", "passes", "dribbles", "tackles", "rating"]
AVG_LABELS = {
    "goals":    "Goals",
    "assists":  "Assists",
    "shots":    "Shots",
    "passes":   "Passes",
    "dribbles": "Dribbles",
    "tackles":  "Tackles",
    "rating":   "Avg Rating",
}

# Only show positions that exist in filtered data
pos_present = [p for p in POSITION_ORDER if p in df["position"].unique()]

pos_avg = (
    df[df["position"].isin(pos_present)]
    .groupby("position", observed=True)[AVG_COLS]
    .mean()
    .round(2)
    .reset_index()
)
pos_avg["position"] = pd.Categorical(pos_avg["position"], categories=pos_present, ordered=True)
pos_avg = pos_avg.sort_values("position")

# Metric selector
metric_choice = st.selectbox(
    "Select metric to compare across positions",
    options=list(AVG_LABELS.keys()),
    format_func=lambda x: AVG_LABELS[x],
    key="pos_metric",
)

fig_pos_bar = px.bar(
    pos_avg,
    x="position",
    y=metric_choice,
    color="position",
    color_discrete_map=POSITION_COLORS,
    text=metric_choice,
    labels={"position": "Position", metric_choice: AVG_LABELS[metric_choice]},
    category_orders={"position": pos_present},
)
fig_pos_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig_pos_bar.update_layout(showlegend=False)
fig_pos_bar = chart_layout(fig_pos_bar, height=380)
st.plotly_chart(fig_pos_bar, use_container_width=True)

st.markdown("---")

# ── Multi-metric grouped bar ───────────────────────────────────────────────
st.markdown("### Multi-Metric Comparison Across Positions")

metrics_selected = st.multiselect(
    "Choose metrics",
    options=list(AVG_LABELS.keys()),
    default=["goals", "assists", "dribbles", "tackles"],
    key="pos_multi_metric",
)

if not metrics_selected:
    st.info("Select at least one metric above.")
else:
    pos_melted = pos_avg.melt(
        id_vars="position",
        value_vars=metrics_selected,
        var_name="Metric",
        value_name="Average",
    )
    pos_melted["Metric"] = pos_melted["Metric"].map(AVG_LABELS)

    fig_multi = px.bar(
        pos_melted,
        x="Metric",
        y="Average",
        color="position",
        barmode="group",
        color_discrete_map=POSITION_COLORS,
        labels={"position": "Position", "Average": "Average Value", "Metric": ""},
        category_orders={"position": pos_present},
        hover_data={"Average": ":.2f"},
    )
    fig_multi = chart_layout(fig_multi, height=420)
    st.plotly_chart(fig_multi, use_container_width=True)

st.markdown("---")

# ── Position distribution donut ────────────────────────────────────────────
st.markdown("### Squad Composition")

col_d, col_t = st.columns([1, 1])

with col_d:
    pos_counts = (
        df.groupby("position", observed=True)["player_id"]
        .nunique()
        .reset_index()
        .rename(columns={"player_id": "Players"})
    )
    pos_counts["position"] = pd.Categorical(
        pos_counts["position"], categories=POSITION_ORDER, ordered=True
    )
    pos_counts = pos_counts.sort_values("position")

    fig_donut = px.pie(
        pos_counts,
        names="position",
        values="Players",
        hole=0.55,
        color="position",
        color_discrete_map=POSITION_COLORS,
    )
    fig_donut.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Players: %{value}<br>Share: %{percent}<extra></extra>",
    )
    fig_donut.update_layout(
        showlegend=True,
        paper_bgcolor=CARD_BG,
        font=dict(color="#e8eaf0"),
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_t:
    st.markdown("**Position Summary Table**")
    summary = pos_avg.copy()
    summary.columns = ["Position"] + [AVG_LABELS[c] for c in AVG_COLS]
    st.dataframe(summary.set_index("Position"), use_container_width=True)

st.markdown("---")

# ── Top player per position ────────────────────────────────────────────────
st.markdown("### Top-Rated Player per Position")

top_per_pos = (
    df.sort_values("rating", ascending=False)
    .groupby("position", observed=True)
    .first()
    .reset_index()[["position", "player_name", "team", "season", "goals", "assists", "rating"]]
    .rename(columns={
        "position":    "Position",
        "player_name": "Player",
        "team":        "Team",
        "season":      "Season",
        "goals":       "Goals",
        "assists":     "Assists",
        "rating":      "Rating",
    })
)
top_per_pos["Position"] = pd.Categorical(
    top_per_pos["Position"], categories=POSITION_ORDER, ordered=True
)
top_per_pos = top_per_pos.sort_values("Position").set_index("Position")
st.dataframe(top_per_pos, use_container_width=True)

"""
app.py — Entry point for the Football Player Performance Analytics Dashboard.
This file serves as the Home / Overview page in Streamlit's native multi-page structure.

NOTE: All data displayed is SYNTHETIC and for demonstration purposes only.
"""

import streamlit as st
import plotly.express as px
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
    CARD_BG,
)

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# ── Load data & apply sidebar filters ─────────────────────────────────────
df_full = load_data()
df = render_sidebar(df_full)

# ── Page header ────────────────────────────────────────────────────────────
st.markdown("## ⚽ Football Player Performance Dashboard")
st.markdown(
    "<span style='color:#f9c74f;font-size:13px;'>"
    "⚠ SYNTHETIC DATA — all statistics are artificially generated and do not "
    "represent real players or real-world results."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── KPI Cards ──────────────────────────────────────────────────────────────
st.markdown("### Key Performance Indicators")

total_players   = df["player_id"].nunique()
total_goals     = int(df["goals"].sum())
total_assists   = int(df["assists"].sum())
total_minutes   = int(df["minutes_played"].sum())
avg_rating      = round(float(df["rating"].mean()), 2)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Players",       f"{total_players:,}")
c2.metric("Total Goals",         f"{total_goals:,}")
c3.metric("Total Assists",       f"{total_assists:,}")
c4.metric("Total Minutes",       f"{total_minutes:,}")
c5.metric("Avg Player Rating",   f"{avg_rating}")

st.markdown("---")

# ── Top 10 Scorers ─────────────────────────────────────────────────────────
st.markdown("### Top 10 Goal Scorers")

top_scorers = (
    df.groupby("player_name", as_index=False)["goals"]
    .sum()
    .sort_values("goals", ascending=False)
    .head(10)
)

fig_scorers = px.bar(
    top_scorers,
    x="goals",
    y="player_name",
    orientation="h",
    color="goals",
    color_continuous_scale=[[0, CARD_BG], [1, PRIMARY_GREEN]],
    labels={"goals": "Goals", "player_name": "Player"},
    hover_data={"goals": True},
)
fig_scorers.update_layout(yaxis=dict(categoryorder="total ascending"), coloraxis_showscale=False)
fig_scorers = chart_layout(fig_scorers, height=400)
st.plotly_chart(fig_scorers, use_container_width=True)

st.markdown("---")

# ── Goals & Assists by Team ────────────────────────────────────────────────
st.markdown("### Goals & Assists by Team")

team_stats = (
    df.groupby("team", as_index=False)
    .agg(Goals=("goals", "sum"), Assists=("assists", "sum"))
    .sort_values("Goals", ascending=False)
)

team_melted = team_stats.melt(id_vars="team", var_name="Metric", value_name="Count")

fig_team = px.bar(
    team_melted,
    x="team",
    y="Count",
    color="Metric",
    barmode="group",
    color_discrete_map={"Goals": PRIMARY_GREEN, "Assists": ACCENT},
    labels={"team": "Team", "Count": "Total", "Metric": ""},
    hover_data={"Count": True},
)
fig_team = chart_layout(fig_team, height=400)
st.plotly_chart(fig_team, use_container_width=True)

st.markdown("---")

# ── Top Rated Players table ────────────────────────────────────────────────
st.markdown("### Top 10 Highest-Rated Players")

top_rated = (
    df.groupby(["player_name", "team", "position"], as_index=False)["rating"]
    .mean()
    .sort_values("rating", ascending=False)
    .head(10)
    .reset_index(drop=True)
)
top_rated.index += 1
top_rated["rating"] = top_rated["rating"].round(2)
top_rated.columns = ["Player", "Team", "Position", "Avg Rating"]
st.dataframe(top_rated, use_container_width=True)

"""
2_Team_Analysis.py — Goals, assists, ratings and squad depth by club.

NOTE: All data is SYNTHETIC — not based on real players or real-world results.
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
    CARD_BG,
)

st.set_page_config(
    page_title="Team Analysis | Football Analytics",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

df_full = load_data()
df = render_sidebar(df_full)

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("## 🏟️ Team Analysis")
st.markdown(
    "<span style='color:#f9c74f;font-size:13px;'>"
    "⚠ SYNTHETIC DATA — all statistics are artificially generated and do not "
    "represent real players or real-world results."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Team attacking output (Goals + Assists grouped bar) ────────────────────
st.markdown("### Goals & Assists by Team")

team_attack = (
    df.groupby("team", as_index=False)
    .agg(Goals=("goals", "sum"), Assists=("assists", "sum"))
    .sort_values("Goals", ascending=False)
)

team_melted = team_attack.melt(id_vars="team", var_name="Metric", value_name="Count")

fig_attack = px.bar(
    team_melted,
    x="team",
    y="Count",
    color="Metric",
    barmode="group",
    color_discrete_map={"Goals": PRIMARY_GREEN, "Assists": ACCENT},
    labels={"team": "Team", "Count": "Total", "Metric": ""},
    text="Count",
    hover_data={"Count": True},
)
fig_attack.update_traces(texttemplate="%{text}", textposition="outside")
fig_attack = chart_layout(fig_attack, height=420)
st.plotly_chart(fig_attack, use_container_width=True)

st.markdown("---")

# ── Average rating per team ────────────────────────────────────────────────
st.markdown("### Average Player Rating by Team")

team_rating = (
    df.groupby("team", as_index=False)["rating"]
    .mean()
    .rename(columns={"rating": "Avg Rating"})
    .sort_values("Avg Rating", ascending=False)
)
team_rating["Avg Rating"] = team_rating["Avg Rating"].round(2)

fig_rating = px.bar(
    team_rating,
    x="team",
    y="Avg Rating",
    color="Avg Rating",
    color_continuous_scale=[[0, CARD_BG], [1, PRIMARY_GREEN]],
    text="Avg Rating",
    labels={"team": "Team", "Avg Rating": "Avg Rating"},
)
fig_rating.update_traces(texttemplate="%{text}", textposition="outside")
fig_rating.update_layout(coloraxis_showscale=False)
fig_rating = chart_layout(fig_rating, height=400)
st.plotly_chart(fig_rating, use_container_width=True)

st.markdown("---")

# ── Player count per team (pie) ────────────────────────────────────────────
col_p, col_s = st.columns([1, 1.2])

with col_p:
    st.markdown("### Squad Size")

    team_counts = (
        df.groupby("team")["player_id"]
        .nunique()
        .reset_index()
        .rename(columns={"player_id": "Players"})
        .sort_values("Players", ascending=False)
    )

    fig_pie = px.pie(
        team_counts,
        names="team",
        values="Players",
        hole=0.45,
        color_discrete_sequence=CHART_COLORS,
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Players: %{value}<br>Share: %{percent}<extra></extra>",
    )
    fig_pie.update_layout(
        paper_bgcolor=CARD_BG,
        font=dict(color="#e8eaf0"),
        height=380,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_s:
    # ── Top performer per team ─────────────────────────────────────────────
    st.markdown("### Top-Rated Player per Team")

    top_per_team = (
        df.sort_values("rating", ascending=False)
        .groupby("team")
        .first()
        .reset_index()[["team", "player_name", "position", "season", "goals", "assists", "rating"]]
        .rename(columns={
            "team":        "Team",
            "player_name": "Player",
            "position":    "Pos",
            "season":      "Season",
            "goals":       "Goals",
            "assists":     "Assists",
            "rating":      "Rating",
        })
        .sort_values("Rating", ascending=False)
        .set_index("Team")
    )
    st.dataframe(top_per_team, use_container_width=True, height=360)

st.markdown("---")

# ── Team summary table ─────────────────────────────────────────────────────
st.markdown("### Full Team Summary")

team_summary = (
    df.groupby("team", as_index=False)
    .agg(
        Players=("player_id", "nunique"),
        Goals=("goals", "sum"),
        Assists=("assists", "sum"),
        Shots=("shots", "sum"),
        Passes=("passes", "sum"),
        Avg_Rating=("rating", "mean"),
    )
    .sort_values("Goals", ascending=False)
)
team_summary["Avg_Rating"] = team_summary["Avg_Rating"].round(2)
team_summary = team_summary.rename(columns={"Avg_Rating": "Avg Rating"}).set_index("team")
team_summary.index.name = "Team"
st.dataframe(team_summary, use_container_width=True)

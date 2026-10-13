"""
1_Player_Analysis.py — Goals vs Assists scatter, Shots vs Goals scatter,
single-player radar chart, and two-player side-by-side bar comparison.

NOTE: All data is SYNTHETIC — not based on real players or real-world results.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

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
    TEXT_MUTED,
)

st.set_page_config(
    page_title="Player Analysis | Football Analytics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

df_full = load_data()
df = render_sidebar(df_full)

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("## 🔍 Player Analysis")
st.markdown(
    "<span style='color:#f9c74f;font-size:13px;'>"
    "⚠ SYNTHETIC DATA — all statistics are artificially generated and do not "
    "represent real players or real-world results."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Section 1: Goals vs Assists Scatter ───────────────────────────────────
st.markdown("### Goals vs Assists")
st.caption("Bubble size = minutes played. Colour = position. Hover for full player details.")

fig_ga = px.scatter(
    df,
    x="assists",
    y="goals",
    color="position",
    color_discrete_map=POSITION_COLORS,
    size="minutes_played",
    size_max=24,
    hover_name="player_name",
    hover_data={
        "team": True,
        "season": True,
        "rating": True,
        "minutes_played": True,
        "position": False,
    },
    labels={"goals": "Goals", "assists": "Assists", "position": "Position"},
    category_orders={"position": ["GK", "DEF", "MID", "FWD"]},
)
fig_ga = chart_layout(fig_ga, height=460)
st.plotly_chart(fig_ga, use_container_width=True)

st.markdown("---")

# ── Section 2: Shots vs Goals Scatter (with OLS trendline) ────────────────
st.markdown("### Shots vs Goals — Conversion Efficiency")
st.caption("OLS trendline shows the average conversion rate across the filtered dataset.")

try:
    fig_sg = px.scatter(
        df,
        x="shots",
        y="goals",
        color="position",
        color_discrete_map=POSITION_COLORS,
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override=ACCENT,
        hover_name="player_name",
        hover_data={
            "team": True,
            "shots_on_target": True,
            "season": True,
            "position": False,
        },
        labels={"shots": "Shots", "goals": "Goals", "position": "Position"},
        category_orders={"position": ["GK", "DEF", "MID", "FWD"]},
    )
except Exception:
    # statsmodels not installed — fall back to scatter without trendline
    fig_sg = px.scatter(
        df,
        x="shots",
        y="goals",
        color="position",
        color_discrete_map=POSITION_COLORS,
        hover_name="player_name",
        hover_data={"team": True, "shots_on_target": True, "season": True, "position": False},
        labels={"shots": "Shots", "goals": "Goals", "position": "Position"},
    )
    st.info("Install statsmodels (`pip install statsmodels`) to show the OLS trendline.")

# Conversion rate annotation
non_zero = df[df["shots"] > 0]
if not non_zero.empty:
    avg_conversion = (non_zero["goals"] / non_zero["shots"]).mean() * 100
    fig_sg.add_annotation(
        x=df["shots"].max() * 0.75,
        y=df["goals"].max() * 0.92,
        text=f"Avg conversion rate: {avg_conversion:.1f}%",
        showarrow=False,
        font=dict(color=ACCENT, size=12),
        bgcolor=CARD_BG,
        bordercolor=ACCENT,
        borderwidth=1,
        borderpad=6,
    )

fig_sg = chart_layout(fig_sg, height=460)
st.plotly_chart(fig_sg, use_container_width=True)

st.markdown("---")

# ── Section 3: Player Radar / Comparison ──────────────────────────────────
selected_players = st.session_state.get("filter_player", [])
n_selected = len(selected_players)

RADAR_COLS = ["goals", "assists", "pass_accuracy", "tackles", "dribbles", "rating"]
RADAR_LABELS = ["Goals", "Assists", "Pass Acc.", "Tackles", "Dribbles", "Rating"]

def normalise(series: pd.Series) -> pd.Series:
    """Normalise to [0, 1] against the max in the full filtered df."""
    max_val = df[series.name].max()
    return series / max_val if max_val > 0 else series * 0


if n_selected == 0:
    st.markdown("### Player Radar Profile")
    st.info(
        "Select a player in the sidebar **Player** filter to view their radar chart. "
        "Select exactly 2 players to compare them side-by-side."
    )

elif n_selected == 1:
    st.markdown(f"### Radar Profile — {selected_players[0]}")

    player_df = df[df["player_name"] == selected_players[0]]
    if player_df.empty:
        st.warning("No data for this player with the current filters.")
    else:
        agg = player_df[RADAR_COLS].mean()
        # Normalise each stat against the filtered dataset's max
        norm_vals = [agg[c] / df[c].max() if df[c].max() > 0 else 0 for c in RADAR_COLS]
        norm_vals_closed = norm_vals + [norm_vals[0]]  # close the polygon
        labels_closed = RADAR_LABELS + [RADAR_LABELS[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=norm_vals_closed,
            theta=labels_closed,
            fill="toself",
            fillcolor=f"rgba(0,255,133,0.15)",
            line=dict(color=PRIMARY_GREEN, width=2),
            name=selected_players[0],
            hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor=CARD_BG,
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickfont=dict(color=TEXT_MUTED, size=10),
                    gridcolor="#2a2d3e",
                    linecolor="#2a2d3e",
                ),
                angularaxis=dict(
                    tickfont=dict(color="#e8eaf0", size=12),
                    gridcolor="#2a2d3e",
                    linecolor="#2a2d3e",
                ),
            ),
            paper_bgcolor=CARD_BG,
            font=dict(color="#e8eaf0"),
            showlegend=True,
            height=480,
            margin=dict(l=60, r=60, t=60, b=60),
        )

        col_r, col_s = st.columns([1.4, 1])
        with col_r:
            st.plotly_chart(fig_radar, use_container_width=True)
        with col_s:
            st.markdown("**Season-by-season breakdown**")
            breakdown = (
                player_df[["season"] + RADAR_COLS]
                .set_index("season")
                .round(2)
            )
            breakdown.columns = RADAR_LABELS
            st.dataframe(breakdown, use_container_width=True)

elif n_selected == 2:
    st.markdown(f"### Head-to-Head Comparison")
    st.caption(f"{selected_players[0]}  vs  {selected_players[1]}")

    COMPARE_COLS = ["goals", "assists", "shots", "passes", "dribbles", "tackles", "rating"]
    COMPARE_LABELS = ["Goals", "Assists", "Shots", "Passes", "Dribbles", "Tackles", "Rating"]

    p1_agg = df[df["player_name"] == selected_players[0]][COMPARE_COLS].mean().round(2)
    p2_agg = df[df["player_name"] == selected_players[1]][COMPARE_COLS].mean().round(2)

    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        name=selected_players[0],
        x=COMPARE_LABELS,
        y=p1_agg.values,
        marker_color=PRIMARY_GREEN,
        hovertemplate="%{x}: %{y:.2f}<extra></extra>",
    ))
    fig_cmp.add_trace(go.Bar(
        name=selected_players[1],
        x=COMPARE_LABELS,
        y=p2_agg.values,
        marker_color="#00c4ff",
        hovertemplate="%{x}: %{y:.2f}<extra></extra>",
    ))
    fig_cmp.update_layout(barmode="group")
    fig_cmp = chart_layout(fig_cmp, height=460)
    st.plotly_chart(fig_cmp, use_container_width=True)

    # Quick delta table
    delta_df = pd.DataFrame({
        "Metric":      COMPARE_LABELS,
        selected_players[0]: p1_agg.values,
        selected_players[1]: p2_agg.values,
    })
    delta_df["Difference"] = (p1_agg.values - p2_agg.values).round(2)
    delta_df = delta_df.set_index("Metric")
    st.dataframe(delta_df, use_container_width=True)

else:
    st.markdown("### Player Radar / Comparison")
    st.info(
        f"You have selected **{n_selected} players**. "
        "Select **1 player** for a radar profile, or **exactly 2 players** for a head-to-head comparison."
    )

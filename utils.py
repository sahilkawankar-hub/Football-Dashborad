"""
utils.py — shared helpers for every page of the Football Analytics Dashboard.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PRIMARY_GREEN = "#00ff85"
DARK_BG = "#0e1117"
CARD_BG = "#1a1d27"
SIDEBAR_BG = "#161923"
ACCENT = "#1db954"
TEXT_MUTED = "#888fa8"

PLOTLY_TEMPLATE = "plotly_dark"
CHART_COLORS = [PRIMARY_GREEN, "#1db954", "#00c4ff", "#ff6b6b", "#f9c74f", "#a78bfa"]

POSITION_ORDER = ["GK", "DEF", "MID", "FWD"]
POSITION_COLORS = {
    "GK":  "#f9c74f",
    "DEF": "#00c4ff",
    "MID": PRIMARY_GREEN,
    "FWD": "#ff6b6b",
}

NUMERIC_COLS = [
    "matches_played", "minutes_played", "goals", "assists",
    "shots", "shots_on_target", "passes", "pass_accuracy",
    "dribbles", "tackles", "yellow_cards", "red_cards", "rating",
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    """Read football_players.csv and return a typed DataFrame."""
    df = pd.read_csv("football_players.csv")
    # Ensure correct dtypes
    int_cols = [
        "player_id", "age", "matches_played", "minutes_played",
        "goals", "assists", "shots", "shots_on_target",
        "passes", "dribbles", "tackles", "yellow_cards", "red_cards",
    ]
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    df["pass_accuracy"] = pd.to_numeric(df["pass_accuracy"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["season"] = df["season"].astype(str)
    df["position"] = pd.Categorical(df["position"], categories=POSITION_ORDER, ordered=True)
    return df


# ---------------------------------------------------------------------------
# Sidebar filters  (cascading: season → team → position → player)
# ---------------------------------------------------------------------------
def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render the sidebar filter widgets and return the filtered DataFrame.
    Calls st.stop() if the result is empty to prevent broken charts.
    """
    st.sidebar.markdown(
        """
        <div style='padding:8px 12px;background:#2d1b00;border-left:3px solid #f9c74f;
                    border-radius:4px;margin-bottom:12px;font-size:12px;color:#f9c74f;'>
        <b>SYNTHETIC DATA</b><br>
        All statistics are artificially generated for demonstration purposes only.
        They do not represent real players or real-world results.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Filters")

    # --- Season ---
    all_seasons = sorted(df["season"].unique().tolist())
    season_choice = st.sidebar.selectbox(
        "Season",
        options=["All Seasons"] + all_seasons,
        key="filter_season",
    )

    df_s = df if season_choice == "All Seasons" else df[df["season"] == season_choice]

    # --- Team ---
    all_teams = sorted(df_s["team"].unique().tolist())
    team_choice = st.sidebar.selectbox(
        "Team",
        options=["All Teams"] + all_teams,
        key="filter_team",
    )

    df_t = df_s if team_choice == "All Teams" else df_s[df_s["team"] == team_choice]

    # --- Position ---
    all_positions = [p for p in POSITION_ORDER if p in df_t["position"].unique()]
    position_choice = st.sidebar.selectbox(
        "Position",
        options=["All Positions"] + all_positions,
        key="filter_position",
    )

    df_p = df_t if position_choice == "All Positions" else df_t[df_t["position"] == position_choice]

    # --- Player (multiselect — drives comparison charts) ---
    all_players = sorted(df_p["player_name"].unique().tolist())
    player_choice = st.sidebar.multiselect(
        "Player (select 1 for radar, 2 for comparison)",
        options=all_players,
        default=[],
        key="filter_player",
    )

    df_final = df_p if not player_choice else df_p[df_p["player_name"].isin(player_choice)]

    # --- Empty guard ---
    if df_final.empty:
        st.warning(
            "No data matches the current filters. "
            "Please adjust the Season, Team, Position, or Player selection."
        )
        st.stop()

    return df_final


# ---------------------------------------------------------------------------
# Theme / CSS injection
# ---------------------------------------------------------------------------
def apply_theme() -> None:
    """Inject dark football-pitch–inspired CSS into every page."""
    st.markdown(
        f"""
        <style>
        /* ── Global background & text ─────────────────────────────────── */
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: {DARK_BG};
            color: #e8eaf0;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }}
        [data-testid="stHeader"] {{
            background-color: {DARK_BG};
        }}

        /* ── Sidebar ───────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG};
            border-right: 1px solid #2a2d3e;
        }}
        [data-testid="stSidebar"] * {{
            color: #e8eaf0 !important;
        }}

        /* ── Metric cards ─────────────────────────────────────────────── */
        [data-testid="stMetric"] {{
            background-color: {CARD_BG};
            border: 1px solid #2a2d3e;
            border-radius: 10px;
            padding: 16px 20px;
        }}
        [data-testid="stMetricValue"] {{
            color: {PRIMARY_GREEN} !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {TEXT_MUTED} !important;
            font-size: 0.78rem !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        /* ── Dataframe ────────────────────────────────────────────────── */
        [data-testid="stDataFrame"] {{
            border: 1px solid #2a2d3e;
            border-radius: 8px;
        }}

        /* ── Headings ─────────────────────────────────────────────────── */
        h1, h2, h3 {{
            color: {PRIMARY_GREEN};
            font-weight: 700;
        }}

        /* ── Buttons ──────────────────────────────────────────────────── */
        [data-testid="stDownloadButton"] > button {{
            background-color: {ACCENT};
            color: #000;
            border-radius: 6px;
            font-weight: 600;
            border: none;
        }}
        [data-testid="stDownloadButton"] > button:hover {{
            background-color: {PRIMARY_GREEN};
        }}

        /* ── Select boxes ─────────────────────────────────────────────── */
        [data-testid="stSelectbox"] label,
        [data-testid="stMultiSelect"] label {{
            color: {TEXT_MUTED} !important;
            font-size: 0.82rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* ── Divider ──────────────────────────────────────────────────── */
        hr {{
            border-color: #2a2d3e;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Shared chart layout helper
# ---------------------------------------------------------------------------
def chart_layout(fig, title: str = "", height: int = 420):
    """Apply consistent dark layout to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(color=PRIMARY_GREEN, size=15)),
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color="#e8eaf0", family="Segoe UI, system-ui, sans-serif"),
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(
            bgcolor=CARD_BG,
            bordercolor="#2a2d3e",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(gridcolor="#2a2d3e", zerolinecolor="#2a2d3e")
    fig.update_yaxes(gridcolor="#2a2d3e", zerolinecolor="#2a2d3e")
    return fig

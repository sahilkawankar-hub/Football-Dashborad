"""
4_Data_Explorer.py — Searchable player statistics table with CSV download.

NOTE: All data is SYNTHETIC — not based on real players or real-world results.
"""

import streamlit as st
import pandas as pd

from utils import load_data, render_sidebar, apply_theme, POSITION_ORDER

st.set_page_config(
    page_title="Data Explorer | Football Analytics",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

df_full = load_data()
df = render_sidebar(df_full)

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("## 📋 Data Explorer")
st.markdown(
    "<span style='color:#f9c74f;font-size:13px;'>"
    "⚠ SYNTHETIC DATA — all statistics are artificially generated and do not "
    "represent real players or real-world results."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Search bar ─────────────────────────────────────────────────────────────
search = st.text_input(
    "Search by player name",
    placeholder="e.g. Carlos Silva",
    key="explorer_search",
)

df_display = df.copy()
if search.strip():
    df_display = df_display[
        df_display["player_name"].str.contains(search.strip(), case=False, na=False)
    ]

# ── Summary counts ─────────────────────────────────────────────────────────
col_a, col_b, col_c = st.columns(3)
col_a.metric("Rows shown", f"{len(df_display):,}")
col_b.metric("Players shown", f"{df_display['player_id'].nunique():,}")
col_c.metric("Teams shown", f"{df_display['team'].nunique():,}")

st.markdown("---")

# ── Column selector ────────────────────────────────────────────────────────
all_cols = list(df_display.columns)
default_cols = [
    "player_name", "season", "team", "position", "age",
    "matches_played", "goals", "assists", "rating",
]
selected_cols = st.multiselect(
    "Choose columns to display",
    options=all_cols,
    default=default_cols,
    key="col_selector",
)

if not selected_cols:
    st.info("Select at least one column above to display the table.")
    st.stop()

# ── Sort controls ──────────────────────────────────────────────────────────
sort_col = st.selectbox(
    "Sort by",
    options=selected_cols,
    index=selected_cols.index("rating") if "rating" in selected_cols else 0,
    key="sort_col",
)
sort_asc = st.checkbox("Ascending order", value=False, key="sort_asc")

df_display = df_display[selected_cols].sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)
df_display.index += 1

# ── Table ──────────────────────────────────────────────────────────────────
st.dataframe(df_display, use_container_width=True, height=480)

st.markdown("---")

# ── CSV Download ───────────────────────────────────────────────────────────
csv_bytes = df[list(df.columns)].to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data as CSV",
    data=csv_bytes,
    file_name="football_players_filtered.csv",
    mime="text/csv",
)

st.caption(
    f"Showing {len(df_display):,} of {len(df):,} filtered rows | "
    "Full filtered dataset is downloaded (all columns, current sidebar filters applied)."
)

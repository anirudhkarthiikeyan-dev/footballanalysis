import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.data import ADVANCED_STAT_SEASONS, PLAYER_SEASONS, load_players
from app.components.theme import divider, eyebrow, inject_theme, kpi_card
from src.analytics.player_stats import add_per90_columns, percentile_rank, player_season_history, top_performers
from src.ml.player_similarity import MIN_SEASON_FOR_SIMILARITY, find_similar_players

st.set_page_config(page_title="Player Explorer | PL Intelligence", layout="wide")
inject_theme()

eyebrow("Premier League · Player data 2019/20–2025/26")
st.title("Player Explorer")
st.caption("Coverage note: expected goals / expected assists are only available from 2022/23 onward — earlier seasons show goals, assists, minutes and cards only.")

players = load_players()
p90 = add_per90_columns(players)

tab_explore, tab_profile, tab_compare, tab_similar = st.tabs(
    ["Explorer", "Player Profile", "Compare", "Similarity"]
)

# ------------------------------------------------------------------ Explorer
with tab_explore:
    c1, c2, c3, c4 = st.columns(4)
    season = c1.selectbox("Season", options=list(reversed(PLAYER_SEASONS)), key="ex_season")
    position = c2.selectbox("Position", options=["All", "GK", "DEF", "MID", "FWD"], key="ex_pos")
    min_minutes = c3.slider("Minimum minutes", 0, 3000, 450, step=90, key="ex_min")
    metric = c4.selectbox(
        "Rank by",
        options=["goals_scored", "assists", "goals_per_90", "assists_per_90"]
        + (["xg_per_90", "xa_per_90"] if season in ADVANCED_STAT_SEASONS else []),
        key="ex_metric",
    )

    pos_filter = None if position == "All" else position
    result = top_performers(p90, season, metric, position=pos_filter, min_minutes=min_minutes, top_n=25)

    divider()
    cols = ["player_name", "team", "position", "minutes", "goals_scored", "assists", "goals_per_90", "assists_per_90"]
    if season in ADVANCED_STAT_SEASONS:
        cols += ["xg_per_90", "xa_per_90"]
    display = result[cols].round(2)
    display.columns = ["Player", "Team", "Pos", "Minutes", "Goals", "Assists", "Goals/90", "Assists/90"] + (
        ["xG/90", "xA/90"] if season in ADVANCED_STAT_SEASONS else []
    )
    st.dataframe(display, width='stretch', hide_index=True, height=560)

# ------------------------------------------------------------------- Profile
with tab_profile:
    all_names = sorted(players["player_name"].unique())
    requested_player = st.query_params.get("player")
    if requested_player in all_names:
        default_idx = all_names.index(requested_player)
    elif "Mohamed Salah" in all_names:
        default_idx = all_names.index("Mohamed Salah")
    else:
        default_idx = 0
    player = st.selectbox("Select a player", options=all_names, index=default_idx, key="profile_player")

    history = player_season_history(p90, player)
    if history.empty:
        st.info("No data for this player.")
    else:
        divider()
        latest = history.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        kpi_card("Seasons tracked", f"{len(history)}", c1)
        kpi_card("Career goals (tracked)", f"{int(history['goals_scored'].sum())}", c2)
        kpi_card("Career assists (tracked)", f"{int(history['assists'].sum())}", c3)
        kpi_card("Latest club", latest["team"], c4)

        divider()
        st.subheader("Season history")
        show_cols = ["season", "team", "position", "minutes", "goals_scored", "assists", "goals_per_90", "assists_per_90"]
        st.dataframe(history[show_cols].round(2), width='stretch', hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Goals & assists per season")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=history["season"], y=history["goals_scored"], name="Goals", marker_color="#22d3ee"))
            fig.add_trace(go.Bar(x=history["season"], y=history["assists"], name="Assists", marker_color="#8b5cf6"))
            fig.update_layout(barmode="group", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(0,0,0,0)", height=360, margin=dict(t=10, l=10, r=10, b=10),
                               legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, width='stretch')
        with c2:
            st.subheader("Per-90 output trend")
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=history["season"], y=history["goals_per_90"], name="Goals/90",
                                        line=dict(color="#22d3ee", width=2.5)))
            fig2.add_trace(go.Scatter(x=history["season"], y=history["assists_per_90"], name="Assists/90",
                                        line=dict(color="#8b5cf6", width=2.5)))
            fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                height=360, margin=dict(t=10, l=10, r=10, b=10), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig2, width='stretch')

        divider()
        st.subheader("Percentile profile (within season + position cohort, min. 450 minutes)")
        pctile_season = st.selectbox("Season for percentile view", options=list(reversed(history["season"].tolist())), key="pctile_season")
        pos_for_season = history[history["season"] == pctile_season].iloc[0]["position"]
        cohort = percentile_rank(p90, pctile_season, pos_for_season)
        row = cohort[cohort["player_name"] == player]
        if row.empty:
            st.caption("Not enough minutes in this season to compute a percentile (needs 450+ minutes).")
        else:
            metrics = [c for c in ["goals_per_90_pctile", "assists_per_90_pctile", "xg_per_90_pctile", "xa_per_90_pctile"] if c in row.columns and row.iloc[0][c] == row.iloc[0][c]]
            labels = [m.replace("_per_90_pctile", "").upper() for m in metrics]
            values = [row.iloc[0][m] for m in metrics]
            fig3 = go.Figure(go.Scatterpolar(r=values, theta=labels, fill="toself",
                                               line=dict(color="#22d3ee"), fillcolor="rgba(34,211,238,0.2)"))
            fig3.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                polar=dict(radialaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.1)")),
                                height=380, margin=dict(t=30, l=40, r=40, b=30))
            st.plotly_chart(fig3, width='stretch')

# ------------------------------------------------------------------- Compare
with tab_compare:
    all_names = sorted(players["player_name"].unique())
    c1, c2 = st.columns(2)
    p1 = c1.selectbox("Player A", options=all_names, key="cmp_p1",
                        index=all_names.index("Mohamed Salah") if "Mohamed Salah" in all_names else 0)
    p2 = c2.selectbox("Player B", options=all_names, key="cmp_p2",
                        index=all_names.index("Erling Haaland") if "Erling Haaland" in all_names else 1)
    season_cmp = st.selectbox("Season", options=list(reversed(PLAYER_SEASONS)), key="cmp_season")

    r1 = p90[(p90["player_name"] == p1) & (p90["season"] == season_cmp)]
    r2 = p90[(p90["player_name"] == p2) & (p90["season"] == season_cmp)]

    if r1.empty or r2.empty:
        st.info("One or both players have no record for that season.")
    else:
        r1, r2 = r1.iloc[0], r2.iloc[0]
        if r1["position"] != r2["position"]:
            st.warning(f"{p1} ({r1['position']}) and {p2} ({r2['position']}) play different positions — "
                       "per-90 output is still comparable, but role expectations differ (e.g. a defender's "
                       "goal output isn't judged the same way as a forward's).")

        divider()
        metrics = ["goals_per_90", "assists_per_90"]
        if season_cmp in ADVANCED_STAT_SEASONS:
            metrics += ["xg_per_90", "xa_per_90"]
        labels = [m.replace("_per_90", "").upper() + "/90" for m in metrics]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[r1[m] for m in metrics], theta=labels, fill="toself", name=p1,
                                        line=dict(color="#22d3ee"), fillcolor="rgba(34,211,238,0.18)"))
        fig.add_trace(go.Scatterpolar(r=[r2[m] for m in metrics], theta=labels, fill="toself", name=p2,
                                        line=dict(color="#8b5cf6"), fillcolor="rgba(139,92,246,0.18)"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=420,
                           legend=dict(orientation="h", y=1.1), margin=dict(t=30, l=40, r=40, b=30))
        st.plotly_chart(fig, width='stretch')

        table = pd.DataFrame({p1: [r1[m] for m in metrics], p2: [r2[m] for m in metrics]}, index=labels).round(2)
        st.dataframe(table, width='stretch')

# ------------------------------------------------------------------ Similarity
with tab_similar:
    st.caption(
        f"Similarity search runs on standardized per-90 output (goals, assists, xG, xA) using k-nearest "
        f"neighbors, restricted to seasons {MIN_SEASON_FOR_SIMILARITY}–2025/26 where all four features exist, "
        f"outfield players only, 450+ minutes. See Methodology for full detail."
    )
    all_names = sorted(players[players["position"] != "GK"]["player_name"].unique())
    sim_player = st.selectbox("Find players similar to", options=all_names,
                                index=all_names.index("Erling Haaland") if "Erling Haaland" in all_names else 0)
    sim_season = st.selectbox("Season", options=list(reversed(ADVANCED_STAT_SEASONS)), key="sim_season")
    same_pos = st.checkbox("Restrict to same position", value=True)

    divider()
    sims = find_similar_players(p90, sim_player, sim_season, same_position_only=same_pos, top_n=8)
    if sims.empty:
        st.info("No similarity result — the player may not meet the minutes threshold for this season, "
                "or not have played in it.")
    else:
        display = sims.round(2)
        display.columns = ["Player", "Team", "Pos", "Goals/90", "Assists/90", "xG/90", "xA/90", "Distance (lower = more similar)"]
        st.dataframe(display, width='stretch', hide_index=True)

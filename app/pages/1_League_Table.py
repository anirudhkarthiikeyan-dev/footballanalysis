import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.graph_objects as go
import streamlit as st

from app.components.data import all_seasons, load_matches
from app.components.theme import divider, eyebrow, inject_theme
from src.analytics.league_table import team_season_table

st.set_page_config(page_title="League Table | PL Intelligence", layout="wide")
inject_theme()

eyebrow("Premier League")
st.title("League Table")

matches = load_matches()
seasons_desc = list(reversed(all_seasons()))

requested_season = st.query_params.get("season")
default_idx = seasons_desc.index(requested_season) if requested_season in seasons_desc else 0

season = st.selectbox("Season", options=seasons_desc, index=default_idx)
table = team_season_table(matches, season)

divider()

display = table[[
    "position", "team", "played", "wins", "draws", "losses",
    "goals_for", "goals_against", "goal_difference", "points",
]].rename(columns={
    "position": "Pos", "team": "Team", "played": "P", "wins": "W", "draws": "D",
    "losses": "L", "goals_for": "GF", "goals_against": "GA",
    "goal_difference": "GD", "points": "Pts",
})


def zone(pos: int, n_teams: int) -> str:
    if pos <= 4:
        return "background-color: rgba(34,211,238,0.10)"
    if pos <= 6:
        return "background-color: rgba(139,92,246,0.08)"
    if pos > n_teams - 3:
        return "background-color: rgba(248,113,113,0.10)"
    return ""


n = len(display)
styled = display.style.apply(
    lambda row: [zone(row["Pos"], n)] * len(row), axis=1
).format({"Pts": "{:.0f}"})

st.dataframe(styled, width='stretch', hide_index=True, height=740)

st.caption("🔵 Champions League qualification · 🟣 Europa/Conference qualification · 🔴 Relegation zone — bands shown are the standard top-4 / 5-6 / bottom-3 convention, not each season's exact European allocation.")

divider()

c1, c2 = st.columns(2)
with c1:
    st.subheader("Points by position")
    fig = go.Figure(go.Bar(
        x=display["Team"], y=display["Pts"],
        marker=dict(color=display["Pts"], colorscale=[[0, "#16264a"], [1, "#22d3ee"]]),
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=420, xaxis_tickangle=-45, margin=dict(t=10, l=10, r=10, b=10),
    )
    st.plotly_chart(fig, width='stretch')

with c2:
    st.subheader("Goal difference")
    colors = ["#34d399" if v >= 0 else "#f87171" for v in display["GD"]]
    fig2 = go.Figure(go.Bar(x=display["Team"], y=display["GD"], marker_color=colors))
    fig2.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=420, xaxis_tickangle=-45, margin=dict(t=10, l=10, r=10, b=10),
    )
    st.plotly_chart(fig2, width='stretch')

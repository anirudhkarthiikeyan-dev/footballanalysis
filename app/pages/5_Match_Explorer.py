import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.components.data import all_seasons, all_teams, load_matches
from app.components.theme import divider, eyebrow, inject_theme

st.set_page_config(page_title="Match Explorer | PL Intelligence", layout="wide")
inject_theme()

eyebrow("Premier League")
st.title("Match Explorer")
st.caption("Filter and browse every match in the dataset.")

matches = load_matches()
seasons = all_seasons()
teams = all_teams()

divider()
c1, c2, c3, c4 = st.columns(4)
season_filter = c1.multiselect("Season", options=list(reversed(seasons)))
team_filter = c2.multiselect("Team (home or away)", options=teams)
result_filter = c3.multiselect("Result", options=["Home win", "Draw", "Away win"])
min_goals = c4.slider("Minimum total goals", 0, 10, 0)

df = matches.copy()
if season_filter:
    df = df[df["season"].isin(season_filter)]
if team_filter:
    df = df[df["home_team"].isin(team_filter) | df["away_team"].isin(team_filter)]
if result_filter:
    code_map = {"Home win": "H", "Draw": "D", "Away win": "A"}
    df = df[df["result"].isin([code_map[r] for r in result_filter])]
if min_goals > 0:
    df = df[(df["home_goals"] + df["away_goals"]) >= min_goals]

st.caption(f"{len(df):,} matches match your filters (out of {len(matches):,} total).")

divider()

display = df[[
    "match_date", "season", "home_team", "home_goals", "away_goals", "away_team",
    "referee", "home_shots", "away_shots", "home_corners", "away_corners",
]].sort_values("match_date", ascending=False).copy()
display["match_date"] = display["match_date"].dt.strftime("%Y-%m-%d")
display.columns = ["Date", "Season", "Home", "HG", "AG", "Away", "Referee", "H.Shots", "A.Shots", "H.Corners", "A.Corners"]

st.dataframe(display, width='stretch', hide_index=True, height=560)

csv = display.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered matches (CSV)", csv, "pl_matches_filtered.csv", "text/csv")

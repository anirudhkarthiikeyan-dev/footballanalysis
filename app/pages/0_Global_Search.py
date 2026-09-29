import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.components.data import all_seasons, all_teams, load_players
from app.components.theme import divider, eyebrow, inject_theme
from src.cleaning.clean_european import SELECTED_CLUBS

st.set_page_config(page_title="Search | GAMESTATE", layout="wide")
inject_theme()

eyebrow("Find anything in GAMESTATE")
st.title("Global Search")
st.caption("Search across teams, clubs, players and seasons — click a result to jump straight to its page.")

divider()

pl_teams = all_teams()
european_only_clubs = sorted(SELECTED_CLUBS - set(pl_teams))
seasons = sorted(all_seasons(), reverse=True)

players_df = load_players()
latest_player_rows = (
    players_df.sort_values("season")
    .groupby("player_name", as_index=False)
    .last()[["player_name", "team", "position", "season"]]
)

query = st.text_input("Search", placeholder="Try \"Arsenal\", \"Haaland\", \"2015/16\", \"Real Madrid\"...", label_visibility="collapsed")

if not query or len(query.strip()) < 2:
    st.info("Type at least 2 characters to search.")
    st.stop()

q = query.strip().lower()

team_matches = [t for t in pl_teams if q in t.lower()]
club_matches = [c for c in european_only_clubs if q in c.lower()]
season_matches = [s for s in seasons if q in s.lower()]
player_matches = latest_player_rows[latest_player_rows["player_name"].str.lower().str.contains(q, na=False)]

total_results = len(team_matches) + len(club_matches) + len(season_matches) + len(player_matches)
st.caption(f"{total_results} result{'s' if total_results != 1 else ''} for \"{query}\"")
divider()

if team_matches:
    st.subheader(f"Teams — Premier League ({len(team_matches)})", anchor=False)
    for team in team_matches[:15]:
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"**{team}**")
        if c2.button("View →", key=f"team_{team}"):
            st.switch_page("pages/3_Team_Explorer.py", query_params={"team": team})
    divider()

if club_matches:
    st.subheader(f"Clubs — European Performance", anchor=False)
    for club in club_matches[:15]:
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"**{club}**")
        if c2.button("View →", key=f"club_{club}"):
            st.switch_page("pages/9_European_Performance.py", query_params={"club": club})
    divider()

if not player_matches.empty:
    st.subheader(f"Players", anchor=False)
    for _, row in player_matches.head(15).iterrows():
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"**{row['player_name']}** — {row['team']} · {row['position']} · last seen {row['season']}")
        if c2.button("View →", key=f"player_{row['player_name']}"):
            st.switch_page("pages/6_Player_Explorer.py", query_params={"player": row["player_name"]})
    divider()

if season_matches:
    st.subheader(f"Seasons", anchor=False)
    for season in season_matches[:10]:
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"**{season}**")
        if c2.button("View →", key=f"season_{season}"):
            st.switch_page("pages/1_League_Table.py", query_params={"season": season})
    divider()

if total_results == 0:
    st.warning(f'No teams, clubs, players or seasons found matching "{query}".')

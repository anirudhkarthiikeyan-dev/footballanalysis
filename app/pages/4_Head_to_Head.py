import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.graph_objects as go
import streamlit as st

from app.components.data import all_teams, load_matches
from app.components.theme import divider, eyebrow, inject_theme, kpi_card
from src.analytics.head_to_head import h2h_matches, h2h_summary, most_frequent_opponents

st.set_page_config(page_title="Head-to-Head | GAMESTATE", layout="wide")
inject_theme()

eyebrow("Premier League")
st.title("Head-to-Head")

matches = load_matches()
teams = all_teams()

c1, c2 = st.columns(2)
team_a = c1.selectbox("Team A", options=teams, index=teams.index("Arsenal") if "Arsenal" in teams else 0)
default_b = "Tottenham Hotspur" if "Tottenham Hotspur" in teams else (teams[1] if teams[0] == team_a else teams[0])
team_b = c2.selectbox("Team B", options=[t for t in teams], index=teams.index(default_b) if default_b in teams else 1)

if team_a == team_b:
    st.warning("Select two different teams.")
    st.stop()

summary = h2h_summary(matches, team_a, team_b)

if summary["meetings"] == 0:
    st.info(f"{team_a} and {team_b} have not met in the Premier League within this dataset's coverage (2012/13–2025/26).")
    st.stop()

divider()
st.subheader(f"{team_a} vs {team_b} — all-time record in this dataset")

c1, c2, c3, c4 = st.columns(4)
kpi_card("Meetings", f"{summary['meetings']}", c1)
kpi_card(f"{team_a} wins", f"{summary[f'{team_a}_wins']} ({summary[f'{team_a}_win_pct']}%)", c2)
kpi_card("Draws", f"{summary['draws']} ({summary['draw_pct']}%)", c3)
kpi_card(f"{team_b} wins", f"{summary[f'{team_b}_wins']} ({summary[f'{team_b}_win_pct']}%)", c4)

divider()

c1, c2 = st.columns([1, 1.4])
with c1:
    st.subheader("Result distribution")
    fig = go.Figure(go.Pie(
        labels=[f"{team_a} win", "Draw", f"{team_b} win"],
        values=[summary[f"{team_a}_wins"], summary["draws"], summary[f"{team_b}_wins"]],
        marker=dict(colors=["#22d3ee", "#8b96ad", "#8b5cf6"]),
        hole=0.55,
    ))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=340,
                       margin=dict(t=10, l=10, r=10, b=10), showlegend=True, legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig, width='stretch')

with c2:
    st.subheader("Goals timeline")
    games = h2h_matches(matches, team_a, team_b)
    a_goals = games.apply(lambda r: r["home_goals"] if r["home_team"] == team_a else r["away_goals"], axis=1)
    b_goals = games.apply(lambda r: r["home_goals"] if r["home_team"] == team_b else r["away_goals"], axis=1)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=games["match_date"], y=a_goals, name=team_a, mode="lines+markers",
                                line=dict(color="#22d3ee")))
    fig2.add_trace(go.Scatter(x=games["match_date"], y=b_goals, name=team_b, mode="lines+markers",
                                line=dict(color="#8b5cf6")))
    fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        height=340, margin=dict(t=10, l=10, r=10, b=10), legend=dict(orientation="h", y=1.1),
                        yaxis_title="Goals scored")
    st.plotly_chart(fig2, width='stretch')

divider()
st.subheader("Home / away record")
c1, c2 = st.columns(2)
for col, team, key in [(c1, team_a, f"{team_a}_home_record"), (c2, team_b, f"{team_b}_home_record")]:
    d = summary[key]
    col.markdown(
        f"""<div class="pli-card"><b>{team} at home</b><br/>
        Played {d['played']} · W{d['wins']} D{d['draws']} L{d['losses']}
        </div>""",
        unsafe_allow_html=True,
    )

divider()
st.subheader("Records")
biggest = games[games["match_id"] == summary["biggest_win_match_id"]].iloc[0]
highest = games[games["match_id"] == summary["highest_scoring_match_id"]].iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Biggest margin", f"{biggest['home_team']} {int(biggest['home_goals'])}-{int(biggest['away_goals'])} {biggest['away_team']}",
           help=str(biggest["match_date"].date()))
c2.metric("Highest scoring meeting", f"{highest['home_team']} {int(highest['home_goals'])}-{int(highest['away_goals'])} {highest['away_team']}",
           help=str(highest["match_date"].date()))
c3.metric("Avg goals per meeting", summary["avg_goals_per_match"])

divider()
st.subheader("Last 10 meetings")
last10 = summary["last_10"][["match_date", "season", "home_team", "home_goals", "away_goals", "away_team"]].copy()
last10 = last10.sort_values("match_date", ascending=False)
last10["match_date"] = last10["match_date"].dt.strftime("%Y-%m-%d")
last10.columns = ["Date", "Season", "Home", "HG", "AG", "Away"]
st.dataframe(last10, width='stretch', hide_index=True)

divider()
st.subheader("Full historical meetings")
full = games[["match_date", "season", "home_team", "home_goals", "away_goals", "away_team", "referee"]].copy()
full = full.sort_values("match_date", ascending=False)
full["match_date"] = full["match_date"].dt.strftime("%Y-%m-%d")
full.columns = ["Date", "Season", "Home", "HG", "AG", "Away", "Referee"]
st.dataframe(full, width='stretch', hide_index=True, height=320)

divider()
st.subheader(f"{team_a}'s most frequent opponents")
freq = most_frequent_opponents(matches, team_a, top_n=10)
fig3 = go.Figure(go.Bar(x=freq["opponent"], y=freq["meetings"], marker_color="#22d3ee"))
fig3.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    height=340, margin=dict(t=10, l=10, r=10, b=10), xaxis_tickangle=-45)
st.plotly_chart(fig3, width='stretch')
st.caption("This ranks opponents by how often they've actually met — no rivalry is assumed or labeled that isn't backed by the data.")

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.graph_objects as go
import streamlit as st

from app.components.data import all_teams, load_matches
from app.components.theme import divider, eyebrow, inject_theme, kpi_card
from src.analytics.team_stats import home_away_split, team_season_journey

st.set_page_config(page_title="Team Explorer | GAMESTATE", layout="wide")
inject_theme()

eyebrow("Premier League")
st.title("Team Explorer")

matches = load_matches()
teams = all_teams()

tab_profile, tab_compare = st.tabs(["Team Profile", "Team Comparison"])

with tab_profile:
    requested_team = st.query_params.get("team")
    default_team = requested_team if requested_team in teams else ("Arsenal" if "Arsenal" in teams else teams[0])
    team = st.selectbox("Select a team", options=teams, index=teams.index(default_team))
    journey = team_season_journey(matches, team)

    if journey.empty:
        st.info("No data for this team in the dataset.")
    else:
        divider()
        latest = journey.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        kpi_card("Seasons in dataset", f"{len(journey)}", c1)
        kpi_card("Best finish", f"P{journey['position'].min()}", c2)
        kpi_card("Total points won", f"{int(journey['points'].sum()):,}", c3)
        kpi_card("Latest season position", f"P{int(latest['position'])}", c4)

        divider()
        st.subheader(f"{team} — season journey")
        fig = go.Figure(go.Scatter(
            x=journey["season"], y=journey["position"], mode="lines+markers",
            line=dict(color="#22d3ee", width=3), marker=dict(size=8, color="#3b82f6"),
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed", title="League position", dtick=2),
            height=380, margin=dict(t=10, l=10, r=10, b=10),
        )
        st.plotly_chart(fig, width='stretch')

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Points per season")
            fig2 = go.Figure(go.Bar(x=journey["season"], y=journey["points"], marker_color="#22d3ee"))
            fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                height=340, margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig2, width='stretch')
        with c2:
            st.subheader("Goals for vs against")
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=journey["season"], y=journey["goals_for"], name="For", marker_color="#34d399"))
            fig3.add_trace(go.Bar(x=journey["season"], y=journey["goals_against"], name="Against", marker_color="#f87171"))
            fig3.update_layout(barmode="group", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)", height=340, margin=dict(t=10, l=10, r=10, b=10),
                                legend=dict(orientation="h", y=1.12))
            st.plotly_chart(fig3, width='stretch')

        divider()
        st.subheader("Home vs away record")
        season_pick = st.selectbox("Season", options=list(reversed(journey["season"].tolist())), key="ha_season")
        split = home_away_split(matches, team, season=season_pick)
        c1, c2 = st.columns(2)
        for col, side in [(c1, "home"), (c2, "away")]:
            d = split[side]
            col.markdown(
                f"""<div class="pli-card">
                <b>{side.title()}</b><br/>
                Played {d['played']} · W{d['wins']} D{d['draws']} L{d['losses']}<br/>
                Goals: {d['goals_for']} for, {d['goals_against']} against
                </div>""",
                unsafe_allow_html=True,
            )

        divider()
        with st.expander("Full season-by-season record"):
            st.dataframe(journey, width='stretch', hide_index=True)

with tab_compare:
    c1, c2 = st.columns(2)
    team_a = c1.selectbox("Team A", options=teams, index=teams.index("Arsenal") if "Arsenal" in teams else 0, key="cmp_a")
    team_b = c2.selectbox("Team B", options=teams, index=teams.index("Chelsea") if "Chelsea" in teams else 1, key="cmp_b")

    ja = team_season_journey(matches, team_a)
    jb = team_season_journey(matches, team_b)

    if ja.empty or jb.empty:
        st.info("Not enough data for one of the selected teams.")
    else:
        divider()
        st.subheader("League position over time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ja["season"], y=ja["position"], name=team_a, line=dict(color="#22d3ee", width=3)))
        fig.add_trace(go.Scatter(x=jb["season"], y=jb["position"], name=team_b, line=dict(color="#8b5cf6", width=3)))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed", title="League position"), height=400,
            margin=dict(t=10, l=10, r=10, b=10), legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig, width='stretch')

        c1, c2, c3 = st.columns(3)
        c1.metric(f"{team_a} total points", int(ja["points"].sum()))
        c2.metric(f"{team_b} total points", int(jb["points"].sum()))
        c3.metric("Seasons compared", f"{ja['season'].nunique()} / {jb['season'].nunique()}")

        merged = ja[["season", "position", "points", "goals_for", "goals_against"]].merge(
            jb[["season", "position", "points", "goals_for", "goals_against"]],
            on="season", suffixes=(f"_{team_a}", f"_{team_b}"),
        )
        with st.expander("Season-by-season comparison table"):
            st.dataframe(merged, width='stretch', hide_index=True)

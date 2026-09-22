import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.theme import divider, eyebrow, inject_theme, kpi_card
from src.analytics.european import (
    STAGE_LABELS,
    club_best_finish,
    club_matches,
    club_season_campaigns,
    domestic_vs_europe,
    european_h2h,
    opponent_history,
)
from src.analytics.league_table import all_seasons_team_table
from src.cleaning.clean_european import CLUB_COUNTRY, SELECTED_CLUBS

st.set_page_config(page_title="European Performance | PL Intelligence", layout="wide")
inject_theme()

eyebrow("UEFA Champions League · 20 selected clubs · 2012/13–2025/26")
st.title("European Performance")
st.caption(
    "A secondary module comparing 20 major European clubs' Champions League record. "
    "The Premier League remains the core product — see Methodology for scope and sourcing."
)


@st.cache_data(show_spinner=False)
def load_eu_matches():
    return pd.read_csv(ROOT / "data" / "processed" / "european_matches_clean.csv", parse_dates=["match_date"])


@st.cache_data(show_spinner=False)
def load_pl_matches():
    return pd.read_csv(ROOT / "data" / "processed" / "matches_clean.csv", parse_dates=["match_date"])


@st.cache_data(show_spinner=False)
def load_campaigns(eu_matches):
    return club_season_campaigns(eu_matches)


eu_matches = load_eu_matches()
pl_matches = load_pl_matches()
campaigns = load_campaigns(eu_matches)
clubs = sorted(SELECTED_CLUBS)

tab_profile, tab_compare, tab_h2h, tab_domestic = st.tabs(
    ["Club Profile", "Comparison", "European H2H", "Domestic vs Europe"]
)

# ------------------------------------------------------------------ Club Profile
with tab_profile:
    club = st.selectbox("Select a club", options=clubs, index=clubs.index("Real Madrid") if "Real Madrid" in clubs else 0)
    club_campaigns = campaigns[campaigns["club"] == club].sort_values("season")

    if club_campaigns.empty:
        st.info(f"{club} has no Champions League campaigns in this dataset's coverage (2012/13–2025/26).")
    else:
        divider()
        best = club_best_finish(campaigns, club)
        c1, c2, c3, c4 = st.columns(4)
        kpi_card("Campaigns played", f"{len(club_campaigns)}", c1)
        kpi_card("Best finish", f"{best['finish_label']} ({best['season']})", c2)
        kpi_card("Total matches", f"{int(club_campaigns['matches_played'].sum())}", c3)
        career_win_pct = round(100 * club_campaigns["wins"].sum() / club_campaigns["matches_played"].sum(), 1)
        kpi_card("Career win %", f"{career_win_pct}%", c4)

        st.caption(
            f"Country: {CLUB_COUNTRY[club]} · Participation seasons shown are the club's actual "
            "qualification history — no season is shown unless they played in it."
        )

        divider()
        st.subheader("Campaign-by-campaign journey")
        fig = go.Figure(go.Scatter(
            x=club_campaigns["season"], y=club_campaigns["finish_rank"], mode="lines+markers",
            line=dict(color="#22d3ee", width=3), marker=dict(size=9, color="#3b82f6"),
            text=club_campaigns["finish_label"], hovertemplate="%{x}: %{text}<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=380, margin=dict(t=10, l=10, r=10, b=10),
            yaxis=dict(
                tickmode="array", tickvals=list(STAGE_LABELS.keys()), ticktext=list(STAGE_LABELS.values()),
                title="Stage reached",
            ),
        )
        st.plotly_chart(fig, width='stretch')
        st.caption(
            "Only the seasons this club actually qualified for are plotted — gaps in the x-axis are "
            "real qualification gaps, not missing data."
        )

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Goals for vs against, per campaign")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=club_campaigns["season"], y=club_campaigns["goals_for"], name="For", marker_color="#34d399"))
            fig2.add_trace(go.Bar(x=club_campaigns["season"], y=club_campaigns["goals_against"], name="Against", marker_color="#f87171"))
            fig2.update_layout(barmode="group", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)", height=340, margin=dict(t=10, l=10, r=10, b=10),
                                legend=dict(orientation="h", y=1.12))
            st.plotly_chart(fig2, width='stretch')
        with c2:
            st.subheader("Win % per campaign")
            fig3 = go.Figure(go.Bar(x=club_campaigns["season"], y=club_campaigns["win_pct"], marker_color="#22d3ee"))
            fig3.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                height=340, margin=dict(t=10, l=10, r=10, b=10), yaxis_title="Win %")
            st.plotly_chart(fig3, width='stretch')

        divider()
        st.subheader("Campaign-by-campaign record")
        display = club_campaigns[[
            "season", "matches_played", "wins", "draws", "losses",
            "goals_for", "goals_against", "goal_difference", "finish_label",
        ]].rename(columns={
            "season": "Season", "matches_played": "P", "wins": "W", "draws": "D", "losses": "L",
            "goals_for": "GF", "goals_against": "GA", "goal_difference": "GD", "finish_label": "Finish",
        })
        st.dataframe(display, width='stretch', hide_index=True)

        divider()
        st.subheader("Opponent history")
        opp_hist = opponent_history(eu_matches, club, top_n=15)
        opp_hist.columns = ["Opponent", "Meetings", "W", "D", "L", "GF", "GA"]
        st.dataframe(opp_hist, width='stretch', hide_index=True)
        st.caption("Ranked by number of meetings — no pairing here is labeled a \"rivalry\" unless the data itself shows a frequent history.")

# ------------------------------------------------------------------ Comparison
with tab_compare:
    selected = st.multiselect("Select clubs to compare (2-4)", options=clubs, default=["Real Madrid", "Manchester City"][:2])
    if len(selected) < 2:
        st.info("Select at least 2 clubs.")
    else:
        divider()
        rows = []
        for c in selected[:4]:
            cc = campaigns[campaigns["club"] == c]
            if cc.empty:
                continue
            best = club_best_finish(campaigns, c)
            rows.append({
                "Club": c, "Campaigns": len(cc), "Best finish": best["finish_label"],
                "Total matches": int(cc["matches_played"].sum()),
                "Win %": round(100 * cc["wins"].sum() / cc["matches_played"].sum(), 1),
                "Goals/match": round(cc["goals_for"].sum() / cc["matches_played"].sum(), 2),
            })
        summary = pd.DataFrame(rows)
        st.dataframe(summary, width='stretch', hide_index=True)

        st.subheader("Stage reached, by season")
        fig = go.Figure()
        colors = ["#22d3ee", "#8b5cf6", "#34d399", "#fbbf24"]
        for i, c in enumerate(selected[:4]):
            cc = campaigns[campaigns["club"] == c].sort_values("season")
            fig.add_trace(go.Scatter(x=cc["season"], y=cc["finish_rank"], name=c, mode="lines+markers",
                                       line=dict(color=colors[i % len(colors)], width=2.5)))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420,
            yaxis=dict(tickmode="array", tickvals=list(STAGE_LABELS.keys()), ticktext=list(STAGE_LABELS.values())),
            legend=dict(orientation="h", y=1.1), margin=dict(t=10, l=10, r=10, b=10),
        )
        st.plotly_chart(fig, width='stretch')

# ------------------------------------------------------------------ European H2H
with tab_h2h:
    c1, c2 = st.columns(2)
    club_a = c1.selectbox("Club A", options=clubs, index=clubs.index("Real Madrid") if "Real Madrid" in clubs else 0, key="eu_h2h_a")
    default_b = "Bayern Munich" if "Bayern Munich" in clubs else clubs[1]
    club_b = c2.selectbox("Club B", options=clubs, index=clubs.index(default_b), key="eu_h2h_b")

    if club_a == club_b:
        st.warning("Select two different clubs.")
    else:
        games = european_h2h(eu_matches, club_a, club_b)
        if games.empty:
            st.info(f"{club_a} and {club_b} have not met in the Champions League within this dataset's coverage.")
        else:
            divider()

            def winner_of(row):
                if row["decided_by_penalties"]:
                    return row["home_team"] if row["penalty_home_goals"] > row["penalty_away_goals"] else row["away_team"]
                if row["home_goals"] > row["away_goals"]:
                    return row["home_team"]
                if row["home_goals"] < row["away_goals"]:
                    return row["away_team"]
                return None
            games = games.copy()
            games["winner"] = games.apply(winner_of, axis=1)
            a_wins = int((games["winner"] == club_a).sum())
            b_wins = int((games["winner"] == club_b).sum())
            draws = len(games) - a_wins - b_wins

            c1, c2, c3, c4 = st.columns(4)
            kpi_card("Meetings", f"{len(games)}", c1)
            kpi_card(f"{club_a} wins", f"{a_wins}", c2)
            kpi_card("Draws", f"{draws}", c3)
            kpi_card(f"{club_b} wins", f"{b_wins}", c4)

            divider()
            st.subheader("All meetings")
            hist = games[["match_date", "season", "stage", "home_team", "home_goals", "away_goals", "away_team", "decided_by_penalties"]].copy()
            hist = hist.sort_values("match_date", ascending=False)
            hist["match_date"] = hist["match_date"].dt.strftime("%Y-%m-%d")
            hist["stage"] = hist["stage"].map(lambda s: s.replace("_", " ").title())
            hist.columns = ["Date", "Season", "Stage", "Home", "HG", "AG", "Away", "Pens"]
            st.dataframe(hist, width='stretch', hide_index=True)

# ------------------------------------------------------------------ Domestic vs Europe
with tab_domestic:
    pl_clubs = sorted(SELECTED_CLUBS & set(pl_matches["home_team"].unique()))
    st.caption("Only the 9 English clubs in the European module have Premier League data to compare against.")
    club = st.selectbox("Select an English club", options=pl_clubs, key="dve_club")

    pl_table = all_seasons_team_table(pl_matches)
    comparison = domestic_vs_europe(pl_table, campaigns, club)

    if comparison["europe"] is None:
        st.info(f"{club} has no Champions League campaigns in this dataset's coverage.")
    else:
        divider()
        st.warning(
            "The Premier League (38 balanced matches/season) and the Champions League (a campaign that "
            "can end after 6-13 matches) have very different structures — this is a side-by-side "
            "comparison, not a claim the two are equivalent."
        )
        d, e = comparison["domestic"], comparison["europe"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="pli-card"><b>Premier League</b><br/>
            {d['seasons']} seasons · {d['played']} matches<br/>
            Win %: {d['win_pct']}%<br/>
            Goals/match: {d['goals_per_match']} for, {d['goals_against_per_match']} against
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="pli-card"><b>Champions League</b><br/>
            {e['seasons']} campaigns · {e['played']} matches<br/>
            Win %: {e['win_pct']}%<br/>
            Goals/match: {e['goals_per_match']} for, {e['goals_against_per_match']} against
            </div>""", unsafe_allow_html=True)

        divider()
        fig = go.Figure(go.Bar(
            x=["Premier League", "Champions League"], y=[d["win_pct"], e["win_pct"]],
            marker_color=["#22d3ee", "#8b5cf6"],
        ))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           height=340, margin=dict(t=10, l=10, r=10, b=10), yaxis_title="Win %")
        st.plotly_chart(fig, width='stretch')

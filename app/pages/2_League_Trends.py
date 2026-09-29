import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.graph_objects as go
import streamlit as st

from app.components.data import load_matches
from app.components.theme import divider, eyebrow, inject_theme
from src.analytics.team_stats import league_goals_trend

st.set_page_config(page_title="League Trends | GAMESTATE", layout="wide")
inject_theme()

eyebrow("Premier League · 2012/13 – 2025/26")
st.title("League Trends")
st.caption("How scoring, home advantage and results have shifted across 14 seasons.")

matches = load_matches()
trend = league_goals_trend(matches)

divider()

c1, c2, c3 = st.columns(3)
c1.metric("Goals/match, 2012/13", trend.iloc[0]["goals_per_match"])
c2.metric("Goals/match, latest season", trend.iloc[-1]["goals_per_match"],
           delta=round(trend.iloc[-1]["goals_per_match"] - trend.iloc[0]["goals_per_match"], 2))
c3.metric("Home win % change", f"{trend.iloc[-1]['home_win_pct']}%",
           delta=round(trend.iloc[-1]["home_win_pct"] - trend.iloc[0]["home_win_pct"], 1))

divider()

st.subheader("Goals per match, by season")
fig = go.Figure(go.Scatter(
    x=trend["season"], y=trend["goals_per_match"], mode="lines+markers",
    line=dict(color="#22d3ee", width=3), marker=dict(size=7, color="#3b82f6"),
    fill="tozeroy", fillcolor="rgba(34,211,238,0.08)",
))
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                   height=380, margin=dict(t=10, l=10, r=10, b=10), yaxis_title="Goals / match")
st.plotly_chart(fig, width='stretch')

st.subheader("Result mix: home win / draw / away win %")
fig2 = go.Figure()
fig2.add_trace(go.Bar(x=trend["season"], y=trend["home_win_pct"], name="Home win", marker_color="#22d3ee"))
fig2.add_trace(go.Bar(x=trend["season"], y=trend["draw_pct"], name="Draw", marker_color="#8b96ad"))
fig2.add_trace(go.Bar(x=trend["season"], y=trend["away_win_pct"], name="Away win", marker_color="#8b5cf6"))
fig2.update_layout(
    barmode="stack", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    height=420, margin=dict(t=10, l=10, r=10, b=10), legend=dict(orientation="h", y=1.08),
)
st.plotly_chart(fig2, width='stretch')

c1, c2 = st.columns(2)
with c1:
    st.subheader("Home vs away goals per match")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=trend["season"], y=trend["avg_home_goals"], name="Home goals",
                                line=dict(color="#22d3ee", width=2.5)))
    fig3.add_trace(go.Scatter(x=trend["season"], y=trend["avg_away_goals"], name="Away goals",
                                line=dict(color="#8b5cf6", width=2.5)))
    fig3.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        height=360, margin=dict(t=10, l=10, r=10, b=10), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig3, width='stretch')

with c2:
    st.subheader("Total goals per season")
    fig4 = go.Figure(go.Bar(x=trend["season"], y=trend["total_goals"], marker_color="#3b82f6"))
    fig4.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        height=360, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig4, width='stretch')

divider()
with st.expander("View underlying season-by-season numbers"):
    st.dataframe(trend, width='stretch', hide_index=True)

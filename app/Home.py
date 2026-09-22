import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.components.data import load_matches, load_players
from app.components.intro import render_intro
from app.components.theme import badge, divider, eyebrow, inject_theme, kpi_card

st.set_page_config(
    page_title="PL Intelligence",
    page_icon="assets/icons/favicon.svg" if (ROOT / "assets" / "icons" / "favicon.svg").exists() else "🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

if "intro_seen" not in st.session_state:
    st.session_state.intro_seen = False

if not st.session_state.intro_seen:
    render_intro(height=560)
    c1, c2, c3 = st.columns([3, 1, 1])
    with c2:
        if st.button("ENTER", width='stretch', type="primary"):
            st.session_state.intro_seen = True
            st.rerun()
    with c3:
        if st.button("Skip Intro", width='stretch'):
            st.session_state.intro_seen = True
            st.rerun()
    st.stop()

# ---------------------------------------------------------------- Home page
matches = load_matches()
players = load_players()

eyebrow("Premier League Football Analytics")
st.title("PL INTELLIGENCE")
st.caption("Data Drives A Deeper Game — an end-to-end analytics product covering the Premier League, 2012/13–2025/26.")

divider()

c1, c2, c3, c4 = st.columns(4)
kpi_card("Seasons covered", f"{matches['season'].nunique()}", c1)
kpi_card("Matches analyzed", f"{len(matches):,}", c2)
kpi_card("Clubs in dataset", f"{matches['home_team'].nunique()}", c3)
kpi_card("Player-seasons tracked", f"{len(players):,}", c4)

divider()

left, right = st.columns([1.3, 1])

with left:
    st.subheader("What's inside")
    st.markdown(
        """
- **Global Search** — find any team, club, player or season and jump straight to its page
- **League Table** — final standings for any season, 2012/13–2025/26
- **League Trends** — goals, home advantage and result mix over 14 seasons
- **Team Explorer** — season-by-season journey, home/away splits, comparisons
- **Head-to-Head** — full engine: overall record, recent form, biggest results, historical timeline
- **Match Explorer** — filter and browse all 5,320 matches in the dataset
- **Player Explorer** — per-90 stats and position-scoped percentiles, 2019/20–2025/26
- **European Performance** — Champions League record for 20 major European clubs, 2012/13–2025/26
- **Methodology** — how the numbers are built, and what isn't included and why
"""
    )
    st.markdown(
        f'{badge("14 seasons")} {badge("5,320 matches")} {badge("37 PL clubs")} '
        f'{badge("1,603 players")} {badge("20 European clubs")}',
        unsafe_allow_html=True,
    )

with right:
    st.subheader("Coverage at a glance")
    st.markdown(
        """
<div class="pli-card">
<b>Match data</b><br/>2012/13 – 2025/26, all 14 seasons<br/><br/>
<b>Player data</b><br/>2019/20 – 2025/26 (7 seasons)<br/><br/>
<b>Expected goals / assists</b><br/>2022/23 – 2025/26 only<br/><br/>
<b>European data (Champions League)</b><br/>20 clubs, actual participation seasons only<br/><br/>
<span style="color:#8b96ad;font-size:0.85rem;">Coverage gaps are real source limitations,
documented in Methodology — not filled with invented numbers.</span>
</div>
""",
        unsafe_allow_html=True,
    )

divider()
st.markdown(
    '<div class="pli-footer">PL INTELLIGENCE is an independent analytics project. '
    "Not affiliated with, endorsed by, or sponsored by the Premier League, its clubs, or any official competition body. "
    "All data sourced from public datasets — see Methodology for full sourcing.</div>",
    unsafe_allow_html=True,
)

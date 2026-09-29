import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from app.components.data import load_matches, load_players
from app.components.home import HOME_CSS, LAB_MODULES, lab_module, section_heading, stat_cards
from app.components.intro import render_intro
from app.components.theme import inject_theme
from src.analytics.european import club_season_campaigns
from src.cleaning.clean_european import SELECTED_CLUBS

st.set_page_config(
    page_title="GAMESTATE",
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


@st.cache_data(show_spinner=False)
def european_totals() -> tuple[int, int]:
    eu = pd.read_csv(ROOT / "data" / "processed" / "european_matches_clean.csv", parse_dates=["match_date"])
    return len(eu), len(club_season_campaigns(eu))


# ---------------------------------------------------------------- Home page
st.markdown(HOME_CSS, unsafe_allow_html=True)
matches = load_matches()
players = load_players()
seasons = sorted(matches["season"].unique())
coverage = f"{seasons[0]} — {seasons[-1]}"

with st.container(key="gs_hero"):
    st.markdown(
        '<div class="gs-hero-copy">'
        '<div class="gs-hero-eyebrow">Premier League &amp; European Football Analytics</div>'
        '<div class="gs-hero-title">GAMESTATE</div>'
        '<div class="gs-hero-tagline">UNDERSTAND THE GAME<br/>THROUGH DATA</div>'
        f'<div class="gs-hero-meta"><i></i><b>{coverage}</b><span>· {len(seasons)} seasons</span></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.container(key="gs_cta", horizontal=True):
        with st.container(key="gs_cta_primary", width="content"):
            st.page_link("pages/1_League_Table.py", label="EXPLORE THE GAME →")
        with st.container(key="gs_cta_secondary", width="content"):
            st.page_link("pages/0_Global_Search.py", label="SEARCH →")

section_heading("Data at a glance")
stat_cards([
    (f"{len(seasons)}", "SEASONS", coverage),
    (f"{len(matches):,}", "MATCHES", "Every Premier League fixture"),
    (f"{matches['home_team'].nunique()}", "CLUBS", "Premier League sides in range"),
    (f"{len(players):,}", "PLAYER-SEASONS", f"{players['season'].min()} — {players['season'].max()}"),
])

section_heading("Analytics modules", "THE GAMESTATE LAB", "Explore the layers behind the game.")
for row in (LAB_MODULES[:3], LAB_MODULES[3:]):
    cols = st.columns(3, gap="medium")
    for col, module in zip(cols, row):
        with col:
            lab_module(LAB_MODULES.index(module), *module)

eu_matches, eu_campaigns = european_totals()
with st.container(key="gs_euro"):
    st.markdown(
        '<div class="gs-euro-kicker">Second layer · Europe</div>'
        '<div class="gs-euro-title">EUROPEAN PERFORMANCE</div>'
        f'<div class="gs-euro-sub">Champions League · {coverage}</div>'
        '<div class="gs-euro-stats">'
        f'<div><div class="gs-euro-val">{len(SELECTED_CLUBS)}</div><div class="gs-euro-lbl">SELECTED CLUBS</div></div>'
        f'<div><div class="gs-euro-val">{eu_matches:,}</div><div class="gs-euro-lbl">CL MATCHES</div></div>'
        f'<div><div class="gs-euro-val">{eu_campaigns}</div><div class="gs-euro-lbl">CAMPAIGNS</div></div>'
        '</div>'
        '<div class="gs-euro-note">Clubs appear only in the seasons they actually qualified for — '
        'not every selected club played every season.</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/9_European_Performance.py", label="OPEN EUROPEAN PERFORMANCE →")

st.markdown(
    '<div class="pli-footer">GAMESTATE is an independent analytics project. '
    "Not affiliated with, endorsed by, or sponsored by the Premier League, UEFA, any club, or any official competition body. "
    "All data sourced from public datasets — see Methodology for full sourcing.</div>",
    unsafe_allow_html=True,
)

"""GAMESTATE visual identity: deep navy/black base, electric blue +
cyan highlights, restrained purple accents. Injected once per page via
inject_theme(). All custom CSS lives here so pages stay free of styling code.
"""
import inspect
from pathlib import Path

import streamlit as st

NAVY_950 = "#050b16"
NAVY_900 = "#0a1428"
NAVY_800 = "#0f1c38"
NAVY_700 = "#16264a"
CYAN = "#22d3ee"
BLUE = "#3b82f6"
PURPLE = "#8b5cf6"
TEXT_PRIMARY = "#e8edf7"
TEXT_MUTED = "#8b96ad"
GREEN = "#34d399"
RED = "#f87171"
AMBER = "#fbbf24"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, sans-serif;
}}

.stApp {{
    background:
        radial-gradient(ellipse 1200px 600px at 15% -10%, rgba(59,130,246,0.14), transparent 60%),
        radial-gradient(ellipse 900px 500px at 110% 10%, rgba(139,92,246,0.10), transparent 55%),
        {NAVY_950};
    color: {TEXT_PRIMARY};
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {NAVY_900}, {NAVY_950});
    border-right: 1px solid rgba(34,211,238,0.12);
}}

h1, h2, h3 {{
    font-family: 'Space Grotesk', 'Inter', sans-serif !important;
    letter-spacing: -0.01em;
}}

h1 {{ font-weight: 700 !important; }}

.pli-eyebrow {{
    color: {CYAN};
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}}

.pli-card {{
    background: linear-gradient(155deg, rgba(22,38,74,0.55), rgba(10,20,40,0.55));
    border: 1px solid rgba(34,211,238,0.14);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}}

.pli-kpi-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    background: linear-gradient(90deg, {CYAN}, {BLUE});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}}

.pli-kpi-label {{
    color: {TEXT_MUTED};
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.35rem;
}}

.pli-badge {{
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    background: rgba(34,211,238,0.12);
    color: {CYAN};
    border: 1px solid rgba(34,211,238,0.28);
}}

.pli-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34,211,238,0.35), transparent);
    margin: 1.4rem 0;
    border: none;
}}

[data-testid="stMetricValue"] {{
    color: {CYAN};
    font-family: 'Space Grotesk', sans-serif;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    background: rgba(255,255,255,0.02);
    border-radius: 8px 8px 0 0;
    color: {TEXT_MUTED};
}}
.stTabs [aria-selected="true"] {{
    color: {CYAN} !important;
    background: rgba(34,211,238,0.08) !important;
}}

.pli-footer {{
    color: {TEXT_MUTED};
    font-size: 0.75rem;
    text-align: center;
    padding-top: 2rem;
    opacity: 0.7;
}}

/* Top bar: blend into the page instead of a solid strip */
[data-testid="stHeader"] {{
    background: rgba(5,11,22,0.72);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(34,211,238,0.06);
}}

/* Sidebar: GAMESTATE wordmark + grouped navigation */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
    padding-top: 0.4rem;
}}
.gs-brand {{
    padding: 0.2rem 0.6rem 1.1rem;
    border-bottom: 1px solid rgba(34,211,238,0.10);
    margin-bottom: 0.4rem;
}}
.gs-brand-word {{
    font-family: 'Space Grotesk', 'Inter', sans-serif;
    font-weight: 700;
    font-size: 1.35rem;
    letter-spacing: 0.16em;
    color: #ffffff;
    line-height: 1;
}}
.gs-brand-word b {{ color: {CYAN}; font-weight: 700; }}
.gs-brand-tag {{
    margin-top: 0.45rem;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    color: {TEXT_MUTED};
    text-transform: uppercase;
}}
.gs-nav-section {{
    font-size: 0.64rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    line-height: 1;
    color: #5f6b85;
    text-transform: uppercase;
    padding: 1.1rem 0.6rem 0.45rem;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    margin-bottom: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
    border-radius: 8px;
    padding: 0.38rem 0.6rem;
    transition: background 0.15s ease;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a span,
section[data-testid="stSidebar"] [data-testid="stPageLink"] a p {{
    color: #aeb8cc;
    font-size: 0.88rem;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
    background: rgba(34,211,238,0.07);
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover span,
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover p {{
    color: #ffffff;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 0.1rem;
}}
section[data-testid="stSidebar"] .st-key-gs_nav_active [data-testid="stPageLink"] a {{
    background: linear-gradient(90deg, rgba(34,211,238,0.24), rgba(34,211,238,0.05) 70%, transparent);
    box-shadow: inset 3px 0 0 {CYAN};
}}
section[data-testid="stSidebar"] .st-key-gs_nav_active [data-testid="stPageLink"] a p {{
    color: #ffffff;
    font-weight: 600;
}}
section[data-testid="stSidebar"] .st-key-gs_nav_active [data-testid="stIconMaterial"] {{
    color: {CYAN};
}}

/* Data tables: framed panel on a dark surface */
[data-testid="stDataFrame"] {{
    border: 1px solid {NAVY_700};
    border-radius: 12px;
    overflow: hidden;
    background: {NAVY_900};
    box-shadow: 0 8px 24px rgba(0,0,0,0.30);
}}

/* Inputs */
[data-testid="stTextInput"] input:focus,
[data-baseweb="select"]:focus-within {{
    box-shadow: 0 0 0 1px {CYAN};
}}

/* Buttons */
[data-testid="stBaseButton-secondary"],
[data-testid="stDownloadButton"] button {{
    background: {NAVY_800};
    border: 1px solid {NAVY_700};
    color: {TEXT_PRIMARY};
}}
[data-testid="stBaseButton-secondary"]:hover,
[data-testid="stDownloadButton"] button:hover {{
    border-color: {CYAN};
    color: {CYAN};
}}
[data-testid="stBaseButton-primary"] {{
    color: {NAVY_950};
    font-weight: 700;
    letter-spacing: 0.08em;
}}

/* Expanders and alerts sit on the same dark surface as cards */
[data-testid="stExpander"] details {{
    background: rgba(15,28,56,0.45);
    border: 1px solid {NAVY_700};
    border-radius: 12px;
}}
[data-testid="stAlert"] {{
    border-radius: 12px;
}}

[data-testid="stMetricLabel"] {{
    color: {TEXT_MUTED};
}}

/* League table zone legend */
.pli-legend {{
    display: flex;
    flex-wrap: wrap;
    gap: 1.1rem;
    color: {TEXT_MUTED};
    font-size: 0.78rem;
    margin-top: 0.6rem;
}}
.pli-legend span {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
}}
.pli-legend i {{
    display: inline-block;
    width: 3px;
    height: 14px;
    border-radius: 2px;
}}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
</style>
"""


# Display labels only - each entry points at the existing page file, so
# routes (/League_Table, /Head_to_Head, ...) are unchanged.
NAV = [
    ("Main", [
        ("Home.py", "Overview", ":material/space_dashboard:"),
        ("pages/0_Global_Search.py", "Search", ":material/search:"),
        ("pages/1_League_Table.py", "Standings", ":material/leaderboard:"),
        ("pages/2_League_Trends.py", "Trends", ":material/trending_up:"),
    ]),
    ("Analysis", [
        ("pages/3_Team_Explorer.py", "Teams", ":material/groups:"),
        ("pages/4_Head_to_Head.py", "Head-to-Head", ":material/compare_arrows:"),
        ("pages/5_Match_Explorer.py", "Matches", ":material/sports_soccer:"),
        ("pages/6_Player_Explorer.py", "Players", ":material/person_search:"),
    ]),
    ("Europe", [
        ("pages/9_European_Performance.py", "European Performance", ":material/public:"),
    ]),
    ("Info", [
        ("pages/7_Methodology.py", "Methodology", ":material/science:"),
        ("pages/8_About.py", "About", ":material/info:"),
    ]),
]


def render_sidebar(current_file: str):
    with st.sidebar:
        st.markdown(
            '<div class="gs-brand"><div class="gs-brand-word">GAME<b>STATE</b></div>'
            '<div class="gs-brand-tag">Understand the game through data</div></div>',
            unsafe_allow_html=True,
        )
        for section, links in NAV:
            st.markdown(f'<div class="gs-nav-section">{section}</div>', unsafe_allow_html=True)
            for page, label, icon in links:
                if Path(page).name == current_file:
                    # Streamlit marks the active page_link only with a generated
                    # class name, so wrap it in a keyed container to style it.
                    with st.container(key="gs_nav_active"):
                        st.page_link(page, label=label, icon=icon)
                else:
                    st.page_link(page, label=label, icon=icon)


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)
    caller = inspect.currentframe().f_back
    render_sidebar(Path(caller.f_code.co_filename).name)


def eyebrow(text: str):
    st.markdown(f'<div class="pli-eyebrow">{text}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, col=None):
    target = col if col is not None else st
    target.markdown(
        f'<div class="pli-card"><div class="pli-kpi-value">{value}</div>'
        f'<div class="pli-kpi-label">{label}</div></div>',
        unsafe_allow_html=True,
    )


def divider():
    st.markdown('<hr class="pli-divider" />', unsafe_allow_html=True)


def badge(text: str) -> str:
    return f'<span class="pli-badge">{text}</span>'

"""GAMESTATE Home page: signature hero, data-at-a-glance strip, the GAMESTATE
Lab module grid and the European layer. All artwork is original inline SVG /
CSS - no photos, logos, crests or broadcast graphics.
"""
from urllib.parse import quote

import streamlit as st

CYAN = "#22d3ee"

# ---------------------------------------------------------------- hero artwork
# Night stadium bowl, floodlight beams, a pitch in perspective and a
# passing-network data layer, drawn as one SVG and used as a CSS background
# so Streamlit widgets (the CTA links) can sit on top of it.
HERO_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 820 460' preserveAspectRatio='xMaxYMax meet'>
<defs>
<linearGradient id='beam' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#bff6ff' stop-opacity='0.22'/><stop offset='1' stop-color='#22d3ee' stop-opacity='0'/></linearGradient>
<linearGradient id='pitch' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#22d3ee' stop-opacity='0.03'/><stop offset='1' stop-color='#22d3ee' stop-opacity='0.12'/></linearGradient>
<radialGradient id='node'><stop offset='0' stop-color='#e6fcff'/><stop offset='1' stop-color='#22d3ee' stop-opacity='0'/></radialGradient>
</defs>
<g fill='none' stroke='#22d3ee'>
<ellipse cx='470' cy='300' rx='400' ry='176' stroke-opacity='0.10'/>
<ellipse cx='470' cy='300' rx='372' ry='160' stroke-opacity='0.16' stroke-dasharray='1.5 5'/>
<ellipse cx='470' cy='300' rx='344' ry='145' stroke-opacity='0.12' stroke-dasharray='1.5 4'/>
<ellipse cx='470' cy='300' rx='316' ry='130' stroke-opacity='0.20'/>
</g>
<g stroke='#9befff' stroke-opacity='0.55' stroke-width='1.2'>
<line x1='200' y1='40' x2='200' y2='150'/><line x1='740' y1='30' x2='740' y2='150'/>
</g>
<g fill='#e6fcff'><rect x='188' y='32' width='24' height='8' rx='2'/><rect x='728' y='22' width='24' height='8' rx='2'/></g>
<polygon points='188,40 212,40 420,300 250,300' fill='url(#beam)'/>
<polygon points='728,30 752,30 700,300 540,300' fill='url(#beam)'/>
<polygon points='250,300 690,300 790,430 150,430' fill='url(#pitch)' stroke='#22d3ee' stroke-opacity='0.55'/>
<g fill='none' stroke='#22d3ee' stroke-opacity='0.45'>
<line x1='470' y1='300' x2='470' y2='430'/>
<ellipse cx='470' cy='362' rx='58' ry='18'/>
<polygon points='232,322 300,322 290,408 186,408'/>
<polygon points='640,322 708,322 754,408 650,408'/>
</g>
<g stroke='#22d3ee' stroke-opacity='0.55' stroke-width='1'>
<line x1='268' y1='372' x2='352' y2='338'/><line x1='352' y1='338' x2='430' y2='392'/>
<line x1='430' y1='392' x2='520' y2='340'/><line x1='520' y1='340' x2='604' y2='384'/>
<line x1='352' y1='338' x2='520' y2='340'/><line x1='604' y1='384' x2='676' y2='352'/>
<line x1='430' y1='392' x2='604' y2='384'/>
</g>
<g stroke='#22d3ee' stroke-opacity='0.35'>
<line x1='520' y1='340' x2='520' y2='236'/><line x1='352' y1='338' x2='352' y2='262'/><line x1='676' y1='352' x2='676' y2='270'/>
</g>
<g fill='#22d3ee' fill-opacity='0.8'>
<rect x='514' y='228' width='12' height='3'/><rect x='346' y='254' width='12' height='3'/><rect x='670' y='262' width='12' height='3'/>
</g>
<g>
<circle cx='268' cy='372' r='9' fill='url(#node)'/><circle cx='352' cy='338' r='10' fill='url(#node)'/>
<circle cx='430' cy='392' r='9' fill='url(#node)'/><circle cx='520' cy='340' r='11' fill='url(#node)'/>
<circle cx='604' cy='384' r='9' fill='url(#node)'/><circle cx='676' cy='352' r='9' fill='url(#node)'/>
</g>
<g fill='#8b5cf6' fill-opacity='0.8'><circle cx='394' cy='360' r='3'/><circle cx='560' cy='366' r='3'/><circle cx='646' cy='330' r='3'/></g>
<g transform='translate(560 70)'>
<rect width='190' height='96' rx='8' fill='#0a1830' fill-opacity='0.75' stroke='#22d3ee' stroke-opacity='0.35'/>
<rect x='14' y='16' width='52' height='4' rx='2' fill='#9befff' fill-opacity='0.7'/>
<rect x='14' y='34' width='150' height='6' rx='3' fill='#22d3ee' fill-opacity='0.18'/><rect x='14' y='34' width='112' height='6' rx='3' fill='#22d3ee' fill-opacity='0.7'/>
<rect x='14' y='52' width='150' height='6' rx='3' fill='#22d3ee' fill-opacity='0.18'/><rect x='14' y='52' width='74' height='6' rx='3' fill='#22d3ee' fill-opacity='0.55'/>
<rect x='14' y='70' width='150' height='6' rx='3' fill='#22d3ee' fill-opacity='0.18'/><rect x='14' y='70' width='96' height='6' rx='3' fill='#8b5cf6' fill-opacity='0.6'/>
</g>
<line x1='655' y1='166' x2='600' y2='232' stroke='#22d3ee' stroke-opacity='0.25' stroke-dasharray='3 4'/>
</svg>"""


def _svg_url(svg: str) -> str:
    return f'url("data:image/svg+xml;charset=utf-8,{quote(" ".join(svg.split()))}")'


# ---------------------------------------------------------------- module mini-visuals
def _mini(kind: str) -> str:
    s = "stroke='#22d3ee'"
    if kind == "match":
        body = (f"<line x1='4' y1='26' x2='196' y2='26' {s} stroke-opacity='0.35'/>"
                + "".join(f"<circle cx='{x}' cy='26' r='{r}' fill='#22d3ee' fill-opacity='{o}'/>"
                          for x, r, o in [(22, 3, .5), (58, 4.5, .9), (96, 3, .5), (131, 4.5, .9), (170, 3, .5)]))
    elif kind == "player":
        body = ("<polygon points='100,4 136,20 128,44 72,44 64,20' fill='none' stroke='#22d3ee' stroke-opacity='0.3'/>"
                "<polygon points='100,12 126,22 118,38 84,40 76,24' fill='#22d3ee' fill-opacity='0.2' stroke='#22d3ee' stroke-opacity='0.8'/>")
    elif kind == "team":
        body = f"<polyline points='4,40 34,30 64,34 94,18 124,22 154,10 196,14' fill='none' {s} stroke-width='2' stroke-opacity='0.8'/>"
    elif kind == "table":
        body = "".join(f"<rect x='4' y='{y}' width='{w}' height='5' rx='2.5' fill='#22d3ee' fill-opacity='{o}'/>"
                       for y, w, o in [(6, 188, .8), (16, 160, .6), (26, 132, .45), (36, 96, .3)])
    elif kind == "h2h":
        body = ("<rect x='4' y='14' width='104' height='8' rx='4' fill='#22d3ee' fill-opacity='0.75'/>"
                "<rect x='112' y='14' width='84' height='8' rx='4' fill='#8b5cf6' fill-opacity='0.7'/>"
                "<rect x='4' y='30' width='60' height='8' rx='4' fill='#22d3ee' fill-opacity='0.35'/>"
                "<rect x='68' y='30' width='128' height='8' rx='4' fill='#8b5cf6' fill-opacity='0.35'/>")
    else:  # europe: progression rungs
        body = f"<polyline points='4,42 44,42 44,32 84,32 84,22 124,22 124,12 164,12 164,6 196,6' fill='none' {s} stroke-width='2' stroke-opacity='0.8'/>"
    return f"<svg viewBox='0 0 200 48' width='100%' height='44' xmlns='http://www.w3.org/2000/svg'>{body}</svg>"


LAB_MODULES = [
    ("01", "MATCH CENTRE", "Historical match intelligence.", "sports_soccer", "match",
     "pages/5_Match_Explorer.py", "Open Match Centre"),
    ("02", "PLAYER LAB", "Player performance and comparison.", "person_search", "player",
     "pages/6_Player_Explorer.py", "Open Player Lab"),
    ("03", "TEAM INTELLIGENCE", "Team performance and historical journeys.", "groups", "team",
     "pages/3_Team_Explorer.py", "Open Teams"),
    ("04", "STANDINGS", "League tables across seasons.", "leaderboard", "table",
     "pages/1_League_Table.py", "Open Standings"),
    ("05", "HEAD-TO-HEAD", "Historical team battles.", "compare_arrows", "h2h",
     "pages/4_Head_to_Head.py", "Open Head-to-Head"),
    ("06", "EUROPEAN PERFORMANCE", "Champions League performance across selected clubs.", "public", "europe",
     "pages/9_European_Performance.py", "Open Europe"),
]

HOME_CSS = f"""
<style>
.block-container {{ padding-top: 2.4rem; max-width: 1280px; }}

/* ---- hero */
.st-key-gs_hero {{
    position: relative;
    overflow: hidden;
    border-radius: 22px;
    border: 1px solid rgba(34,211,238,0.14);
    padding: 3rem 3.2rem 2.6rem;
    min-height: 430px;
    justify-content: center;
    background:
        {_svg_url(HERO_SVG)} right bottom / auto 100% no-repeat,
        radial-gradient(ellipse 620px 300px at 76% -6%, rgba(155,239,255,0.16), transparent 70%),
        radial-gradient(ellipse 900px 180px at 68% 104%, rgba(34,211,238,0.16), transparent 70%),
        repeating-linear-gradient(0deg, rgba(34,211,238,0.035) 0 1px, transparent 1px 44px),
        repeating-linear-gradient(90deg, rgba(34,211,238,0.035) 0 1px, transparent 1px 44px),
        linear-gradient(120deg, #060d1c 0%, #0a1630 58%, #061022 100%);
    box-shadow: 0 24px 60px rgba(0,0,0,0.45);
}}
.st-key-gs_hero::before, .st-key-gs_hero::after {{
    content: ""; position: absolute; width: 26px; height: 26px; pointer-events: none;
    border-color: rgba(34,211,238,0.6); border-style: solid;
}}
.st-key-gs_hero::before {{ top: 16px; left: 16px; border-width: 1px 0 0 1px; }}
.st-key-gs_hero::after {{ bottom: 16px; right: 16px; border-width: 0 1px 1px 0; }}
.gs-hero-copy {{ max-width: 560px; position: relative; z-index: 1; }}
.gs-hero-eyebrow {{
    color: {CYAN}; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.24em;
    text-transform: uppercase; margin-bottom: 1rem;
}}
.gs-hero-title {{
    font-family: 'Space Grotesk', 'Inter', sans-serif; font-weight: 700;
    font-size: clamp(3rem, 6vw, 4.8rem); line-height: 0.95; letter-spacing: 0.06em;
    background: linear-gradient(92deg, #ffffff 0%, #dff8ff 55%, {CYAN} 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.gs-hero-tagline {{
    margin-top: 1.1rem; color: #eaf2ff; font-family: 'Space Grotesk', 'Inter', sans-serif;
    font-weight: 600; font-size: clamp(1.2rem, 2.2vw, 1.7rem); line-height: 1.2; letter-spacing: 0.05em;
}}
.gs-hero-meta {{
    margin-top: 1.2rem; display: flex; align-items: center; gap: 0.8rem;
    color: #8b96ad; font-size: 0.8rem; letter-spacing: 0.14em; text-transform: uppercase;
}}
.gs-hero-meta i {{ display: inline-block; width: 28px; height: 1px; background: {CYAN}; }}
.gs-hero-meta b {{ color: #d7e0f0; font-weight: 600; }}
.st-key-gs_cta {{ margin-top: 1.4rem; gap: 0.7rem; position: relative; z-index: 1; }}
.st-key-gs_cta [data-testid="stPageLink"] a {{
    border-radius: 999px; padding: 0.55rem 1.3rem; border: 1px solid rgba(34,211,238,0.45);
    background: rgba(5,11,22,0.55); transition: all 0.15s ease;
}}
.st-key-gs_cta [data-testid="stPageLink"] a p, .st-key-gs_cta [data-testid="stPageLink"] a span {{
    color: #e8edf7; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.16em;
}}
.st-key-gs_cta [data-testid="stPageLink"] a:hover {{ border-color: {CYAN}; background: rgba(34,211,238,0.10); }}
.st-key-gs_cta_primary [data-testid="stPageLink"] a {{ background: {CYAN}; border-color: {CYAN}; box-shadow: 0 0 24px rgba(34,211,238,0.25); }}
.st-key-gs_cta_primary [data-testid="stPageLink"] a p, .st-key-gs_cta_primary [data-testid="stPageLink"] a span {{ color: #041019; }}
.st-key-gs_cta_primary [data-testid="stPageLink"] a:hover {{ background: #67e8f9; }}

/* ---- section headings */
.gs-section {{ margin: 2.8rem 0 1.1rem; }}
.gs-section-kicker {{
    display: flex; align-items: center; gap: 0.8rem; color: {CYAN}; font-size: 0.72rem;
    font-weight: 700; letter-spacing: 0.24em; text-transform: uppercase;
}}
.gs-section-kicker::after {{ content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(34,211,238,0.35), transparent); }}
.gs-section-title {{ font-family: 'Space Grotesk','Inter',sans-serif; font-size: 1.9rem; font-weight: 700; color: #fff; margin-top: 0.5rem; letter-spacing: 0.02em; }}
.gs-section-sub {{ color: #8b96ad; font-size: 0.95rem; margin-top: 0.2rem; }}

/* ---- data at a glance */
.gs-stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.9rem; }}
.gs-stat {{
    position: relative; padding: 1.2rem 1.3rem 1.1rem; border-radius: 14px;
    background: linear-gradient(160deg, rgba(15,28,56,0.85), rgba(8,16,34,0.85));
    border: 1px solid rgba(34,211,238,0.12); overflow: hidden;
}}
.gs-stat::before {{ content: ""; position: absolute; top: 0; left: 1.3rem; width: 34px; height: 2px; background: {CYAN}; }}
.gs-stat-idx {{ color: #4e5b76; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.2em; }}
.gs-stat-val {{ font-family: 'Space Grotesk','Inter',sans-serif; font-size: 2.4rem; font-weight: 700; color: #fff; line-height: 1.05; margin-top: 0.35rem; }}
.gs-stat-lbl {{ color: {CYAN}; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.2em; margin-top: 0.35rem; }}
.gs-stat-sub {{ color: #8b96ad; font-size: 0.78rem; margin-top: 0.25rem; }}
.gs-stat-ticks {{ margin-top: 0.9rem; height: 6px; background: repeating-linear-gradient(90deg, rgba(34,211,238,0.35) 0 1px, transparent 1px 7px); opacity: 0.6; }}

/* ---- lab */
[class*="st-key-gs_lab_"] {{
    padding: 1.2rem 1.25rem 0.9rem; border-radius: 16px; height: 100%;
    background: linear-gradient(165deg, rgba(15,28,56,0.75), rgba(7,14,30,0.9));
    border: 1px solid rgba(34,211,238,0.10); transition: border-color 0.15s ease, transform 0.15s ease;
}}
[class*="st-key-gs_lab_"]:hover {{ border-color: rgba(34,211,238,0.45); transform: translateY(-2px); }}
/* equal-height cards per row, with the action link pinned to the bottom */
[data-testid="stHorizontalBlock"]:has([class*="st-key-gs_lab_"]) {{ align-items: stretch; }}
[data-testid="stColumn"]:has([class*="st-key-gs_lab_"]) > [data-testid="stVerticalBlock"],
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-gs_lab_"]) {{ height: 100%; }}
[class*="st-key-gs_lab_"] > :last-child {{ margin-top: auto; }}
.gs-lab-top {{ display: flex; justify-content: space-between; align-items: center; }}
.gs-lab-num {{ font-family: 'Space Grotesk','Inter',sans-serif; color: #4e5b76; font-weight: 700; font-size: 0.9rem; letter-spacing: 0.12em; }}
.gs-icon {{
    font-family: 'Material Symbols Rounded'; font-weight: normal; font-style: normal; line-height: 1;
    letter-spacing: normal; text-transform: none; white-space: nowrap; direction: ltr;
    -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga'; -webkit-font-smoothing: antialiased;
}}
.gs-lab-icon {{
    font-size: 22px; color: {CYAN}; width: 40px; height: 40px; border-radius: 10px;
    display: inline-flex; align-items: center; justify-content: center;
    background: rgba(34,211,238,0.08); border: 1px solid rgba(34,211,238,0.2);
}}
.gs-lab-title {{ margin-top: 1rem; color: #fff; font-family: 'Space Grotesk','Inter',sans-serif; font-weight: 700; font-size: 1.02rem; letter-spacing: 0.08em; }}
.gs-lab-desc {{ color: #8b96ad; font-size: 0.86rem; line-height: 1.5; margin-top: 0.3rem; min-height: 3em; }}
.gs-lab-viz {{ margin-top: 0.8rem; opacity: 0.9; }}
[class*="st-key-gs_lab_"] [data-testid="stPageLink"] a {{ padding: 0.2rem 0; }}
[class*="st-key-gs_lab_"] [data-testid="stPageLink"] a p, [class*="st-key-gs_lab_"] [data-testid="stPageLink"] a span {{
    color: {CYAN}; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
}}
[class*="st-key-gs_lab_"] [data-testid="stPageLink"] a:hover {{ background: transparent; }}
[class*="st-key-gs_lab_"] [data-testid="stPageLink"] a:hover p {{ color: #fff; }}

/* ---- european layer */
.st-key-gs_euro {{
    position: relative; overflow: hidden; margin-top: 2.8rem; border-radius: 20px;
    padding: 2.2rem 2.4rem 1.8rem;
    border: 1px solid rgba(59,130,246,0.30);
    background:
        radial-gradient(circle at 88% 50%, transparent 0 78px, rgba(34,211,238,0.14) 79px 80px, transparent 81px 128px,
                        rgba(34,211,238,0.10) 129px 130px, transparent 131px 182px, rgba(59,130,246,0.14) 183px 184px, transparent 185px),
        radial-gradient(ellipse 520px 260px at 90% 50%, rgba(59,130,246,0.22), transparent 70%),
        linear-gradient(115deg, #06112a 0%, #0a1f4d 60%, #07163a 100%);
    box-shadow: inset 4px 0 0 {CYAN};
}}
.gs-euro-kicker {{ color: #93c5fd; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.24em; text-transform: uppercase; }}
.gs-euro-title {{ font-family: 'Space Grotesk','Inter',sans-serif; font-weight: 700; font-size: 2rem; color: #fff; margin-top: 0.4rem; letter-spacing: 0.04em; }}
.gs-euro-sub {{ color: #bcd3f5; font-size: 0.95rem; margin-top: 0.2rem; letter-spacing: 0.06em; }}
.gs-euro-stats {{ display: flex; flex-wrap: wrap; gap: 2.6rem; margin-top: 1.5rem; }}
.gs-euro-val {{ font-family: 'Space Grotesk','Inter',sans-serif; font-size: 2rem; font-weight: 700; color: #fff; line-height: 1; }}
.gs-euro-lbl {{ color: {CYAN}; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.2em; margin-top: 0.4rem; }}
.gs-euro-note {{ color: #8ea6c8; font-size: 0.8rem; margin-top: 1.3rem; max-width: 560px; }}
.st-key-gs_euro [data-testid="stPageLink"] a {{ margin-top: 0.5rem; padding: 0.45rem 1.1rem; border-radius: 999px; border: 1px solid rgba(147,197,253,0.45); }}
.st-key-gs_euro [data-testid="stPageLink"] a p, .st-key-gs_euro [data-testid="stPageLink"] a span {{ color: #e8edf7; font-weight: 700; font-size: 0.78rem; letter-spacing: 0.14em; }}
.st-key-gs_euro [data-testid="stPageLink"] a:hover {{ border-color: {CYAN}; background: rgba(34,211,238,0.08); }}

@media (max-width: 1100px) {{
    .gs-stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .st-key-gs_hero {{ padding: 2.4rem 2rem 2.2rem; background-size: auto 78%, auto, auto, auto, auto, auto; }}
}}
</style>
"""


def section_heading(kicker: str, title: str | None = None, sub: str | None = None):
    html = f'<div class="gs-section"><div class="gs-section-kicker">{kicker}</div>'
    if title:
        html += f'<div class="gs-section-title">{title}</div>'
    if sub:
        html += f'<div class="gs-section-sub">{sub}</div>'
    st.markdown(html + "</div>", unsafe_allow_html=True)


def stat_cards(items: list[tuple[str, str, str]]):
    cards = "".join(
        f'<div class="gs-stat"><div class="gs-stat-idx">{i:02d}</div><div class="gs-stat-val">{val}</div>'
        f'<div class="gs-stat-lbl">{label}</div><div class="gs-stat-sub">{sub}</div><div class="gs-stat-ticks"></div></div>'
        for i, (val, label, sub) in enumerate(items, start=1)
    )
    st.markdown(f'<div class="gs-stats">{cards}</div>', unsafe_allow_html=True)


def lab_module(index: int, num: str, title: str, desc: str, icon: str, viz: str, page: str, link_label: str):
    with st.container(key=f"gs_lab_{index}"):
        st.markdown(
            f'<div class="gs-lab-top"><span class="gs-lab-num">{num}</span>'
            f'<span class="gs-icon gs-lab-icon">{icon}</span></div>'
            f'<div class="gs-lab-title">{title}</div><div class="gs-lab-desc">{desc}</div>'
            f'<div class="gs-lab-viz">{_mini(viz)}</div>',
            unsafe_allow_html=True,
        )
        st.page_link(page, label=link_label, icon=":material/arrow_forward:", icon_position="right")

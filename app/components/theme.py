"""PL INTELLIGENCE visual identity: deep navy/black base, electric blue +
cyan highlights, restrained purple accents. Injected once per page via
inject_theme(). All custom CSS lives here so pages stay free of styling code.
"""
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

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
</style>
"""


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)


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

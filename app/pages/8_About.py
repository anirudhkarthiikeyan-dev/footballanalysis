import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.components.theme import divider, eyebrow, inject_theme

st.set_page_config(page_title="About | GAMESTATE", layout="wide")
inject_theme()

eyebrow("Project")
st.title("About GAMESTATE")

divider()
st.markdown(
    """
**GAMESTATE** is an end-to-end Premier League football analytics product covering 2012/13–2025/26,
built as a portfolio-grade demonstration of the full data analytics stack: ingestion, cleaning,
validation, a star-schema SQLite database, an analytics/ML layer, and a custom Streamlit product —
the single, final dashboard layer for the project.

### Why this project exists
To demonstrate — end to end, on real public data — the workflow a data analyst or data scientist
uses in practice: sourcing and validating imperfect real-world data, building a queryable warehouse,
computing analytics that are checked against known ground truth, and shipping a usable product on top.

### Technology
Python · Pandas · NumPy · SQLite · scikit-learn · Plotly · Streamlit · pytest · Playwright

### Data honesty policy
Every number in this product traces back to a documented public source. Where a metric isn't
reliably available for a season, it's shown as missing (or the season/feature is simply out of
scope) rather than estimated or invented. See **Methodology** and `docs/data/DATA_SOURCES.md`.

### Independence
This is an independent project. It is not affiliated with, endorsed by, or sponsored by the Premier
League, its clubs, the FA, or any official competition body. No official logos, crests or broadcast
graphics are used — all visual identity is original.

### Author
Built by Anirudh Karthikeyan as a personal analytics/data engineering portfolio project.
"""
)

divider()
st.markdown(
    '<div class="pli-footer">See docs/PROJECT_PROGRESS.md in the repository for current build status.</div>',
    unsafe_allow_html=True,
)

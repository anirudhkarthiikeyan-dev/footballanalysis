import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.components.theme import divider, eyebrow, inject_theme

st.set_page_config(page_title="Methodology | GAMESTATE", layout="wide")
inject_theme()

eyebrow("How the numbers are built")
st.title("Methodology")

divider()
st.subheader("Data sources")
st.markdown(
    """
| Domain | Source | Coverage | Notes |
|---|---|---|---|
| Match results & stats | [football-data.co.uk](https://www.football-data.co.uk/englandm.php) | 2012/13 – 2025/26 (all 14 seasons, 5,320 matches) | Free, widely used, structured CSVs per season |
| Player-season stats | [vaastav/Fantasy-Premier-League](https://github.com/vaastav/Fantasy-Premier-League) (public GitHub archive) | 2019/20 – 2025/26 (7 seasons) | FPL's own tracked data; team lookup unavailable for 2016/17–2018/19 so those are excluded |
| Expected goals / assists | Same FPL archive | 2022/23 – 2025/26 only | FPL began tracking xG/xA mid-2020s; earlier seasons are `null`, never `0` |

Full field-level documentation lives in `docs/data/DATA_SOURCES.md` and `docs/data/DATA_DICTIONARY.md`.
"""
)

divider()
st.subheader("Cleaning pipeline")
st.markdown(
    """
1. **Ingestion** — raw season CSVs downloaded verbatim (`src/ingestion/`), nothing altered.
2. **Cleaning** — drop known blank trailing rows, parse mixed date formats (`dd/mm/yy` vs `dd/mm/yyyy`),
   map raw team-name strings from *both* sources to one canonical team list (`data/external/team_master.csv`) —
   e.g. `"Man United"` (football-data) and `"Man Utd"` (FPL) both resolve to `"Manchester United"`.
3. **Validation** — automated checks: no duplicate matches, home ≠ away, non-negative goals/minutes,
   result code agrees with the goal columns, every season has exactly 20 teams and 380 matches.
   See `src/validation/validate_matches.py` and `tests/`.
4. **Transformation** — cleaned rows load into a star-schema SQLite database
   (`database/pl_intelligence.db`): `DIM_TEAM`, `DIM_SEASON`, `DIM_DATE`, `DIM_PLAYER`,
   `FACT_MATCH`, `FACT_TEAM_SEASON`, `FACT_PLAYER_SEASON`.
"""
)

divider()
st.subheader("League table & tie-breaks")
st.markdown(
    """
Points: 3 for a win, 1 for a draw, 0 for a loss. Ties are broken by **points → goal difference →
goals scored → alphabetical**, which matches the Premier League's actual rule for the large majority
of seasons. Rare historical play-off or head-to-head tie-breaks are not modeled — see `LIMITATIONS.md`.
"""
)

divider()
st.subheader("Player similarity model")
st.markdown(
    """
**Question:** which outfield players had a statistically similar per-90 production profile in a season?

**Method:** k-nearest neighbors (scikit-learn) on standardized per-90 features —
`goals/90, assists/90, xG/90, xA/90` — restricted to 2022/23–2025/26 (all four features required),
outfield players only, 450+ minutes played.

**Why ML:** comparing four correlated rate stats simultaneously needs a distance metric over a
multi-dimensional space — a plain sort or filter can't answer "who looks statistically like player X."

**Normalization:** `StandardScaler` (zero mean, unit variance) fit per search cohort, so goals
(larger raw values) don't dominate assists/xA purely from unit scale.

**Limitations:** no positional sub-role awareness, no minutes-weighting beyond the cutoff, and small
cohorts (e.g. few forwards clearing 450 minutes in one season) mean the neighbor pool can be small.
Full writeup in `src/ml/player_similarity.py`.
"""
)

divider()
st.subheader("European Performance module")
st.markdown(
    """
**Scope:** the 20 clubs named in the project brief, UEFA Champions League only, 2012/13–2025/26.
A club appears for a season only if it actually played in that season's competition — verified for
clubs with limited history (e.g. Leicester City's only campaign in range is 2016/17).

**Source:** [openfootball/champions-league](https://github.com/openfootball/champions-league), a
public-domain structured text archive.

**On-pitch goals vs penalties:** a shootout score is recorded separately from real goals scored —
never counted as a goal. Every final in the dataset was checked against independently known real
results as part of building this module.

**Cross-era progression scale:** seasons before 2024/25 used a traditional 8-group format; 2024/25+
uses a 36-team "Swiss model" league phase. Both are mapped to one 1–7 progression scale for
comparability, with the caveat that the two formats aren't perfectly equivalent in difficulty.

Full detail in `docs/methodology/METHODOLOGY.md`.
"""
)

divider()
st.subheader("What's intentionally not shown")
st.markdown(
    """
- **No player data before 2019/20** — the source doesn't publish it reliably for this project's scope.
- **No xG/xA before 2022/23** — not tracked by the source; shown as blank, not zero.
- **No fabricated advanced metrics** (progressive passes, pressures, etc.) — not available from a
  free, reliable source across enough of the historical range to be worth including.
- **No player-level European statistics** — the Champions League source is match-level only.
"""
)

divider()
st.markdown(
    '<div class="pli-footer">GAMESTATE is an independent analytics project, not affiliated with '
    "the Premier League or any club.</div>",
    unsafe_allow_html=True,
)

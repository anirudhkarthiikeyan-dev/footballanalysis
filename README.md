# GAMESTATE

### Premier League & European Football Analytics

*Understand the game through data*

An end-to-end football analytics product covering the Premier League,
2012/13–2025/26: a real data pipeline, a star-schema SQLite database, a
tested analytics/ML layer, and a Streamlit product with a cinematic
(visual-only) intro.

This is a from-scratch rebuild — not a continuation of any prior
version of this project. See `docs/PROJECT_PROGRESS.md` for exactly
what's built, what's pending, and why.

---

## Why this project exists

To demonstrate, on real public data, the full workflow a data analyst /
data engineer uses in practice: sourcing and validating imperfect
real-world data, building a queryable warehouse, computing analytics
that are checked against known ground truth (not just "it ran without
errors"), and shipping a usable product on top.

## What's actually built right now

- **Data pipeline** (`src/ingestion`, `src/cleaning`, `src/validation`,
  `src/transformation`) — downloads real Premier League match data
  (2012/13–2025/26, 5,320 matches) from football-data.co.uk, player
  season data (2019/20–2025/26, 3,799 player-seasons) from the public
  vaastav/Fantasy-Premier-League archive, and UEFA Champions League
  match data (2012/13–2025/26) from the public-domain
  openfootball/champions-league archive — cleans it, resolves
  team-name variants across sources to one canonical list, and
  validates it.
- **Star-schema SQLite database** (`database/pl_intelligence.db`) —
  `DIM_TEAM`, `DIM_SEASON`, `DIM_DATE`, `DIM_PLAYER`, `DIM_COMPETITION`,
  `FACT_MATCH`, `FACT_TEAM_SEASON`, `FACT_PLAYER_SEASON`,
  `FACT_EUROPEAN_MATCH`, `FACT_CLUB_SEASON_EUROPE`.
- **Analytics engine** (`src/analytics`) — league tables, head-to-head,
  team season journeys, league-wide trends, player per-90/percentiles,
  and European campaign analytics — each verified against known real
  results (e.g. Leicester City's 2015/16 title, Haaland's 2022/23 goal
  record, Man City's unbeaten 2022/23 Champions League campaign).
- **ML player similarity** (`src/ml/player_similarity.py`) — k-nearest
  neighbors over standardized per-90 output, documented with its
  question, features, normalization, distance metric and limitations.
- **European Performance module** — real UEFA Champions League data for
  the 20 clubs named in the project brief, filtered to each club's
  actual participation seasons (no fabricated campaigns), verified
  against 11 independently known real finals.
- **Streamlit product** (`app/`, 11 pages) — Home (cinematic
  visual-only intro), Global Search, League Table, League Trends, Team
  Explorer (profile + comparison), Head-to-Head, Match Explorer, Player
  Explorer (explorer, profile, comparison, similarity), European
  Performance (club profile, comparison, European H2H, domestic vs
  Europe), Methodology, About. This is the single, final dashboard
  layer for the project — see "Architecture decisions" below.
- **Tests** — 57 fast unit/data/database/analytics tests (`tests/`),
  100% reliable, covering data quality, database integrity, analytics
  correctness, the ML module, and the European module. Plus 41
  Playwright browser tests (`tests/ui/`) covering every page loading,
  navigation, filters actually changing real data, no console errors,
  no horizontal overflow, and the intro's Enter/Skip buttons — correct
  and passes fully in isolation, but shows environment-dependent
  flakiness under repeated back-to-back runs on a shared machine (see
  `LIMITATIONS.md`); treat it as a strong signal, not an absolute gate.

## Architecture decisions

**Streamlit is the single, final dashboard layer.** Power BI was
explored during development — a real star-schema export and a
48-measure DAX library were built, and the model was opened and wired
successfully in Power BI Desktop — but was then intentionally dropped
in favor of finishing one dashboard well rather than maintaining two.
That exploration is preserved, unedited, in
`_archive_old/powerbi_exploration/` as a record of the work, but **it
is not part of the product and nothing in this repo requires Power BI
to run.** See `docs/PROJECT_PROGRESS.md` for the decision and date.

## What's not built yet

See `docs/PROJECT_PROGRESS.md` and `LIMITATIONS.md` for the full,
honest list. Headline items: the full learning-log/interview-prep
topic set promised by the original project brief, and public
deployment.

---

## Project structure

```
pl-intelligence/
├── app/                    # Streamlit product (Home.py + pages/) — the final dashboard
├── data/
│   ├── raw/                # Downloaded, untouched source data (gitignored — regenerate via ingestion scripts)
│   ├── processed/          # Cleaned, analysis-ready tables (gitignored — regenerate via cleaning scripts)
│   └── external/           # Hand-maintained reference data (team_master.csv) — committed
├── database/                # schema.sql (committed) + pl_intelligence.db (gitignored, regenerate)
├── src/
│   ├── ingestion/           # Download raw data (matches, players, European)
│   ├── cleaning/            # Clean + normalize
│   ├── validation/          # Automated data-quality checks
│   ├── transformation/      # Build the SQLite database
│   ├── analytics/           # League table, H2H, team/player/European stats
│   ├── ml/                  # Player similarity model
│   └── utils/                # Shared helpers (season labels, paths)
├── tests/                    # pytest suite (unit/data/db/analytics) + tests/ui/ (Playwright)
├── docs/                     # Architecture, data, methodology, learning docs
├── assets/                   # Icons/images (no official league/club branding)
└── _archive_old/             # Descoped/superseded material kept for history (old unrelated project files, the Power BI exploration)
```

## Setup

Requires Python 3.11+.

```bash
pip install -r requirements.txt
```

## Running the pipeline (regenerates all data + the database)

Raw and processed data aren't committed to the repo (see `.gitignore`
and `LIMITATIONS.md` for why) — run the pipeline once after cloning:

```bash
python -m src.ingestion.fetch_matches
python -m src.ingestion.fetch_players
python -m src.ingestion.fetch_european
python -m src.cleaning.clean_matches
python -m src.cleaning.clean_players
python -m src.cleaning.clean_european
python -m src.transformation.build_database
```

## Running the Streamlit app

```bash
streamlit run app/Home.py
```

## Running the tests

Fast unit/data/database/analytics suite (no browser needed):

```bash
python -m pytest tests/ -v --ignore=tests/ui
```

Browser UI suite (Playwright — launches a real Streamlit server and a
real headless Chromium browser; slower, run separately):

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium
python -m pytest tests/ui/ -v
```

## Data sources & licensing

See `docs/data/DATA_SOURCES.md` for full source documentation
(coverage, fields, license notes) and `LIMITATIONS.md` for what isn't
included and why.

## Independence

This is an independent project. It is not affiliated with, endorsed
by, or sponsored by the Premier League, its clubs, the FA, or any
official competition body. No official logos, crests or broadcast
graphics are used.

## Author

Anirudh Karthikeyan — built as a personal data analytics / data
engineering portfolio project.

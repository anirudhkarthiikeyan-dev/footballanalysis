# PL INTELLIGENCE

### Premier League Football Analytics

*Data Drives A Deeper Game*

An end-to-end football analytics product covering the Premier League,
2012/13–2025/26: a real data pipeline, a star-schema SQL database, a
tested analytics/ML layer, a Power BI-ready model, and a custom
Streamlit product with a cinematic (visual-only) intro.

This is a from-scratch rebuild — not a continuation of any prior
version of this project. See `docs/PROJECT_PROGRESS.md` for exactly
what's built, what's pending, and why.

---

## Why this project exists

To demonstrate, on real public data, the full workflow a data analyst /
data engineer uses in practice: sourcing and validating imperfect
real-world data, building a queryable warehouse, computing analytics
that are checked against known ground truth (not just "it ran without
errors"), and shipping a usable product on top — in both a BI tool
(Power BI) and a custom app (Streamlit).

## What's actually built right now

- **Data pipeline** (`src/ingestion`, `src/cleaning`, `src/validation`,
  `src/transformation`) — downloads real Premier League match data
  (2012/13–2025/26, 5,320 matches) from football-data.co.uk and player
  season data (2019/20–2025/26, 3,799 player-seasons) from the public
  vaastav/Fantasy-Premier-League archive, cleans it, resolves team-name
  variants across sources to one canonical list, and validates it.
- **Star-schema SQLite database** (`database/pl_intelligence.db`) —
  `DIM_TEAM`, `DIM_SEASON`, `DIM_DATE`, `DIM_PLAYER`, `FACT_MATCH`,
  `FACT_TEAM_SEASON`, `FACT_PLAYER_SEASON`.
- **Analytics engine** (`src/analytics`) — league tables, head-to-head,
  team season journeys, league-wide trends, player per-90/percentiles —
  each verified against known real results (e.g. Leicester City's
  2015/16 title, Haaland's 2022/23 goal record).
- **ML player similarity** (`src/ml/player_similarity.py`) — k-nearest
  neighbors over standardized per-90 output, documented with its
  question, features, normalization, distance metric and limitations.
- **Power BI-ready model** (`powerbi/`) — CSV exports of every
  dimension/fact table plus a full DAX measure library. No `.pbix` file
  is included (Power BI Desktop wasn't available in the build
  environment) — see `powerbi/README.md` for the exact build steps.
- **Streamlit product** (`app/`) — Home (with cinematic visual-only
  intro), Global Search (teams, clubs, players, seasons — click a
  result to jump straight to it), League Table, League Trends, Team
  Explorer (profile + comparison), Head-to-Head, Match Explorer,
  Player Explorer (explorer, profile, comparison, similarity),
  Methodology, About, and European Performance (club profile,
  comparison, European H2H, domestic vs Europe).
- **European Performance module** — real UEFA Champions League data
  (2012/13–2025/26) for the 20 clubs named in the project brief,
  parsed from a public-domain source, filtered to each club's actual
  participation seasons (no fabricated campaigns), verified against 11
  independently known real finals.
- **Tests** — 57 fast unit/data/database/analytics tests (`tests/`)
  covering data quality, database integrity, analytics correctness, the
  ML module, and the European module, plus 41 Playwright browser tests
  (`tests/ui/`) covering every page loading, navigation, filters
  actually changing real data, no console errors, no horizontal
  overflow, and the intro's Enter/Skip buttons. 98 tests total, all
  passing.
- **Global Search** — search teams, European clubs, players and
  seasons from one box; results deep-link straight to the right page
  with the right entity pre-selected.

## What's not built yet

See `docs/PROJECT_PROGRESS.md` and `LIMITATIONS.md` for the full,
honest list. Headline items: a compiled `.pbix` file and the full
learning-log/interview-prep set promised by the original project brief.

---

## Project structure

```
pl-intelligence/
├── app/                    # Streamlit product (Home.py + pages/)
├── data/
│   ├── raw/                # Downloaded, untouched source CSVs (gitignored — regenerate via ingestion scripts)
│   ├── processed/          # Cleaned, analysis-ready tables (gitignored — regenerate via cleaning scripts)
│   └── external/           # Hand-maintained reference data (team_master.csv) — committed
├── database/                # schema.sql (committed) + pl_intelligence.db (gitignored, regenerate)
├── src/
│   ├── ingestion/           # Download raw data
│   ├── cleaning/            # Clean + normalize
│   ├── validation/          # Automated data-quality checks
│   ├── transformation/      # Build the SQLite DB + Power BI exports
│   ├── analytics/           # League table, H2H, team/player stats
│   ├── ml/                  # Player similarity model
│   └── utils/                # Shared helpers (season labels, paths)
├── powerbi/                  # Model exports + DAX measures + build guide
├── tests/                    # pytest suite
├── docs/                     # Architecture, data, methodology, learning docs
└── assets/                   # Icons/images (no official league/club branding)
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
python -m src.transformation.export_powerbi
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

## Running the Streamlit app

```bash
streamlit run app/Home.py
```

## Power BI

See `powerbi/README.md` for exact model-build steps and the DAX
measure library.

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

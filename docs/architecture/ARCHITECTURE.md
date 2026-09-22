# Architecture

## Pipeline

```
RAW DATA (football-data.co.uk, FPL archive, openfootball/champions-league)
   │  src/ingestion/fetch_matches.py, fetch_players.py, fetch_european.py
   ▼
data/raw/  (verbatim CSVs / text files, gitignored)
   │  src/cleaning/clean_matches.py, clean_players.py, clean_european.py
   │  - drop blank/malformed rows
   │  - parse mixed date formats / semi-structured text match listings
   │  - resolve team names to one canonical list (data/external/team_master.csv)
   │  - enforce dtypes, drop duplicates
   ▼
data/processed/  (matches_clean.csv, players_clean.csv, european_matches_clean.csv)
   │  src/validation/validate_matches.py
   │  - automated assertions: no dup matches, home != away, non-negative
   │    goals, valid seasons, result agrees with goals, 20 teams / 380
   │    matches per season
   ▼
   │  src/transformation/build_database.py
   ▼
database/pl_intelligence.db  (star schema: DIM_* / FACT_*)
   │  src/analytics/*.py  (league table, H2H, team/player stats, European campaigns)
   │  src/ml/player_similarity.py  (KNN similarity)
   ├──► app/  (Streamlit product — reads processed CSVs + the DB)
   └──► src/transformation/export_powerbi.py ──► powerbi/model_exports/*.csv ──► Power BI
```

Every stage is a standalone, re-runnable script (`python -m src.<stage>.<script>`)
with no hidden state — running the whole chain from scratch reproduces
the database byte-for-byte from the same raw inputs.

## Why SQLite

The dataset (5,320 matches, 3,799 player-seasons) is small enough that
SQLite gives a real, standards-compliant SQL database with zero
infrastructure — appropriate for a portfolio project meant to run
locally or on Streamlit Community Cloud. A production version at larger
scale (more competitions, event-level data) would move to Postgres.

## Why a star schema

`FACT_MATCH`, `FACT_TEAM_SEASON` and `FACT_PLAYER_SEASON` each have a
single clear grain, joined to shared dimensions (`DIM_TEAM`,
`DIM_SEASON`, `DIM_DATE`, `DIM_PLAYER`). This is the same shape the
Power BI model uses directly (see `powerbi/README.md`) — no separate
"BI version" of the schema to keep in sync.

## Why the Streamlit app reads both the DB and the CSVs

Analytics functions in `src/analytics/` operate on plain pandas
DataFrames (loaded once via `st.cache_data` from the processed CSVs) so
the exact same functions are unit-tested in `tests/` and used live in
the app — no logic duplicated between "tested code" and "app code".
Direct SQL queries against `database/pl_intelligence.db` are used where
a page benefits from letting SQLite do the aggregation (see
`app/components/data.py:query`).

## App structure

Streamlit's native multi-page mechanism: `app/Home.py` is the entry
point, `app/pages/*.py` are auto-discovered and become the sidebar nav.
Shared code lives in `app/components/` (theming, data access, the intro
animation) so every page stays focused on its own content.

## European Performance module

Extends the same star schema rather than forking it: `DIM_TEAM` was
extended (not duplicated) with the 11 non-Premier-League clubs among
the 20 selected for this module, so `FACT_EUROPEAN_MATCH` and
`FACT_CLUB_SEASON_EUROPE` join to the exact same `dim_team` and
`dim_season` tables the Premier League fact tables use — a club like
Manchester City has one `team_id` referenced from both domestic and
European fact tables, which is what makes the Domestic vs Europe
comparison page possible without a manual join. `DIM_COMPETITION` is a
new, minimal dimension (currently one row) that keeps the schema
extensible to another competition later without reshaping the fact
tables. See `docs/data/DATA_SOURCES.md` for the source (a public-domain
text-format archive) and `src/cleaning/clean_european.py` for the
parsing approach.

## Not yet built

- A real `.pbix` file (model + DAX are ready; building the file itself
  requires Power BI Desktop, not available in this build environment).

See `docs/PROJECT_PROGRESS.md` for current status.

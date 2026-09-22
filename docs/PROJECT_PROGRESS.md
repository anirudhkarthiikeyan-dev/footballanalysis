# Project Progress

## 2026-09-22 — Initial build

### Completed (built, run, and verified — not just planned)

- **Workspace reset.** Old unrelated files (Tic-Tac-Toe Streamlit app,
  NLP scripts) moved to `_archive_old/` per user decision. Fresh project
  structure scaffolded from scratch.
- **Data ingestion.** Real Premier League match data, 2012/13–2025/26
  (14 seasons, 5,320 matches), downloaded from football-data.co.uk.
  Real player-season data, 2019/20–2025/26 (7 seasons, 3,799 rows),
  downloaded from the vaastav/Fantasy-Premier-League public archive.
  Both verified against known real results (Leicester's 2015/16 title,
  Haaland's 36-goal 2022/23 season).
- **Cleaning + entity resolution.** Team names from both sources
  (`"Man United"` / `"Man Utd"` / `"Spurs"` / `"Sheffield Utd"`, etc.)
  resolved to one canonical list (`data/external/team_master.csv`).
  Known blank-row artifact in the 2014/15 source file handled explicitly.
- **Validation.** Automated checks (20 teams/380 matches per season,
  no dup matches, home≠away, result agrees with goals, non-negative
  values) — all passing.
- **Star-schema SQLite database** built: `DIM_TEAM`, `DIM_SEASON`,
  `DIM_DATE`, `DIM_PLAYER`, `FACT_MATCH`, `FACT_TEAM_SEASON`,
  `FACT_PLAYER_SEASON`.
- **Analytics engine**: league table (with real tie-break rules),
  head-to-head, team season journeys, league-wide trends, player
  per-90/percentiles — all with dedicated pytest coverage.
- **ML player similarity** (KNN, standardized per-90 features,
  documented question/method/limitations).
- **Power BI-ready model**: all 7 tables exported to CSV, full DAX
  measure library written and documented. No `.pbix` compiled — Power
  BI Desktop isn't installed in this environment (see `LIMITATIONS.md`).
- **Streamlit product**, 9 pages, built and manually verified live in a
  browser (every page loaded, no console errors, nav confirmed working,
  intro animation confirmed rendering and the Enter/Skip buttons
  confirmed functional): Home (cinematic visual-only intro), League
  Table, League Trends, Team Explorer, Head-to-Head, Match Explorer,
  Player Explorer, Methodology, About.
- **Tests**: 32 pytest tests, all passing
  (`python -m pytest tests/ -v`).
- **Core docs**: README, DATA_SOURCES, DATA_DICTIONARY, ARCHITECTURE,
  METHODOLOGY, LIMITATIONS, FUTURE_IMPROVEMENTS (this file).

### Explicit decisions made without stopping to ask

- Excluded 2016/17–2018/19 from the player module rather than guess
  player→team mapping without a source `teams.csv` for those seasons.
- Cut player data at 2019/20 start and xG/xA at 2022/23 start, per the
  project's own "document coverage rather than fabricate" rule.
- Used football-data.co.uk's real tie-break approximation (points → GD
  → GF) rather than modeling rare historical tie-break edge cases.
- Chose SQLite over a heavier database given the dataset's actual size.
- Removed the deprecated `use_container_width` parameter usage
  proactively (Streamlit flagged it as being removed) — replaced with
  `width='stretch'` across the app.

### Not yet built (see LIMITATIONS.md and FUTURE_IMPROVEMENTS.md)

- European Performance module (20-club Champions League comparison) —
  no CL match data sourced yet.
- Compiled `.pbix` file.
- Playwright automated UI test suite (manual browser verification was
  done instead).
- Full learning log / interview prep covering every topic in the
  original brief — a solid starting version exists, not the exhaustive one.
- Public deployment.

### Next session should start with

1. Source Champions League match data for the European module (check
   football-data.co.uk's European competition CSVs first).
2. If Power BI Desktop becomes available, build and commit the `.pbix`.
3. Expand `docs/learning/LEARNING_LOG.md` and `INTERVIEW_PREP.md`.

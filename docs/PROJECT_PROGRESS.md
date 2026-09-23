# Project Progress

## 2026-09-23 — Power BI dropped: Streamlit is the final, single dashboard layer

### Decision

Power BI is no longer part of the PL Intelligence product. This was a
deliberate scope decision, made after the model had already been
opened and wired successfully in Power BI Desktop (see the entry
below, same day) — not a fallback after something failed. Maintaining
two dashboard layers for a solo portfolio project split effort without
adding proportional value; the Streamlit app already covers everything
a Power BI report would have shown. Streamlit is now the single,
final, complete dashboard layer.

### What was done

- Moved `powerbi/README.md`, `powerbi/dax/measures.dax`, and
  `src/transformation/export_powerbi.py` to
  `_archive_old/powerbi_exploration/` via `git mv` (preserved as
  history, not deleted — real work was done and is worth keeping as a
  record). Added a clear "descoped, archived" note to the top of that
  README.
- Could not move `powerbi/model_exports/` (including the user's saved
  `pl.intelligence.pbix`) because Power BI Desktop had those files open
  on disk at the time (Windows file lock) — left untouched rather than
  forcing it, since force-moving files out from under an open
  application risks corrupting the user's in-progress work. Added
  `powerbi/` and `*.pbix` to `.gitignore` so this leftover local
  folder can never be accidentally committed. The user's `.pbix` is
  theirs to keep, delete, or move manually once they close Power BI
  Desktop — this project no longer references or requires it either way.
- Removed `SQLAlchemy` from `requirements.txt` — grepped the whole
  codebase first and confirmed it was never actually imported anywhere
  (the project always used `sqlite3` directly); it was dead weight
  even before this change.
- Updated every file that referenced Power BI as part of the product:
  `README.md` (full rewrite — final stack, project structure, setup/run
  instructions all Streamlit-only now), `LIMITATIONS.md`,
  `FUTURE_IMPROVEMENTS.md`, `docs/architecture/ARCHITECTURE.md`,
  `docs/learning/LEARNING_LOG.md` (added a "Final architecture, stated
  plainly" section plus reframed the existing Power BI entry as
  "evaluated, then descoped"), `docs/learning/INTERVIEW_PREP.md`
  (reframed "Why did you choose Power BI?" as "Why did you evaluate
  Power BI, and why did you drop it?" — an honest answer, not a deleted
  question), and `app/pages/8_About.py` (technology list and product
  description).
- Ran the full fast test suite before and after (`pytest tests/
  --ignore=tests/ui`): 57/57 passing both times — these changes were
  documentation/dependency-list only plus one small text edit in
  `About.py`, no analytics/pipeline/database code touched.
- Ran the Playwright suite (`tests/ui/`, 41 tests) 5 times in a row to
  check for regressions. Result, honestly reported: it did not pass
  cleanly every time (41/41 in isolation earlier in the project; today's
  back-to-back runs ranged from 41/41 down to 34/41, with a *different*
  set of tests failing each run). Every individual failure passed when
  that specific test was checked in isolation, and no failure pattern
  matched anything touched this session (About.py's text, requirements.txt,
  moved files). This points to environmental resource contention from
  running 5 heavy headless-browser suites back-to-back on a shared
  machine (the user's own Chrome and other applications were also
  running throughout), not an application defect. One genuine
  improvement was made along the way: `tests/ui/conftest.py`'s
  `streamlit_server` fixture now does a one-time browser warm-up
  request before yielding, since the *first* real page load after
  server start pays a one-time Python import/render cost that was
  intermittently exceeding individual tests' timeouts — a legitimate
  root-cause fix (confirmed it eliminated that specific failure mode),
  not a timeout increase to paper over a real bug. Given repeated runs
  were making things slower, not more conclusive, further re-running
  was stopped rather than continued indefinitely. **The fast suite
  (57 tests) is the reliable, repeatable signal; the Playwright suite
  is correct but shows environment-dependent flakiness on this machine
  under sustained back-to-back load — see `FUTURE_IMPROVEMENTS.md`.**

### Verified, not assumed

- Confirmed via `grep` that no other Python file referenced
  `SQLAlchemy`, `export_powerbi`, or the `powerbi/` path before removing
  those references.
- Confirmed the moved files actually stayed tracked by git despite
  `_archive_old/` being gitignored (`git mv` on an already-tracked file
  overrides the ignore rule — verified with `git diff --cached --stat`
  before committing).

---

## 2026-09-23 — Power BI Desktop now available: model verified, docs finalized

Power BI Desktop became available on the user's machine. No PL or
European module code was touched this session (explicitly out of
scope per the user's instructions) — this was inspection plus Power
BI-side documentation only.

### Verified (inspection only, nothing rebuilt)

- All 10 `powerbi/model_exports/*.csv` files exist and their row
  counts match `database/pl_intelligence.db` exactly (header row
  excluded): `dim_team` 48, `dim_season` 14, `dim_date` 1,544,
  `dim_player` 1,603, `dim_competition` 1, `fact_match` 5,320,
  `fact_team_season` 280, `fact_player_season` 3,799,
  `fact_european_match` 1,326, `fact_club_season_europe` 174. No
  re-export was needed.
- CSV encoding confirmed UTF-8 (relevant for accented club names like
  "Atlético Madrid").
- Git repository state confirmed clean; no rebuild of the PL or
  European modules performed or needed.

### Completed (Power BI documentation, prepared for the user to execute in Desktop)

- Rewrote `powerbi/README.md`'s build steps as a literal, ordered
  checklist (Import → Relationships → Measures → Pages) with exact
  click sequences, matching row counts to self-check against, and a
  concrete explanation of the home/away dual-relationship behavior
  (Power BI auto-marks the second one inactive — expected, not an
  error).
- Added 6 new DAX measures (`H2H Team A Id`, `H2H Team B Id`,
  `H2H Meetings`, `H2H Team A Wins`, `H2H Team B Wins`, `H2H Draws`) to
  `powerbi/dax/measures.dax` — the previous session's page table listed
  a Head-to-Head page but never provided the DAX for it, and the
  existing relationships genuinely can't express "matches where either
  side is one of two selected teams" without them. Documented with the
  disconnected-slicer-table setup they require. Total measures: 48.
- `powerbi/dax/measures.dax` is still **unexecuted DAX** — written and
  reviewed against the schema, but not yet opened in Power BI Desktop.
  This is flagged explicitly in the README so it isn't mistaken for
  verified-working.

### Not yet done

- The actual `.pbix` file — this requires manual work in Power BI
  Desktop on the user's machine (import, wire relationships, paste
  measures, build pages), which Claude cannot do remotely. The
  checklist above is designed to make that close to mechanical.
- Confirming the 48 DAX measures actually evaluate without error in
  Desktop (can't be verified from this environment).

---

## 2026-09-22 — Global Search + Playwright browser test suite

### Completed (built, run, and verified — not just planned)

- **Global Search** (`app/pages/0_Global_Search.py`) — a real gap from
  the original brief (section 13) that had gone unbuilt across the
  first two sessions. Searches teams, European clubs, players and
  seasons; results deep-link via `st.switch_page(..., query_params=...)`
  straight to the right page with the right entity pre-selected. Wired
  query-param reading into League Table, Team Explorer, Player
  Explorer, and European Performance.
- **Playwright browser test suite** (`tests/ui/`, 41 tests, kept
  separate from the fast `tests/` suite since it launches a real
  server + headless browser) — covers every page loading, no
  console/network errors, no horizontal overflow, sidebar navigation,
  filters actually changing real data (verified against known facts,
  e.g. selecting 2015/16 shows Leicester above Arsenal), the intro's
  Enter/Skip buttons, and the new search-to-navigation flow.
- **Real debugging, not just writing tests that happened to pass
  first try** — three genuine issues were found and fixed along the
  way, each confirmed with a standalone diagnostic script before
  patching the test suite:
  1. A `networkidle` wait strategy hung indefinitely because
     Streamlit keeps a persistent WebSocket open (network never goes
     idle) — switched to `load` + explicit element waits.
  2. `st.dataframe` renders via a canvas-based grid (glide-data-grid)
     whose JS bundle lazy-loads — a fixed timeout raced it, causing
     table-content assertions to intermittently fail depending on
     browser cache state. Fixed by waiting for the grid's container
     element instead of a fixed delay.
  3. `st.switch_page` navigation was flagged as "not navigating" by
     an early version of the search tests — actually a false alarm:
     the test's own wait condition (`text=Team Explorer`) matched the
     sidebar link that's present on every page, including the
     pre-navigation one, so the URL assertion ran before the real
     navigation completed. Fixed with `page.wait_for_url()`.
- **A hardcoded test port was replaced with a dynamically allocated
  one** after a leftover process from an earlier run caused an entire
  suite run to silently skip instead of testing anything — caught by
  actually reading the skip reason rather than only checking "did it
  fail."
- Fast suite still at 57 tests, all passing throughout — this work
  touched only new files plus 4 pre-existing pages' selectbox default
  logic (additive, not destructive).
- Docs updated: LIMITATIONS, FUTURE_IMPROVEMENTS, README, this file.

### Decisions made without stopping to ask

- Kept the Playwright suite in a separate `tests/ui/` directory with
  its own `conftest.py` rather than merging it into the main suite, so
  the documented fast command (`pytest tests/ --ignore=tests/ui`)
  stays fast and doesn't require Playwright/Chromium to be installed
  just to run the core suite.
- Used `st.query_params` (real, shareable-URL deep-linking) rather than
  `st.session_state` for passing search selections between pages —
  more standard for this use case and lets a search result's
  destination be a real bookmarkable/shareable link.
- Didn't add the Playwright suite to a CI pipeline (no CI exists for
  this project) — listed as a future improvement instead of building
  CI infrastructure that wasn't asked for.

### Not yet built

- Same as before: compiled `.pbix`, full learning-log/interview-prep
  expansion, public deployment, CI wiring for the new Playwright suite.

---

## 2026-09-22 — European Performance module

### Completed (built, run, and verified — not just planned)

- **Sourced real Champions League data.** Found and validated
  openfootball/champions-league, a public-domain, structured text
  archive covering every UEFA Champions League match 2012/13–2025/26.
  Downloaded all 14 season files (`src/ingestion/fetch_european.py`).
- **Built a text-format parser** (`src/cleaning/clean_european.py`)
  handling: mixed date formats, stage-header naming that changed
  across eras (including a literal source typo, "Gruppe G"/"Gruppe H"),
  and knockout legs decided by extra time/penalties — with on-pitch
  goals recorded separately from penalty-shootout scores. The parser
  self-validates against each season file's own declared match count.
- **Extended `team_master.csv`** with 28 new raw-name aliases: 11 new
  non-Premier-League clubs (Real Madrid, Barcelona, Atlético Madrid,
  Sevilla, Valencia, Bayern Munich, Borussia Dortmund, Bayer
  Leverkusen, RB Leipzig, Juventus, Inter Milan) plus Champions-League-
  specific name variants for the 9 Premier League clubs already in
  scope. Caught and fixed two real gaps during testing (a missing
  "Manchester City"/"Manchester United" plain-name alias that was
  silently excluding some of their matches, including a Champions
  League final, from the filtered dataset — found via a failing test,
  not assumed away).
- **Verified against real football history**: all 11 independently
  checkable finals 2012/13–2023/24 match known results exactly (Bayern
  2-1 Dortmund 2013; Real Madrid 4-1 aet Atlético 2014; Man City 1-0
  Inter Milan 2023; etc.). Leicester City's and Aston Villa's real,
  well-known limited Champions League histories (2016/17 only; 2024/25
  only) are reproduced exactly — no fabricated seasons.
- **Extended the database**: `dim_competition`, `fact_european_match`
  (1,326 rows), `fact_club_season_europe` (174 rows — one row per club
  per season actually played, not 20×14). `dim_team` extended from 37
  to 48 clubs.
- **Built the analytics engine** (`src/analytics/european.py`):
  campaign aggregation (with a documented convention for how a
  penalty-shootout-decided tie is counted in win/draw/loss tallies),
  a cross-era 1–7 progression scale, opponent history, European H2H,
  and a domestic-vs-Europe comparison that explicitly flags the two
  competitions' different structures rather than implying equivalence.
- **Built and manually verified the Streamlit page**
  (`app/pages/9_European_Performance.py`, 4 tabs: Club Profile,
  Comparison, European H2H, Domestic vs Europe) live in a browser — no
  console errors, real data confirmed in every tab.
- **25 new tests** (data parsing, database integrity, analytics
  correctness) — full suite now 57 passing tests, up from 32.
- **Power BI model extended**: 3 new tables exported, new DAX measures
  for European campaigns documented in `powerbi/dax/measures.dax`.
- **Docs updated**: DATA_SOURCES, DATA_DICTIONARY, ARCHITECTURE,
  METHODOLOGY, LIMITATIONS, FUTURE_IMPROVEMENTS, README, in-app
  Methodology page, and this file.
- **Existing Premier League functionality confirmed unchanged** — all
  32 original tests still pass; the only changes to already-shipped
  code were additive (new rows in `team_master.csv`, new tables in the
  schema/build script).
- **No audio/music added**, per this session's explicit instruction.

### Decisions made without stopping to ask

- Excluded 3 of the source's own name variants from being needed by
  verifying every raw team-name string actually used for the 20 clubs
  across all 14 files, rather than adding aliases reactively — still
  caught and fixed 2 real gaps via failing tests (see above).
- Counted a penalty-shootout-decided tie's individual leg by its own
  real on-pitch result for win/draw/loss purposes (standard
  competition-statistics convention), not as an automatic draw for
  both legs.
- Scoped "European H2H" to the 20 selected clubs only (meetings
  against other clubs are covered by Opponent History instead) —
  building a full canonical name list for every club that's ever
  played in the Champions League was out of scope.
- Mapped both competition formats (pre-2024/25 groups, 2024/25+ Swiss
  model) onto one progression scale rather than tracking them
  separately, with the comparability caveat documented in three places
  (METHODOLOGY.md, LIMITATIONS.md, the in-app Methodology page).

### Not yet built

- Compiled `.pbix` file (still blocked on Power BI Desktop availability).
- Canonical names for non-selected European opponents (they display
  with their raw source name).
- Europa League / Conference League (out of scope per the brief).
- Full learning log / interview prep expansion (unchanged from last session).

---

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
  **since built; see the entry above this one, dated the same day.**
- Compiled `.pbix` file.
- Playwright automated UI test suite (manual browser verification was
  done instead).
- Full learning log / interview prep covering every topic in the
  original brief — a solid starting version exists, not the exhaustive one.
- Public deployment.

### Next session should start with

*(Superseded by the entry above — the European module was completed
same-day. Remaining open items: compiled `.pbix`, learning log/interview
prep expansion, Playwright tests, public deployment.)*

# Methodology

This mirrors the in-app **Methodology** page (`app/pages/7_Methodology.py`)
as a standalone document.

## Cleaning pipeline

1. **Ingestion** (`src/ingestion/`) — raw season CSVs downloaded
   verbatim, nothing altered.
2. **Cleaning** (`src/cleaning/`) — drop known blank trailing rows
   (a real artifact found in the 2014/15 source file), parse mixed date
   formats (`dd/mm/yy` vs `dd/mm/yyyy`), map raw team-name strings from
   *both* sources to one canonical team list (`data/external/team_master.csv`).
3. **Validation** (`src/validation/validate_matches.py`) — automated
   checks: no duplicate matches, home ≠ away, non-negative goals,
   result code agrees with the goal columns, every season has exactly
   20 teams and 380 matches. Enforced in CI via `tests/test_data_quality.py`.
4. **Transformation** (`src/transformation/build_database.py`) —
   cleaned rows load into the star-schema SQLite database.

## League table & tie-breaks

Points: 3 for a win, 1 for a draw, 0 for a loss. Ties: **points → goal
difference → goals scored → alphabetical**, matching the Premier
League's real rule for the large majority of seasons. Rare historical
play-off or head-to-head tie-breaks are not modeled (see `LIMITATIONS.md`).
Verified against a known result: Leicester City's 2015/16 title (81
points, 23-12-3) — `tests/test_database.py::test_leicester_2015_16_title`.

## Player per-90 and percentiles

Per-90 rate = raw stat ÷ (minutes / 90). Percentiles are always computed
**within the same season + position cohort** at a 450+ minute threshold
(~5 full matches) to avoid small-sample noise and apples-to-oranges
comparisons across roles. See `src/analytics/player_stats.py`.

## Player similarity model

**Question:** which outfield players had a statistically similar per-90
production profile in a season?

**Method:** k-nearest neighbors (scikit-learn) on standardized per-90
features — `goals/90, assists/90, xG/90, xA/90` — restricted to
2022/23–2025/26 (the only seasons with all four features), outfield
players only, 450+ minutes.

**Why ML:** comparing four correlated rate stats simultaneously needs a
distance metric over a multi-dimensional space — a plain sort or filter
answers "who scored the most," not "who looks statistically like player X."

**Normalization:** `StandardScaler` (zero mean, unit variance) fit per
search cohort, so goals (larger raw values) don't dominate assists/xA
purely from unit scale.

**Distance metric:** Euclidean distance on standardized features
(`sklearn.neighbors.NearestNeighbors`, default metric).

**Limitations:** no positional sub-role awareness (a standardized
striker and a standardized winger with similar output can look
"similar" even though their in-game role differs), no minutes-weighting
beyond the cutoff, and small season/position cohorts (e.g. few forwards
clearing 450 minutes) mean the neighbor pool can be small. Full writeup
in `src/ml/player_similarity.py`.

## European Performance module

**Scope:** the 20 clubs named in the project brief (9 Premier League,
5 Spanish, 4 German, 2 Italian), UEFA Champions League only,
2012/13–2025/26. A club appears for a season **only if it actually
played in that season's competition** — no season is fabricated for a
club that didn't qualify (verified in tests, e.g. Leicester City's
only campaign in range is 2016/17, Aston Villa's is 2024/25).

**Source:** openfootball/champions-league, a public-domain, structured
text archive (see `docs/data/DATA_SOURCES.md`). Parsed by
`src/cleaning/clean_european.py`.

**On-pitch goals vs penalty shootouts:** a knockout tie settled by
penalties is recorded with the real goals scored during play (including
extra time) as `home_goals`/`away_goals` — the shootout score is stored
separately in `penalty_home_goals`/`penalty_away_goals` and is never
counted as goals. Every one of the 14 season finals in this dataset was
checked against independently known real results as part of building
this module (e.g. Real Madrid 4-1 aet Atlético Madrid, 2014; Man City
1-0 Inter Milan, 2023).

**Win/draw/loss counting:** each match (each leg of a two-legged tie)
is counted individually by its own on-pitch result — a team can record
a genuine "win" in a leg it later lost the tie from on aggregate/
penalties, which matches how competition-statistics pages conventionally
present a club's record (see `src/analytics/european.py` docstring).

**Progression/"finish" scale:** stage formats changed over the dataset's
range (2012/13–2023/24 used a traditional 8-group stage; 2024/25+ uses
a 36-team "Swiss model" league phase plus a playoff round before the
Round of 16). Both are mapped onto one consistent 1–7 progression scale
(Group/League Phase → Playoff Round → Round of 16 → Quarterfinal →
Semifinal → Runner-up → Winner) so a club's best finish is comparable
across eras — with the caveat that "reached the knockout stage" meant
finishing top-2 of an 8-team group pre-2024/25, versus finishing top-8
of 36 teams from 2024/25 on; the scale doesn't fully normalize that
difficulty difference (see `LIMITATIONS.md`).

**Domestic vs Europe comparison:** presented side by side, explicitly
labeled as structurally different competitions (a 38-match balanced
league vs a campaign that can end after 6–13 matches) — not framed as
an apples-to-apples statistic.

## What's intentionally not shown

- No player data before 2019/20 — not reliably available from the source.
- No xG/xA before 2022/23 — not tracked by the source; shown as
  missing, never zero.
- No fabricated advanced metrics (progressive passes, pressures, etc.)
  — not available from a free, reliable source across enough of the
  historical range to be worth including.
- No player-level European statistics — the Champions League source is
  match-level only.

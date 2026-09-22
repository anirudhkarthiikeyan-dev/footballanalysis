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

## What's intentionally not shown

- No player data before 2019/20 — not reliably available from the source.
- No xG/xA before 2022/23 — not tracked by the source; shown as
  missing, never zero.
- No fabricated advanced metrics (progressive passes, pressures, etc.)
  — not available from a free, reliable source across enough of the
  historical range to be worth including.
- European Performance module — on the roadmap, not yet built (see
  `docs/PROJECT_PROGRESS.md`).

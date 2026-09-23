# PL Intelligence — Power BI Model (descoped, archived)

## This is no longer part of the PL Intelligence product

Power BI was explored during development — a real star-schema export
and a 48-measure DAX library were built and documented (below), and
the model was successfully opened and wired up in Power BI Desktop.
It was then **intentionally dropped** in favor of a Streamlit-only
final product, to keep the deliverable focused rather than maintaining
two parallel dashboard layers. See `docs/PROJECT_PROGRESS.md` for the
decision and date.

**Nothing here is required to run PL Intelligence.** The files below
are kept only as an honest record of the exploration — not because
Power BI is a build dependency. The rest of this document is the
original build guide, unedited, for reference.

## Original status note (kept for history)

This folder contains a **real, working data model export and full DAX
documentation**. No `.pbix` is committed to the repo yet (Power BI
Desktop wasn't available when this model was built) — build it
locally by following the steps below. All 10 `model_exports/*.csv`
files are current and were verified row-for-row against the live
database before this note was written (see `docs/PROJECT_PROGRESS.md`
for the verification date).

## What's here

- `model_exports/*.csv` — the exact star-schema tables from
  `database/pl_intelligence.db`, exported by
  `src/transformation/export_powerbi.py`. Re-run that script any time
  the underlying data changes to refresh these files. Now includes the
  European Performance module tables (`dim_competition`,
  `fact_european_match`, `fact_club_season_europe`).
- `dax/measures.dax` — every DAX measure listed in the project spec
  (points, win %, goals/match, clean sheets, home/away splits, per-90
  player metrics, percentile rank, plus European campaign measures),
  written to the model's actual column names below.

## Building the model in Power BI Desktop

### 1. Import

**Get Data → Folder** → point at the full path to `powerbi/model_exports/`
→ **Combine & Transform** is not needed (don't combine into one table) —
in the navigator, tick all 10 files and **Load** each as its own table.
(Equivalently: **Get Data → Text/CSV**, once per file.) The files are
UTF-8 — Power BI's CSV import auto-detects this, but if any accented
club name (`Atlético Madrid`, `Bayern München`) looks garbled after
load, re-import that one file and explicitly set **File Origin: 65001:
Unicode (UTF-8)** in the import dialog.

You should end up with exactly these 10 tables, matching row counts
(header row not counted) as of this check:

| Table | Rows | Grain |
|---|---|---|
| `dim_team` | 48 | one row per club (37 Premier League + 11 European-only) |
| `dim_season` | 14 | one row per season, 2012/13–2025/26 |
| `dim_date` | 1,544 | one row per calendar date with a match |
| `dim_player` | 1,603 | one row per unique player |
| `dim_competition` | 1 | "UEFA Champions League" |
| `fact_match` | 5,320 | one row per Premier League match |
| `fact_team_season` | 280 | one row per team per PL season |
| `fact_player_season` | 3,799 | one row per player per season, 2019/20–2025/26 |
| `fact_european_match` | 1,326 | one row per Champions League match (each leg) |
| `fact_club_season_europe` | 174 | one row per club per CL campaign *actually played* |

If any count doesn't match, stop and re-export rather than continuing
— see "Refreshing data" below.

### 2. Relationships

In **Model view**, create these (drag `team_id`/`season_id`/etc. from
the dimension table onto the matching column in the fact table — Power
BI infers direction automatically as dimension → fact, one-to-many):

| From | To |
|---|---|
| `dim_team[team_id]` | `fact_match[home_team_id]` |
| `dim_team[team_id]` | `fact_match[away_team_id]` |
| `dim_team[team_id]` | `fact_team_season[team_id]` |
| `dim_team[team_id]` | `fact_player_season[team_id]` |
| `dim_team[team_id]` | `fact_club_season_europe[team_id]` |
| `dim_team[team_id]` | `fact_european_match[home_team_id]` |
| `dim_team[team_id]` | `fact_european_match[away_team_id]` |
| `dim_season[season_id]` | `fact_match[season_id]` |
| `dim_season[season_id]` | `fact_team_season[season_id]` |
| `dim_season[season_id]` | `fact_player_season[season_id]` |
| `dim_season[season_id]` | `fact_club_season_europe[season_id]` |
| `dim_season[season_id]` | `fact_european_match[season_id]` |
| `dim_date[date_id]` | `fact_match[date_id]` |
| `dim_player[player_id]` | `fact_player_season[player_id]` |
| `dim_competition[competition_id]` | `fact_european_match[competition_id]` |
| `dim_competition[competition_id]` | `fact_club_season_europe[competition_id]` |

**`dim_team` has two relationships each to `fact_match` and to
`fact_european_match`** (home + away). Power BI does not allow two
*active* relationships between the same pair of tables — when you
create the second one, it will automatically draw it as a **dashed
line (inactive)** in Model view. This is expected, not an error. Leave
`home_team_id` as the active one in both cases (that's the default —
the first relationship you create becomes active). 42 of the 48
measures in `dax/measures.dax` and 6 of the 7 suggested pages below work fine with
just that — `fact_team_season` and `fact_club_season_europe` already
carry pre-computed home/away splits, so you don't need
`USERELATIONSHIP` for standard team/season/player KPIs. The one
exception is **Head-to-Head**, which needs matches where *either* side
is one of two selected teams — see its own recipe below, which uses a
disconnected slicer table instead of the relationship graph (simpler
than juggling `USERELATIONSHIP` for this specific case).

Two European FK columns (`fact_european_match[home_team_id]` /
`[away_team_id]`) are legitimately **blank** on many rows — that's not
missing data, it's a club outside the 20 selected clubs (e.g. a group
opponent). Use `home_team_display` / `away_team_display` (plain text
columns, always populated) for labels on any visual involving
opponents outside the 20; only use the ID relationship when you
specifically want to filter/slice by one of the 20.

### 3. Measures

Add a new table: **Model view → New Table**, formula bar: type
`Measures = {}` (a placeholder blank table just to hold measures, a
standard Power BI pattern) → Enter. Then, for every measure in
`powerbi/dax/measures.dax` (48 measures, grouped by section — Team/
League KPIs, Match-level, Form, Player KPIs, European Performance,
Head-to-Head): right-click the `Measures` table → **New Measure** →
paste that measure's full definition (`Name := formula`) into the
formula bar → Enter. Do this once per measure — there's no bulk-import
for measures in Power BI Desktop.

The 6 **Head-to-Head** measures need two small setup steps first
(disconnected slicer tables) — see the Head-to-Head row in the page
table below and the comment block above those measures in
`dax/measures.dax` for the exact steps. Build those after the other 42.

**Verify as you go**: this DAX was written and documented against the
schema but has not previously been executed in Power BI Desktop (it
wasn't installed when it was written). Most should paste in cleanly,
but if any measure shows a red squiggle or an error on creation, that's
genuinely new information — check the column/table name in the error
against the tables above (case and underscores must match exactly).

### 4. Build the pages

| Page | Primary table(s) | Key visuals |
|---|---|---|
| League Overview | `fact_team_season` | Table (league table), KPI cards (Points, Win %, Goals/Match) |
| Team Performance | `fact_team_season`, `fact_match` | Line chart (position by season), bar (home/away win %) |
| Player Performance | `fact_player_season` | Table with Goals/90, Assists/90, xG/90, percentile rank |
| Season Trends | `fact_match` | Line chart (goals/match by season), stacked bar (result mix) |
| Head-to-Head | `fact_match` + 2 disconnected selector tables | 2 slicers (Team A, Team B), KPI cards (H2H Meetings, H2H Team A Wins, H2H Draws, H2H Team B Wins) — see setup steps above |
| Advanced Analytics | `fact_player_season` | Scatter (xG vs actual goals), percentile matrix using `Goals per 90 Percentile` |
| European Performance | `fact_club_season_europe`, `fact_european_match` | Table of campaigns, stage-reached line chart, KPI cards (EU Win %, EU Goals per Match) |

## Refreshing data

Re-run the pipeline, then re-export:

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

Then in Power BI Desktop: **Home → Refresh**.

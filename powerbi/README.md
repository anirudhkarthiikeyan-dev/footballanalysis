# PL Intelligence — Power BI Model

## Status

This folder contains a **real, working data model export and full DAX
documentation** — but no `.pbix` file, because Power BI Desktop is not
installed in the environment this project was built in. Opening and
wiring the model below takes ~10 minutes in Power BI Desktop. This is
documented honestly rather than claiming a `.pbix` exists when it
doesn't (see `docs/PROJECT_PROGRESS.md`).

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

1. **Get Data → Folder** → point at `powerbi/model_exports/`, or
   **Get Data → Text/CSV** once per file.
2. Load all ten tables: `dim_team`, `dim_season`, `dim_date`,
   `dim_player`, `dim_competition`, `fact_match`, `fact_team_season`,
   `fact_player_season`, `fact_european_match`, `fact_club_season_europe`.
3. In **Model view**, create these relationships (all single-direction,
   dimension → fact):
   - `dim_team[team_id]` → `fact_match[home_team_id]`
   - `dim_team[team_id]` → `fact_match[away_team_id]` *(mark as inactive;
     activate with `USERELATIONSHIP` in away-specific measures, or
     duplicate `dim_team` as `dim_team_away` for simplicity)*
   - `dim_team[team_id]` → `fact_team_season[team_id]`
   - `dim_team[team_id]` → `fact_player_season[team_id]`
   - `dim_team[team_id]` → `fact_club_season_europe[team_id]`
   - `dim_team[team_id]` → `fact_european_match[home_team_id]` *(inactive; this FK is NULL whenever the opponent isn't one of the 20 selected clubs — use `home_team_display`/`away_team_display` text columns for opponent labels instead of relying on the join)*
   - `dim_team[team_id]` → `fact_european_match[away_team_id]` *(inactive, same reason)*
   - `dim_season[season_id]` → `fact_match[season_id]`
   - `dim_season[season_id]` → `fact_team_season[season_id]`
   - `dim_season[season_id]` → `fact_player_season[season_id]`
   - `dim_season[season_id]` → `fact_club_season_europe[season_id]`
   - `dim_season[season_id]` → `fact_european_match[season_id]`
   - `dim_date[date_id]` → `fact_match[date_id]`
   - `dim_player[player_id]` → `fact_player_season[player_id]`
   - `dim_competition[competition_id]` → `fact_european_match[competition_id]`
   - `dim_competition[competition_id]` → `fact_club_season_europe[competition_id]`
4. Add a **Measures** table (New Table → blank) and paste in each
   measure from `dax/measures.dax` as a separate `New Measure`.
5. Build the pages listed below.

## Suggested pages

| Page | Primary table(s) | Key visuals |
|---|---|---|
| League Overview | `fact_team_season` | Table (league table), KPI cards (Points, Win %, Goals/Match) |
| Team Performance | `fact_team_season`, `fact_match` | Line chart (position by season), bar (home/away win %) |
| Player Performance | `fact_player_season` | Table with Goals/90, Assists/90, xG/90, percentile rank |
| Season Trends | `fact_match` | Line chart (goals/match by season), stacked bar (result mix) |
| Head-to-Head | `fact_match` (filtered to two teams) | Table of meetings, KPI cards |
| Advanced Analytics | `fact_player_season` | Scatter (xG vs actual goals), percentile matrix |
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

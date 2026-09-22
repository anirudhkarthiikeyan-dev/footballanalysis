# Data Dictionary

Grain and field reference for every table in `database/pl_intelligence.db`.
Types are the SQLite storage types actually used.

## DIM_TEAM
One row per club that appears in the match dataset (37 clubs across
2012/13–2025/26, reflecting promotion/relegation).

| Column | Type | Notes |
|---|---|---|
| team_id | INTEGER PK | Stable surrogate key |
| canonical_name | TEXT | Full club name, e.g. "Manchester United" |
| short_name | TEXT | Display-friendly short name, e.g. "Man United" |

## DIM_SEASON
One row per season, 2012/13–2025/26.

| Column | Type | Notes |
|---|---|---|
| season_id | INTEGER PK | |
| season_label | TEXT | e.g. "2015/16" |
| start_year | INTEGER | e.g. 2015 |

## DIM_DATE
One row per calendar date on which at least one match was played.

| Column | Type | Notes |
|---|---|---|
| date_id | INTEGER PK | YYYYMMDD |
| full_date | TEXT | ISO date string |
| day / month / year | INTEGER | |
| weekday_name | TEXT | e.g. "Saturday" |

## DIM_PLAYER
One row per unique player name appearing in the 2019/20–2025/26 player data.

| Column | Type | Notes |
|---|---|---|
| player_id | INTEGER PK | |
| player_name | TEXT | Full name (first + second) |
| web_name | TEXT | FPL's short display name |

## FACT_MATCH
Grain: **one row per match**. 5,320 rows (14 seasons × 380 matches).

| Column | Type | Notes |
|---|---|---|
| match_id | TEXT PK | e.g. "M00001" |
| season_id, date_id, home_team_id, away_team_id | INTEGER FK | |
| home_goals, away_goals | INTEGER | Full-time |
| home_goals_ht, away_goals_ht | INTEGER | Half-time |
| result | TEXT | "H" / "D" / "A" (full-time) |
| result_ht | TEXT | Half-time result |
| referee | TEXT | |
| home_shots, away_shots | INTEGER | |
| home_shots_on_target, away_shots_on_target | INTEGER | |
| home_corners, away_corners | INTEGER | |
| home_yellow_cards, away_yellow_cards | INTEGER | |
| home_red_cards, away_red_cards | INTEGER | |

## FACT_TEAM_SEASON
Grain: **one row per team per season**. 280 rows (14 × 20).
Computed by `src/analytics/league_table.py` from FACT_MATCH — final
standings for that season, both overall and home/away splits.

| Column | Type | Notes |
|---|---|---|
| team_id, season_id | INTEGER FK | Composite PK |
| played, wins, draws, losses | INTEGER | |
| goals_for, goals_against | INTEGER | |
| points | INTEGER | 3×wins + draws |
| home_wins/draws/losses, away_wins/draws/losses | INTEGER | |
| clean_sheets | INTEGER | Matches where the team conceded 0 |
| league_position | INTEGER | 1 = champions; tie-break: points → GD → GF → alphabetical |

## FACT_PLAYER_SEASON
Grain: **one row per player per season**, 2019/20–2025/26 only.
3,799 rows.

| Column | Type | Notes |
|---|---|---|
| player_season_id | TEXT PK | e.g. "P00001" |
| player_id, team_id, season_id | INTEGER FK | |
| position | TEXT | GK / DEF / MID / FWD |
| minutes, starts | INTEGER | `starts` may be NULL for early seasons in range |
| goals_scored, assists, clean_sheets, goals_conceded | INTEGER | |
| yellow_cards, red_cards | INTEGER | |
| saves, own_goals, penalties_missed, bonus | INTEGER | |
| expected_goals, expected_assists, expected_goal_involvements, expected_goals_conceded | REAL | **NULL before 2022/23** — not tracked by the source, never fabricated as 0 |
| now_cost_m | REAL | FPL's player value in £m at end of the season pulled, informational only |

Only players with `minutes > 0` in a season are included (i.e. squad
players who never played that season are excluded from that season's rows).

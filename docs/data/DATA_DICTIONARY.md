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

## DIM_COMPETITION
One row (currently): `{competition_id: 1, name: "UEFA Champions League"}`.
A separate dimension exists so the model can extend to another
competition later without changing FACT_EUROPEAN_MATCH's shape.

## FACT_EUROPEAN_MATCH
Grain: **one row per Champions League match** (each two-legged
knockout tie contributes 2 rows, one per leg — matching how the
matches were actually played) involving at least one of the 20 clubs
selected for the European Performance module. 1,326 rows, 2012/13–2025/26.

| Column | Type | Notes |
|---|---|---|
| match_id | TEXT PK | e.g. "EU00001" |
| competition_id, season_id | INTEGER FK | |
| stage | TEXT | Normalized: group_stage / league_phase / playoff_round / round_of_16 / quarterfinal / semifinal / final |
| stage_order | INTEGER | 1 (earliest) – 6 (final) — see `src/analytics/european.py` for the full progression scale including win/runner-up split |
| match_date | TEXT | ISO date |
| home_team_id, away_team_id | INTEGER FK, **nullable** | NULL when that side is an opponent outside the 20-club scope (e.g. a group-stage opponent not among the 20) |
| home_team_display, away_team_display | TEXT | Always populated — canonical name for a selected club, source name otherwise |
| home_goals, away_goals | INTEGER | **On-pitch goals only** — a penalty-shootout score is never counted here |
| result | TEXT | "H"/"D"/"A" for *this match's own scoreline* (a two-legged tie's individual leg can be a genuine win even if the aggregate tie was later decided by penalties) |
| went_to_extra_time, decided_by_penalties | INTEGER (0/1) | |
| penalty_home_goals, penalty_away_goals | INTEGER, nullable | Shootout score, only when `decided_by_penalties = 1` |

## FACT_CLUB_SEASON_EUROPE
Grain: **one row per club per season it actually participated in** —
never a fabricated row for a season a club didn't qualify for. 174 rows
across the 20 selected clubs (participation varies from 1 season for a
club like Leicester City to all 14 for ever-present clubs like Real
Madrid). Computed from FACT_EUROPEAN_MATCH by `src/analytics/european.py::club_season_campaigns`.

| Column | Type | Notes |
|---|---|---|
| team_id, season_id, competition_id | INTEGER FK | Composite PK |
| matches_played, wins, draws, losses | INTEGER | Summed from each individual match's own result (standard competition-statistics convention — see METHODOLOGY.md) |
| goals_for, goals_against, goal_difference | INTEGER | |
| win_pct, goals_per_match | REAL | |
| clean_sheets | INTEGER | |
| finish_rank | INTEGER | 1=Group/League Phase, 2=Playoff Round, 3=Round of 16, 4=Quarterfinal, 5=Semifinal, 6=Runner-up, 7=Winner |
| finish_label | TEXT | Human-readable version of `finish_rank` |

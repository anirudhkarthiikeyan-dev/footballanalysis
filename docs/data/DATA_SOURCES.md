# Data Sources

## 1. Match results & statistics — football-data.co.uk

- **URL:** https://www.football-data.co.uk/englandm.php
- **Files used:** `https://www.football-data.co.uk/mmz4281/{season_code}/E0.csv`
  for each season 2012/13–2025/26 (season codes `1213`…`2526`)
- **Coverage:** 14 seasons, 5,320 matches, all fields present for every season
- **Fields used:** date, home/away team, full-time and half-time goals and
  result, referee, shots, shots on target, corners, yellow/red cards
- **Fields available but NOT used:** the many bookmaker-odds columns
  (B365*, BW*, PS*, etc.) — out of scope for this project, not
  analytics we compute
- **License / usage notes:** football-data.co.uk states its data is
  free to use for personal/non-commercial analysis; it does not publish
  a formal machine-readable license. Data is not redistributed in this
  repository — `data/raw/` is gitignored, and `src/ingestion/fetch_matches.py`
  re-downloads it fresh from the source.
- **Known limitations:** does not publish player-level data, xG/xA, or
  possession stats for this era.

## 2. Player-season statistics — vaastav/Fantasy-Premier-League

- **URL:** https://github.com/vaastav/Fantasy-Premier-League
- **Files used:** `data/{season}/players_raw.csv` and
  `data/{season}/teams.csv` for seasons 2019-20 through 2025-26
- **Coverage:** 7 seasons, 3,799 player-season rows, 1,603 unique players
- **Why not 2016/17–2018/19:** `players_raw.csv` exists for those
  seasons but the source doesn't publish a matching `teams.csv` for
  them, so player→team assignment can't be done reliably without
  guessing. Rather than guess (and risk a wrong club attribution), those
  three seasons are excluded from the player module entirely — see
  `src/ingestion/fetch_players.py` for the full reasoning.
- **Fields used:** name, team, position, minutes, starts, goals,
  assists, clean sheets, cards, saves, own goals, bonus points, cost,
  and (2022/23+) expected_goals, expected_assists,
  expected_goal_involvements, expected_goals_conceded
- **Why xG/xA start at 2022/23:** the Fantasy Premier League game itself
  only began publishing these fields around that season. Earlier
  player-season rows have `expected_goals`/`expected_assists` as `NULL`
  — never a fabricated `0`.
- **License / usage notes:** community-maintained public archive of
  data originally published by the official Fantasy Premier League
  game/API. Used here for non-commercial analytics; not redistributed
  in raw form (`data/raw/` gitignored).
- **Known limitations:** this is Fantasy Premier League's own tracked
  data, not a professional match-event provider — it doesn't include
  progressive passes, pressures, touches-in-box or similar advanced
  event metrics.

## 3. Team name reference — hand-built (`data/external/team_master.csv`)

- **Purpose:** resolves every raw team-name string seen across both
  sources above (e.g. `"Man United"`, `"Man Utd"` → `Manchester United`;
  `"Spurs"` → `Tottenham Hotspur`) to one canonical name, so the same
  club is never split into two entities because of source-specific
  naming.
- **Maintained by:** this project. Extend it if a new source or a new
  club naming variant is added later.

## 4. Not yet sourced

- **Champions League match data** for the planned European Performance
  module (20 clubs) — not yet acquired. See `docs/PROJECT_PROGRESS.md`.
- **Advanced positional/tracking data** (progressive passes, pressures,
  xG shot maps) — no free, reliable, full-history source identified;
  would need a paid provider (e.g. Opta/StatsBomb) to do properly.

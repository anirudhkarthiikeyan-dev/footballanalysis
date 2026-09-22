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

## 3. European Performance module — openfootball/champions-league

- **URL:** https://github.com/openfootball/champions-league
- **Format:** `football.txt` — a structured plain-text match listing
  (date, stage, teams, score), documented at http://openfootball.github.io.
- **Files used:** `{season}/cl.txt` for every UEFA Champions League
  season 2012/13–2025/26.
- **Coverage:** every match (group/league phase and knockout) in every
  season in range. This project filters that full dataset down to
  matches involving at least one of the 20 clubs selected for the
  European Performance module (project brief section 22) — see
  `src/cleaning/clean_european.py` for the exact list and the 20-club
  scope rationale.
- **License:** the repository's README explicitly states it is *"a
  free open public domain football database... Free open public
  domain football datasets for Europe."* It is community-maintained,
  sourced primarily from Wikipedia's competition articles (see the
  repo's own `NOTES.md`) rather than an official UEFA feed.
- **Verification performed:** every one of the 14 finals in this
  dataset (2012/13–2025/26) was checked against independently known
  real results (e.g. Bayern Munich 2-1 Borussia Dortmund, 2013; Man
  City 1-0 Inter Milan, 2023) — see `tests/test_european_data.py::test_known_finals_match_real_history`.
  Leicester City's and Aston Villa's participation seasons were also
  checked against their real, well-known Champions League debut
  campaigns (2016/17 and 2024/25 respectively) to confirm no season
  was fabricated for a club that didn't actually qualify.
- **Format quirks handled during cleaning** (see `src/cleaning/clean_european.py`
  docstring for full detail):
  - Team names vary by season/source formatting (e.g. `"Manchester
    City"` vs `"Manchester City FC"`, `"Bayern München"` vs `"FC Bayern
    München"`) — resolved via `data/external/team_master.csv`, the same
    canonical mapping used for the Premier League data.
  - Stage section headers vary by era: `"Group A"`.."Group H" (and a
    literal source typo, `"Gruppe G"`/`"Gruppe H"`, for 2020/21–2022/23)
    for the traditional format; `"League, Matchday N"` /
    `"Playoffs, Matchday N"` for the 2024/25+ Swiss-model format. All
    normalized to one consistent stage scale.
  - Knockout legs decided by extra time and/or penalties use inline
    annotations (e.g. `"3-4 pen. 1-1 a.e.t. (1-1, 0-1)"`) — parsed to
    record the actual **on-pitch goals** separately from the penalty
    shootout score, since a shootout goal is not a real goal.
- **Known limitations:** community-maintained, not an official UEFA
  data feed — see `LIMITATIONS.md`. No player-level European stats are
  available from this source.

## 4. Team name reference — hand-built (`data/external/team_master.csv`)

- **Purpose:** resolves every raw team-name string seen across both
  sources above (e.g. `"Man United"`, `"Man Utd"` → `Manchester United`;
  `"Spurs"` → `Tottenham Hotspur`) to one canonical name, so the same
  club is never split into two entities because of source-specific
  naming.
- **Maintained by:** this project. Extend it if a new source or a new
  club naming variant is added later.

## 5. Not sourced

- **Advanced positional/tracking data** (progressive passes, pressures,
  xG shot maps) — no free, reliable, full-history source identified;
  would need a paid provider (e.g. Opta/StatsBomb) to do properly.
- **Player-level European statistics** — the openfootball archive is
  match-level only; no free, reliable per-player Champions League stat
  source covering the full 2012/13–2025/26 range was identified.
- **Europa League / Conference League data** — out of scope per the
  project brief (Champions League only for the European module).

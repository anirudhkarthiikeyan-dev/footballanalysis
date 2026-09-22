-- PL Intelligence analytical database schema.
-- Star-schema oriented: FACT_MATCH is the primary fact table, joined to
-- DIM_TEAM, DIM_SEASON and DIM_DATE. Designed to be exported/imported
-- into Power BI unchanged (see powerbi/ for the model documentation).

CREATE TABLE dim_team (
    team_id       INTEGER PRIMARY KEY,
    canonical_name TEXT NOT NULL UNIQUE,
    short_name    TEXT NOT NULL
);

CREATE TABLE dim_season (
    season_id     INTEGER PRIMARY KEY,
    season_label  TEXT NOT NULL UNIQUE,   -- e.g. '2012/13'
    start_year    INTEGER NOT NULL
);

CREATE TABLE dim_date (
    date_id       INTEGER PRIMARY KEY,    -- YYYYMMDD
    full_date     TEXT NOT NULL UNIQUE,
    day           INTEGER NOT NULL,
    month         INTEGER NOT NULL,
    year          INTEGER NOT NULL,
    weekday_name  TEXT NOT NULL
);

CREATE TABLE fact_match (
    match_id              TEXT PRIMARY KEY,
    season_id             INTEGER NOT NULL REFERENCES dim_season(season_id),
    date_id               INTEGER NOT NULL REFERENCES dim_date(date_id),
    home_team_id          INTEGER NOT NULL REFERENCES dim_team(team_id),
    away_team_id          INTEGER NOT NULL REFERENCES dim_team(team_id),
    home_goals            INTEGER NOT NULL,
    away_goals            INTEGER NOT NULL,
    home_goals_ht         INTEGER,
    away_goals_ht         INTEGER,
    result                TEXT NOT NULL CHECK (result IN ('H','D','A')),
    result_ht              TEXT,
    referee               TEXT,
    home_shots            INTEGER,
    away_shots            INTEGER,
    home_shots_on_target  INTEGER,
    away_shots_on_target  INTEGER,
    home_corners          INTEGER,
    away_corners          INTEGER,
    home_yellow_cards     INTEGER,
    away_yellow_cards     INTEGER,
    home_red_cards        INTEGER,
    away_red_cards        INTEGER,
    CHECK (home_team_id != away_team_id)
);

CREATE INDEX idx_fact_match_season ON fact_match(season_id);
CREATE INDEX idx_fact_match_home_team ON fact_match(home_team_id);
CREATE INDEX idx_fact_match_away_team ON fact_match(away_team_id);
CREATE INDEX idx_fact_match_date ON fact_match(date_id);

-- FACT_TEAM_SEASON: pre-aggregated one row per team per season, used by
-- the league table, team profile and trend pages without recomputing
-- from fact_match every time.
-- DIM_PLAYER / FACT_PLAYER_SEASON: player module covers 2019/20-2025/26
-- only (see docs/data/DATA_SOURCES.md for why earlier seasons are
-- excluded). expected_* columns are NULL before 2022/23 by design -
-- never a fabricated 0.
CREATE TABLE dim_player (
    player_id     INTEGER PRIMARY KEY,
    player_name   TEXT NOT NULL,
    web_name      TEXT
);

CREATE TABLE fact_player_season (
    player_season_id      TEXT PRIMARY KEY,
    player_id             INTEGER NOT NULL REFERENCES dim_player(player_id),
    team_id                INTEGER NOT NULL REFERENCES dim_team(team_id),
    season_id             INTEGER NOT NULL REFERENCES dim_season(season_id),
    position               TEXT NOT NULL,
    minutes                INTEGER NOT NULL,
    starts                 INTEGER,
    goals_scored           INTEGER NOT NULL,
    assists                INTEGER NOT NULL,
    clean_sheets           INTEGER,
    goals_conceded         INTEGER,
    yellow_cards           INTEGER,
    red_cards              INTEGER,
    saves                  INTEGER,
    own_goals               INTEGER,
    penalties_missed        INTEGER,
    bonus                   INTEGER,
    expected_goals           REAL,
    expected_assists         REAL,
    expected_goal_involvements REAL,
    expected_goals_conceded  REAL,
    now_cost_m              REAL
);

CREATE INDEX idx_fact_player_season_season ON fact_player_season(season_id);
CREATE INDEX idx_fact_player_season_team ON fact_player_season(team_id);
CREATE INDEX idx_fact_player_season_player ON fact_player_season(player_id);

CREATE TABLE fact_team_season (
    team_id        INTEGER NOT NULL REFERENCES dim_team(team_id),
    season_id      INTEGER NOT NULL REFERENCES dim_season(season_id),
    played         INTEGER NOT NULL,
    wins           INTEGER NOT NULL,
    draws          INTEGER NOT NULL,
    losses         INTEGER NOT NULL,
    goals_for      INTEGER NOT NULL,
    goals_against  INTEGER NOT NULL,
    points         INTEGER NOT NULL,
    home_wins      INTEGER NOT NULL,
    home_draws     INTEGER NOT NULL,
    home_losses    INTEGER NOT NULL,
    away_wins      INTEGER NOT NULL,
    away_draws     INTEGER NOT NULL,
    away_losses    INTEGER NOT NULL,
    clean_sheets   INTEGER NOT NULL,
    league_position INTEGER NOT NULL,
    PRIMARY KEY (team_id, season_id)
);

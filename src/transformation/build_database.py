"""Build the PL Intelligence SQLite analytical database from the cleaned
match table: creates the schema, loads dimension tables, loads
FACT_MATCH, and computes + loads FACT_TEAM_SEASON.
"""
import sqlite3

import pandas as pd

from src.analytics.european import club_season_campaigns
from src.analytics.league_table import all_seasons_team_table
from src.utils.seasons import PROJECT_ROOT

SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
DB_PATH = PROJECT_ROOT / "database" / "pl_intelligence.db"
CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "matches_clean.csv"
PLAYERS_CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "players_clean.csv"
EU_CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "european_matches_clean.csv"
TEAM_MASTER_PATH = PROJECT_ROOT / "data" / "external" / "team_master.csv"


def build():
    matches = pd.read_csv(CLEAN_PATH, parse_dates=["match_date"])
    players = pd.read_csv(PLAYERS_CLEAN_PATH)
    eu_matches = pd.read_csv(EU_CLEAN_PATH, parse_dates=["match_date"])
    team_master = pd.read_csv(TEAM_MASTER_PATH)

    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    # DIM_TEAM
    canonical_teams = sorted(team_master["canonical_name"].unique())
    short_names = team_master.drop_duplicates("canonical_name").set_index("canonical_name")["short_name"]
    dim_team = pd.DataFrame({
        "team_id": range(1, len(canonical_teams) + 1),
        "canonical_name": canonical_teams,
        "short_name": [short_names[t] for t in canonical_teams],
    })
    dim_team.to_sql("dim_team", conn, if_exists="append", index=False)
    team_to_id = dict(zip(dim_team["canonical_name"], dim_team["team_id"]))

    # DIM_SEASON
    season_labels = sorted(matches["season"].unique())
    dim_season = pd.DataFrame({
        "season_id": range(1, len(season_labels) + 1),
        "season_label": season_labels,
        "start_year": [int(s.split("/")[0]) for s in season_labels],
    })
    dim_season.to_sql("dim_season", conn, if_exists="append", index=False)
    season_to_id = dict(zip(dim_season["season_label"], dim_season["season_id"]))

    # DIM_DATE (only dates that actually have matches)
    unique_dates = sorted(matches["match_date"].dt.normalize().unique())
    dim_date = pd.DataFrame({
        "date_id": [int(pd.Timestamp(d).strftime("%Y%m%d")) for d in unique_dates],
        "full_date": [pd.Timestamp(d).strftime("%Y-%m-%d") for d in unique_dates],
        "day": [pd.Timestamp(d).day for d in unique_dates],
        "month": [pd.Timestamp(d).month for d in unique_dates],
        "year": [pd.Timestamp(d).year for d in unique_dates],
        "weekday_name": [pd.Timestamp(d).day_name() for d in unique_dates],
    })
    dim_date.to_sql("dim_date", conn, if_exists="append", index=False)

    # FACT_MATCH
    fact_match = pd.DataFrame({
        "match_id": matches["match_id"],
        "season_id": matches["season"].map(season_to_id),
        "date_id": matches["match_date"].dt.strftime("%Y%m%d").astype(int),
        "home_team_id": matches["home_team"].map(team_to_id),
        "away_team_id": matches["away_team"].map(team_to_id),
        "home_goals": matches["home_goals"],
        "away_goals": matches["away_goals"],
        "home_goals_ht": matches["home_goals_ht"],
        "away_goals_ht": matches["away_goals_ht"],
        "result": matches["result"],
        "result_ht": matches["result_ht"],
        "referee": matches["referee"],
        "home_shots": matches["home_shots"],
        "away_shots": matches["away_shots"],
        "home_shots_on_target": matches["home_shots_on_target"],
        "away_shots_on_target": matches["away_shots_on_target"],
        "home_corners": matches["home_corners"],
        "away_corners": matches["away_corners"],
        "home_yellow_cards": matches["home_yellow_cards"],
        "away_yellow_cards": matches["away_yellow_cards"],
        "home_red_cards": matches["home_red_cards"],
        "away_red_cards": matches["away_red_cards"],
    })
    fact_match.to_sql("fact_match", conn, if_exists="append", index=False)

    # FACT_TEAM_SEASON
    team_season = all_seasons_team_table(matches)
    fact_team_season = pd.DataFrame({
        "team_id": team_season["team"].map(team_to_id),
        "season_id": team_season["season"].map(season_to_id),
        "played": team_season["played"],
        "wins": team_season["wins"],
        "draws": team_season["draws"],
        "losses": team_season["losses"],
        "goals_for": team_season["goals_for"],
        "goals_against": team_season["goals_against"],
        "points": team_season["points"],
        "home_wins": team_season["home_wins"],
        "home_draws": team_season["home_draws"],
        "home_losses": team_season["home_losses"],
        "away_wins": team_season["away_wins"],
        "away_draws": team_season["away_draws"],
        "away_losses": team_season["away_losses"],
        "clean_sheets": team_season["clean_sheets"],
        "league_position": team_season["position"],
    })
    fact_team_season.to_sql("fact_team_season", conn, if_exists="append", index=False)

    # DIM_PLAYER (one row per unique player name) + FACT_PLAYER_SEASON
    unique_players = sorted(players["player_name"].unique())
    dim_player = pd.DataFrame({
        "player_id": range(1, len(unique_players) + 1),
        "player_name": unique_players,
        "web_name": [players.loc[players["player_name"] == p, "web_name"].iloc[0] for p in unique_players],
    })
    dim_player.to_sql("dim_player", conn, if_exists="append", index=False)
    player_to_id = dict(zip(dim_player["player_name"], dim_player["player_id"]))

    fact_player_season = pd.DataFrame({
        "player_season_id": players["player_season_id"],
        "player_id": players["player_name"].map(player_to_id),
        "team_id": players["team"].map(team_to_id),
        "season_id": players["season"].map(season_to_id),
        "position": players["position"],
        "minutes": players["minutes"],
        "starts": players["starts"],
        "goals_scored": players["goals_scored"],
        "assists": players["assists"],
        "clean_sheets": players["clean_sheets"],
        "goals_conceded": players["goals_conceded"],
        "yellow_cards": players["yellow_cards"],
        "red_cards": players["red_cards"],
        "saves": players["saves"],
        "own_goals": players["own_goals"],
        "penalties_missed": players["penalties_missed"],
        "bonus": players["bonus"],
        "expected_goals": players["expected_goals"],
        "expected_assists": players["expected_assists"],
        "expected_goal_involvements": players["expected_goal_involvements"],
        "expected_goals_conceded": players["expected_goals_conceded"],
        "now_cost_m": players["now_cost_m"],
    })
    fact_player_season.to_sql("fact_player_season", conn, if_exists="append", index=False)

    # DIM_COMPETITION + FACT_EUROPEAN_MATCH + FACT_CLUB_SEASON_EUROPE
    dim_competition = pd.DataFrame({"competition_id": [1], "name": ["UEFA Champions League"]})
    dim_competition.to_sql("dim_competition", conn, if_exists="append", index=False)

    fact_european_match = pd.DataFrame({
        "match_id": eu_matches["match_id"],
        "competition_id": 1,
        "season_id": eu_matches["season"].map(season_to_id),
        "stage": eu_matches["stage"],
        "stage_order": eu_matches["stage_order"],
        "match_date": eu_matches["match_date"].dt.strftime("%Y-%m-%d"),
        "home_team_id": eu_matches["home_team"].map(team_to_id),
        "away_team_id": eu_matches["away_team"].map(team_to_id),
        "home_team_display": eu_matches["home_team_display"],
        "away_team_display": eu_matches["away_team_display"],
        "home_goals": eu_matches["home_goals"],
        "away_goals": eu_matches["away_goals"],
        "result": eu_matches["result"],
        "went_to_extra_time": eu_matches["went_to_extra_time"].astype(int),
        "decided_by_penalties": eu_matches["decided_by_penalties"].astype(int),
        "penalty_home_goals": eu_matches["penalty_home_goals"],
        "penalty_away_goals": eu_matches["penalty_away_goals"],
    })
    fact_european_match.to_sql("fact_european_match", conn, if_exists="append", index=False)

    campaigns = club_season_campaigns(eu_matches)
    fact_club_season_europe = pd.DataFrame({
        "team_id": campaigns["club"].map(team_to_id),
        "season_id": campaigns["season"].map(season_to_id),
        "competition_id": 1,
        "matches_played": campaigns["matches_played"],
        "wins": campaigns["wins"],
        "draws": campaigns["draws"],
        "losses": campaigns["losses"],
        "goals_for": campaigns["goals_for"],
        "goals_against": campaigns["goals_against"],
        "goal_difference": campaigns["goal_difference"],
        "win_pct": campaigns["win_pct"],
        "goals_per_match": campaigns["goals_per_match"],
        "clean_sheets": campaigns["clean_sheets"],
        "finish_rank": campaigns["finish_rank"],
        "finish_label": campaigns["finish_label"],
    })
    fact_club_season_europe.to_sql("fact_club_season_europe", conn, if_exists="append", index=False)

    conn.commit()

    counts = {}
    for table in [
        "dim_team", "dim_season", "dim_date", "fact_match", "fact_team_season",
        "dim_player", "fact_player_season", "dim_competition", "fact_european_match",
        "fact_club_season_europe",
    ]:
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn.close()

    print(f"Built {DB_PATH}")
    for table, count in counts.items():
        print(f"  {table}: {count} rows")
    return counts


if __name__ == "__main__":
    build()

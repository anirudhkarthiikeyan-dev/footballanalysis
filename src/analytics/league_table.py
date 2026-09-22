"""Core league-table analytics: build a full team-season stats table
(the source for FACT_TEAM_SEASON) from cleaned match-level data.

Tie-break rule: points -> goal difference -> goals for -> alphabetical.
This matches the Premier League's actual tie-break rules (points, then
goal difference, then goals scored) for the vast majority of seasons;
head-to-head/playoff tie-breaks used in rare historical edge cases are
not modeled. See docs/methodology/METHODOLOGY.md.
"""
import pandas as pd


def team_season_table(matches: pd.DataFrame, season: str) -> pd.DataFrame:
    """Return one row per team for the given season, sorted by final
    league position (1 = champions)."""
    season_matches = matches[matches["season"] == season]
    teams = sorted(set(season_matches["home_team"]) | set(season_matches["away_team"]))

    rows = []
    for team in teams:
        home = season_matches[season_matches["home_team"] == team]
        away = season_matches[season_matches["away_team"] == team]

        home_wins = int((home["result"] == "H").sum())
        home_draws = int((home["result"] == "D").sum())
        home_losses = int((home["result"] == "A").sum())
        away_wins = int((away["result"] == "A").sum())
        away_draws = int((away["result"] == "D").sum())
        away_losses = int((away["result"] == "H").sum())

        wins = home_wins + away_wins
        draws = home_draws + away_draws
        losses = home_losses + away_losses
        played = wins + draws + losses

        goals_for = int(home["home_goals"].sum() + away["away_goals"].sum())
        goals_against = int(home["away_goals"].sum() + away["home_goals"].sum())
        points = wins * 3 + draws

        clean_sheets = int((home["away_goals"] == 0).sum() + (away["home_goals"] == 0).sum())

        rows.append({
            "team": team, "season": season, "played": played,
            "wins": wins, "draws": draws, "losses": losses,
            "goals_for": goals_for, "goals_against": goals_against,
            "goal_difference": goals_for - goals_against, "points": points,
            "home_wins": home_wins, "home_draws": home_draws, "home_losses": home_losses,
            "away_wins": away_wins, "away_draws": away_draws, "away_losses": away_losses,
            "clean_sheets": clean_sheets,
        })

    table = pd.DataFrame(rows)
    table = table.sort_values(
        by=["points", "goal_difference", "goals_for", "team"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    table.insert(0, "position", range(1, len(table) + 1))
    return table


def all_seasons_team_table(matches: pd.DataFrame) -> pd.DataFrame:
    frames = [team_season_table(matches, s) for s in sorted(matches["season"].unique())]
    return pd.concat(frames, ignore_index=True)

"""Team-level analytics: season journey, form, trends, home/away splits."""
import pandas as pd

from src.analytics.league_table import team_season_table


def team_season_journey(matches: pd.DataFrame, team: str) -> pd.DataFrame:
    """One row per season the team played in the dataset, with league
    position, points and goal record — the input to a season trajectory chart."""
    rows = []
    for season in sorted(matches["season"].unique()):
        table = team_season_table(matches, season)
        row = table[table["team"] == team]
        if not row.empty:
            rows.append(row.iloc[0])
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).reset_index(drop=True)


def team_form(matches: pd.DataFrame, team: str, season: str | None = None, last_n: int = 5) -> pd.DataFrame:
    games = matches[(matches["home_team"] == team) | (matches["away_team"] == team)]
    if season:
        games = games[games["season"] == season]
    games = games.sort_values("match_date").tail(last_n).copy()

    def outcome(r):
        if r["result"] == "D":
            return "D"
        won_home = r["home_team"] == team and r["result"] == "H"
        won_away = r["away_team"] == team and r["result"] == "A"
        return "W" if (won_home or won_away) else "L"

    games["outcome"] = games.apply(outcome, axis=1)
    return games


def league_goals_trend(matches: pd.DataFrame) -> pd.DataFrame:
    """Goals-per-match and home-advantage trend across every season -
    feeds the League Trends page."""
    rows = []
    for season, group in matches.groupby("season"):
        total_goals = group["home_goals"].sum() + group["away_goals"].sum()
        home_wins = (group["result"] == "H").sum()
        away_wins = (group["result"] == "A").sum()
        draws = (group["result"] == "D").sum()
        n = len(group)
        rows.append({
            "season": season,
            "matches": n,
            "total_goals": int(total_goals),
            "goals_per_match": round(total_goals / n, 2),
            "home_win_pct": round(100 * home_wins / n, 1),
            "draw_pct": round(100 * draws / n, 1),
            "away_win_pct": round(100 * away_wins / n, 1),
            "avg_home_goals": round(group["home_goals"].mean(), 2),
            "avg_away_goals": round(group["away_goals"].mean(), 2),
        })
    return pd.DataFrame(rows).sort_values("season").reset_index(drop=True)


def home_away_split(matches: pd.DataFrame, team: str, season: str | None = None) -> dict:
    games = matches[(matches["home_team"] == team) | (matches["away_team"] == team)]
    if season:
        games = games[games["season"] == season]
    home = games[games["home_team"] == team]
    away = games[games["away_team"] == team]
    return {
        "home": {
            "played": len(home),
            "wins": int((home["result"] == "H").sum()),
            "draws": int((home["result"] == "D").sum()),
            "losses": int((home["result"] == "A").sum()),
            "goals_for": int(home["home_goals"].sum()),
            "goals_against": int(home["away_goals"].sum()),
        },
        "away": {
            "played": len(away),
            "wins": int((away["result"] == "A").sum()),
            "draws": int((away["result"] == "D").sum()),
            "losses": int((away["result"] == "H").sum()),
            "goals_for": int(away["away_goals"].sum()),
            "goals_against": int(away["home_goals"].sum()),
        },
    }

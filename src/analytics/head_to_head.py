"""Head-to-head analytics engine for any two teams.

All functions take the full cleaned matches DataFrame (data/processed/matches_clean.csv)
so they can be reused identically by the SQLite-backed Streamlit app and by tests.
"""
import pandas as pd


def h2h_matches(matches: pd.DataFrame, team_a: str, team_b: str) -> pd.DataFrame:
    mask = (
        ((matches["home_team"] == team_a) & (matches["away_team"] == team_b)) |
        ((matches["home_team"] == team_b) & (matches["away_team"] == team_a))
    )
    return matches[mask].sort_values("match_date").reset_index(drop=True)


def h2h_summary(matches: pd.DataFrame, team_a: str, team_b: str) -> dict:
    games = h2h_matches(matches, team_a, team_b)
    if games.empty:
        return {"meetings": 0}

    a_wins = int((((games["home_team"] == team_a) & (games["result"] == "H")) |
                   ((games["away_team"] == team_a) & (games["result"] == "A"))).sum())
    b_wins = int((((games["home_team"] == team_b) & (games["result"] == "H")) |
                   ((games["away_team"] == team_b) & (games["result"] == "A"))).sum())
    draws = int((games["result"] == "D").sum())

    a_goals = int(games.apply(lambda r: r["home_goals"] if r["home_team"] == team_a else r["away_goals"], axis=1).sum())
    b_goals = int(games.apply(lambda r: r["home_goals"] if r["home_team"] == team_b else r["away_goals"], axis=1).sum())

    a_home = games[games["home_team"] == team_a]
    b_home = games[games["home_team"] == team_b]

    total_goals = games["home_goals"] + games["away_goals"]
    biggest_margin_idx = (games["home_goals"] - games["away_goals"]).abs().idxmax()
    highest_scoring_idx = total_goals.idxmax()

    return {
        "meetings": len(games),
        "team_a": team_a, "team_b": team_b,
        f"{team_a}_wins": a_wins, f"{team_b}_wins": b_wins, "draws": draws,
        f"{team_a}_goals": a_goals, f"{team_b}_goals": b_goals,
        f"{team_a}_win_pct": round(100 * a_wins / len(games), 1),
        f"{team_b}_win_pct": round(100 * b_wins / len(games), 1),
        "draw_pct": round(100 * draws / len(games), 1),
        f"{team_a}_home_record": {
            "played": len(a_home),
            "wins": int((a_home["result"] == "H").sum()),
            "draws": int((a_home["result"] == "D").sum()),
            "losses": int((a_home["result"] == "A").sum()),
        },
        f"{team_b}_home_record": {
            "played": len(b_home),
            "wins": int((b_home["result"] == "H").sum()),
            "draws": int((b_home["result"] == "D").sum()),
            "losses": int((b_home["result"] == "A").sum()),
        },
        "avg_goals_per_match": round(float(total_goals.mean()), 2),
        "biggest_win_match_id": games.loc[biggest_margin_idx, "match_id"],
        "highest_scoring_match_id": games.loc[highest_scoring_idx, "match_id"],
        "last_meeting": games.iloc[-1].to_dict(),
        "last_5": games.tail(5),
        "last_10": games.tail(10),
    }


def most_frequent_opponents(matches: pd.DataFrame, team: str, top_n: int = 10) -> pd.DataFrame:
    games = matches[(matches["home_team"] == team) | (matches["away_team"] == team)].copy()
    games["opponent"] = games.apply(lambda r: r["away_team"] if r["home_team"] == team else r["home_team"], axis=1)
    counts = games.groupby("opponent").size().sort_values(ascending=False).head(top_n)
    return counts.rename("meetings").reset_index()

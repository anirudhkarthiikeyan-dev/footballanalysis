"""European Performance analytics: UEFA Champions League campaign stats
for the 20 selected clubs (src/cleaning/clean_european.py), built on the
same match-level grain discipline as src/analytics/league_table.py.

Progression stage ordering used throughout this module (see
docs/methodology/METHODOLOGY.md for the full writeup on why 2024/25+
"Swiss model" seasons are folded into the same scale as the older
group-stage format):

  1 = group stage / league phase   4 = quarterfinal
  2 = playoff round (2024/25+)     5 = semifinal
  3 = round of 16                  6 = final (runner-up)
                                    7 = final (winner)
"""
import pandas as pd

STAGE_LABELS = {
    1: "Group/League Phase", 2: "Playoff Round", 3: "Round of 16",
    4: "Quarterfinal", 5: "Semifinal", 6: "Runner-up", 7: "Winner",
}


def _match_winner(row) -> str | None:
    """Who actually won this match, accounting for penalty shootouts."""
    if row["decided_by_penalties"]:
        if row["penalty_home_goals"] > row["penalty_away_goals"]:
            return row["home_team_display"]
        return row["away_team_display"]
    if row["home_goals"] > row["away_goals"]:
        return row["home_team_display"]
    if row["home_goals"] < row["away_goals"]:
        return row["away_team_display"]
    return None  # genuine draw in a non-decisive (e.g. group/league-phase) match


def club_season_campaigns(eu_matches: pd.DataFrame) -> pd.DataFrame:
    """One row per club per season the club actually played in — never
    a fabricated row for a season a club didn't qualify for."""
    long_rows = []
    for _, r in eu_matches.iterrows():
        for side, team_col, opp_col, gf_col, ga_col in [
            ("home", "home_team", "away_team_display", "home_goals", "away_goals"),
            ("away", "away_team", "home_team_display", "away_goals", "home_goals"),
        ]:
            club = r[team_col]
            if pd.isna(club):
                continue
            long_rows.append({
                "club": club, "season": r["season"], "stage": r["stage"], "stage_order": r["stage_order"],
                "goals_for": r[gf_col], "goals_against": r[ga_col],
                "match_id": r["match_id"], "decided_by_penalties": r["decided_by_penalties"],
                "winner": _match_winner(r),
            })
    long_df = pd.DataFrame(long_rows)

    campaigns = []
    for (club, season), grp in long_df.groupby(["club", "season"]):
        played = len(grp)
        wins = int((grp["winner"] == club).sum())
        losses = int(grp["winner"].notna().sum() - wins)
        draws = played - wins - losses
        gf = int(grp["goals_for"].sum())
        ga = int(grp["goals_against"].sum())
        clean_sheets = int((grp["goals_against"] == 0).sum())

        max_stage_order = int(grp["stage_order"].max())
        last_stage_matches = grp[grp["stage_order"] == max_stage_order]
        finish_rank = max_stage_order
        if max_stage_order == 6:  # final
            won_final = (last_stage_matches["winner"] == club).any()
            finish_rank = 7 if won_final else 6

        campaigns.append({
            "club": club, "season": season,
            "matches_played": played, "wins": wins, "draws": draws, "losses": losses,
            "goals_for": gf, "goals_against": ga, "goal_difference": gf - ga,
            "win_pct": round(100 * wins / played, 1) if played else 0.0,
            "goals_per_match": round(gf / played, 2) if played else 0.0,
            "clean_sheets": clean_sheets,
            "finish_rank": finish_rank,
            "finish_label": STAGE_LABELS[finish_rank],
        })

    return pd.DataFrame(campaigns).sort_values(["club", "season"]).reset_index(drop=True)


def club_best_finish(campaigns: pd.DataFrame, club: str) -> dict | None:
    rows = campaigns[campaigns["club"] == club]
    if rows.empty:
        return None
    best = rows.loc[rows["finish_rank"].idxmax()]
    return {"season": best["season"], "finish_rank": int(best["finish_rank"]), "finish_label": best["finish_label"]}


def club_matches(eu_matches: pd.DataFrame, club: str) -> pd.DataFrame:
    mask = (eu_matches["home_team"] == club) | (eu_matches["away_team"] == club)
    return eu_matches[mask].sort_values("match_date").reset_index(drop=True)


def opponent_history(eu_matches: pd.DataFrame, club: str, top_n: int = 15) -> pd.DataFrame:
    games = club_matches(eu_matches, club).copy()
    games["opponent"] = games.apply(
        lambda r: r["away_team_display"] if r["home_team"] == club else r["home_team_display"], axis=1
    )
    games["club_goals"] = games.apply(lambda r: r["home_goals"] if r["home_team"] == club else r["away_goals"], axis=1)
    games["opp_goals"] = games.apply(lambda r: r["away_goals"] if r["home_team"] == club else r["home_goals"], axis=1)
    games["winner"] = games.apply(_match_winner, axis=1)

    rows = []
    for opp, grp in games.groupby("opponent"):
        played = len(grp)
        wins = int((grp["winner"] == club).sum())
        losses = int(grp["winner"].notna().sum() - wins)
        draws = played - wins - losses
        rows.append({
            "opponent": opp, "meetings": played, "wins": wins, "draws": draws, "losses": losses,
            "goals_for": int(grp["club_goals"].sum()), "goals_against": int(grp["opp_goals"].sum()),
        })
    result = pd.DataFrame(rows).sort_values("meetings", ascending=False)
    return result.head(top_n).reset_index(drop=True)


def european_h2h(eu_matches: pd.DataFrame, club_a: str, club_b: str) -> pd.DataFrame:
    """Full historical Champions League meetings between two of the 20
    selected clubs (both must be in SELECTED_CLUBS for this to be
    meaningful — meetings against clubs outside the 20 are covered by
    opponent_history() instead)."""
    mask = (
        ((eu_matches["home_team"] == club_a) & (eu_matches["away_team"] == club_b)) |
        ((eu_matches["home_team"] == club_b) & (eu_matches["away_team"] == club_a))
    )
    return eu_matches[mask].sort_values("match_date").reset_index(drop=True)


def domestic_vs_europe(pl_team_season: pd.DataFrame, eu_campaigns: pd.DataFrame, club: str) -> dict:
    """Compare a club's Premier League record against its Champions
    League record, only across seasons where both exist. Competitions
    have very different structures (38 balanced league games vs a
    campaign that can end after 6-8 matches) - this is presented as a
    side-by-side comparison, not a claim the two are equivalent."""
    pl = pl_team_season[pl_team_season["team"] == club]
    eu = eu_campaigns[eu_campaigns["club"] == club]

    def summarize(df, gf_col="goals_for", ga_col="goals_against", w_col="wins", p_col="played"):
        if df.empty:
            return None
        played = int(df[p_col].sum())
        wins = int(df[w_col].sum())
        return {
            "seasons": df["season"].nunique() if "season" in df.columns else 0,
            "played": played,
            "win_pct": round(100 * wins / played, 1) if played else 0.0,
            "goals_per_match": round(df[gf_col].sum() / played, 2) if played else 0.0,
            "goals_against_per_match": round(df[ga_col].sum() / played, 2) if played else 0.0,
        }

    pl_summary = summarize(pl, "goals_for", "goals_against", "wins", "played")
    eu_summary = summarize(eu, "goals_for", "goals_against", "wins", "matches_played")
    return {"domestic": pl_summary, "europe": eu_summary}

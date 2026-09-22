"""Player analytics: per-90 rates and position-aware percentiles.

Percentiles are always computed within the same (season, position) group -
comparing a forward's goals/90 to a defender's would be misleading, so
every percentile function requires a position to compare within.
"""
import pandas as pd

PER90_SOURCE_COLS = {
    "goals_scored": "goals_per_90",
    "assists": "assists_per_90",
    "expected_goals": "xg_per_90",
    "expected_assists": "xa_per_90",
    "expected_goal_involvements": "xgi_per_90",
}

MIN_MINUTES_DEFAULT = 450  # ~5 full matches, avoids small-sample noise


def add_per90_columns(players: pd.DataFrame) -> pd.DataFrame:
    df = players.copy()
    nineties = df["minutes"] / 90.0
    for src, dst in PER90_SOURCE_COLS.items():
        df[dst] = (df[src] / nineties).where(nineties > 0)
    return df


def percentile_rank(players: pd.DataFrame, season: str, position: str,
                     min_minutes: int = MIN_MINUTES_DEFAULT) -> pd.DataFrame:
    """Percentile (0-100) of each per-90 metric within the season+position
    cohort meeting the minutes threshold. Higher percentile = better."""
    df = add_per90_columns(players)
    cohort = df[(df["season"] == season) & (df["position"] == position) & (df["minutes"] >= min_minutes)].copy()
    if cohort.empty:
        return cohort

    metric_cols = list(PER90_SOURCE_COLS.values())
    for col in metric_cols:
        if cohort[col].notna().sum() == 0:
            continue
        cohort[f"{col}_pctile"] = cohort[col].rank(pct=True, na_option="keep") * 100
    return cohort


def top_performers(players: pd.DataFrame, season: str, metric: str, position: str | None = None,
                    min_minutes: int = MIN_MINUTES_DEFAULT, top_n: int = 10) -> pd.DataFrame:
    df = add_per90_columns(players)
    subset = df[(df["season"] == season) & (df["minutes"] >= min_minutes)]
    if position:
        subset = subset[subset["position"] == position]
    return subset.sort_values(metric, ascending=False).head(top_n)


def player_season_history(players: pd.DataFrame, player_name: str) -> pd.DataFrame:
    df = add_per90_columns(players)
    return df[df["player_name"] == player_name].sort_values("season").reset_index(drop=True)

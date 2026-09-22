"""Automated data-quality checks for the cleaned match table.

These are the checks required by the project's data validation rules:
exactly one home/away team per match, home != away, non-negative goals,
valid dates, valid seasons, no duplicate matches, consistent goal
difference. Raises AssertionError with a clear message on first failure
so this can run both as a script and inside pytest.
"""
from pathlib import Path

import pandas as pd

from src.utils.seasons import PROJECT_ROOT, all_season_labels

CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "matches_clean.csv"

VALID_SEASONS = set(all_season_labels())
VALID_RESULTS = {"H", "D", "A"}


def load_clean_matches() -> pd.DataFrame:
    return pd.read_csv(CLEAN_PATH, parse_dates=["match_date"])


def validate(df: pd.DataFrame) -> list[str]:
    errors = []

    if df["match_id"].duplicated().any():
        errors.append("Duplicate match_id values found.")

    if (df["home_team"] == df["away_team"]).any():
        errors.append("Found matches where home_team == away_team.")

    if (df["home_goals"] < 0).any() or (df["away_goals"] < 0).any():
        errors.append("Found negative goal values.")

    if df["match_date"].isna().any():
        errors.append("Found unparseable match dates.")

    bad_seasons = set(df["season"]) - VALID_SEASONS
    if bad_seasons:
        errors.append(f"Found season labels outside expected range: {bad_seasons}")

    bad_results = set(df["result"]) - VALID_RESULTS
    if bad_results:
        errors.append(f"Found invalid result codes: {bad_results}")

    # result must agree with the goal difference
    computed = pd.Series("D", index=df.index)
    computed[df["home_goals"] > df["away_goals"]] = "H"
    computed[df["home_goals"] < df["away_goals"]] = "A"
    mismatches = df[computed != df["result"]]
    if len(mismatches):
        errors.append(f"{len(mismatches)} rows where result column disagrees with goals (e.g. match_id={mismatches['match_id'].iloc[0]}).")

    dup_fixtures = df.duplicated(subset=["season", "home_team", "away_team"], keep=False)
    if dup_fixtures.sum() > 0:
        counts = df[dup_fixtures].groupby(["season", "home_team", "away_team"]).size()
        over = counts[counts > 1]
        if len(over):
            errors.append(f"Found fixtures repeated more than once within a season: {over.index.tolist()[:5]}")

    for season, group in df.groupby("season"):
        teams = set(group["home_team"]) | set(group["away_team"])
        if len(teams) != 20:
            errors.append(f"Season {season} has {len(teams)} teams (expected 20).")
        if len(group) != 380:
            errors.append(f"Season {season} has {len(group)} matches (expected 380).")

    return errors


def main():
    df = load_clean_matches()
    errors = validate(df)
    if errors:
        print(f"VALIDATION FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)
    print(f"VALIDATION PASSED: {len(df)} matches, {df['season'].nunique()} seasons, no issues found.")


if __name__ == "__main__":
    main()

"""Clean and normalize raw football-data.co.uk match CSVs into one
tidy, analysis-ready table.

Steps performed (see docs/methodology/METHODOLOGY.md for the full writeup):
  1. Load every raw season file.
  2. Drop fully-blank trailing rows (a known artifact of the source files).
  3. Parse dates robustly (source mixes dd/mm/yy and dd/mm/yyyy formats).
  4. Attach a canonical season label derived from the filename, not the
     row data, since that's the one field the source guarantees.
  5. Map raw team name strings to canonical team names via
     data/external/team_master.csv (entity resolution).
  6. Select and rename the columns we trust (results, goals, shots,
     shots on target, corners, cards, referee).
  7. Enforce dtypes and drop rows that fail basic sanity checks.
  8. Deduplicate exact-duplicate match rows.

Output: data/processed/matches_clean.csv
"""
from pathlib import Path

import pandas as pd

from src.utils.seasons import PROJECT_ROOT, season_code_to_label

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "matches"
TEAM_MASTER_PATH = PROJECT_ROOT / "data" / "external" / "team_master.csv"
OUT_PATH = PROJECT_ROOT / "data" / "processed" / "matches_clean.csv"

COLUMN_MAP = {
    "Date": "date_raw",
    "HomeTeam": "home_team_raw",
    "AwayTeam": "away_team_raw",
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "result",
    "HTHG": "home_goals_ht",
    "HTAG": "away_goals_ht",
    "HTR": "result_ht",
    "Referee": "referee",
    "HS": "home_shots",
    "AS": "away_shots",
    "HST": "home_shots_on_target",
    "AST": "away_shots_on_target",
    "HC": "home_corners",
    "AC": "away_corners",
    "HY": "home_yellow_cards",
    "AY": "away_yellow_cards",
    "HR": "home_red_cards",
    "AR": "away_red_cards",
}


def load_team_master() -> pd.DataFrame:
    return pd.read_csv(TEAM_MASTER_PATH)


def load_raw_season(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin1")
    df = df.dropna(subset=["HomeTeam", "AwayTeam", "FTR"], how="any")
    code = path.stem.split("_")[1]
    keep_cols = [c for c in COLUMN_MAP if c in df.columns]
    df = df[keep_cols].rename(columns=COLUMN_MAP).copy()
    df["season"] = season_code_to_label(code)
    return df


def parse_date_mixed(series: pd.Series) -> pd.Series:
    """football-data.co.uk mixes dd/mm/yy and dd/mm/yyyy across seasons."""
    return pd.to_datetime(series, format="mixed", dayfirst=True)


def clean_all() -> pd.DataFrame:
    raw_files = sorted(RAW_DIR.glob("E0_*.csv"))
    if not raw_files:
        raise FileNotFoundError(f"No raw match files found in {RAW_DIR}. Run src/ingestion/fetch_matches.py first.")

    frames = [load_raw_season(f) for f in raw_files]
    df = pd.concat(frames, ignore_index=True)

    df["match_date"] = parse_date_mixed(df["date_raw"])
    df = df.drop(columns=["date_raw"])

    team_master = load_team_master()
    name_to_canonical = dict(zip(team_master["raw_name"], team_master["canonical_name"]))
    unmapped = set(df["home_team_raw"]).union(df["away_team_raw"]) - set(name_to_canonical)
    if unmapped:
        raise ValueError(f"Unmapped team names found, add to team_master.csv: {sorted(unmapped)}")

    df["home_team"] = df["home_team_raw"].map(name_to_canonical)
    df["away_team"] = df["away_team_raw"].map(name_to_canonical)
    df = df.drop(columns=["home_team_raw", "away_team_raw"])

    numeric_cols = [
        "home_goals", "away_goals", "home_goals_ht", "away_goals_ht",
        "home_shots", "away_shots", "home_shots_on_target", "away_shots_on_target",
        "home_corners", "away_corners",
        "home_yellow_cards", "away_yellow_cards", "home_red_cards", "away_red_cards",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["home_goals"] = df["home_goals"].astype("Int64")
    df["away_goals"] = df["away_goals"].astype("Int64")

    before = len(df)
    df = df[df["home_team"] != df["away_team"]]
    df = df[df["home_goals"].notna() & df["away_goals"].notna()]
    df = df[df["home_goals"] >= 0]
    df = df[df["away_goals"] >= 0]
    df = df[df["result"].isin(["H", "D", "A"])]
    dropped_sanity = before - len(df)

    before = len(df)
    df = df.drop_duplicates(subset=["season", "match_date", "home_team", "away_team"], keep="first")
    dropped_dupes = before - len(df)

    df = df.sort_values(["match_date", "season"]).reset_index(drop=True)
    df.insert(0, "match_id", [f"M{i:05d}" for i in range(1, len(df) + 1)])

    print(f"Cleaned {len(df)} matches across {df['season'].nunique()} seasons.")
    print(f"Dropped {dropped_sanity} rows failing sanity checks, {dropped_dupes} exact duplicates.")

    return df


def main():
    df = clean_all()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} ({len(df)} rows, {len(df.columns)} columns)")


if __name__ == "__main__":
    main()

"""Clean and normalize per-season player data (vaastav FPL archive) into
one tidy player-season table.

Coverage rule (see docs/data/DATA_SOURCES.md):
  - Basic stats (minutes, goals, assists, cards, clean sheets, saves):
    2019/20 - 2025/26.
  - Advanced stats (expected_goals, expected_assists, starts):
    2022/23 - 2025/26 only — FPL did not track these earlier. Rows before
    2022/23 keep these columns as null (NaN), never a fabricated zero.

Output: data/processed/players_clean.csv, one row per player per season.
"""
import re

import pandas as pd

from src.utils.seasons import PROJECT_ROOT

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "players"
TEAM_MASTER_PATH = PROJECT_ROOT / "data" / "external" / "team_master.csv"
OUT_PATH = PROJECT_ROOT / "data" / "processed" / "players_clean.csv"

SEASONS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
ADVANCED_STATS_FROM = "2022-23"

POSITION_MAP = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

BASIC_COLS = [
    "minutes", "starts", "goals_scored", "assists", "clean_sheets",
    "goals_conceded", "yellow_cards", "red_cards", "saves", "own_goals",
    "penalties_missed", "bonus",
]
ADVANCED_COLS = [
    "expected_goals", "expected_assists", "expected_goal_involvements",
    "expected_goals_conceded",
]


def season_label(fpl_season: str) -> str:
    """'2019-20' -> '2019/20'"""
    start, end = fpl_season.split("-")
    return f"{start}/{end}"


def strip_accents_safe(text: str) -> str:
    return text if isinstance(text, str) else text


def clean_season(fpl_season: str, name_to_canonical: dict) -> pd.DataFrame:
    players = pd.read_csv(RAW_DIR / f"players_{fpl_season}.csv", low_memory=False)
    teams = pd.read_csv(RAW_DIR / f"teams_{fpl_season}.csv")
    team_id_to_raw_name = dict(zip(teams["id"], teams["name"]))

    df = pd.DataFrame()
    df["player_name"] = (players["first_name"].fillna("") + " " + players["second_name"].fillna("")).str.strip()
    df["web_name"] = players.get("web_name")
    df["season"] = season_label(fpl_season)
    df["position"] = players["element_type"].map(POSITION_MAP)

    raw_team_name = players["team"].map(team_id_to_raw_name)
    unmapped = set(raw_team_name.dropna()) - set(name_to_canonical)
    if unmapped:
        raise ValueError(f"Unmapped FPL team names for {fpl_season}: {sorted(unmapped)}")
    df["team"] = raw_team_name.map(name_to_canonical)

    for col in BASIC_COLS:
        df[col] = pd.to_numeric(players.get(col), errors="coerce")

    if fpl_season >= ADVANCED_STATS_FROM:
        for col in ADVANCED_COLS:
            df[col] = pd.to_numeric(players.get(col), errors="coerce")
    else:
        for col in ADVANCED_COLS:
            df[col] = pd.NA

    df["now_cost_m"] = pd.to_numeric(players.get("now_cost"), errors="coerce") / 10.0

    df = df[df["minutes"].fillna(0) > 0].reset_index(drop=True)
    return df


def clean_all() -> pd.DataFrame:
    team_master = pd.read_csv(TEAM_MASTER_PATH)
    name_to_canonical = dict(zip(team_master["raw_name"], team_master["canonical_name"]))

    frames = [clean_season(s, name_to_canonical) for s in SEASONS]
    df = pd.concat(frames, ignore_index=True)

    df = df.drop_duplicates(subset=["season", "player_name", "team"], keep="first")
    df.insert(0, "player_season_id", [f"P{i:05d}" for i in range(1, len(df) + 1)])

    for col in BASIC_COLS + ["now_cost_m"]:
        assert not (df[col] < 0).any(), f"Negative values found in {col}"

    print(f"Cleaned {len(df)} player-season rows across {df['season'].nunique()} seasons "
          f"({df['player_name'].nunique()} unique player names).")
    return df


def main():
    df = clean_all()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} ({len(df)} rows, {len(df.columns)} columns)")


if __name__ == "__main__":
    main()

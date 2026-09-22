"""Parse the openfootball Champions League `football.txt`-format season
files into a clean, analysis-ready match table, filtered to the 20
selected European clubs named in the project brief.

Format notes (see docs/data/DATA_SOURCES.md for the full writeup):
  - Each season file has stage sections marked with a leading "▪"
    (e.g. "▪ Group A", "▪ Gruppe G" [a source typo for "Group G" -
    normalized here], "▪ Round of 16", "▪ League, Matchday 3" for the
    2024/25+ Swiss-model format, "▪ Finals, Quarterfinals").
  - Date lines look like "Tue Sep 18 2012" (year shown once, implied
    afterward until it changes).
  - Match lines look like:
      "20:45  Team One (ENG)          v Team Two (GER)        4-1 (3-0)"
    with continuation lines (same kickoff time) omitting the "HH:MM ".
  - Knockout legs decided beyond 90 minutes are annotated, e.g.:
      "3-4 pen. 1-1 a.e.t. (1-1, 0-1)"
    read right-to-left: (90-min FT, 90-min HT), then the extra-time
    score ("1-1 a.e.t."), then the penalty shootout score ("3-4 pen.").
    This project records the **on-pitch goals** (the score after extra
    time, or the normal full-time score if no extra time was played)
    as `home_goals`/`away_goals` — a penalty shootout is not a goal —
    and separately flags `decided_by_penalties` / `went_to_extra_time`.
    A penalty-shootout result counts as a **draw** for win/draw/loss
    purposes, matching standard competition-statistics convention: the
    match itself finished level; only progression to the next round
    was decided by penalties.
"""
import re
from pathlib import Path

import pandas as pd

from src.utils.seasons import PROJECT_ROOT

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "european"
TEAM_MASTER_PATH = PROJECT_ROOT / "data" / "external" / "team_master.csv"
OUT_PATH = PROJECT_ROOT / "data" / "processed" / "european_matches_clean.csv"

# The 20 clubs selected for the European Performance module (project brief section 22).
SELECTED_CLUBS = {
    # England
    "Arsenal", "Chelsea", "Liverpool", "Manchester City", "Manchester United",
    "Tottenham Hotspur", "Leicester City", "Newcastle United", "Aston Villa",
    # Spain
    "Real Madrid", "Barcelona", "Atlético Madrid", "Sevilla", "Valencia",
    # Germany
    "Bayern Munich", "Borussia Dortmund", "Bayer Leverkusen", "RB Leipzig",
    # Italy
    "Juventus", "Inter Milan",
}

CLUB_COUNTRY = {
    "Arsenal": "England", "Chelsea": "England", "Liverpool": "England",
    "Manchester City": "England", "Manchester United": "England",
    "Tottenham Hotspur": "England", "Leicester City": "England",
    "Newcastle United": "England", "Aston Villa": "England",
    "Real Madrid": "Spain", "Barcelona": "Spain", "Atlético Madrid": "Spain",
    "Sevilla": "Spain", "Valencia": "Spain",
    "Bayern Munich": "Germany", "Borussia Dortmund": "Germany",
    "Bayer Leverkusen": "Germany", "RB Leipzig": "Germany",
    "Juventus": "Italy", "Inter Milan": "Italy",
}

MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
DATE_RE = re.compile(rf"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+({MONTHS})\s+(\d{{1,2}})(?:\s+(\d{{4}}))?\s*$")
MATCH_RE = re.compile(
    r"^(?:\d{1,2}:\d{2}\s+)?"
    r"(?P<home>.+?)\s+\((?P<home_cc>[A-Z]{2,3})\)\s+v\s+"
    r"(?P<away>.+?)\s+\((?P<away_cc>[A-Z]{2,3})\)\s+"
    r"(?P<score_expr>.+)$"
)
SCORE_PAIR_RE = re.compile(r"(\d+)-(\d+)")

STAGE_ORDER = {
    "group_stage": 1, "league_phase": 1, "playoff_round": 2,
    "round_of_16": 3, "quarterfinal": 4, "semifinal": 5, "final": 6,
}


def normalize_stage(raw_header: str) -> str:
    header = raw_header.strip()
    if "," in header:
        prefix, suffix = [p.strip() for p in header.split(",", 1)]
    else:
        prefix, suffix = header, ""

    if prefix in ("League",):
        return "league_phase"
    if prefix in ("Playoffs",):
        return "playoff_round"
    if prefix == "Finals":
        return normalize_stage(suffix)
    if prefix.startswith("Group") or prefix.startswith("Gruppe"):
        return "group_stage"
    if "Round of 16" in header:
        return "round_of_16"
    if "Quarterfinal" in header or "Quarter-final" in header:
        return "quarterfinal"
    if "Semifinal" in header or "Semi-final" in header:
        return "semifinal"
    if header == "Final":
        return "final"
    raise ValueError(f"Unrecognized stage header: {raw_header!r}")


def parse_score_expr(expr: str):
    """Returns (home_goals, away_goals, went_to_extra_time, decided_by_penalties,
    pen_home, pen_away) from the score portion of a match line."""
    before_parens = expr.split("(")[0].strip()
    pairs = SCORE_PAIR_RE.findall(before_parens)
    if not pairs:
        raise ValueError(f"No score found in expression: {expr!r}")

    went_to_et = "a.e.t." in before_parens
    decided_by_pens = "pen." in before_parens

    if decided_by_pens:
        # order in source text: "<pen_score> pen. <aet_score> a.e.t."
        pen_h, pen_a = pairs[0]
        goals_h, goals_a = pairs[-1]
        return int(goals_h), int(goals_a), True, True, int(pen_h), int(pen_a)
    if went_to_et:
        goals_h, goals_a = pairs[-1]
        return int(goals_h), int(goals_a), True, False, None, None

    goals_h, goals_a = pairs[0]
    return int(goals_h), int(goals_a), False, False, None, None


def parse_season_file(path: Path, season_label: str) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8").splitlines()

    stage_raw = None
    stage_norm = None
    current_date = None
    current_year = int(season_label.split("/")[0])
    rows = []
    declared_match_count = None

    for raw_line in lines:
        stripped = raw_line.strip()

        if stripped.startswith("# Matches"):
            declared_match_count = int(re.search(r"\d+", stripped).group())
            continue

        if stripped.startswith("▪"):
            stage_raw = stripped.lstrip("▪").strip()
            stage_norm = normalize_stage(stage_raw)
            continue

        date_match = DATE_RE.match(stripped)
        if date_match:
            _, mon, day, year = date_match.groups()
            if year:
                current_year = int(year)
            current_date = pd.Timestamp(f"{current_year}-{mon}-{day.zfill(2)}")
            continue

        if not stripped or stage_norm is None:
            continue

        match = MATCH_RE.match(stripped)
        if not match:
            continue

        try:
            goals_h, goals_a, aet, pens, pen_h, pen_a = parse_score_expr(match.group("score_expr"))
        except ValueError:
            continue

        rows.append({
            "season": season_label,
            "stage_raw": stage_raw,
            "stage": stage_norm,
            "stage_order": STAGE_ORDER[stage_norm],
            "match_date": current_date,
            "home_team_raw": match.group("home").strip(),
            "away_team_raw": match.group("away").strip(),
            "home_goals": goals_h,
            "away_goals": goals_a,
            "went_to_extra_time": aet,
            "decided_by_penalties": pens,
            "penalty_home_goals": pen_h,
            "penalty_away_goals": pen_a,
        })

    df = pd.DataFrame(rows)
    if declared_match_count is not None and len(df) != declared_match_count:
        raise ValueError(
            f"{path.name}: parsed {len(df)} matches but the source file declares "
            f"{declared_match_count} — parser likely missed or double-counted rows."
        )
    return df


def clean_all() -> pd.DataFrame:
    team_master = pd.read_csv(TEAM_MASTER_PATH)
    name_to_canonical = dict(zip(team_master["raw_name"], team_master["canonical_name"]))

    season_files = sorted(RAW_DIR.glob("cl_*.txt"))
    if not season_files:
        raise FileNotFoundError(f"No raw European files found in {RAW_DIR}. Run src/ingestion/fetch_european.py first.")

    frames = []
    for path in season_files:
        code = path.stem.split("_", 1)[1]  # "2012-13"
        start, end = code.split("-")
        season_label = f"{start}/{end}"
        frames.append(parse_season_file(path, season_label))
    all_matches = pd.concat(frames, ignore_index=True)

    all_matches["home_team"] = all_matches["home_team_raw"].map(name_to_canonical)
    all_matches["away_team"] = all_matches["away_team_raw"].map(name_to_canonical)
    # Opponents outside the 20-club scope aren't in team_master.csv (not needed -
    # we don't run analytics on them), so fall back to their raw source name for display.
    all_matches["home_team_display"] = all_matches["home_team"].fillna(all_matches["home_team_raw"])
    all_matches["away_team_display"] = all_matches["away_team"].fillna(all_matches["away_team_raw"])

    is_selected = all_matches["home_team"].isin(SELECTED_CLUBS) | all_matches["away_team"].isin(SELECTED_CLUBS)
    df = all_matches[is_selected].copy()

    df = df[df["home_goals"].notna() & df["away_goals"].notna()]
    df = df[df["home_team_raw"] != df["away_team_raw"]]

    def result(row):
        if row["home_goals"] > row["away_goals"]:
            return "H"
        if row["home_goals"] < row["away_goals"]:
            return "A"
        return "D"

    df["result"] = df.apply(result, axis=1)

    df = df.sort_values(["match_date", "season", "stage_order"]).reset_index(drop=True)
    df.insert(0, "match_id", [f"EU{i:05d}" for i in range(1, len(df) + 1)])

    print(f"Parsed {len(all_matches)} total Champions League matches across {all_matches['season'].nunique()} seasons.")
    print(f"Filtered to {len(df)} matches involving at least one of the 20 selected clubs.")

    return df


def main():
    df = clean_all()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} ({len(df)} rows, {len(df.columns)} columns)")


if __name__ == "__main__":
    main()

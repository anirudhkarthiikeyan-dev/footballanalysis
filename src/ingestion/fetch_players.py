"""Download raw season-level player data from the vaastav/Fantasy-Premier-League
public GitHub archive (https://github.com/vaastav/Fantasy-Premier-League).

Coverage: this project uses player data for 2019/20-2025/26 only (7 seasons).
The source has player totals back to 2016/17, but does not publish a
teams.csv lookup for 2016/17-2018/19, so player-to-team mapping cannot be
done reliably for those 3 seasons without risking a wrong assignment.
Rather than guess, those seasons are excluded from the player module.
Seasons 2012/13-2018/19 have NO player-level data in this project — that is
documented, not backfilled with fabricated numbers. See docs/data/DATA_SOURCES.md.

We only pull player-season totals here (players_raw.csv per season), which is
enough for per-90 stats, percentiles and similarity without needing
gameweek-by-gameweek granularity.
"""
import time
from pathlib import Path

import requests

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "players"

PLAYER_SEASONS = [
    "2019-20", "2020-21",
    "2021-22", "2022-23", "2023-24", "2024-25", "2025-26",
]

PLAYERS_URL = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season}/players_raw.csv"
TEAMS_URL = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season}/teams.csv"


def fetch(url: str, dest: Path) -> Path:
    resp = requests.get(url, timeout=25)
    resp.raise_for_status()
    if len(resp.content) < 200:
        raise ValueError(f"Suspiciously small response for {dest.name} ({len(resp.content)} bytes)")
    dest.write_bytes(resp.content)
    return dest


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ok, fail = 0, []
    for season in PLAYER_SEASONS:
        try:
            p = fetch(PLAYERS_URL.format(season=season), RAW_DIR / f"players_{season}.csv")
            t = fetch(TEAMS_URL.format(season=season), RAW_DIR / f"teams_{season}.csv")
            print(f"[OK]   {season} -> {p.name} ({p.stat().st_size:,}B), {t.name} ({t.stat().st_size:,}B)")
            ok += 1
        except Exception as exc:
            print(f"[FAIL] {season} -> {exc}")
            fail.append(season)
        time.sleep(0.3)
    print(f"\n{ok}/{len(PLAYER_SEASONS)} player seasons downloaded.")
    if fail:
        raise SystemExit(f"Failed: {fail}")


if __name__ == "__main__":
    main()

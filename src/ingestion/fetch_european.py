"""Download raw UEFA Champions League season files from the
openfootball/champions-league public-domain archive
(https://github.com/openfootball/champions-league, football.txt format,
explicitly public domain per its README/NOTES).

Coverage: 2012/13-2025/26, matching this project's Premier League range.
Every match in every group/league-phase and knockout round is included
in the source; this script only downloads it verbatim — filtering to
the 20 selected clubs happens in src/cleaning/clean_european.py.
"""
import time
from pathlib import Path

import requests

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "european"

SEASONS = [
    "2012-13", "2013-14", "2014-15", "2015-16", "2016-17", "2017-18",
    "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24",
    "2024-25", "2025-26",
]

URL = "https://raw.githubusercontent.com/openfootball/champions-league/master/{season}/cl.txt"


def fetch_season(season: str) -> Path:
    resp = requests.get(URL.format(season=season), timeout=20)
    resp.raise_for_status()
    if len(resp.content) < 500:
        raise ValueError(f"Suspiciously small response for {season} ({len(resp.content)} bytes)")
    dest = RAW_DIR / f"cl_{season}.txt"
    dest.write_bytes(resp.content)
    return dest


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ok, fail = 0, []
    for season in SEASONS:
        try:
            dest = fetch_season(season)
            print(f"[OK]   {season} -> {dest.name} ({dest.stat().st_size:,} bytes)")
            ok += 1
        except Exception as exc:
            print(f"[FAIL] {season} -> {exc}")
            fail.append(season)
        time.sleep(0.3)
    print(f"\n{ok}/{len(SEASONS)} seasons downloaded.")
    if fail:
        raise SystemExit(f"Failed: {fail}")


if __name__ == "__main__":
    main()

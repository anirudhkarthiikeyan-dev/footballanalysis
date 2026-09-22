"""Download raw Premier League match-level CSVs from football-data.co.uk.

Source: https://www.football-data.co.uk/englandm.php
Competition code for the Premier League on that site is "E0".
Each season file covers one season's full match list plus match stats
(shots, corners, cards) and bookmaker odds columns we do not use.

This script only downloads and saves the raw files verbatim under
data/raw/matches/ — no cleaning or transformation happens here.
"""
import sys
import time
from pathlib import Path

import requests

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "matches"

# football-data.co.uk season codes run AUG-year -> MAY-year, e.g. 2012/13 -> "1213"
SEASONS = [f"{y % 100:02d}{(y + 1) % 100:02d}" for y in range(2012, 2026)]
SEASON_LABELS = {f"{y % 100:02d}{(y + 1) % 100:02d}": f"{y}/{(y + 1) % 100:02d}" for y in range(2012, 2026)}

BASE_URL = "https://www.football-data.co.uk/mmz4281/{code}/E0.csv"


def fetch_season(code: str) -> Path:
    url = BASE_URL.format(code=code)
    dest = RAW_DIR / f"E0_{code}.csv"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    if len(resp.content) < 500:
        raise ValueError(f"Suspiciously small response for {code} ({len(resp.content)} bytes)")
    dest.write_bytes(resp.content)
    return dest


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for code in SEASONS:
        label = SEASON_LABELS[code]
        try:
            dest = fetch_season(code)
            size = dest.stat().st_size
            results.append((label, code, "OK", size))
            print(f"[OK]   {label} ({code}) -> {dest.name} ({size:,} bytes)")
        except Exception as exc:
            results.append((label, code, f"FAIL: {exc}", 0))
            print(f"[FAIL] {label} ({code}) -> {exc}")
        time.sleep(0.3)

    failures = [r for r in results if r[2] != "OK"]
    print(f"\n{len(results) - len(failures)}/{len(results)} seasons downloaded successfully.")
    if failures:
        print("Failures:")
        for label, code, err, _ in failures:
            print(f"  {label} ({code}): {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()

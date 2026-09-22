"""Season code/label helpers shared across the pipeline."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FIRST_SEASON_START_YEAR = 2012
LAST_SEASON_START_YEAR = 2025


def season_code_to_label(code: str) -> str:
    """'1213' -> '2012/13'"""
    start = int(code[:2])
    end = code[2:]
    century = "20"
    return f"{century}{start:02d}/{end}"


def all_season_labels() -> list[str]:
    return [f"{y}/{(y + 1) % 100:02d}" for y in range(FIRST_SEASON_START_YEAR, LAST_SEASON_START_YEAR + 1)]


def season_start_year(label: str) -> int:
    return int(label.split("/")[0])

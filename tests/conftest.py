import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def matches():
    return pd.read_csv(ROOT / "data" / "processed" / "matches_clean.csv", parse_dates=["match_date"])


@pytest.fixture(scope="session")
def db_conn():
    conn = sqlite3.connect(ROOT / "database" / "pl_intelligence.db")
    yield conn
    conn.close()

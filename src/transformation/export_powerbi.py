"""Export the star-schema tables straight out of the SQLite database as
CSVs Power BI can load directly (Get Data > Text/CSV, or Get Data >
Folder). This keeps Power BI's model in lockstep with the same
dimension/fact tables the Streamlit app and tests use — no separate
copy of the transformation logic.
"""
import sqlite3

import pandas as pd

from src.utils.seasons import PROJECT_ROOT

DB_PATH = PROJECT_ROOT / "database" / "pl_intelligence.db"
OUT_DIR = PROJECT_ROOT / "powerbi" / "model_exports"

TABLES = [
    "dim_team", "dim_season", "dim_date", "dim_player",
    "fact_match", "fact_team_season", "fact_player_season",
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    for table in TABLES:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        dest = OUT_DIR / f"{table}.csv"
        df.to_csv(dest, index=False)
        print(f"Exported {table}: {len(df)} rows -> {dest.relative_to(PROJECT_ROOT)}")
    conn.close()


if __name__ == "__main__":
    main()

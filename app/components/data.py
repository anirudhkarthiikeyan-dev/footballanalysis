"""Cached data access layer for the Streamlit app. All pages read through
here so there is exactly one place that knows about file paths / the DB.
"""
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "pl_intelligence.db"
MATCHES_PATH = ROOT / "data" / "processed" / "matches_clean.csv"
PLAYERS_PATH = ROOT / "data" / "processed" / "players_clean.csv"

PLAYER_SEASONS = ["2019/20", "2020/21", "2021/22", "2022/23", "2023/24", "2024/25", "2025/26"]
ADVANCED_STAT_SEASONS = ["2022/23", "2023/24", "2024/25", "2025/26"]


@st.cache_data(show_spinner=False)
def load_matches() -> pd.DataFrame:
    return pd.read_csv(MATCHES_PATH, parse_dates=["match_date"])


@st.cache_data(show_spinner=False)
def load_players() -> pd.DataFrame:
    return pd.read_csv(PLAYERS_PATH)


@st.cache_data(show_spinner=False)
def all_seasons() -> list[str]:
    return sorted(load_matches()["season"].unique())


@st.cache_data(show_spinner=False)
def all_teams() -> list[str]:
    return sorted(set(load_matches()["home_team"]) | set(load_matches()["away_team"]))


@st.cache_resource(show_spinner=False)
def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(show_spinner=False)
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql(sql, conn, params=params)

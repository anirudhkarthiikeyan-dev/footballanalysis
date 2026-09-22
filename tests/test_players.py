import pandas as pd
import pytest

from src.analytics.player_stats import add_per90_columns, percentile_rank

ROOT_PLAYERS = "data/processed/players_clean.csv"


@pytest.fixture(scope="module")
def players():
    return pd.read_csv(ROOT_PLAYERS)


def test_player_seasons_within_documented_coverage(players):
    seasons = set(players["season"])
    assert seasons <= {"2019/20", "2020/21", "2021/22", "2022/23", "2023/24", "2024/25", "2025/26"}


def test_no_negative_stats(players):
    for col in ["minutes", "goals_scored", "assists", "yellow_cards", "red_cards"]:
        assert (players[col] >= 0).all(), col


def test_advanced_stats_null_before_2022_23(players):
    pre = players[players["season"].isin(["2019/20", "2020/21", "2021/22"])]
    assert pre["expected_goals"].isna().all()
    assert pre["expected_assists"].isna().all()


def test_advanced_stats_present_from_2022_23(players):
    post = players[players["season"] == "2022/23"]
    assert post["expected_goals"].notna().any()


def test_haaland_2022_23_matches_known_record(players):
    row = players[(players["season"] == "2022/23") & (players["player_name"].str.contains("Haaland"))]
    assert len(row) == 1
    assert int(row.iloc[0]["goals_scored"]) == 36


def test_per90_calculation(players):
    df = add_per90_columns(players)
    sample = df[df["minutes"] > 0].iloc[0]
    expected = sample["goals_scored"] / (sample["minutes"] / 90)
    assert abs(sample["goals_per_90"] - expected) < 1e-9


def test_percentile_rank_position_scoped(players):
    result = percentile_rank(players, "2022/23", "FWD", min_minutes=450)
    if not result.empty:
        assert (result["position"] == "FWD").all()
        assert result["goals_per_90_pctile"].max() <= 100
        assert result["goals_per_90_pctile"].min() >= 0

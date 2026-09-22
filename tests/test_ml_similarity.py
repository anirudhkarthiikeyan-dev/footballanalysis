import pandas as pd
import pytest

from src.analytics.player_stats import add_per90_columns
from src.ml.player_similarity import find_similar_players


@pytest.fixture(scope="module")
def players_per90():
    players = pd.read_csv("data/processed/players_clean.csv")
    return add_per90_columns(players)


def test_similarity_excludes_query_player(players_per90):
    res = find_similar_players(players_per90, "Erling Haaland", "2022/23", top_n=5)
    assert "Erling Haaland" not in res["player_name"].values


def test_similarity_same_position_only(players_per90):
    res = find_similar_players(players_per90, "Erling Haaland", "2022/23", same_position_only=True, top_n=5)
    assert (res["position"] == "FWD").all()


def test_similarity_excludes_goalkeepers(players_per90):
    res = find_similar_players(players_per90, "Erling Haaland", "2022/23", same_position_only=False, top_n=20)
    assert "GK" not in res["position"].values


def test_similarity_unknown_player_returns_empty(players_per90):
    res = find_similar_players(players_per90, "Not A Real Player", "2022/23")
    assert res.empty


def test_similarity_distance_sorted_ascending(players_per90):
    res = find_similar_players(players_per90, "Mohamed Salah", "2023/24", top_n=6)
    if not res.empty:
        assert list(res["similarity_distance"]) == sorted(res["similarity_distance"])

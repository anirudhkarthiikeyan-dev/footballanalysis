import pandas as pd
import pytest

from src.analytics.european import (
    club_best_finish,
    club_season_campaigns,
    domestic_vs_europe,
    european_h2h,
    opponent_history,
)
from src.analytics.league_table import all_seasons_team_table


@pytest.fixture(scope="module")
def eu_matches():
    return pd.read_csv("data/processed/european_matches_clean.csv", parse_dates=["match_date"])


@pytest.fixture(scope="module")
def campaigns(eu_matches):
    return club_season_campaigns(eu_matches)


def test_leicester_campaign_matches_known_quarterfinal_run(campaigns):
    row = campaigns[(campaigns["club"] == "Leicester City") & (campaigns["season"] == "2016/17")].iloc[0]
    assert row["finish_label"] == "Quarterfinal"
    assert row["matches_played"] > 0


def test_best_finish_unknown_club_returns_none(campaigns):
    assert club_best_finish(campaigns, "Not A Real Club") is None


def test_best_finish_real_madrid_is_winner(campaigns):
    best = club_best_finish(campaigns, "Real Madrid")
    assert best["finish_label"] == "Winner"


def test_european_h2h_symmetric(eu_matches):
    a = european_h2h(eu_matches, "Real Madrid", "Bayern Munich")
    b = european_h2h(eu_matches, "Bayern Munich", "Real Madrid")
    assert len(a) == len(b)
    assert len(a) > 0  # these two have met many times historically


def test_european_h2h_only_between_the_two_named_clubs(eu_matches):
    games = european_h2h(eu_matches, "Real Madrid", "Bayern Munich")
    teams = set(games["home_team"]) | set(games["away_team"])
    assert teams <= {"Real Madrid", "Bayern Munich"}


def test_opponent_history_excludes_self(eu_matches):
    hist = opponent_history(eu_matches, "Arsenal")
    assert "Arsenal" not in hist["opponent"].values


def test_opponent_history_meetings_sum_reasonable(eu_matches):
    hist = opponent_history(eu_matches, "Real Madrid", top_n=1000)
    club_matches_count = len(eu_matches[(eu_matches["home_team"] == "Real Madrid") | (eu_matches["away_team"] == "Real Madrid")])
    assert hist["meetings"].sum() == club_matches_count


def test_domestic_vs_europe_structure(campaigns):
    pl_table = all_seasons_team_table(pd.read_csv("data/processed/matches_clean.csv", parse_dates=["match_date"]))
    result = domestic_vs_europe(pl_table, campaigns, "Arsenal")
    assert result["domestic"] is not None
    assert result["europe"] is not None
    assert result["domestic"]["win_pct"] >= 0
    assert result["europe"]["win_pct"] >= 0

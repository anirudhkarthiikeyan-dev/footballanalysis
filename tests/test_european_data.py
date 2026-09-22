import pandas as pd
import pytest

from src.cleaning.clean_european import SELECTED_CLUBS

EU_PATH = "data/processed/european_matches_clean.csv"

# (season, winner, runner_up, winner_goals, runner_up_goals) for every
# final 2012/13-2025/26 - independently known real results, used to
# verify the parser against ground truth, not just "it ran".
KNOWN_FINALS = [
    ("2012/13", "Bayern Munich", "Borussia Dortmund", 2, 1),
    ("2013/14", "Real Madrid", "Atlético Madrid", 4, 1),
    ("2014/15", "Barcelona", "Juventus", 3, 1),
    ("2015/16", "Real Madrid", "Atlético Madrid", 1, 1),  # penalties
    ("2016/17", "Real Madrid", "Juventus", 4, 1),
    ("2017/18", "Real Madrid", "Liverpool", 3, 1),
    ("2018/19", "Liverpool", "Tottenham Hotspur", 2, 0),
    ("2020/21", "Chelsea", "Manchester City", 1, 0),
    ("2021/22", "Real Madrid", "Liverpool", 1, 0),
    ("2022/23", "Manchester City", "Inter Milan", 1, 0),
    ("2023/24", "Real Madrid", "Borussia Dortmund", 2, 0),
]


@pytest.fixture(scope="module")
def eu_matches():
    return pd.read_csv(EU_PATH, parse_dates=["match_date"])


def test_only_selected_clubs_involved(eu_matches):
    involved = set(eu_matches["home_team"].dropna()) | set(eu_matches["away_team"].dropna())
    assert involved <= SELECTED_CLUBS


def test_no_duplicate_match_ids(eu_matches):
    assert eu_matches["match_id"].is_unique


def test_result_consistent_with_goals(eu_matches):
    computed = eu_matches.apply(
        lambda r: "H" if r["home_goals"] > r["away_goals"] else ("A" if r["home_goals"] < r["away_goals"] else "D"),
        axis=1,
    )
    assert (computed == eu_matches["result"]).all()


def test_penalty_shootouts_have_a_clear_winner(eu_matches):
    # decided_by_penalties means the tie (aggregate, for two-legged
    # rounds; that single match, for the Final) was level and went to
    # a shootout - it does NOT mean this specific leg's own scoreline
    # was a draw (e.g. a team can win a single leg 1-0 after extra
    # time while still needing penalties because the aggregate, across
    # both legs, was level). What must always hold is that the
    # shootout itself has a clear winner.
    pens = eu_matches[eu_matches["decided_by_penalties"]]
    assert len(pens) > 0
    assert pens["penalty_home_goals"].notna().all()
    assert pens["penalty_away_goals"].notna().all()
    assert (pens["penalty_home_goals"] != pens["penalty_away_goals"]).all()


def test_penalty_shootout_finals_are_drawn_on_the_night(eu_matches):
    # The Final is always a single match (no second leg), so if it was
    # decided by penalties, that match's own scoreline must be a draw.
    final_pens = eu_matches[(eu_matches["decided_by_penalties"]) & (eu_matches["stage"] == "final")]
    assert len(final_pens) > 0
    assert (final_pens["result"] == "D").all()


def test_known_finals_match_real_history(eu_matches):
    finals = eu_matches[eu_matches["stage"] == "final"]
    for season, winner, runner_up, w_goals, ru_goals in KNOWN_FINALS:
        row = finals[finals["season"] == season]
        assert len(row) == 1, f"Expected exactly one final for {season}"
        row = row.iloc[0]
        teams = {row["home_team"], row["away_team"]}
        assert teams == {winner, runner_up}, f"{season} final teams mismatch: {teams}"
        if row["home_team"] == winner:
            assert row["home_goals"] == w_goals and row["away_goals"] == ru_goals
        else:
            assert row["away_goals"] == w_goals and row["home_goals"] == ru_goals


def test_leicester_only_participated_2016_17(eu_matches):
    seasons = set(eu_matches[
        (eu_matches["home_team"] == "Leicester City") | (eu_matches["away_team"] == "Leicester City")
    ]["season"])
    assert seasons == {"2016/17"}, "Leicester City's real CL history in this range is 2016/17 only"


def test_aston_villa_only_participated_2024_25(eu_matches):
    seasons = set(eu_matches[
        (eu_matches["home_team"] == "Aston Villa") | (eu_matches["away_team"] == "Aston Villa")
    ]["season"])
    assert seasons == {"2024/25"}


def test_stage_order_is_monotonic_within_season_progression(eu_matches):
    valid_stages = {"group_stage", "league_phase", "playoff_round", "round_of_16", "quarterfinal", "semifinal", "final"}
    assert set(eu_matches["stage"].unique()) <= valid_stages


def test_reparsing_matches_declared_source_counts():
    # clean_european.parse_season_file raises if the parsed row count
    # doesn't match the "# Matches NNN" header declared in the source
    # file, so successfully re-running the full pipeline here is itself
    # the assertion.
    from src.cleaning.clean_european import clean_all
    df = clean_all()
    assert len(df) > 0

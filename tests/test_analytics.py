from src.analytics.head_to_head import h2h_summary
from src.analytics.league_table import team_season_table
from src.analytics.team_stats import home_away_split, league_goals_trend


def test_league_table_known_result_2015_16(matches):
    table = team_season_table(matches, "2015/16")
    champion = table.iloc[0]
    assert champion["team"] == "Leicester City"
    assert champion["points"] == 81
    assert champion["wins"] == 23
    assert champion["draws"] == 12
    assert champion["losses"] == 3


def test_league_table_20_teams_and_totals_sane(matches):
    table = team_season_table(matches, "2019/20")
    assert len(table) == 20
    assert table["played"].sum() == 380 * 2  # each match counted for both teams
    assert (table["points"] >= 0).all()


def test_h2h_symmetry(matches):
    a_perspective = h2h_summary(matches, "Arsenal", "Chelsea")
    b_perspective = h2h_summary(matches, "Chelsea", "Arsenal")
    assert a_perspective["meetings"] == b_perspective["meetings"]
    assert a_perspective["Arsenal_wins"] == b_perspective["Arsenal_wins"]
    assert a_perspective["draws"] == b_perspective["draws"]


def test_h2h_wins_draws_losses_sum_to_meetings(matches):
    s = h2h_summary(matches, "Manchester United", "Liverpool")
    total = s["Manchester United_wins"] + s["Liverpool_wins"] + s["draws"]
    assert total == s["meetings"]


def test_home_away_split_sums_to_total(matches):
    split = home_away_split(matches, "Arsenal", season="2018/19")
    home, away = split["home"], split["away"]
    total_played = home["played"] + away["played"]
    assert total_played == 38


def test_league_goals_trend_covers_all_seasons(matches):
    trend = league_goals_trend(matches)
    assert len(trend) == 14
    assert (trend["matches"] == 380).all()
    assert (trend["goals_per_match"] > 0).all()

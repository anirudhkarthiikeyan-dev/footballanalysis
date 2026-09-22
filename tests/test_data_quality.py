from src.validation.validate_matches import validate


def test_no_validation_errors(matches):
    errors = validate(matches)
    assert errors == []


def test_row_count_matches_expected_seasons(matches):
    assert len(matches) == 14 * 380


def test_no_duplicate_match_ids(matches):
    assert matches["match_id"].is_unique


def test_home_never_equals_away(matches):
    assert (matches["home_team"] != matches["away_team"]).all()


def test_goals_non_negative(matches):
    assert (matches["home_goals"] >= 0).all()
    assert (matches["away_goals"] >= 0).all()


def test_every_season_has_20_teams_and_380_matches(matches):
    for season, group in matches.groupby("season"):
        teams = set(group["home_team"]) | set(group["away_team"])
        assert len(teams) == 20, f"{season} has {len(teams)} teams"
        assert len(group) == 380, f"{season} has {len(group)} matches"


def test_result_consistent_with_goals(matches):
    computed = matches.apply(
        lambda r: "H" if r["home_goals"] > r["away_goals"] else ("A" if r["home_goals"] < r["away_goals"] else "D"),
        axis=1,
    )
    assert (computed == matches["result"]).all()

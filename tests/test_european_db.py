def test_european_tables_exist(db_conn):
    tables = {r[0] for r in db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"dim_competition", "fact_european_match", "fact_club_season_europe"} <= tables


def test_dim_team_includes_all_20_selected_clubs(db_conn):
    expected = {
        "Arsenal", "Chelsea", "Liverpool", "Manchester City", "Manchester United",
        "Tottenham Hotspur", "Leicester City", "Newcastle United", "Aston Villa",
        "Real Madrid", "Barcelona", "Atlético Madrid", "Sevilla", "Valencia",
        "Bayern Munich", "Borussia Dortmund", "Bayer Leverkusen", "RB Leipzig",
        "Juventus", "Inter Milan",
    }
    names = {r[0] for r in db_conn.execute("SELECT canonical_name FROM dim_team")}
    assert expected <= names


def test_fact_european_match_foreign_keys_resolve_for_selected_clubs(db_conn):
    # home/away team_id can legitimately be NULL (opponent outside the
    # 20-club scope) but season_id and competition_id must always resolve.
    (orphans,) = db_conn.execute("""
        SELECT COUNT(*) FROM fact_european_match fem
        LEFT JOIN dim_season s ON s.season_id = fem.season_id
        LEFT JOIN dim_competition c ON c.competition_id = fem.competition_id
        WHERE s.season_id IS NULL OR c.competition_id IS NULL
    """).fetchone()
    assert orphans == 0


def test_fact_club_season_europe_no_fabricated_seasons(db_conn):
    # Leicester City's only real Champions League campaign in this
    # dataset's range is 2016/17 - this asserts against the live
    # database, not just the intermediate CSV, that no other season
    # was fabricated for them.
    rows = db_conn.execute("""
        SELECT s.season_label FROM fact_club_season_europe fce
        JOIN dim_team t ON t.team_id = fce.team_id
        JOIN dim_season s ON s.season_id = fce.season_id
        WHERE t.canonical_name = 'Leicester City'
    """).fetchall()
    assert [r[0] for r in rows] == ["2016/17"]


def test_man_city_2022_23_winning_campaign(db_conn):
    row = db_conn.execute("""
        SELECT fce.matches_played, fce.wins, fce.draws, fce.losses, fce.finish_label
        FROM fact_club_season_europe fce
        JOIN dim_team t ON t.team_id = fce.team_id
        JOIN dim_season s ON s.season_id = fce.season_id
        WHERE t.canonical_name = 'Manchester City' AND s.season_label = '2022/23'
    """).fetchone()
    assert row == (13, 8, 5, 0, "Winner")


def test_matches_played_equals_wins_draws_losses(db_conn):
    (bad,) = db_conn.execute("""
        SELECT COUNT(*) FROM fact_club_season_europe
        WHERE matches_played != (wins + draws + losses)
    """).fetchone()
    assert bad == 0


def test_goal_difference_consistent_europe(db_conn):
    (bad,) = db_conn.execute("""
        SELECT COUNT(*) FROM fact_club_season_europe
        WHERE goal_difference != (goals_for - goals_against)
    """).fetchone()
    assert bad == 0

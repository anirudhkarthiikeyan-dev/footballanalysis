def test_expected_tables_exist(db_conn):
    tables = {r[0] for r in db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"dim_team", "dim_season", "dim_date", "fact_match", "fact_team_season"} <= tables


def test_fact_match_row_count(db_conn):
    (count,) = db_conn.execute("SELECT COUNT(*) FROM fact_match").fetchone()
    assert count == 14 * 380


def test_fact_team_season_row_count(db_conn):
    (count,) = db_conn.execute("SELECT COUNT(*) FROM fact_team_season").fetchone()
    assert count == 14 * 20


def test_fact_match_foreign_keys_resolve(db_conn):
    (orphans,) = db_conn.execute("""
        SELECT COUNT(*) FROM fact_match fm
        LEFT JOIN dim_team ht ON ht.team_id = fm.home_team_id
        LEFT JOIN dim_team at ON at.team_id = fm.away_team_id
        LEFT JOIN dim_season s ON s.season_id = fm.season_id
        WHERE ht.team_id IS NULL OR at.team_id IS NULL OR s.season_id IS NULL
    """).fetchone()
    assert orphans == 0


def test_points_formula_consistent(db_conn):
    (bad_points,) = db_conn.execute("""
        SELECT COUNT(*) FROM fact_team_season WHERE points != (3 * wins + draws)
    """).fetchone()
    assert bad_points == 0


def test_played_equals_wins_draws_losses(db_conn):
    (bad,) = db_conn.execute("""
        SELECT COUNT(*) FROM fact_team_season WHERE played != (wins + draws + losses)
    """).fetchone()
    assert bad == 0


def test_leicester_2015_16_title(db_conn):
    row = db_conn.execute("""
        SELECT t.canonical_name, fts.points, fts.league_position
        FROM fact_team_season fts
        JOIN dim_team t ON t.team_id = fts.team_id
        JOIN dim_season s ON s.season_id = fts.season_id
        WHERE s.season_label = '2015/16' AND fts.league_position = 1
    """).fetchone()
    assert row == ("Leicester City", 81, 1)

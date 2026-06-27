from app.db.session import DATABASE_URL


def test_database_url_comes_from_env_or_default() -> None:
    assert DATABASE_URL != ''

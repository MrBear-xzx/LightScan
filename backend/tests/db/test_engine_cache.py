from app.db.session import get_engine


def test_get_engine_reuses_cached_instance_for_same_url() -> None:
    url = 'sqlite+pysqlite:///./lightscan.db'
    e1 = get_engine(url)
    e2 = get_engine(url)
    assert e1 is e2

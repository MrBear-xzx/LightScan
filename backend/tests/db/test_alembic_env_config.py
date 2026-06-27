from pathlib import Path


def test_alembic_env_reads_database_url_from_env() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    text = (repo_root / 'backend' / 'alembic' / 'env.py').read_text(encoding='utf-8')
    assert "os.getenv('DATABASE_URL')" in text
    assert "config.set_main_option('sqlalchemy.url', database_url)" in text

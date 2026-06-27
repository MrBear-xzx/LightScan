from pathlib import Path


def test_initial_migration_contains_core_tables() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    migration_file = repo_root / 'backend' / 'alembic' / 'versions' / '0001_init_core_tables.py'
    migration = migration_file.read_text(encoding='utf-8')
    for table in ['assets', 'scan_tasks', 'events', 'findings', 'vuln_cases', 'policies', 'users']:
        assert f"'{table}'" in migration

from pathlib import Path


def test_backend_ci_workflow_has_concurrency_and_pr_path() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    workflow_file = repo_root / '.github' / 'workflows' / 'backend-ci.yml'
    content = workflow_file.read_text(encoding='utf-8')

    assert 'concurrency:' in content
    assert 'cancel-in-progress: true' in content
    assert 'pull_request:' in content
    assert 'paths:' in content
    assert "backend/**" in content
    assert ".github/workflows/backend-ci.yml" in content


def test_backend_ci_workflow_has_quality_gates() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    workflow_file = repo_root / '.github' / 'workflows' / 'backend-ci.yml'
    content = workflow_file.read_text(encoding='utf-8')

    assert 'Run lint' in content
    assert 'python -m ruff check app tests' in content

    assert 'Run db tests' in content
    assert 'python -m pytest tests/db -q' in content
    assert 'Run service tests' in content
    assert 'python -m pytest tests/services -q' in content
    assert 'Run api tests' in content
    assert 'python -m pytest tests/api -q' in content
    assert 'Run e2e smoke tests' in content
    assert 'python -m pytest tests/e2e -q' in content

    assert 'Run coverage gate' in content
    assert '--cov=app' in content
    assert '--cov-fail-under=70' in content

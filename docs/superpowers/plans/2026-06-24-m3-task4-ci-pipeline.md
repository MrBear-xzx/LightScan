# M3 任务4（发布流水线完善）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为仓库提供最小可用 CI 流水线，确保每次提交/PR 都自动执行后端回归测试。

**Architecture:** 使用 GitHub Actions 新增 `backend-ci` 工作流，拉起 PostgreSQL service，安装后端依赖并执行 `pytest tests -q`。同时补全 `pyproject.toml` 依赖定义，避免环境漂移。

**Tech Stack:** GitHub Actions、Python 3.12、PostgreSQL、pytest

---

## 任务拆解

1. 补齐后端依赖清单（SQLAlchemy/Alembic/psycopg/Celery/Redis）。
2. 新增 `.github/workflows/backend-ci.yml`（push + PR 触发）。
3. 在 CI 中配置 PostgreSQL service 与测试数据库连接。
4. 文档化本阶段计划并执行本地全量测试回归。

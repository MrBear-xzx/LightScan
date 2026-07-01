# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

LightScan 是一个面向私有化部署的漏洞分析平台。后端 FastAPI + SQLAlchemy + Celery，前端 Vue 3 + Vite + Pinia，数据库默认 SQLite（生产用 PostgreSQL）。

## 常用命令

### 后端开发

```bash
# 安装依赖
cd backend && pip install .

# 启动 API 服务（默认 http://localhost:8000）
cd backend && uvicorn app.main:app --reload

# 运行全部测试（默认 SQLite 本地，CI 用 PostgreSQL）
cd backend && python -m pytest tests -q

# 运行单个测试文件/用例
cd backend && python -m pytest tests/api/test_vuln_cases.py -q
cd backend && python -m pytest tests/api/test_vuln_cases.py::test_list_vuln_cases -q

# 分层测试（与 CI 一致）
cd backend && python -m pytest tests/db -q
cd backend && python -m pytest tests/services -q
cd backend && python -m pytest tests/api -q
cd backend && python -m pytest tests/worker -q
cd backend && python -m pytest tests/e2e -q

# Lint 检查
cd backend && python -m ruff check app tests

# 覆盖率检查（门禁 >= 70%）
cd backend && python -m pytest tests -q --cov=app --cov-fail-under=70

# 数据库迁移（生产 PostgreSQL 环境）
cd backend && alembic upgrade head
```

### 前端开发

```bash
# 开发模式（http://localhost:5173，API 自动代理到 8000）
cd frontend && npm run dev

# 生产构建（产物输出到 backend/app/static/）
cd frontend && npm run build
```

## 架构总览

### 分层架构

```
frontend/src/          Vue 3 SPA，通过 Vite proxy 连接后端
backend/app/
├── main.py            应用入口，注册路由和中间件
├── api/routes/        FastAPI 路由层（薄层，参数校验后调用 service）
│   └── tenant_guard.py 租户隔离依赖注入
├── services/          业务逻辑层（核心逻辑都在这里，不含 HTTP 依赖）
├── models/            SQLAlchemy ORM 模型（Asset, ScanTask, Finding, VulnCase, Policy, Event, User 等）
├── schemas/           Pydantic 请求/响应模型
├── auth/              JWT 生成/验证（jwt.py）和 RBAC 权限校验（rbac.py）
├── plugins/           插件抽象基类（base.py）+ 注册表（registry.py）+ 内置插件
│   ├── discovery/     HttpProbeDiscoveryPlugin
│   └── scanner/       NucleiJsonScannerPlugin, MockXJsonScannerPlugin
├── core/              核心配置加载（如 plugin_rollout 策略读取）
├── middleware/         AuditLogMiddleware（非 GET 写操作自动记录审计日志）
├── db/                session.py（引擎管理 + 建表）+ base.py（DeclarativeBase）
└── workers/           Celery 应用（celery_app.py）+ 任务（jobs.py）
```

### 关键设计决策

- **数据库引擎获取**：始终通过 `app.db.session.get_engine()` 获取，内部有 LRU 缓存。不要自己 `create_engine`。
- **测试数据库**：`tests/conftest.py` 会在每个测试前后清理所有表。CI 环境通过 `TEST_DATABASE_URL` 切换 PostgreSQL，本地默认 SQLite。测试中 Celery 始终 eager 模式。
- **租户隔离**：租户通过路由依赖注入 `require_tenant_guard` 获取（默认读 query param `tenant_id`），大部分接口需要此参数。
- **插件体系**：`DiscoveryPlugin`（discover + health）和 `ScannerPlugin`（scan + normalize + health）两个抽象基类。注册表 `PluginRegistry` 管理生命周期（status: enabled/disabled, rollout: stable/canary）。每个租户的插件 rollout 策略独立存储。
- **Celery fallback**：`celery_app.py` 在 Celery 未安装或 `CELERY_TASK_ALWAYS_EAGER=1` 时自动降级为本地同步调用，避免开发环境依赖 Redis。
- **前端构建集成**：`vite build` 输出到 `backend/app/static/`，FastAPI 检测到静态文件存在后启动 SPA fallback 中间件，非 API 路由的 404 返回 `index.html`。
- **审计日志**：`AuditLogMiddleware` 对非 GET/非 2xx 响应的请求自动写入 Event 表。

### 权限模型

三级角色：`admin` > `analyst` > `viewer`。路由通过 `require_role` 或 `require_permission` 依赖注入校验，具体权限映射见 `app/auth/rbac.py`。

### 前端页面路由

| 路径 | 页面 | 鉴权 |
|------|------|------|
| `/` | 登录/注册 | 否 |
| `/dashboard` | 仪表盘 | 是 |
| `/scans` | 扫描任务 | 是 |
| `/scans/:id` | 任务详情 | 是 |
| `/vulns` | 漏洞管理 | 是 |
| `/reports` | 报表中心 | 是 |
| `/notifications` | 通知管理 | 是 |
| `/plugins` | 插件管理 | 是 |
| `/admin` | 系统管理 | 是 |

路由守卫：`router.beforeEach` 检查 `localStorage.token`。API 模块 `api.js` 封装通用 `request()` 函数，自动添加 Bearer token，401 时自动跳回登录页。

## 协作约定

- `AGENT.md` 定义了项目级的协作约束（语言、Git 规范、质量门禁等），同样需要遵守
- Commit 格式：`<type>(<scope>): <中文标题>`，详见 `docs/governance/commit-convention.md`
- 分支命名：`feature/*`、`fix/*`、`hotfix/*`、`chore/*`
- 合并策略：Squash and merge，禁止直接 push main
- CI 触发：`pull_request(main)` 仅 `backend/**` 等路径变更时运行

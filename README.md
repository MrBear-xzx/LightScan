# LightScan

LightScan 是一个面向私有化部署的漏洞分析平台项目，当前已具备可运行的后端 API 骨架与核心能力，支持在本地或私有环境进行演示与联调。

## 当前版本可用能力

### 1. 基础系统能力

- 健康检查接口：`GET /health`
- 指标导出接口：`GET /metrics`（Prometheus 文本格式）
- OpenAPI 文档：`/docs`

### 2. 扫描引擎（M5）

- 扫描任务创建：`POST /api/v1/discovery/tasks`
- 批量扫描：`POST /api/v1/scan/batch`（多目标组并发创建发现任务，返回批次 ID）
- 扫描结果聚合：`GET /api/v1/scan/aggregation`（按资产维度聚合，返回严重等级分布与 Top 插件）
- 扫描任务进度查询：`GET /api/v1/scan/progress`（按 batch_id 或 task_ids 查询进度）
- 扫描任务取消：`POST /api/v1/scan/{task_id}/cancel`
- 超时任务检测：`POST /api/v1/scan/timeout-check`
- 扫描策略模板管理：`GET/PUT/DELETE /api/v1/scan/policies`

### 3. 插件管理系统（M4）

- 插件列表：`GET /api/v1/plugins`（支持 `tenant_id`、`capability`、`status` 过滤）
- 插件健康：`GET /api/v1/plugins/health`（仅统计 enabled 插件）
- 插件 rollout 策略：`GET/PUT /api/v1/plugins/rollout-policy`（PUT 响应包含 diff）
- 插件 rollout 审计：`GET /api/v1/plugins/rollout-audit`（支持分页、时间窗口、事件类型、插件 ID 过滤）
- 插件启停/灰度基座：配置驱动 `enabled/disabled` 与 `stable/canary`
- 内置扫描插件示例：`nuclei_json`、`mockx_json`
- 插件契约：`discover/scan/normalize/health` 全部可测

### 4. 漏洞运营（M2 + M6）

- 漏洞状态流转：`PATCH /api/v1/vuln-cases/{case_id}/state`
- 漏洞列表查询：`GET /api/v1/vuln-cases`（支持 tenant_id/state/owner/overdue_only/sort/sort_order/page/page_size）
- 漏洞指派与 SLA 设置：`PATCH /api/v1/vuln-cases/{case_id}/assign`
- 漏洞标签管理：`GET/POST/DELETE /api/v1/vuln-cases/tags` + case 标签分配
- 漏洞关联分析：`GET /api/v1/vuln-cases/correlation`（按资产聚合漏洞分布）
- 漏洞生命周期仪表盘：`GET /api/v1/reports/vuln/lifecycle`（状态分布、新增趋势、平均存在时间）
- 风险评分规则引擎：`GET/PUT /api/v1/risk/rules`（可配权重、严重等级映射、阈值）
- 运营事件留痕

### 5. 报表与通知（M2 + M8）

- 漏洞汇总报表：`GET /api/v1/reports/vuln/summary`
- 漏洞 CSV 导出：`GET /api/v1/reports/vuln/export.csv`
- 通知预览：`GET /api/v1/notifications/preview`
- 通知派发：`POST /api/v1/notifications/dispatch`（支持 webhook/feishu/dingtalk/wecom，支持同步/异步/去重）
- 租户通知策略：`GET/PUT /api/v1/notifications/policy`
- 通知模板引擎：`GET/POST/DELETE /api/v1/notifications/templates`（支持 {case_id}/{risk_score} 变量渲染）
- Webhook 事件订阅：`GET/POST/DELETE /api/v1/notifications/webhooks`
- 定时报表推送配置：`GET/POST/DELETE /api/v1/reports/scheduled`
- SLA 看板总览：`GET /api/v1/reports/sla/overview`（含 owner_breakdown）
- SLA 趋势：`GET /api/v1/reports/sla/trend`（支持 days/granularity）

### 6. 异步任务与重试（M3）

- 工单联动基座（Mock）：`POST /api/v1/tickets/sync`
- 异步任务状态查询：`GET /api/v1/jobs/status`
- 失败任务重试：`POST /api/v1/jobs/retry`
- 重试策略配置：`GET/PUT /api/v1/jobs/retry-policy`
- 重试历史查询：`GET /api/v1/jobs/retries`（支持分页、类型/关键字/时间窗口过滤、columns 裁剪）
- 重试历史导出：`GET /api/v1/jobs/retries/export.csv`
- 重试历史总览：`GET /api/v1/jobs/retries/overview`

### 7. 用户与权限（M7）

- 用户注册：`POST /api/v1/auth/register`
- 用户登录：`POST /api/v1/auth/login`（返回 JWT token）
- 当前用户信息：`GET /api/v1/auth/me`
- 用户权限查询：`GET /api/v1/auth/permissions`
- 角色权限模型：admin / analyst / viewer 三级角色 + 资源级权限校验
- 操作审计日志：`GET /api/v1/ops/logs`（自动中间件记录写操作）
- 项目空间管理：`GET/POST/DELETE /api/v1/projects` + 成员管理

### 8. 运维与部署（M9）

- 操作日志查询：`GET /api/v1/ops/logs`（支持分页与事件类型过滤）
- 告警规则管理：`GET/POST/DELETE /api/v1/ops/alert-rules`
- 备份记录管理：`GET/POST /api/v1/ops/backups`
- Kubernetes 部署清单：`deploy/k8s/`（ConfigMap + Deployment + Service）
- Docker Compose 部署：`deploy/docker-compose.yml`
- Prometheus 指标导出：`/metrics`
- GitHub Actions CI：`pull_request(main)` 自动 ruff + 分层测试 + 覆盖率门禁



## 前端交互页面 (Vue 3 SPA)

系统提供基于 Vue 3 + Vite 构建的 Web 前端界面，开发时通过代理连接后端 API，构建后由 FastAPI 作为静态文件提供服务。

### 页面构成

| 页面 | 路由 | 主要功能 |
|------|------|----------|
| 登录/注册 | / | 租户登录、用户注册 |
| 仪表盘 | /dashboard | 漏洞统计概览 |
| 扫描任务 | /scans | 创建/批量扫描、策略管理 |
| 漏洞管理 | /vulns | 列表/状态/分配/标签/风险规则 |
| 报表中心 | /reports | SLA概览趋势、漏洞汇总、定时报表 |
| 通知管理 | /notifications | 通知发送/策略/模板/Webhook |
| 插件管理 | /plugins | 插件启停/健康/灰度/审计 |
| 系统管理 | /admin | 用户/告警/日志/备份/项目 |

### 本地开发

`
cd frontend && npm run dev
`

默认 http://localhost:5173，API 自动代理到 8000 端口。

### 生产构建

`
cd frontend && npm run build
`

构建产物输出到 backend/app/static/，启动后端即可访问 http://localhost:8000/ 看到完整前端页面。

## 质量与测试状态

- 当前后端测试：`cd backend && python -m pytest tests -q`
- 最新通过：105 passed（PostgreSQL 环境）
- 测试覆盖：API、服务、Worker、数据库、最小 e2e 冒烟

## 关键文档

- 产品与架构设计：`docs/superpowers/specs/2026-06-23-vulnerability-analysis-platform-design.md`
- 实施计划：`docs/superpowers/plans/`
- 私有化部署说明：`docs/operations/private-deploy.md`
- 发布与回滚模板：`docs/operations/release-rollback-template.md`
- 依赖源说明（国内可选）：`docs/governance/dependency-source.md`

## 仓库信息

- 默认分支：`main`
- 远程仓库：`git@github.com:MrBear-xzx/LightScan.git`

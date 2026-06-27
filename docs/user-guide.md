# LightScan 使用手册

> 版本 0.1.0 | 面向私有化部署的漏洞分析平台

---

## 目录

1. [快速开始](#1-快速开始)
2. [用户认证](#2-用户认证)
3. [扫描任务](#3-扫描任务)
4. [插件管理](#4-插件管理)
5. [漏洞运营](#5-漏洞运营)
6. [报表与通知](#6-报表与通知)
7. [异步任务与重试](#7-异步任务与重试)
8. [运维管理](#8-运维管理)
9. [部署指南](#9-部署指南)
10. [常见问题](#10-常见问题)

---

## 1. 快速开始

### 1.1 环境要求

- Python >= 3.12
- pip 依赖（自动安装）

### 1.2 启动服务

```bash
cd backend
pip install -r requirements.txt  # 或手动安装: fastapi uvicorn sqlalchemy pydantic pyjwt
uvicorn app.main:app --reload --port 8000
```

服务启动后会自动创建 SQLite 数据库和所有表。

### 1.3 验证服务

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# 响应: {"status":"ok"}
```

### 1.4 API 文档

浏览器访问 http://127.0.0.1:8000/docs 查看 Swagger 交互式文档。


### 1.5 前端交互页面

前端基于 Vue 3 + Vite 构建，支持 IE11+ 和所有现代浏览器。构建后由 FastAPI 作为静态文件提供，访问 http://127.0.0.1:8000/ 即可使用。

#### 1.5.1 页面导览

系统提供 8 个前端页面，通过左侧导航栏切换：

| 页面 | 路由 | 用途 |
|------|------|------|
| 登录/注册 | / | 用户注册与登录，注册后自动登录 |
| 仪表盘 | /dashboard | 漏洞总量/待处理/今日新增/平均存在时间、状态分布、最近操作、扫描聚合 |
| 扫描任务 | /scans | 创建扫描任务、批量扫描、任务列表与进度、扫描策略管理 |
| 漏洞管理 | /vulns | 漏洞列表（搜索/状态筛选）、状态变更弹窗、指派责任人、标签CRUD、关联分析、风险规则配置 |
| 报表中心 | /reports | SLA概览（含severity分解）、SLA趋势（日期范围查询）、漏洞汇总与CSV导出、生命周期分析、定时报表CRUD |
| 通知管理 | /notifications | 手动通知发送、通知策略配置、模板CRUD、Webhook订阅管理 |
| 插件管理 | /plugins | 插件列表与启停、健康状态大盘、灰度策略配置、操作审计记录 |
| 系统管理 | /admin | 用户管理、告警规则CRUD、操作日志（类型筛选）、数据备份、项目空间管理 |

#### 1.5.2 开发模式

编辑前端页面后需要重新构建：

```bash
cd frontend
npm run dev          # 开发模式，http://localhost:5173
npm run build        # 生产构建，输出到 backend/app/static/
```

> 开发模式下 API 自动代理到 http://127.0.0.1:8000，无需额外配置。

#### 1.5.3 常见操作

- **注册**：填写租户 ID、用户名、密码、角色，提交后自动登录并跳转仪表盘
- **搜索漏洞**：在漏洞管理页面可使用搜索框按目标/漏洞名搜索，也可按状态筛选
- **修改漏洞状态**：点击漏洞旁的"改状态"按钮，选择目标状态并填写备注
- **指派漏洞**：点击"分配"按钮，输入责任人用户名
- **创建定时报表**：填入名称、Cron 表达式、收件人邮箱即可
- **数据导出**：在报表中心的漏洞汇总页，点击"导出 CSV"
---

## 2. 用户认证

系统使用 JWT 令牌进行身份认证，支持三级角色：admin、analyst、viewer。

### 2.1 注册用户

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "username": "admin", "password": "admin123", "role": "admin"}'
```

### 2.2 登录获取令牌

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "username": "admin", "password": "admin123"}'
```

响应中的 `access_token` 后续请求作为 Bearer Token 使用。

### 2.3 使用令牌访问受保护接口

```bash
# 获取当前用户信息
curl http://127.0.0.1:8000/api/v1/auth/me \
  -H "Authorization: Bearer <token>"

# 查询当前用户权限
curl http://127.0.0.1:8000/api/v1/auth/permissions \
  -H "Authorization: Bearer <token>"
```

### 2.4 角色权限说明

| 角色 | 权限等级 | 可执行操作 |
|------|---------|-----------|
| viewer | 10 | 只读操作（查看漏洞、报表、日志） |
| analyst | 50 | 读写操作（创建扫描、管理漏洞、派发通知） |
| admin | 100 | 全部权限（管理用户、告警规则、项目空间） |

---

## 3. 扫描任务

### 3.1 创建发现任务

```bash
curl -X POST http://127.0.0.1:8000/api/v1/discovery/tasks \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "targets": ["example.com"], "policy_id": "default-external"}'
```

### 3.2 批量扫描

一次提交多个目标组，每个组独立创建任务。

```bash
curl -X POST http://127.0.0.1:8000/api/v1/scan/batch \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "t1",
    "batches": [
      {"targets": ["example.com"], "policy_id": "default-external"},
      {"targets": ["10.0.0.1", "10.0.0.2"], "policy_id": "internal-scan"}
    ]
  }'
```

响应包含 `batch_id` 和各任务 ID。

### 3.3 查询扫描进度

按批次 ID 查询：

```bash
curl "http://127.0.0.1:8000/api/v1/scan/progress?tenant_id=t1&batch_id=batch-20260625-xxxx"
```

按任务 ID 列表查询：

```bash
curl "http://127.0.0.1:8000/api/v1/scan/progress?tenant_id=t1&task_ids=1,2,3"
```

响应包含 `completed/failed/running/pending` 分布统计。

### 3.4 取消扫描任务

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scan/1/cancel?tenant_id=t1"
```

### 3.5 超时任务检测

检查并自动标记超时任务（默认 300 秒，可配）。

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scan/timeout-check?tenant_id=t1&timeout_seconds=300"
```

### 3.6 扫描结果聚合

按资产维度聚合所有扫描发现结果。

```bash
curl "http://127.0.0.1:8000/api/v1/scan/aggregation?tenant_id=t1"
```

返回包含按资产分组的严重等级分布和 Top 插件统计。

### 3.7 扫描策略模板

创建扫描策略模板：

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/scan/policies \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "t1",
    "name": "quick-scan",
    "description": "快速扫描",
    "plugins": [{"plugin_id": "nuclei_json", "enabled": true, "config": {"timeout": 30}}],
    "extra_config": {"max_concurrency": 5}
  }'
```

查询、删除：

```bash
# 列表
curl "http://127.0.0.1:8000/api/v1/scan/policies?tenant_id=t1"
# 详情
curl "http://127.0.0.1:8000/api/v1/scan/policies/quick-scan?tenant_id=t1"
# 删除
curl -X DELETE "http://127.0.0.1:8000/api/v1/scan/policies/quick-scan?tenant_id=t1"
```

---

## 4. 插件管理

### 4.1 查询插件列表

```bash
# 全部插件
curl "http://127.0.0.1:8000/api/v1/plugins?tenant_id=t1"
# 按能力过滤
curl "http://127.0.0.1:8000/api/v1/plugins?tenant_id=t1&capability=scan"
# 按状态过滤
curl "http://127.0.0.1:8000/api/v1/plugins?tenant_id=t1&status=enabled"
```

### 4.2 插件健康状态

```bash
curl "http://127.0.0.1:8000/api/v1/plugins/health?tenant_id=t1"
```

### 4.3 配置插件 Rollout 策略

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/plugins/rollout-policy \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "t1",
    "plugins": {
      "nuclei_json": {"status": "enabled", "rollout": "stable"},
      "http_probe": {"status": "enabled", "rollout": "canary"}
    }
  }'
```

响应包含本次变更的 `diff`。

查询当前策略：

```bash
curl "http://127.0.0.1:8000/api/v1/plugins/rollout-policy?tenant_id=t1"
```

### 4.4 Rollout 审计

```bash
# 基本查询
curl "http://127.0.0.1:8000/api/v1/plugins/rollout-audit?tenant_id=t1"
# 分页
curl "http://127.0.0.1:8000/api/v1/plugins/rollout-audit?tenant_id=t1&page=1&page_size=10"
# 按事件类型过滤
curl "http://127.0.0.1:8000/api/v1/plugins/rollout-audit?tenant_id=t1&event_type=plugin_rollout_policy_updated"
# 按时间窗口过滤
curl "http://127.0.0.1:8000/api/v1/plugins/rollout-audit?tenant_id=t1&requested_from=2026-01-01T00:00:00Z&requested_to=2026-12-31T23:59:59Z"
```

---

## 5. 漏洞运营

### 5.1 漏洞状态流转

```bash
# 更新漏洞状态
curl -X PATCH http://127.0.0.1:8000/api/v1/vuln-cases/1/state \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "state": "in_progress"}'
```

可用状态：`new → in_progress → resolved / false_positive / rejected`

### 5.2 查询漏洞列表

```bash
# 基本查询
curl "http://127.0.0.1:8000/api/v1/vuln-cases?tenant_id=t1"
# 按状态过滤
curl "http://127.0.0.1:8000/api/v1/vuln-cases?tenant_id=t1&state=new"
# 按负责人过滤
curl "http://127.0.0.1:8000/api/v1/vuln-cases?tenant_id=t1&owner=admin"
# 排序
curl "http://127.0.0.1:8000/api/v1/vuln-cases?tenant_id=t1&sort_by=risk_score&sort_order=desc"
# 分页
curl "http://127.0.0.1:8000/api/v1/vuln-cases?tenant_id=t1&page=1&page_size=20"
```

### 5.3 指派与设置 SLA

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/vuln-cases/1/assign \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "owner": "analyst01", "sla_hours": 24}'
```

### 5.4 风险评分规则配置

```bash
# 查询当前规则
curl "http://127.0.0.1:8000/api/v1/risk/rules?tenant_id=t1"

# 更新规则
curl -X PUT "http://127.0.0.1:8000/api/v1/risk/rules?tenant_id=t1" \
  -H "Content-Type: application/json" \
  -d '{
    "severity_map": {"critical": 10.0, "high": 8.0, "medium": 5.0, "low": 2.0, "unknown": 1.0},
    "weights": {
      "severity_weight": 0.3, "asset_criticality_weight": 0.25,
      "exposure_weight": 0.2, "exploitability_weight": 0.2,
      "compensating_control_penalty": 0.05
    },
    "thresholds": {"critical": 8.0, "high": 6.0, "medium": 3.0, "low": 0.0}
  }'
```

### 5.5 漏洞标签管理

```bash
# 创建标签
curl -X POST http://127.0.0.1:8000/api/v1/vuln-cases/tags \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "name": "critical", "color": "#ff0000"}'

# 标签列表
curl "http://127.0.0.1:8000/api/v1/vuln-cases/tags?tenant_id=t1"

# 删除标签
curl -X DELETE "http://127.0.0.1:8000/api/v1/vuln-cases/tags/1?tenant_id=t1"

# 给漏洞案例分配标签
curl -X POST http://127.0.0.1:8000/api/v1/vuln-cases/1/tags?tenant_id=t1 \
  -H "Content-Type: application/json" \
  -d '{"case_id": 1, "tag_ids": [1, 2]}'

# 查询案例的标签
curl "http://127.0.0.1:8000/api/v1/vuln-cases/1/tags?tenant_id=t1"
```

### 5.6 漏洞关联分析

```bash
curl "http://127.0.0.1:8000/api/v1/vuln-cases/correlation?tenant_id=t1"
```

按资产维度聚合，返回各资产的漏洞等级分布和最高风险摘要。

### 5.7 漏洞生命周期仪表盘

```bash
curl "http://127.0.0.1:8000/api/v1/reports/vuln/lifecycle?tenant_id=t1"
```

返回状态分布、今日/本周新增、平均存在时间等指标。

---

## 6. 报表与通知

### 6.1 漏洞汇总报表

```bash
curl "http://127.0.0.1:8000/api/v1/reports/vuln/summary?tenant_id=t1"
```

### 6.2 漏洞 CSV 导出

```bash
curl "http://127.0.0.1:8000/api/v1/reports/vuln/export.csv?tenant_id=t1"
```

### 6.3 SLA 看板总览

```bash
curl "http://127.0.0.1:8000/api/v1/reports/sla/overview?tenant_id=t1"
```

### 6.4 SLA 趋势

```bash
# 按天粒度
curl "http://127.0.0.1:8000/api/v1/reports/sla/trend?tenant_id=t1&days=7&granularity=day"
# 按周粒度
curl "http://127.0.0.1:8000/api/v1/reports/sla/trend?tenant_id=t1&days=30&granularity=week"
```

### 6.5 通知派发

```bash
curl -X POST http://127.0.0.1:8000/api/v1/notifications/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "t1",
    "min_risk_score": 7.0,
    "provider": "webhook",
    "webhook_url": "https://hooks.example.com/alert",
    "dedup_window_minutes": 30
  }'
```

支持 provider：`webhook`、`feishu`、`dingtalk`、`wecom`。

### 6.6 通知模板管理

```bash
# 创建模板
curl -X POST "http://127.0.0.1:8000/api/v1/notifications/templates?tenant_id=t1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "vuln-alert",
    "provider": "dingtalk",
    "title_template": "漏洞告警 #{case_id}",
    "body_template": "风险评分: {risk_score}\n状态: {state}"
  }'

# 模板列表
curl "http://127.0.0.1:8000/api/v1/notifications/templates?tenant_id=t1"
```

模板支持变量：`{case_id}`、`{risk_score}`、`{state}`、`{owner}`、`{tenant_id}`。

### 6.7 Webhook 订阅

```bash
# 创建订阅
curl -X POST "http://127.0.0.1:8000/api/v1/notifications/webhooks?tenant_id=t1" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://hooks.example.com/events",
    "event_types": ["vuln_case_created", "vuln_case_state_changed"],
    "enabled": true
  }'

# 订阅列表
curl "http://127.0.0.1:8000/api/v1/notifications/webhooks?tenant_id=t1"

# 删除订阅
curl -X DELETE "http://127.0.0.1:8000/api/v1/notifications/webhooks/1?tenant_id=t1"
```

### 6.8 定时报表推送配置

```bash
# 创建定时报表
curl -X POST "http://127.0.0.1:8000/api/v1/reports/scheduled?tenant_id=t1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weekly-vuln-summary",
    "report_type": "vuln_summary",
    "cron_expression": "0 9 * * 1",
    "provider": "dingtalk",
    "webhook_url": "https://oapi.dingtalk.com/robot/send"
  }'

# 列表
curl "http://127.0.0.1:8000/api/v1/reports/scheduled?tenant_id=t1"
```

报表类型：`vuln_summary`、`sla_overview`、`risk_trend`

### 6.9 通知策略配置

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/notifications/policy \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "t1",
    "dedup_window_minutes": 30,
    "dedup_policy_by_risk": {"high": 60, "medium": 30, "low": 10}
  }'
```

---

## 7. 异步任务与重试

### 7.1 查询任务状态

```bash
curl "http://127.0.0.1:8000/api/v1/jobs/status?tenant_id=t1&job_id=job-xxx"
```

### 7.2 重试失败任务

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jobs/retry \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "job_id": "job-xxx"}'
```

### 7.3 配置重试策略

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/jobs/retry-policy \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "max_retry_count": 5, "retry_cooldown_seconds": 120}'
```

### 7.4 重试历史查询

```bash
# 基本查询
curl "http://127.0.0.1:8000/api/v1/jobs/retries?tenant_id=t1"
# 分页 + 过滤
curl "http://127.0.0.1:8000/api/v1/jobs/retries?tenant_id=t1&page=1&page_size=10&job_type=notification&sort_order=desc"
# 列裁剪
curl "http://127.0.0.1:8000/api/v1/jobs/retries?tenant_id=t1&columns=source_job_id,new_job_id,retry_count"
```

### 7.5 重试历史导出 CSV

```bash
curl "http://127.0.0.1:8000/api/v1/jobs/retries/export.csv?tenant_id=t1"
```

### 7.6 重试历史总览

```bash
curl "http://127.0.0.1:8000/api/v1/jobs/retries/overview?tenant_id=t1"
```

---

## 8. 运维管理

### 8.1 操作日志查询

```bash
# 基本查询（最近 20 条）
curl "http://127.0.0.1:8000/api/v1/ops/logs?tenant_id=t1"
# 分页 + 事件类型过滤
curl "http://127.0.0.1:8000/api/v1/ops/logs?tenant_id=t1&page=1&page_size=50&event_type=api_post"
```

### 8.2 告警规则管理

```bash
# 创建告警规则
curl -X POST "http://127.0.0.1:8000/api/v1/ops/alert-rules?tenant_id=t1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "high-task-failure",
    "enabled": true,
    "severity": "critical",
    "metrics": [
      {"metric_name": "lightscan_tasks_total", "operator": ">", "threshold": 100, "duration_seconds": 300}
    ]
  }'

# 规则列表
curl "http://127.0.0.1:8000/api/v1/ops/alert-rules?tenant_id=t1"

# 删除规则
curl -X DELETE "http://127.0.0.1:8000/api/v1/ops/alert-rules/1?tenant_id=t1"
```

### 8.3 备份记录管理

```bash
# 创建备份记录
curl -X POST "http://127.0.0.1:8000/api/v1/ops/backups?tenant_id=t1&description=pre-upgrade"
# 备份列表
curl "http://127.0.0.1:8000/api/v1/ops/backups?tenant_id=t1"
```

### 8.4 项目空间管理

```bash
# 创建项目
curl -X POST http://127.0.0.1:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "t1", "name": "核心业务线", "description": "核心业务资产扫描"}'

# 项目列表
curl "http://127.0.0.1:8000/api/v1/projects?tenant_id=t1"

# 添加成员
curl -X POST "http://127.0.0.1:8000/api/v1/projects/1/members?tenant_id=t1" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "role": "admin"}'

# 成员列表
curl "http://127.0.0.1:8000/api/v1/projects/1/members?tenant_id=t1"

# 删除项目
curl -X DELETE "http://127.0.0.1:8000/api/v1/projects/1?tenant_id=t1"
```

### 8.5 Prometheus 指标

```bash
curl http://127.0.0.1:8000/metrics
```

---

## 9. 部署指南

### 9.1 Docker Compose 部署

```bash
cd deploy
docker compose up -d
```

### 9.2 Kubernetes 部署

```bash
kubectl apply -f deploy/k8s/configmap.yaml
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml
```

### 9.3 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATABASE_URL | sqlite:///./lightscan.db | 数据库连接串 |
| SECRET_KEY | dev-secret-key-change-in-production | JWT 签名密钥 |
| REDIS_URL | redis://redis:6379/0 | Redis 连接串 |
| CELERY_TASK_ALWAYS_EAGER | (unset) | 测试时设置为 "1" |

---

## 10. 常见问题

### 10.1 启动后表不存在怎么办

服务启动时自动调用 `ensure_tables()` 创建所有表。如手动删除数据库文件，重启服务即可重建。

### 10.2 如何重置数据

```bash
rm backend/lightscan.db
# 重启服务即可自动重建
```

### 10.3 JWT 令牌过期

默认 24 小时过期，重新登录获取新令牌。

### 10.4 所有接口都返回 401

确认请求头中包含 `Authorization: Bearer <token>`。

### 10.5 接口返回 403

当前用户角色权限不足。联系 admin 提升角色等级。

---

> 更多信息请参阅 README.md 和 docs/ 目录下的设计文档。

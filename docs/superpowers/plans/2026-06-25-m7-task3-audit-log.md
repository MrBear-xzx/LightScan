# M7 任务3（操作审计日志）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 通过中间件自动记录所有写操作与异常请求的审计日志。  
**Architecture:** FastAPI BaseHTTPMiddleware，拦截 POST/PUT/PATCH/DELETE 和非 200 GET 请求，写入 events 表。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

## 任务拆解

1. 新增 backend/app/middleware/audit_log.py 中间件。
2. 注册到 main.py。
3. 新增测试：通过 API 调用验证审计事件被记录。
4. 更新 README。

## 验收标准

- [ ] 写操作（POST/PUT/PATCH/DELETE）自动记录审计事件。
- [ ] 审计事件包含 method、path、status_code、duration_ms。
- [ ] 定向测试通过。

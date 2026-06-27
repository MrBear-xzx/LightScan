# M3 任务12（重试护栏：上限与冷却）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为失败任务重试接口增加基础防抖与防风暴护栏，避免无限重试和瞬时重放。

**Architecture:** 在 `POST /api/v1/jobs/retry` 增加规则：默认最大重试次数 3、重试冷却 60 秒；重试成功时回写 `retry_count/last_retry_at` 到事件 payload。

**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：超过上限与冷却窗口返回 409。
2. 实现重试上限与冷却判断逻辑。
3. 重试成功时记录重试元数据（计数与时间戳）。
4. 全量回归验证并更新文档。

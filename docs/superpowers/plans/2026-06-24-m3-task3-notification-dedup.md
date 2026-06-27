# M3 任务3（通知去重抑制）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为通知派发提供短时去重抑制能力，避免重复告警风暴，支持后续策略化扩展。

**Architecture:** 在通知服务中基于 `events` 表最近 `notification_dispatched` 事件进行窗口判断；命中窗口则记录 `notification_suppressed` 并跳过发送。API 请求增加 `dedup_window_minutes`，响应返回 `suppressed` 计数。

**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：同一漏洞在去重窗口内二次派发应被抑制并记录事件。
2. 扩展 schema：新增 `dedup_window_minutes` 与响应 `suppressed`。
3. 实现服务逻辑：查询最近派发事件并执行抑制。
4. 路由与 worker 接入新参数，更新 README 与全量测试。

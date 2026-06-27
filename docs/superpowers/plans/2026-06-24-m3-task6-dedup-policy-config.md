# M3 任务6（告警抑制策略配置化）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将通知去重从“单一窗口”升级为“按风险级别可配置窗口”，提升高危/中危告警策略灵活性。

**Architecture:** 在通知派发请求中新增 `dedup_policy_by_risk`（`high/medium/low`），服务层按漏洞风险分解析去重窗口并执行抑制判断；未配置策略时保持原 `dedup_window_minutes` 行为。

**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：高危与中危在不同策略窗口下应出现不同抑制结果。
2. 扩展 schema：新增 `dedup_policy_by_risk` 请求参数。
3. 服务层实现：按风险分解析窗口并执行去重判断。
4. 路由与 worker 透传策略参数，执行全量测试回归。

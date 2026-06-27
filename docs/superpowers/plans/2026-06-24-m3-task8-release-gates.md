# M3 任务8（发布门禁规则细化）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 优化 CI 门禁触发策略，避免重复流水线与资源浪费，同时确保主干合并门禁稳定。

**Architecture:** `backend-ci` 工作流改为 `pull_request(main)` 主触发，并增加路径过滤；引入 `concurrency` 组以自动取消同分支旧任务。

**Tech Stack:** GitHub Actions、pytest

---

## 任务拆解

1. 新增失败测试：校验 workflow 含并发互斥与路径过滤配置。
2. 调整 workflow 触发策略（PR + paths）。
3. 增加 concurrency（`cancel-in-progress: true`）。
4. 执行全量测试并同步文档。

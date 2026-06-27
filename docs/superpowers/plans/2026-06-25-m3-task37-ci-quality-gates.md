# M3 任务37（CI 质量门禁增强）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 强化后端 CI 质量门禁，纳入 lint、分层测试与覆盖率阈值检查。  
**Architecture:** 在现有 `backend-ci.yml` 基础上追加门禁步骤，不改变触发策略与并发互斥策略。  
**Tech Stack:** GitHub Actions、pytest、ruff、pytest-cov

---

## 任务拆解

1. 新增失败测试：workflow 必须包含 lint、分层测试、覆盖率门禁步骤。  
2. 更新 CI workflow：增加 `Run lint`、`Run db/service/api/e2e tests`、`Run coverage gate`。  
3. 更新依赖：补充 `ruff` 与 `pytest-cov`。  
4. 更新 README 的 CI 说明。  
5. 运行 workflow 测试与后端全量回归。

## 验收标准

- [ ] workflow 包含 lint、分层测试、覆盖率门禁。  
- [ ] 覆盖率门禁阈值为 `--cov-fail-under=70`。  
- [ ] workflow 相关 e2e 测试通过。  
- [ ] 后端全量测试通过。

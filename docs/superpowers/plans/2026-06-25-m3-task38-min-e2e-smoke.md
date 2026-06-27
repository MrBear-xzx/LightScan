# M3 任务38（最小 e2e 冒烟链路）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 补齐最小可运行 e2e 冒烟链路，确保关键 API 串联可快速验证。  
**Architecture:** 在现有 `tests/e2e/test_smoke_pipeline.py` 基础上增加端到端冒烟用例，覆盖健康、发现、异步通知、异步工单、任务状态、指标链路。  
**Tech Stack:** FastAPI TestClient、pytest

---

## 任务拆解

1. 扩展 e2e 测试：新增最小冒烟链路测试用例。  
2. 更新 README：补充最小 e2e 覆盖链路说明。  
3. 更新私有化部署文档：补充手工冒烟验证命令。  
4. 运行 e2e 定向测试与后端全量回归。

## 验收标准

- [ ] e2e 测试覆盖关键链路：`health -> discovery -> notifications(async) -> tickets(async) -> jobs/status -> metrics`。  
- [ ] 私有化部署文档包含可执行的最小冒烟命令步骤。  
- [ ] e2e 定向测试与后端全量测试通过。

# M3 任务34（重试历史 SQL 层过滤）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将重试历史列表与导出接口的主要筛选条件下推到 SQL 层，减少全量拉取后内存过滤的开销。  
**Architecture:** 抽取统一查询构建函数，复用在 `GET /api/v1/jobs/retries` 与 `GET /api/v1/jobs/retries/export.csv`；分页总数改为 SQL count。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 抽取重试事件查询构建函数。  
2. 列表接口改为 SQL 层过滤 + SQL count + SQL 分页。  
3. 导出接口改为 SQL 层过滤。  
4. 新增组合筛选回归测试（列表与导出）。  
5. 更新 README 能力说明。  
6. 运行定向测试与全量回归。

## 验收标准

- [ ] 列表与导出接口在组合筛选（类型+关键字）下结果正确。  
- [ ] 列表接口 `total` 与 SQL 过滤结果一致。  
- [ ] 不改变既有响应字段结构。  
- [ ] 定向测试与全量测试通过。

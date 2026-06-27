# M3 任务35（重试总览关键词过滤）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为重试总览接口补充源任务与新任务关键词过滤，保证与重试历史列表/导出筛选口径一致。  
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 参数 `job_id_keyword/new_job_id_keyword`，并复用统一 SQL 查询构建函数。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：总览支持 `job_id_keyword`。  
2. 新增失败测试：总览支持 `new_job_id_keyword`。  
3. 扩展总览路由参数并接入统一查询构建逻辑。  
4. 更新 README 能力说明。  
5. 运行定向测试与全量回归。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 支持 `job_id_keyword` 过滤。  
- [ ] `GET /api/v1/jobs/retries/overview` 支持 `new_job_id_keyword` 过滤。  
- [ ] 过滤后统计字段（总量、类型、分布、最近记录）均一致。  
- [ ] 定向测试与全量测试通过。

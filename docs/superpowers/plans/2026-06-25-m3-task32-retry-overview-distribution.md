# M3 任务32（重试总览重试次数分布）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在重试总览中补充重试次数分布指标，便于快速判断重试深度结构与集中区间。  
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 返回 `retry_count_distribution`（key 为重试次数字符串，value 为对应事件数），并与现有过滤口径保持一致。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：overview 返回 `retry_count_distribution`。  
2. 扩展 schema：增加 `retry_count_distribution` 字段。  
3. 扩展 overview 路由：在遍历过滤后事件时聚合分布并返回。  
4. 运行定向测试与全量回归。  
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `retry_count_distribution`。  
- [ ] 分布结果按过滤后数据计算（包含 `job_type` 过滤场景）。  
- [ ] 无匹配数据时返回空对象 `{}`。  
- [ ] 定向测试与全量测试通过。

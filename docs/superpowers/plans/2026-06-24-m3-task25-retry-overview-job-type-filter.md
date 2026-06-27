# M3 任务25（重试总览按任务类型过滤）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为重试总览接口增加 `job_type` 过滤能力，支持看板按任务类型独立观察重试指标。
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 参数 `job_type=notification|ticket_sync`；在聚合统计时只纳入匹配类型记录，保持总览字段结构不变。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：overview 在 `job_type` 过滤下返回正确统计。
2. 扩展 overview 路由参数：新增 `job_type` 校验。
3. 调整聚合逻辑：过滤后再计算 `total_retries/job_type_counts/max/avg`。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 支持 `job_type` 过滤。
- [ ] 过滤后 `total_retries`、`max_retry_count`、`avg_retry_count` 与计数一致。
- [ ] 未传 `job_type` 时保持现有行为兼容。
- [ ] 定向测试与全量测试通过。

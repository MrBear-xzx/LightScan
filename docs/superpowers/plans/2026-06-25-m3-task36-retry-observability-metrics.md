# M3 任务36（重试可观测指标）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `/metrics` 中补充重试链路质量指标，便于监控重试请求规模与失败比例。  
**Architecture:** 基于 `events` 聚合新增 3 个指标：`lightscan_job_retry_requested_total`、`lightscan_job_retry_failed_total`、`lightscan_job_retry_success_rate`。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：`/metrics` 文本包含重试指标。  
2. 新增失败测试：构造重试失败场景并断言指标值。  
3. 扩展 metrics 路由实现并保证跨数据库兼容。  
4. 更新 README 指标说明。  
5. 运行定向测试与全量回归。

## 验收标准

- [ ] `/metrics` 返回新增重试请求总数指标。  
- [ ] `/metrics` 返回新增重试失败总数指标。  
- [ ] `/metrics` 返回新增重试成功率指标（0~1）。  
- [ ] 定向测试与全量测试通过。

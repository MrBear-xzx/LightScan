# M6 任务4（漏洞生命周期仪表盘）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供漏洞生命周期仪表盘，展示状态分布、新增趋势、平均存在时间等指标。  
**Architecture:** 从 vuln_cases 表聚合统计数据，按状态/时间维度计算。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：StateDistribution、VulnerabilityLifecycleResponse。
2. 新增 vuln_lifecycle_service：计算状态分布、新增趋势、平均存在时间。
3. 新增路由：GET /api/v1/reports/vuln/lifecycle。
4. 注册到 main.py。
5. 新增测试：空数据、有数据。
6. 更新 README。

## 验收标准

- [ ] GET /api/v1/reports/vuln/lifecycle 返回漏洞生命周期指标。
- [ ] 包含状态分布、今日/本周新增、平均存在天数。
- [ ] 定向测试通过。

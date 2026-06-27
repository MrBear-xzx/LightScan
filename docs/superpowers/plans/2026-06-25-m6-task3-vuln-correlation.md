# M6 任务3（漏洞关联分析）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供按资产维度聚合漏洞案例的关联分析接口，帮助定位高风险资产。  
**Architecture:** 从 vuln_cases 表按 asset_id 聚合，计算分布与 top risk 摘要。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：VulnCaseSummary、AssetCorrelationItem、VulnCorrelationResponse。
2. 新增 vuln_correlation_service：按 asset_id 分组聚合 vuln_cases。
3. 新增路由：GET /api/v1/vuln-cases/correlation。
4. 注册到 main.py。
5. 新增测试：空数据、有数据。
6. 更新 README。

## 验收标准

- [ ] GET /api/v1/vuln-cases/correlation 返回按资产聚合的漏洞分布。
- [ ] 每个资产包含 critical/high/medium/low 分布与 top risk 漏洞摘要。
- [ ] 定向测试通过。

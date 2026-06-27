# M6 任务1（风险评分规则引擎）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 将硬编码风险评分公式变为可配置的规则引擎，支持租户级权重、严重等级映射和风险等级阈值。  
**Architecture:** 基于 policy 表存储，提供 GET/PUT /api/v1/risk/rules 配置接口，扩展 risk_service 支持从配置读取规则。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：SeverityWeightMap、RiskScoreWeights、RiskLevelThreshold、RiskRuleConfig、RiskRuleResponse。
2. 新增 risk_rules_service：持久化规则到 policy 表、提供默认值、calculate_risk_score_with_rules + classify_risk_level。
3. 新增路由：GET/PUT /api/v1/risk/rules。
4. 注册到 main.py。
5. 新增测试：默认值、upsert、持久化。
6. 更新 README。

## 验收标准

- [ ] GET /api/v1/risk/rules 返回默认规则或已配置规则。
- [ ] PUT /api/v1/risk/rules 更新并持久化规则。
- [ ] calculate_risk_score_with_rules 根据配置计算评分。
- [ ] classify_risk_level 根据阈值返回 critical/high/medium/low。
- [ ] 定向测试通过。

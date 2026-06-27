# M4 任务11（rollout 审计时间窗口筛选）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强 rollout 审计查询能力，支持按时间窗口筛选。  
**Architecture:** 在现有分页审计接口上新增 `requested_from/requested_to` 过滤参数；service 统一查询构建并支持总数统计；非法窗口返回 400。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：审计接口支持时间窗口过滤。  
2. 新增失败测试：非法时间窗口返回 400。  
3. 扩展 service 查询构建与 count/list 过滤参数。  
4. 扩展路由参数与窗口校验。  
5. 更新 README 审计接口说明。  
6. 运行定向测试与全量回归。

## 验收标准

- [ ] `GET /api/v1/plugins/rollout-audit` 支持 `requested_from/requested_to`。  
- [ ] 当 `requested_from > requested_to` 时返回 `400`。  
- [ ] 与分页参数组合使用时结果正确。  
- [ ] 定向测试与全量测试通过。

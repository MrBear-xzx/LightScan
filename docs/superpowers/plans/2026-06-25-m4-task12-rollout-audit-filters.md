# M4 任务12（rollout 审计维度筛选）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强 rollout 审计检索能力，支持事件类型与插件维度筛选。  
**Architecture:** 在现有分页+时间窗口审计查询基础上增加 `event_type/plugin_id` 参数，并扩展 service 统一查询构建逻辑。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：`event_type` 过滤。  
2. 新增失败测试：`plugin_id` 过滤。  
3. 扩展 service 查询构建函数增加筛选条件。  
4. 扩展路由参数并透传到 count/list 查询。  
5. 更新 README 审计接口参数说明。  
6. 运行定向测试与全量回归。

## 验收标准

- [ ] rollout 审计支持 `event_type` 过滤。  
- [ ] rollout 审计支持 `plugin_id` 过滤。  
- [ ] 与分页/时间窗口组合查询结果正确。  
- [ ] 定向测试与全量测试通过。

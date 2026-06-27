# M4 任务2（插件契约测试增强）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 强化插件契约测试，覆盖标准接口与关键异常路径。  
**Architecture:** 新增独立契约测试文件，覆盖 discovery/scanner 插件的 `discover/scan/normalize/health` 与异常输入处理。  
**Tech Stack:** pytest

---

## 任务拆解

1. 新增契约测试：discovery 插件接口与 health。  
2. 新增契约测试：scanner 插件接口与 health。  
3. 新增异常测试：`normalize` 缺失 `template-id`。  
4. 新增异常测试：`discover` 空 target。  
5. 最小实现：补齐异常校验逻辑。  
6. 更新 README 说明。  
7. 运行定向测试与全量回归。

## 验收标准

- [ ] discovery/scanner 插件契约测试通过。  
- [ ] 缺失 `template-id` 返回明确异常。  
- [ ] 空 target 返回明确异常。  
- [ ] 定向测试与全量测试通过。

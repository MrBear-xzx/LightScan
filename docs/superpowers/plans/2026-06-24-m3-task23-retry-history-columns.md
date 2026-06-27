# M3 任务23（重试历史列表列裁剪）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为重试历史列表接口提供按列返回能力，减少前端冗余字段处理。
**Architecture:** 在 `GET /api/v1/jobs/retries` 新增 `columns` 参数；默认返回全字段，指定列时按顺序输出；非法列返回 400。与导出接口的列裁剪规则保持一致。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：列表接口支持 `columns` 列裁剪。
2. 新增失败测试：列表接口对非法列返回 400。
3. 扩展列表路由：新增参数解析、字段白名单校验、按列构建 items。
4. 调整响应模型：支持动态字段字典返回。
5. 运行定向测试与全量回归，更新 README。

## 验收标准

- [ ] `GET /api/v1/jobs/retries` 支持 `columns` 参数。
- [ ] 未传 `columns` 时保持全字段兼容。
- [ ] 非法列返回 `400 invalid columns parameter`。
- [ ] 定向测试与全量测试通过。

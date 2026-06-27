# M3 任务22（重试历史导出列裁剪）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 支持任务重试历史 CSV 导出时按需选择字段列，满足不同报表场景。
**Architecture:** 在 `GET /api/v1/jobs/retries/export.csv` 新增 `columns` 参数（逗号分隔）；默认导出全列，传参时按指定列顺序输出；若包含未知列则返回 400。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：支持 `columns` 指定导出列集合与顺序。
2. 新增失败测试：`columns` 含非法列时返回 400。
3. 扩展导出路由：新增参数解析、合法性校验、按列输出 CSV。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `export.csv` 支持 `columns` 参数（例如 `job_id,job_type,retry_count`）。
- [ ] 未传 `columns` 时保持全列导出兼容。
- [ ] 非法列返回 `400 invalid columns parameter`。
- [ ] 定向测试与全量测试通过。

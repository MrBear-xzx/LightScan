# M6 任务2（漏洞标签与分类体系）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 为漏洞提供可管理的标签/分类体系，支持标签 CRUD 和漏洞案例标签分配。  
**Architecture:** 新增 vuln_tags 表和 vuln_case_tags 关联表，通过 SQLAlchemy 自动创建。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 Model：VulnTag（标签定义）、VulnCaseTag（多对多关联）。
2. 新增 schema：标签 CRUD + 标签分配请求。
3. 新增 vuln_tag_service：CRUD + case 标签管理。
4. 新增路由：标签 CRUD + case 标签分配/查询。
5. 注册到 main.py。
6. 新增测试：标签 CRUD、case 标签分配、未知 case。
7. 更新 README。

## 验收标准

- [ ] GET/POST/DELETE /api/v1/vuln-cases/tags 标签 CRUD。
- [ ] GET/POST /api/v1/vuln-cases/{case_id}/tags 标签分配与查询。
- [ ] 删除标签 CASCADE 删除关联。
- [ ] 定向测试通过。

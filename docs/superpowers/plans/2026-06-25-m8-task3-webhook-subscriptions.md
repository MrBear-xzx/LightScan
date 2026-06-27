# M8 任务3（Webhook 事件订阅机制）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供 Webhook 事件订阅管理，支持按事件类型订阅外部 Webhook。  
**Architecture:** 基于 policy 表（webhook_sub_ 前缀）持久化，提供 CRUD 接口。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：WebhookSubscription、WebhookSubscriptionResponse、WebhookSubscriptionListResponse。
2. 新增 webhook_subscription_service：基于 policy 表 CRUD。
3. 新增路由：GET/POST/DELETE /api/v1/notifications/webhooks。
4. 注册到 main.py。
5. 新增测试：CRUD 全流程。
6. 更新 README。

## 验收标准

- [ ] 订阅支持 URL + 事件类型列表配置。
- [ ] CRUD 接口完整可用。
- [ ] 定向测试通过。

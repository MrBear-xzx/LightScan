# M8 任务1（通知适配器扩展）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 扩展通知适配器，支持飞书、钉钉、企业微信的消息格式。  
**Architecture:** 新增 notification_adapters 模块，定义各平台 payload builder，集成到现有通知流程。  
**Tech Stack:** Python、pytest

## 任务拆解

1. 新增 notification_adapters.py：飞书/钉钉/企微 payload builder。
2. 集成到 notification_service.py，替换硬编码 feishu 逻辑。
3. 新增测试：验证各平台 payload 格式正确。
4. 更新 README。

## 验收标准

- [ ] 飞书 payload 使用 post 消息格式。
- [ ] 钉钉 payload 使用 markdown 消息格式。
- [ ] 企业微信 payload 使用 text 消息格式。
- [ ] 集成后现有通知流程不受影响。
- [ ] 定向测试通过。

# M7 任务1（用户认证 JWT）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 实现基于 JWT 的用户认证，支持注册、登录、令牌验证。  
**Architecture:** 新增 auth 模块，基于 users 表 + pyjwt 签发 token。  
**Tech Stack:** FastAPI、PyJWT、SQLAlchemy、pytest

## 任务拆解

1. 创建 app/auth/ 目录 + jwt.py（签名/验证、密码哈希）。
2. 新增 auth route：register、login、me。
3. 注册到 main.py。
4. 新增测试：注册、登录、me、重复注册、错误凭证。
5. 更新 README。

## 验收标准

- [ ] POST /api/v1/auth/register 注册用户。
- [ ] POST /api/v1/auth/login 登录返回 JWT token。
- [ ] GET /api/v1/auth/me 验证 token 返回用户信息。
- [ ] 定向测试通过。

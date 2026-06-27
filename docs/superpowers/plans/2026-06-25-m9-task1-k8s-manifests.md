# M9 任务1（K8s 部署清单）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供基础的 Kubernetes 部署清单，支持后端服务在 K8s 集群中部署。  
**Architecture:** Deployment + Service + ConfigMap 三件套，Probe 健康检查。  
**Tech Stack:** Kubernetes YAML

## 任务拆解

1. 创建 deploy/k8s/ 目录。
2. 编写 ConfigMap（数据库/Redis 连接配置）。
3. 编写 Deployment（2 副本 + 健康检查 + 资源限制）。
4. 编写 Service（ClusterIP 暴露 8000 端口）。
5. 更新 README。

## 验收标准

- [ ] deploy/k8s/configmap.yaml 存在。
- [ ] deploy/k8s/deployment.yaml 存在。
- [ ] deploy/k8s/service.yaml 存在。

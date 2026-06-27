# LightScan 私有化部署运行手册

## 前置条件

- Docker Engine 26+
- Docker Compose v2
- 建议最低资源：4 CPU / 8 GB RAM

## 启动

1. `docker compose -f deploy/docker-compose.yml up -d --build`
2. `curl http://127.0.0.1:8000/health`
3. `curl http://127.0.0.1:8000/metrics`
4. 最小冒烟链路（建议按顺序）：
   - `curl -X POST http://127.0.0.1:8000/api/v1/discovery/tasks -H "Content-Type: application/json" -d "{\"tenant_id\":\"t1\",\"targets\":[\"example.com\"],\"policy_id\":\"default-external\"}"`
   - `curl -X POST http://127.0.0.1:8000/api/v1/notifications/dispatch -H "Content-Type: application/json" -d "{\"tenant_id\":\"t1\",\"provider\":\"webhook\",\"min_risk_score\":7.0,\"mode\":\"async\"}"`
   - `curl -X POST http://127.0.0.1:8000/api/v1/tickets/sync -H "Content-Type: application/json" -d "{\"tenant_id\":\"t1\",\"provider\":\"mock_jira\",\"case_ids\":[1],\"mode\":\"async\"}"`
   - `curl \"http://127.0.0.1:8000/api/v1/jobs/status?tenant_id=t1&job_id=<上一步返回的job_id>\"`

## 停止

1. `docker compose -f deploy/docker-compose.yml down`

# LightScan 发布与回滚模板

> 用途：每次发布前复制本模板，填写完整后随发布记录归档。  
> 建议命名：`docs/operations/releases/YYYY-MM-DD-<version>-release-note.md`

## 1. 发布基本信息

- 版本号：
- 发布环境：`staging` / `production`
- 发布窗口（开始-结束）：
- 发布负责人：
- 参与人（开发/测试/运维）：
- 关联 PR/Issue：

## 2. 变更说明

### 2.1 功能变更

- 

### 2.2 缺陷修复

- 

### 2.3 不兼容变更（如有）

- 

## 3. 发布前检查清单

- [ ] CI 全绿（lint / 分层测试 / 覆盖率门禁通过）
- [ ] 数据库迁移脚本已评审并在预发验证
- [ ] 关键配置项已校验（数据库、Redis、外部回调地址）
- [ ] 最小 e2e 冒烟链路通过
- [ ] 回滚方案已演练或确认可执行
- [ ] 监控与告警阈值已确认

## 4. 发布步骤

1. 同步代码到目标版本：
   - `git fetch --all --prune`
   - `git checkout <release-tag-or-commit>`
2. 执行部署：
   - `docker compose -f deploy/docker-compose.yml up -d --build`
3. 执行发布后验证（见第 5 节）。

## 5. 发布后验证

- [ ] `GET /health` 返回 200
- [ ] `GET /metrics` 返回 200 且关键指标可见
- [ ] 最小链路验证通过：`discovery -> notifications(async) -> tickets(async) -> jobs/status`
- [ ] 核心业务接口抽样验证通过

异常记录：
- 

## 6. 回滚触发条件

- P0/P1 级故障持续超过 `15` 分钟未恢复
- 核心链路错误率持续高于基线阈值
- 数据一致性出现不可接受偏差

## 7. 回滚步骤

1. 回滚到上一个稳定版本：
   - `git checkout <previous-stable-tag-or-commit>`
2. 重新部署：
   - `docker compose -f deploy/docker-compose.yml up -d --build`
3. 如涉及迁移，执行对应回滚脚本（若可回滚）：
   - `<填写迁移回滚命令>`

## 8. 回滚后验证

- [ ] `GET /health` 恢复正常
- [ ] 核心 API 抽样通过
- [ ] 关键指标恢复到回滚前基线
- [ ] 告警恢复正常

## 9. 复盘记录

- 结果：发布成功 / 回滚成功 / 其他
- 结论与改进项：
- 后续动作负责人：

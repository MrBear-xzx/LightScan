<template>
  <Layout title="系统管理">
    <div class="tabs">
      <span class="tab-btn" :class="{ active: tab === 'alerts' }" @click="tab = 'alerts'">告警规则</span>
      <span class="tab-btn" :class="{ active: tab === 'logs' }" @click="tab = 'logs'">操作日志</span>
      <span class="tab-btn" :class="{ active: tab === 'backups' }" @click="tab = 'backups'">数据备份</span>
    </div>
    <div v-if="tab === 'alerts'" class="card">
      <div class="card-title">告警规则</div>
      <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:flex-end">
        <div class="form-group" style="margin:0"><label>名称</label><input v-model="alertForm.name" style="width:130px" /></div>
        <div class="form-group" style="margin:0"><label>指标</label><select v-model="alertForm.metric" style="width:120px"><option value="new_vulns">新漏洞</option><option value="sla_breach">SLA 违规</option><option value="scan_failure">扫描失败</option></select></div>
        <div class="form-group" style="margin:0"><label>阈值</label><input v-model.number="alertForm.threshold" type="number" style="width:70px" /></div>
        <div class="form-group" style="margin:0"><label>窗口(min)</label><input v-model.number="alertForm.window_minutes" type="number" style="width:70px" /></div>
        <button class="btn btn-primary btn-sm" @click="handleCreateAlert">创建</button>
      </div>
      <div v-if="alertRules.length === 0" class="empty">暂无规则</div>
      <table v-else><thead><tr><th>名称</th><th>指标</th><th>阈值</th><th>窗口</th><th>状态</th><th>操作</th></tr></thead>
        <tbody><tr v-for="r in alertRules" :key="r.id"><td>{{ r.name }}</td><td>{{ {new_vulns:'新漏洞',sla_breach:'SLA 违规',scan_failure:'扫描失败'}[r.metric] || r.metric }}</td><td>{{ r.threshold }}</td><td>{{ r.window_minutes }}min</td><td><span class="badge" :class="r.enabled ? 'badge-resolved' : 'badge-rejected'">{{ r.enabled ? '启用' : '停用' }}</span></td><td><button class="btn btn-sm btn-danger" @click="handleDeleteAlert(r.id)">删除</button></td></tr></tbody>
      </table>
    </div>
    <div v-if="tab === 'logs'" class="card">
      <div class="card-title">操作日志</div>
      <div style="margin-bottom:12px;display:flex;gap:8px">
        <select v-model="logType" style="padding:6px 10px;background:#0f172a;border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:13px">
          <option value="">全部</option><option value="scan">扫描</option><option value="vuln">漏洞</option><option value="auth">认证</option><option value="plugin">插件</option><option value="admin">管理</option>
        </select>
        <button class="btn btn-sm btn-ghost" @click="loadLogs">刷新</button>
      </div>
      <div v-if="logs.length === 0" class="empty">暂无日志</div>
      <table v-else><thead><tr><th>时间</th><th>类型</th><th>操作</th><th>操作人</th><th>目标</th></tr></thead>
        <tbody><tr v-for="l in filteredLogs" :key="l.event_id||l.id"><td style="font-size:12px;color:var(--text-muted);white-space:nowrap">{{ (l.created_at||'').slice(0,16).replace('T',' ') }}</td><td><span class="badge badge-new">{{ l.event_type || '-' }}</span></td><td>{{ l.action || l.operation || '-' }}</td><td>{{ l.operator || l.username || '-' }}</td><td style="max-width:100px;overflow:hidden;text-overflow:ellipsis">{{ l.target || l.resource_id || '-' }}</td></tr></tbody>
      </table>
    </div>
    <div v-if="tab === 'backups'" class="card">
      <div class="card-title">数据备份</div>
      <div style="margin-bottom:16px"><button class="btn btn-primary" @click="handleCreateBackup" :disabled="backupLoading">{{ backupLoading ? '创建中...' : '创建备份' }}</button></div>
      <div v-if="backups.length === 0" class="empty">暂无备份</div>
      <table v-else><thead><tr><th>ID</th><th>大小</th><th>状态</th><th>时间</th></tr></thead>
        <tbody><tr v-for="b in backups" :key="b.id"><td style="font-family:monospace;font-size:12px">{{ (b.id||'').slice(0,8) }}</td><td>{{ b.file_size ? ((b.file_size/1024).toFixed(1)+'KB') : '-' }}</td><td><span class="badge" :class="b.status === 'completed' ? 'badge-resolved' : b.status === 'failed' ? 'badge-critical' : 'badge-in-progress'">{{ b.status }}</span></td><td style="font-size:12px;color:var(--text-muted)">{{ (b.created_at||'').slice(0,16).replace('T',' ') }}</td></tr></tbody>
      </table>
    </div>
  </Layout>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../api';
import Layout from '../components/Layout.vue';
const tab = ref('alerts');
const alertForm = ref({ name: '', metric: 'new_vulns', threshold: 10, window_minutes: 5 }); const alertRules = ref([]);
const logType = ref(''); const logs = ref([]);
const filteredLogs = computed(() => !logType.value ? logs.value : logs.value.filter(l => (l.event_type||'').toLowerCase().startsWith(logType.value)));
const backupLoading = ref(false); const backups = ref([]);
async function handleCreateAlert() { try { await api.createAlertRule(alertForm.value); alertForm.value = { name: '', metric: 'new_vulns', threshold: 10, window_minutes: 5 }; await loadAlerts(); } catch (e) { alert('创建失败'); } }
async function handleDeleteAlert(id) { try { await api.deleteAlertRule(id); await loadAlerts(); } catch (e) { alert('删除失败'); } }
async function handleCreateBackup() { backupLoading.value = true; try { await api.createBackup(); await loadBackups(); } catch (e) { alert('备份失败'); } finally { backupLoading.value = false; } }
async function loadAlerts() { try { const d = await api.alertRules(); alertRules.value = d.items ?? d ?? []; } catch (e) { console.error(e); } }
async function loadLogs() { try { const d = await api.opsLogs({ page_size: 50 }); logs.value = d.items ?? d ?? []; } catch (e) { console.error(e); } }
async function loadBackups() { try { const d = await api.backups(); backups.value = d.items ?? d ?? []; } catch (e) { console.error(e); } }
onMounted(() => { loadAlerts(); loadLogs(); loadBackups(); });
</script>

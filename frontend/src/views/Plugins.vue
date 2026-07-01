<template>
  <Layout title="插件管理">
    <div class="tabs">
      <span class="tab-btn" :class="{ active: tab === 'list' }" @click="tab = 'list'">插件列表</span>
      <span class="tab-btn" :class="{ active: tab === 'health' }" @click="tab = 'health'">健康状态</span>
      <span class="tab-btn" :class="{ active: tab === 'rollout' }" @click="tab = 'rollout'">灰度策略</span>
      <span class="tab-btn" :class="{ active: tab === 'audit' }" @click="tab = 'audit'">操作审计</span>
    </div>
    <div v-if="tab === 'list'" class="card">
      <div class="card-title">已安装插件</div>
      <div v-if="plugins.length === 0" class="empty">暂无插件</div>
      <table v-else><thead><tr><th>名称</th><th>版本</th><th>描述</th><th>状态</th><th>操作</th></tr></thead>
        <tbody><tr v-for="p in plugins" :key="p.id"><td>{{ p.plugin_id }}</td><td style="font-family:monospace;font-size:12px">{{ p.version || '-' }}</td><td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ p.description || '-' }}</td><td><span class="badge" :class="p.enabled ? 'badge-resolved' : 'badge-rejected'">{{ p.enabled ? '启用' : '禁用' }}</span></td>
          <td><button class="btn btn-sm btn-ghost" @click="togglePlugin(p)">{{ p.enabled ? '禁用' : '启用' }}</button></td></tr></tbody>
      </table>
    </div>
    <div v-if="tab === 'health'" class="card">
      <div class="card-title">插件健康检查</div>
      <div v-if="!healthData" class="empty">加载中...</div>
      <template v-else>
        <div class="grid-4">
          <div class="stat-card"><div class="stat-value" :style="{ color: healthData.total_healthy === healthData.total ? 'var(--success)' : 'var(--danger)' }">{{ healthData.total_healthy }}/{{ healthData.total }}</div><div class="stat-label">健康率</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--success)' }">{{ healthData.total_healthy }}</div><div class="stat-label">健康</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--danger)' }">{{ (healthData.total||0) - (healthData.total_healthy||0) }}</div><div class="stat-label">异常</div></div>
        </div>
        <div v-for="p in (healthData.plugins || [])" :key="p.plugin_id" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px"><span>{{ p.plugin_id }} v{{ p.version }}</span><span :style="{ color: p.healthy ? 'var(--success)' : 'var(--danger)' }">{{ p.healthy ? '健康' : p.error || '异常' }}</span></div>
      </template>
    </div>
    <div v-if="tab === 'rollout'" class="card">
      <div class="card-title">灰度发布策略</div>
      <div class="form-group"><label>模式</label><select v-model="rolloutPolicy.mode"><option value="all">全量发布</option><option value="percentage">按百分比</option><option value="targeted">指定租户</option></select></div>
      <div class="form-group" v-if="rolloutPolicy.mode === 'percentage'"><label>灰度比例 (%)</label><input v-model.number="rolloutPolicy.percentage" type="number" min="1" max="100" /></div>
      <div class="form-group"><label>自动回滚</label><select v-model="rolloutPolicy.auto_rollback"><option :value="true">启用</option><option :value="false">禁用</option></select></div>
      <div class="form-group"><label>健康阈值 (%)</label><input v-model.number="rolloutPolicy.health_threshold" type="number" min="0" max="100" /></div>
      <button class="btn btn-primary" @click="handleSaveRollout">保存</button>
    </div>
    <div v-if="tab === 'audit'" class="card">
      <div class="card-title">操作记录</div>
      <div v-if="auditData.length === 0" class="empty">暂无记录</div>
      <table v-else><thead><tr><th>时间</th><th>插件</th><th>版本</th><th>操作</th><th>状态</th></tr></thead>
        <tbody><tr v-for="a in auditData" :key="a.id"><td style="font-size:12px;color:var(--text-muted)">{{ (a.created_at||'').slice(0,16).replace('T',' ') }}</td><td>{{ a.plugin_name }}</td><td style="font-family:monospace;font-size:12px">{{ a.version }}</td><td>{{ a.action }}</td><td><span class="badge" :class="a.status === 'success' ? 'badge-resolved' : 'badge-critical'">{{ a.status }}</span></td></tr></tbody>
      </table>
    </div>
  </Layout>
</template>
<script setup>
import { ref, onMounted } from 'vue';

import { api } from '../api';
import Layout from '../components/Layout.vue';
const tab = ref('list'); const plugins = ref([]); const healthData = ref(null);
const rolloutPolicy = ref({ mode: 'all', percentage: 10, target_tenants: '', auto_rollback: true, health_threshold: 20 }); const rolloutMsg = ref(''); const auditData = ref([]);
async function togglePlugin(p) { try { await api.updateRolloutPolicy({ plugin_id: p.id, enabled: !p.enabled }); await loadPlugins(); } catch (e) { alert('操作失败'); } }
async function handleSaveRollout() { rolloutMsg.value = ''; try { await api.updateRolloutPolicy({ ...rolloutPolicy.value }); rolloutMsg.value = '保存成功！'; } catch (e) { rolloutMsg.value = '保存失败: ' + e.message; } }
async function loadPlugins() { try { const d = await api.plugins({}); plugins.value = d.items ?? d ?? []; } catch (e) { console.error(e); } }
async function loadHealth() { try { healthData.value = await api.pluginHealth(); } catch (e) { console.error(e); } }
async function loadRolloutPolicy() { try { const d = await api.rolloutPolicy(); if (d) rolloutPolicy.value = { ...rolloutPolicy.value, ...d }; } catch (e) { console.error(e); } }
async function loadAudit() { try { const d = await api.rolloutAudit({ page_size: 30 }); auditData.value = d.items ?? d ?? []; } catch (e) { console.error(e); } }
onMounted(() => { loadPlugins(); loadHealth(); loadRolloutPolicy(); loadAudit(); });
</script>

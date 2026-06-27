<template>
  <Layout title="通知管理">
    <div class="tabs">
      <span class="tab-btn" :class="{ active: tab === 'dispatch' }" @click="tab = 'dispatch'">手动通知</span>
      <span class="tab-btn" :class="{ active: tab === 'policy' }" @click="tab = 'policy'">通知策略</span>
      <span class="tab-btn" :class="{ active: tab === 'templates' }" @click="tab = 'templates'">通知模板</span>
      <span class="tab-btn" :class="{ active: tab === 'webhooks' }" @click="tab = 'webhooks'">Webhook</span>
    </div>
    <div v-if="tab === 'dispatch'" class="card">
      <div class="card-title">发送通知</div>
      <div class="form-row"><div class="form-group"><label>类型</label><select v-model="dispatchForm.channel"><option value="email">邮件</option><option value="webhook">Webhook</option></select></div><div class="form-group"><label>收件人</label><input v-model="dispatchForm.recipient" placeholder="邮箱/URL" /></div></div>
      <div class="form-group"><label>标题</label><input v-model="dispatchForm.title" /></div>
      <div class="form-group"><label>内容</label><textarea v-model="dispatchForm.body" rows="4"></textarea></div>
      <button class="btn btn-primary" @click="handleDispatch" :disabled="dispatchLoading">{{ dispatchLoading ? '发送中...' : '发送通知' }}</button>
      <p v-if="dispatchMsg" style="margin-top:8px;font-size:13px">{{ dispatchMsg }}</p>
    </div>
    <div v-if="tab === 'policy'" class="card">
      <div class="card-title">通知策略</div>
      <div class="form-group"><label>新漏洞通知</label><select v-model="policy.new_vuln"><option value="enabled">启用</option><option value="disabled">禁用</option></select></div>
      <div class="form-group"><label>高危通知</label><select v-model="policy.high_risk"><option value="enabled">启用</option><option value="disabled">禁用</option></select></div>
      <div class="form-group"><label>SLA 违规通知</label><select v-model="policy.sla_breach"><option value="enabled">启用</option><option value="disabled">禁用</option></select></div>
      <div class="form-group"><label>默认渠道</label><select v-model="policy.default_channel"><option value="email">邮件</option><option value="webhook">Webhook</option></select></div>
      <button class="btn btn-primary" @click="handleSavePolicy">保存</button>
    </div>
    <div v-if="tab === 'templates'" class="card">
      <div class="card-title">通知模板</div>
      <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:flex-end">
        <div class="form-group" style="margin:0"><label>名称</label><input v-model="templateForm.name" style="width:140px" /></div>
        <div class="form-group" style="margin:0"><label>类型</label><select v-model="templateForm.type" style="width:110px"><option value="email">邮件</option><option value="webhook">Webhook</option></select></div>
        <button class="btn btn-primary btn-sm" @click="handleCreateTemplate">创建</button>
      </div>
      <div v-if="templates.length === 0" class="empty">暂无模板</div>
      <table v-else><thead><tr><th>名称</th><th>类型</th><th>操作</th></tr></thead><tbody><tr v-for="t in templates" :key="t.id"><td>{{ t.name }}</td><td>{{ t.type }}</td><td><button class="btn btn-sm btn-danger" @click="handleDeleteTemplate(t.id)">删除</button></td></tr></tbody></table>
    </div>
    <div v-if="tab === 'webhooks'" class="card">
      <div class="card-title">Webhook 订阅</div>
      <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:flex-end">
        <div class="form-group" style="margin:0"><label>名称</label><input v-model="webhookForm.name" style="width:140px" /></div>
        <div class="form-group" style="margin:0"><label>URL</label><input v-model="webhookForm.url" placeholder="https://hooks.example.com" style="width:240px" /></div>
        <div class="form-group" style="margin:0"><label>事件</label><select v-model="webhookForm.event_type" style="width:130px"><option value="vuln_created">漏洞创建</option><option value="vuln_state_changed">状态变更</option><option value="sla_breached">SLA 违规</option><option value="scan_completed">扫描完成</option><option value="all">全部</option></select></div>
        <button class="btn btn-primary btn-sm" @click="handleCreateWebhook">创建</button>
      </div>
      <div v-if="webhooks.length === 0" class="empty">暂无 Webhook</div>
      <table v-else><thead><tr><th>名称</th><th>URL</th><th>事件</th><th>状态</th><th>操作</th></tr></thead>
        <tbody><tr v-for="w in webhooks" :key="w.id"><td>{{ w.name }}</td><td style="font-size:12px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ w.url }}</td><td>{{ w.event_type }}</td><td><span class="badge" :class="w.enabled ? 'badge-resolved' : 'badge-rejected'">{{ w.enabled ? '启用' : '停用' }}</span></td><td><button class="btn btn-sm btn-danger" @click="handleDeleteWebhook(w.id)">删除</button></td></tr></tbody>
      </table>
    </div>
  </Layout>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { api } from '../api';
import Layout from '../components/Layout.vue';
const auth = useAuthStore();
const tab = ref('dispatch');
const dispatchForm = ref({ channel: 'email', recipient: '', title: '', body: '' });
const dispatchLoading = ref(false); const dispatchMsg = ref('');
const policy = ref({ new_vuln: 'enabled', high_risk: 'enabled', sla_breach: 'enabled', default_channel: 'email' });
const policyMsg = ref('');
const templateForm = ref({ name: '', type: 'email' }); const templates = ref([]);
const webhookForm = ref({ name: '', url: '', event_type: 'vuln_created' }); const webhooks = ref([]);
async function handleDispatch() { dispatchMsg.value = ''; dispatchLoading.value = true; try { await api.dispatchNotification({ tenant_id: auth.tenantId, provider: dispatchForm.value.channel === 'email' ? 'webhook' : dispatchForm.value.channel, webhook_url: dispatchForm.value.recipient || undefined, min_risk_score: 7.0 }); dispatchMsg.value = '通知已发送！'; dispatchForm.value = { channel: 'email', recipient: '', title: '', body: '' }; } catch (e) { dispatchMsg.value = '发送失败: ' + e.message; } finally { dispatchLoading.value = false; } }
async function handleSavePolicy() { try { await api.updateNotifyPolicy({ tenant_id: auth.tenantId, dedup_window_minutes: policy.value.dedup_window_minutes || 30 }); policyMsg.value = '策略保存成功！'; } catch (e) { policyMsg.value = '保存失败: ' + e.message; } }
async function handleCreateTemplate() { try { await api.createNotifyTemplate(auth.tenantId, { name: templateForm.value.name, provider: templateForm.value.type || 'webhook', title_template: '', body_template: '', enabled: true }); templateForm.value = { name: '', type: 'email' }; await loadTemplates(); } catch (e) { alert('创建失败'); } }
async function handleDeleteTemplate(id) { try { await api.deleteNotifyTemplate(id, auth.tenantId); await loadTemplates(); } catch (e) { alert('删除失败'); } }
async function handleCreateWebhook() { try { await api.createWebhookSub(auth.tenantId, { url: webhookForm.value.url, event_types: [webhookForm.value.event_type], description: webhookForm.value.name, enabled: true }); webhookForm.value = { name: '', url: '', event_type: 'vuln_created' }; await loadWebhooks(); } catch (e) { alert('创建失败'); } }
async function handleDeleteWebhook(id) { try { await api.deleteWebhookSub(id, auth.tenantId); await loadWebhooks(); } catch (e) { alert('删除失败'); } }
async function loadPolicy() { try { const d = await api.notifyPolicy(auth.tenantId); if (d) policy.value.dedup_window_minutes = d.dedup_window_minutes; } catch (e) { console.error(e); } }
async function loadTemplates() { try { const d = await api.notifyTemplates(auth.tenantId); const raw = d.items ?? d ?? []; templates.value = raw.map(function(t) { return { id: t.template_id, name: t.config && t.config.name || '', type: t.config && t.config.provider || '' }; }); } catch (e) { console.error(e); } }
async function loadWebhooks() { try { const d = await api.webhookSubs(auth.tenantId); const raw = d.items ?? d ?? []; webhooks.value = raw.map(function(w) { var cfg = w.config || {}; return { id: w.sub_id, name: cfg.description || '', url: cfg.url || '', event_type: (cfg.event_types || []).join(';'), enabled: cfg.enabled !== false }; }); } catch (e) { console.error(e); } }
onMounted(() => { loadPolicy(); loadTemplates(); loadWebhooks(); });
</script>

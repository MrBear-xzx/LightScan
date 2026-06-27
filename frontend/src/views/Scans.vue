<template>
  <Layout title="扫描任务">
    <div class="tabs">
      <span class="tab-btn" :class="{ active: tab === 'create' }" @click="tab = 'create'">创建扫描</span>
      <span class="tab-btn" :class="{ active: tab === 'list' }" @click="tab = 'list'">任务列表</span>
      <span class="tab-btn" :class="{ active: tab === 'batch' }" @click="tab = 'batch'">批量扫描</span>
      <span class="tab-btn" :class="{ active: tab === 'policies' }" @click="tab = 'policies'">扫描策略</span>
    </div>
    <div v-if="tab === 'create'" class="card">
      <div class="card-title">新建扫描任务</div>
      <div class="form-row">
        <div class="form-group"><label>目标 URL / IP</label><input v-model="createForm.target" placeholder="如 https://example.com" /></div>
        <div class="form-group"><label>选择策略</label><select v-model="createForm.policy_id"><option value="">默认策略</option><option v-for="p in policies" :key="p.id" :value="p.id">{{ p.name }}{{ p.is_default ? ' (默认)' : '' }}</option></select></div>
      </div>
      <button class="btn btn-primary" @click="handleCreate" :disabled="createLoading">{{ createLoading ? '创建中...' : '创建任务' }}</button>
      <p v-if="createMsg" style="margin-top:8px;font-size:13px">{{ createMsg }}</p>
    </div>
    <div v-if="tab === 'list'">
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <span class="card-title" style="margin:0">任务列表</span>
          <button class="btn btn-sm btn-ghost" @click="loadTasks">刷新</button>
        </div>
        <div v-if="tasks.length === 0" class="empty">暂无扫描任务</div>
        <table v-else>
          <thead><tr><th>目标</th><th>状态</th><th>发现数</th><th>失败原因</th><th>时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="t in tasks" :key="t.id">
              <td><a href="javascript:void(0)" @click="goDetail(t.task_id)" style="color:var(--primary);text-decoration:none">{{ t.target }}</a></td>
              <td><span class="badge" :class="'badge-' + (t.status === 'completed' ? 'resolved' : t.status === 'running' ? 'in-progress' : t.status === 'failed' ? 'critical' : 'low')">{{ t.status }}</span></td>
              <td>{{ t.findings_count ?? '-' }}</td>
              <td style="font-size:12px;color:var(--danger);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" :title="t.error_message || ''">{{ t.error_message || '-' }}</td>
              <td style="font-size:12px;color:var(--text-muted)">{{ formatTime(t.started_at) }}</td>
              <td><button v-if="t.status === 'running' || t.status === 'pending'" class="btn btn-sm btn-danger" @click="handleCancel(t.task_id)">取消</button></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="card" v-if="progress && progress.total">
        <div class="card-title">当前进度</div>
        <div>已完成 {{ progress.completed }} / {{ progress.total }} 个子任务</div>
        <div style="height:6px;background:var(--border);border-radius:3px;overflow:hidden"><div style="height:100%;background:var(--primary);border-radius:3px" :style="{ width: (progress.completed / progress.total * 100) + '%' }"></div></div>
      </div>
    </div>
    <div v-if="tab === 'batch'" class="card">
      <div class="card-title">批量扫描</div>
      <div class="form-group"><label>目标列表（每行一个）</label><textarea v-model="batchTargets" rows="5" placeholder="https://example1.com\nhttps://example2.com"></textarea></div>
      <button class="btn btn-primary" @click="handleBatch" :disabled="batchLoading">{{ batchLoading ? '提交中...' : '提交批量扫描' }}</button>
      <p v-if="batchMsg" style="margin-top:8px;font-size:13px">{{ batchMsg }}</p>
    </div>
    <div v-if="tab === 'policies'" class="card">
      <div class="card-title">扫描策略</div>
      <div v-if="policies.length === 0" class="empty">暂无策略</div>
      <table v-else><thead><tr><th>名称</th><th>端口范围</th><th>超时</th><th>状态</th></tr></thead>
        <tbody><tr v-for="p in policies" :key="p.id"><td>{{ p.name }}</td><td>{{ p.port_range || '-' }}</td><td>{{ p.timeout || '-' }}s</td><td><span class="badge" :class="p.enabled ? 'badge-resolved' : 'badge-rejected'">{{ p.enabled ? '启用' : '禁用' }}</span></td></tr></tbody>
      </table>
    </div>
  </Layout>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { api } from '../api';
import Layout from '../components/Layout.vue';
const auth = useAuthStore();
const router = useRouter();
function goDetail(id) { router.push('/scans/' + id); }
const tab = ref('create');
const createForm = ref({ target: '', policy_id: '' });
const createLoading = ref(false); const createMsg = ref(''); const tasks = ref([]); const progress = ref(null);
const batchTargets = ref(''); const batchLoading = ref(false); const batchMsg = ref(''); const policies = ref([]);
async function handleCreate() { createMsg.value = ''; createLoading.value = true; try { await api.createTask({ tenant_id: auth.tenantId, targets: [createForm.value.target], policy_id: createForm.value.policy_id || "default-external" }); createMsg.value = '任务创建成功！'; createForm.value = { target: '', policy_id: '' }; } catch (e) { createMsg.value = '创建失败: ' + e.message; } finally { createLoading.value = false; } }
async function loadTasks() { try { const prog = await api.scanProgress({ tenant_id: auth.tenantId }); progress.value = prog; tasks.value = prog.tasks ?? []; } catch (e) { console.error(e); } }
async function handleCancel(taskId) { try { await api.cancelTask(taskId, auth.tenantId); await loadTasks(); } catch (e) { alert('取消失败: ' + e.message); } }
async function handleBatch() { batchMsg.value = ''; batchLoading.value = true; try { const lines = batchTargets.value.split('\n').map(s => s.trim()).filter(Boolean); if (!lines.length) { batchMsg.value = '请输入目标'; return; } await api.batchScan({ tenant_id: auth.tenantId, targets: lines }); batchMsg.value = '批量扫描已提交，共 ' + lines.length + ' 个任务'; } catch (e) { batchMsg.value = '提交失败: ' + e.message; } finally { batchLoading.value = false; } }
async function loadPolicies() { try { const data = await api.scanPolicies(auth.tenantId); policies.value = Array.isArray(data) ? data : (data.items ?? []); } catch (e) { console.error(e); } }
function formatTime(t) { if (!t) return '-'; var d = new Date(t); var p = function(n) { return String(n).padStart(2, '0'); }; return d.getFullYear() + '-' + p(d.getMonth()+1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes()); }
onMounted(() => { loadTasks(); loadPolicies(); });
</script>

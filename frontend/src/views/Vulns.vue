<template>
  <Layout title="漏洞管理">
    <div class="tabs">
      <span class="tab-btn" :class="{ active: tab === 'list' }" @click="tab = 'list'">漏洞列表</span>
      <span class="tab-btn" :class="{ active: tab === 'tags' }" @click="tab = 'tags'">标签管理</span>
      <span class="tab-btn" :class="{ active: tab === 'correlation' }" @click="tab = 'correlation'">关联分析</span>
      <span class="tab-btn" :class="{ active: tab === 'risk' }" @click="tab = 'risk'">风险规则</span>
    </div>
    <div v-if="tab === 'list'">
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
          <span class="card-title" style="margin:0">全部漏洞</span>
          <div style="display:flex;gap:8px">
            <input v-model="searchQuery" placeholder="搜索目标/漏洞名" style="padding:6px 10px;background:#0f172a;border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:13px;width:180px" />
            <select v-model="stateFilter" style="padding:6px 10px;background:#0f172a;border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:13px">
              <option value="">全部状态</option>
              <option value="new">待处理</option>
              <option value="in_progress">处理中</option>
              <option value="resolved">已修复</option>
              <option value="false_positive">误报</option>
              <option value="rejected">忽略</option>
            </select>
            <button class="btn btn-sm btn-ghost" @click="loadVulns">刷新</button>
          </div>
        </div>
        <div v-if="vulns.length === 0" class="empty">暂无漏洞数据</div>
        <table v-else>
          <thead><tr><th>漏洞名称</th><th>目标</th><th>严重程度</th><th>状态</th><th>责任人</th><th>发现时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="v in filteredVulns" :key="v.case_id">
              <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ v.title || '-' }}</td>
              <td>{{ v.target || '-' }}</td>
              <td><span class="badge" :class="'badge-' + (v.severity === 'critical' ? 'critical' : v.severity === 'high' ? 'high' : v.severity === 'medium' ? 'medium' : 'low')">{{ v.severity }}</span></td>
              <td><span class="badge" :class="'badge-' + v.state">{{ {new:'待处理', in_progress:'处理中', resolved:'已修复', false_positive:'误报', rejected:'忽略'}[v.state] || v.state }}</span></td>
              <td>{{ v.owner || '-' }}</td>
              <td style="font-size:12px;color:var(--text-muted)">{{ (v.created_at || '').slice(0,16).replace('T',' ') || '-' }}</td>
              <td>
                <button class="btn btn-sm btn-ghost" @click="openStateModal(v)">改状态</button>
                <button class="btn btn-sm btn-ghost" @click="openAssignModal(v)">分配</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="stateModal" class="modal-overlay" @click.self="stateModal = null">
        <div class="modal">
          <h3>修改状态 - {{ stateModal.title }}</h3>
          <div class="form-group"><label>新状态</label><select v-model="newState"><option value="new">待处理</option><option value="in_progress">处理中</option><option value="resolved">已修复</option><option value="false_positive">误报</option><option value="rejected">忽略</option></select></div>
          <div class="form-group"><label>备注</label><textarea v-model="stateNote" rows="3" placeholder="可选备注"></textarea></div>
          <div class="modal-actions"><button class="btn btn-ghost" @click="stateModal = null">取消</button><button class="btn btn-primary" @click="handleStateChange">确认</button></div>
        </div>
      </div>
      <div v-if="assignModal" class="modal-overlay" @click.self="assignModal = null">
        <div class="modal">
          <h3>分配 - {{ assignModal.title }}</h3>
          <div class="form-group"><label>责任人</label><input v-model="assignee" placeholder="输入用户名" /></div>
          <div class="modal-actions"><button class="btn btn-ghost" @click="assignModal = null">取消</button><button class="btn btn-primary" @click="handleAssign">确认</button></div>
        </div>
      </div>
    </div>
    <div v-if="tab === 'tags'" class="card">
      <div class="card-title">漏洞标签</div>
      <div style="display:flex;gap:8px;margin-bottom:16px">
        <input v-model="newTagName" placeholder="标签名称" style="flex:1;padding:8px 12px;background:#0f172a;border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:13px" />
        <input v-model="newTagColor" type="color" style="width:40px;height:36px;border:none;border-radius:6px;cursor:pointer" />
        <button class="btn btn-primary" @click="handleCreateTag">创建</button>
      </div>
      <div v-if="tags.length === 0" class="empty">暂无标签</div>
      <div v-else style="display:flex;flex-wrap:wrap;gap:8px">
        <div v-for="tag in tags" :key="tag.id" style="display:flex;align-items:center;gap:6px;padding:6px 12px;border-radius:6px;font-size:13px;border:1px solid var(--border)">
          <span class="tag" :style="{ background: tag.color || '#3b82f6' }">{{ tag.name }}</span>
          <span style="color:var(--text-muted);font-size:11px">{{ tag.case_count || 0 }}个漏洞</span>
          <span style="cursor:pointer;color:var(--danger);font-size:14px" @click="handleDeleteTag(tag.id)">x</span>
        </div>
      </div>
    </div>
    <div v-if="tab === 'correlation'" class="card">
      <div class="card-title">关联分析</div>
      <div v-if="correlationLoading" class="empty">加载中...</div>
      <div v-else-if="correlationData.length === 0" class="empty">暂无关联数据</div>
      <table v-else>
        <thead><tr><th>#</th><th>关联类型</th><th>漏洞数</th><th>目标</th></tr></thead>
        <tbody><tr v-for="(c,i) in correlationData" :key="i"><td>{{ i+1 }}</td><td>{{ c.correlation_type || '-' }}</td><td>{{ c.case_count }}</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis">{{ c.targets?.join(', ')?.slice(0,40) || '-' }}</td></tr></tbody>
      </table>
    </div>
    <div v-if="tab === 'risk'" class="card">
      <div class="card-title">风险规则配置</div>
      <div class="form-group"><label>严重 (critical) 最低分</label><input v-model.number="riskRules.critical_threshold" type="number" /></div>
      <div class="form-group"><label>高危 (high) 最低分</label><input v-model.number="riskRules.high_threshold" type="number" /></div>
      <div class="form-group"><label>自动升级条件</label><input v-model.number="riskRules.auto_escalate_count" type="number" /></div>
      <div class="form-group"><label>通知阈值</label><input v-model.number="riskRules.notify_threshold" type="number" /></div>
      <button class="btn btn-primary" @click="handleSaveRisk">保存规则</button>
    </div>
  </Layout>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { api } from '../api';
import Layout from '../components/Layout.vue';
const auth = useAuthStore();
const tab = ref('list');
const vulns = ref([]);
const searchQuery = ref('');
const stateFilter = ref('');
const filteredVulns = computed(() => {
  let list = vulns.value;
  if (stateFilter.value) list = list.filter(v => v.state === stateFilter.value);
  if (searchQuery.value) { const q = searchQuery.value.toLowerCase(); list = list.filter(v => (v.title||v.vuln_name||'').toLowerCase().includes(q) || (v.target||v.asset||'').toLowerCase().includes(q)); }
  return list;
});
const stateModal = ref(null); const newState = ref('new'); const stateNote = ref('');
const assignModal = ref(null); const assignee = ref('');
const tags = ref([]); const newTagName = ref(''); const newTagColor = ref('#3b82f6');
const correlationLoading = ref(false); const correlationData = ref([]);
const riskRules = ref({ critical_threshold: 9, high_threshold: 7, auto_escalate_count: 3, notify_threshold: 10 });
const riskMsg = ref('');
function openStateModal(v) { stateModal.value = v; newState.value = v.state || 'new'; stateNote.value = ''; }
function openAssignModal(v) { assignModal.value = v; assignee.value = v.owner || ''; }
async function handleStateChange() { try { await api.updateState(stateModal.value.case_id, { new_state: newState.value }); stateModal.value = null; await loadVulns(); } catch (e) { alert('更新失败: ' + e.message); } }
async function handleAssign() { try { await api.assignCase(assignModal.value.case_id, { owner: assignee.value }); assignModal.value = null; await loadVulns(); } catch (e) { alert('分配失败: ' + e.message); } }
async function handleCreateTag() { if (!newTagName.value.trim()) return; try { await api.createTag({ tenant_id: auth.tenantId, name: newTagName.value.trim(), color: newTagColor.value }); newTagName.value = ''; await loadTags(); } catch (e) { alert('创建失败: ' + e.message); } }
async function handleDeleteTag(tagId) { try { await api.deleteTag(tagId, auth.tenantId); await loadTags(); } catch (e) { alert('删除失败: ' + e.message); } }
async function handleSaveRisk() { riskMsg.value = ''; try { await api.updateRiskRules(auth.tenantId, riskRules.value); riskMsg.value = '规则保存成功！'; } catch (e) { riskMsg.value = '保存失败: ' + e.message; } }
async function loadVulns() { try { const data = await api.vulnCases({ tenant_id: auth.tenantId, page_size: 50 }); vulns.value = data.items ?? data ?? []; } catch (e) { console.error(e); } }
async function loadTags() { try { const data = await api.vulnTags(auth.tenantId); tags.value = data.items ?? data ?? []; } catch (e) { console.error(e); } }
async function loadCorrelation() { correlationLoading.value = true; try { const data = await api.correlation(auth.tenantId); correlationData.value = data.items ?? data ?? []; } catch (e) { console.error(e); } finally { correlationLoading.value = false; } }
async function loadRiskRules() { try { const data = await api.riskRules(auth.tenantId); if (data) riskRules.value = { ...riskRules.value, ...data }; } catch (e) { console.error(e); } }
onMounted(() => { loadVulns(); loadTags(); loadCorrelation(); loadRiskRules(); });
</script>

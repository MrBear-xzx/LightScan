<template>
  <Layout :title="'任务详情 - ' + (task ? task.target : '')">
    <div v-if="loading" class="empty">加载中...</div>
    <template v-else-if="task">
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <span class="card-title" style="margin:0">基本信息</span>
          <button class="btn btn-sm btn-ghost" @click="goBack">返回列表</button>
        </div>
        <div class="grid-4">
          <div class="stat-card"><div class="stat-label">目标</div><div class="stat-value" style="font-size:14px">{{ task.target }}</div></div>
          <div class="stat-card">
            <div class="stat-label">状态</div>
            <div class="stat-value" style="font-size:14px">
              <span class="badge" :class="{'badge-resolved':task.status==='completed','badge-in-progress':task.status==='running','badge-critical':task.status==='failed','badge-low':true}">{{ task.status }}</span>
            </div>
          </div>
          <div class="stat-card"><div class="stat-label">开始时间</div><div class="stat-value" style="font-size:14px">{{ formatTime(task.started_at) }}</div></div>
          <div class="stat-card"><div class="stat-label">结束时间</div><div class="stat-value" style="font-size:14px">{{ formatTime(task.ended_at) }}</div></div>
        </div>
      </div>
      <div class="card" style="margin-top:16px">
        <div class="card-title">检查结果</div>
        <div v-if="checks.length === 0" class="empty">暂无检查数据</div>
        <div v-else>
          <div style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap">
            <span>通过: <strong style="color:var(--success)">{{ passCount }}</strong></span>
            <span>警告: <strong style="color:var(--warning)">{{ warnCount }}</strong></span>
            <span>失败: <strong style="color:var(--danger)">{{ failCount }}</strong></span>
            <span>信息: <strong style="color:var(--text-muted)">{{ infoCount }}</strong></span>
          </div>
          <table>
            <thead><tr><th>检查项</th><th>状态</th><th>详情</th><th>严重程度</th></tr></thead>
            <tbody>
              <tr v-for="(chk, i) in checks" :key="i">
                <td>{{ chk.name }}</td>
                <td>
                  <span class="badge" :class="chk.status==='passed'?'badge-resolved':chk.status==='warning'?'badge-in-progress':chk.status==='failed'?'badge-critical':'badge-low'">{{ {passed:'通过',warning:'警告',failed:'失败',info:'信息'}[chk.status]||chk.status }}</span>
                </td>
                <td style="font-size:13px;max-width:300px">{{ chk.detail }}</td>
                <td><span v-if="chk.severity" class="badge" :class="'badge-'+chk.severity">{{ chk.severity }}</span><span v-else style="color:var(--text-muted)">-</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
    <div v-else class="empty">任务不存在</div>
  </Layout>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { api } from '../api';
import Layout from '../components/Layout.vue';
const route = useRoute(); const router = useRouter(); const auth = useAuthStore();
const loading = ref(true); const task = ref(null); const checks = ref([]);
const passCount = computed(() => checks.value.filter(c => c.status === 'passed').length);
const warnCount = computed(() => checks.value.filter(c => c.status === 'warning').length);
const failCount = computed(() => checks.value.filter(c => c.status === 'failed').length);
const infoCount = computed(() => checks.value.filter(c => c.status === 'info').length);
function formatTime(t) { if (!t) return '-'; try { var d = new Date(t.endsWith('+00:00') ? t.replace('+00:00','Z') : t+'Z'); var p = function(n) { return String(n).padStart(2,'0'); }; return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes()); } catch(e) { return t.slice(0,16).replace('T',' '); } }
function goBack() { router.push('/scans'); }
onMounted(async () => { try { var d = await api.taskDetail(route.params.id, auth.tenantId); task.value = d; checks.value = d.check_results || []; } catch(e) { console.error(e); task.value = null; } finally { loading.value = false; } });
</script>

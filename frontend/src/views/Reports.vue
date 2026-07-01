<template>
  <Layout title="报表中心">
    <div class="tabs">
      <span class="tab-btn" :class="{ active: tab === 'sla' }" @click="tab = 'sla'">SLA 概览</span>
      <span class="tab-btn" :class="{ active: tab === 'trend' }" @click="tab = 'trend'">SLA 趋势</span>
      <span class="tab-btn" :class="{ active: tab === 'summary' }" @click="tab = 'summary'">漏洞汇总</span>
      <span class="tab-btn" :class="{ active: tab === 'lifecycle' }" @click="tab = 'lifecycle'">生命周期</span>
      <span class="tab-btn" :class="{ active: tab === 'scheduled' }" @click="tab = 'scheduled'">定时报表</span>
    </div>
    <div v-if="tab === 'sla'">
      <div v-if="slaLoading" class="empty">加载中...</div>
      <template v-else>
        <div class="grid-4">
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--primary)' }">{{ sla.within_sla_percent ?? '-' }}%</div><div class="stat-label">SLA 达成率</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--success)' }">{{ sla.within_sla ?? 0 }}</div><div class="stat-label">SLA 内完成</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--danger)' }">{{ sla.breached ?? 0 }}</div><div class="stat-label">SLA 违规</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--text-muted)' }">{{ sla.total_resolved ?? 0 }}</div><div class="stat-label">已修复总数</div></div>
        </div>
        <div class="card" style="margin-top:16px">
          <div class="card-title">SLA 详情</div>
          <div v-if="sla.by_severity?.length"><table><thead><tr><th>等级</th><th>总数</th><th>达成</th><th>违规</th><th>率</th></tr></thead><tbody><tr v-for="s in sla.by_severity" :key="s.severity"><td>{{ s.severity }}</td><td>{{ s.total }}</td><td>{{ s.within_sla }}</td><td>{{ s.breached }}</td><td>{{ s.within_sla_percent ?? '-' }}%</td></tr></tbody></table></div>
          <div v-else class="empty">暂无数据</div>
        </div>
      </template>
    </div>
    <div v-if="tab === 'trend'" class="card">
      <div class="card-title">SLA 趋势</div>
      <div class="form-row" style="margin-bottom:12px">
        <div class="form-group"><label>起始日期</label><input v-model="trendStart" type="date" /></div>
        <div class="form-group"><label>结束日期</label><input v-model="trendEnd" type="date" /></div>
        <div class="form-group" style="display:flex;align-items:flex-end"><button class="btn btn-primary btn-sm" @click="loadTrend">查询</button></div>
      </div>
      <div v-if="trendLoading" class="empty">加载中...</div>
      <div v-else-if="trendData.length === 0" class="empty">暂无数据</div>
      <table v-else><thead><tr><th>日期</th><th>总数</th><th>SLA 内</th><th>违规</th><th>率</th></tr></thead><tbody><tr v-for="d in trendData" :key="d.date"><td>{{ d.date }}</td><td>{{ d.total }}</td><td>{{ d.within_sla }}</td><td>{{ d.breached }}</td><td :style="{ color: (d.within_sla_percent||0) >= 90 ? 'var(--success)' : 'var(--danger)' }">{{ d.within_sla_percent ?? '-' }}%</td></tr></tbody></table>
    </div>
    <div v-if="tab === 'summary'" class="card">
      <div class="card-title">漏洞汇总</div>
      <div v-if="!summary" class="empty">暂无数据</div>
      <template v-else>
        <div class="grid-4">
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--danger)' }">{{ summary.total_critical || 0 }}</div><div class="stat-label">严重</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--high)' }">{{ summary.total_high || 0 }}</div><div class="stat-label">高危</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--warning)' }">{{ summary.total_medium || 0 }}</div><div class="stat-label">中危</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--low)' }">{{ summary.total_low || 0 }}</div><div class="stat-label">低危</div></div>
        </div>
        <button class="btn btn-sm btn-ghost" style="margin-top:12px" @click="handleExport">导出 CSV</button>
      </template>
    </div>
    <div v-if="tab === 'lifecycle'" class="card">
      <div class="card-title">生命周期</div>
      <div v-if="!lifecycle" class="empty">暂无数据</div>
      <template v-else>
        <div class="grid-4">
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--danger)' }">{{ lifecycle.total_cases || 0 }}</div><div class="stat-label">总漏洞数</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--warning)' }">{{ lifecycle.total_open || 0 }}</div><div class="stat-label">待处理</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--success)' }">{{ lifecycle.created_today || 0 }}</div><div class="stat-label">今日新增</div></div>
          <div class="stat-card"><div class="stat-value" :style="{ color: 'var(--text-muted)' }">{{ lifecycle.avg_days_open ?? '-' }}天</div><div class="stat-label">平均存在时间</div></div>
        </div>
      </template>
    </div>
    <div v-if="tab === 'scheduled'" class="card">
      <div class="card-title">定时报表</div>
      <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:flex-end">
        <div class="form-group" style="margin:0"><label>名称</label><input v-model="schedForm.name" style="width:140px" /></div>
        <div class="form-group" style="margin:0"><label>Cron</label><input v-model="schedForm.cron" placeholder="0 8 * * 1" style="width:120px" /></div>
        <div class="form-group" style="margin:0"><label>收件人</label><input v-model="schedForm.recipients" placeholder="admin@ex.com" style="width:180px" /></div>
        <button class="btn btn-primary btn-sm" @click="handleCreateSched">创建</button>
      </div>
      <div v-if="schedReports.length === 0" class="empty">暂无定时报表</div>
      <table v-else><thead><tr><th>名称</th><th>Cron</th><th>收件人</th><th>状态</th><th>操作</th></tr></thead>
        <tbody><tr v-for="r in schedReports" :key="r.id"><td>{{ r.name }}</td><td style="font-family:monospace">{{ r.cron }}</td><td style="font-size:12px">{{ r.recipients }}</td><td><span class="badge" :class="r.enabled ? 'badge-resolved' : 'badge-rejected'">{{ r.enabled ? '启用' : '停用' }}</span></td><td><button class="btn btn-sm btn-danger" @click="handleDeleteSched(r.id)">删除</button></td></tr></tbody>
      </table>
    </div>
  </Layout>
</template>
<script setup>
import { ref, onMounted } from 'vue';

import { api } from '../api';
import Layout from '../components/Layout.vue';
const tab = ref('sla');
const slaLoading = ref(false); const sla = ref({});
const trendStart = ref(new Date(Date.now()-30*86400000).toISOString().slice(0,10)); const trendEnd = ref(new Date().toISOString().slice(0,10)); const trendLoading = ref(false); const trendData = ref([]);
const summaryLoading = ref(false); const summary = ref(null);
const lifecycleLoading = ref(false); const lifecycle = ref(null);
const schedForm = ref({ name: '', cron: '0 8 * * 1', recipients: '' }); const schedReports = ref([]);
async function loadSla() { slaLoading.value = true; try { const d = await api.slaOverview(); sla.value = { within_sla_percent: d.total_cases > 0 ? Math.round((d.total_cases - d.overdue_cases) / d.total_cases * 100) : 0, within_sla: d.total_cases - d.overdue_cases, breached: d.overdue_cases, total_resolved: d.status_counts?.fixed || 0, total_cases: d.total_cases, by_severity: [] }; } catch (e) { console.error(e); } finally { slaLoading.value = false; } }
async function loadTrend() { trendLoading.value = true; try { const d = await api.slaTrend({ start_date: trendStart.value, end_date: trendEnd.value }); const pts = d.points ?? []; trendData.value = pts.map(function(p) { return { date: p.date, total: p.total_cases, within_sla: p.total_cases - p.overdue_cases, breached: p.overdue_cases, within_sla_percent: p.total_cases > 0 ? Math.round((p.total_cases - p.overdue_cases) / p.total_cases * 100) : 0 }; }); } catch (e) { console.error(e); } finally { trendLoading.value = false; } }
async function loadSummary() { summaryLoading.value = true; try { const d = await api.vulnSummary(); const cnt = d.counts || {}; summary.value = { total_critical: cnt.critical || 0, total_high: cnt.high || 0, total_medium: cnt.medium || 0, total_low: cnt.low || 0, vuln_new: cnt.new || 0, vuln_confirmed: cnt.confirmed || 0, vuln_in_progress: cnt.in_progress || 0, vuln_fixed: cnt.fixed || 0 }; } catch (e) { console.error(e); } finally { summaryLoading.value = false; } }
async function loadLifecycle() { try { lifecycle.value = await api.lifecycle(); } catch (e) { console.error(e); } }
async function loadSchedReports() { try { const d = await api.scheduledReports(); schedReports.value = d.points ?? []; } catch (e) { console.error(e); } }
async function handleCreateSched() { try { await api.createScheduledReport(schedForm.value); schedForm.value = { name: '', cron: '0 8 * * 1', recipients: '' }; await loadSchedReports(); } catch (e) { alert('创建失败'); } }
async function handleDeleteSched(id) { try { await api.deleteScheduledReport(id); await loadSchedReports(); } catch (e) { alert('删除失败'); } }
async function handleExport() { try { const r = await api.exportCsv(); const b = await r.blob(); const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'vuln-export.csv'; a.click(); } catch (e) { alert('导出失败'); } }
onMounted(() => { loadSla(); loadTrend(); loadSummary(); loadLifecycle(); loadSchedReports(); });
</script>

<template>
  <Layout title="仪表盘">
    <div v-if="loading" class="empty">加载中...</div>
    <template v-else>
      <div class="grid-4">
        <div class="stat-card">
          <div class="stat-value" :style="{ color: 'var(--primary)' }">{{ lifecycle.total_cases }}</div>
          <div class="stat-label">漏洞总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" :style="{ color: 'var(--warning)' }">{{ lifecycle.total_open }}</div>
          <div class="stat-label">待处理</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" :style="{ color: 'var(--success)' }">{{ lifecycle.created_today }}</div>
          <div class="stat-label">今日新增</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" :style="{ color: 'var(--text-muted)' }">{{ lifecycle.avg_days_open }}天</div>
          <div class="stat-label">平均存在时间</div>
        </div>
      </div>

      <div class="grid-2" style="margin-top: 16px">
        <div class="card">
          <div class="card-title">状态分布</div>
          <div v-if="lifecycle.state_distribution">
            <div style="display:flex;justify-content:space-between;padding:6px 0;font-size:13px">
              <span>待处理 (new)</span><span>{{ lifecycle.state_distribution.new }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:6px 0;font-size:13px">
              <span>处理中</span><span>{{ lifecycle.state_distribution.in_progress }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:6px 0;font-size:13px">
              <span>已修复</span><span>{{ lifecycle.state_distribution.resolved }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:6px 0;font-size:13px">
              <span>误报/忽略</span><span>{{ lifecycle.state_distribution.false_positive + lifecycle.state_distribution.rejected }}</span>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">最近操作</div>
          <div v-if="logs.length === 0" class="empty">暂无操作记录</div>
          <div v-for="log in logs.slice(0, 5)" :key="log.event_id" style="padding:6px 0;font-size:13px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between">
            <span>{{ log.event_type }}</span>
            <span style="color:var(--text-muted);font-size:11px">{{ formatTime(log.created_at) }}</span>
          </div>
        </div>
      </div>

      <div class="card" style="margin-top:16px">
        <div class="card-title">扫描结果聚合</div>
        <div v-if="aggr.total_findings === 0" class="empty">暂无扫描结果，请先创建扫描任务</div>
        <div v-else>
          <div style="display:flex;gap:20px;margin-bottom:12px">
            <span>涉及资产: <strong>{{ aggr.total_assets }}</strong></span>
            <span>总发现: <strong>{{ aggr.total_findings }}</strong></span>
          </div>
          <div style="display:flex;gap:12px">
            <span class="badge badge-critical">严重 {{ aggr.severity_breakdown.critical }}</span>
            <span class="badge badge-high">高危 {{ aggr.severity_breakdown.high }}</span>
            <span class="badge badge-medium">中危 {{ aggr.severity_breakdown.medium }}</span>
            <span class="badge badge-low">低危 {{ aggr.severity_breakdown.low }}</span>
          </div>
        </div>
      </div>
    </template>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { api } from '../api';
import Layout from '../components/Layout.vue';

const auth = useAuthStore();
const loading = ref(true);
const lifecycle = ref({ state_distribution: {}, total_cases: 0, total_open: 0, created_today: 0, avg_days_open: 0 });
const aggr = ref({ total_assets: 0, total_findings: 0, severity_breakdown: { critical:0, high:0, medium:0, low:0, unknown:0 } });
const logs = ref([]);

function formatTime(t) { return t ? t.slice(0, 16).replace('T', ' ') : ''; }

onMounted(async () => {
  try {
    const [lc, ag, lg] = await Promise.all([
      api.lifecycle(auth.tenantId),
      api.scanAggregation(auth.tenantId),
      api.opsLogs({ tenant_id: auth.tenantId, page_size: 5 }),
    ]);
    lifecycle.value = lc;
    aggr.value = ag;
    logs.value = lg.items || [];
  } catch (e) { console.error(e); }
  finally { loading.value = false; }
});
</script>

const BASE = '';

async function request(url, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const res = await fetch(BASE + url, { ...options, headers });
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) {
    const data = await res.json();
    if (!res.ok) throw new Error(Array.isArray(data.detail) ? data.detail.map(function(e) { return e.msg; }).join('; ') : data.detail || '请求失败');
    return data;
  }
  if (!res.ok) throw new Error('请求失败');
  return res;
}

export const api = {
  // 扫描
  createTask: (data) => request('/api/v1/discovery/tasks', { method: 'POST', body: JSON.stringify(data) }),
  batchScan: (data) => request('/api/v1/scan/batch', { method: 'POST', body: JSON.stringify(data) }),
  scanProgress: (params) => request('/api/v1/scan/progress?' + new URLSearchParams(params)),
  cancelTask: (taskId) => request('/api/v1/scan/' + taskId + '/cancel', { method: 'POST' }),
  taskDetail: (id) => request('/api/v1/scan/tasks/' + id),
  scanAggregation: () => request('/api/v1/scan/aggregation'),
  scanPolicies: () => request('/api/v1/scan/policies'),

  // 漏洞
  vulnCases: (params) => request('/api/v1/vuln-cases?' + new URLSearchParams(params)),
  updateState: (caseId, data) => request('/api/v1/vuln-cases/' + caseId + '/state', { method: 'PATCH', body: JSON.stringify(data) }),
  assignCase: (caseId, data) => request('/api/v1/vuln-cases/' + caseId + '/assign', { method: 'PATCH', body: JSON.stringify(data) }),
  vulnTags: () => request('/api/v1/vuln-cases/tags'),
  createTag: (data) => request('/api/v1/vuln-cases/tags', { method: 'POST', body: JSON.stringify(data) }),
  deleteTag: (tagId) => request('/api/v1/vuln-cases/tags/' + tagId, { method: 'DELETE' }),
  caseTags: (caseId) => request('/api/v1/vuln-cases/' + caseId + '/tags'),
  assignTags: (caseId, data) => request('/api/v1/vuln-cases/' + caseId + '/tags', { method: 'POST', body: JSON.stringify(data) }),
  correlation: () => request('/api/v1/vuln-cases/correlation'),
  lifecycle: () => request('/api/v1/reports/vuln/lifecycle'),
  riskRules: () => request('/api/v1/risk/rules'),
  updateRiskRules: (data) => request('/api/v1/risk/rules', { method: 'PUT', body: JSON.stringify(data) }),

  // 插件
  plugins: (params) => request('/api/v1/plugins?' + new URLSearchParams(params)),
  pluginHealth: () => request('/api/v1/plugins/health'),
  rolloutPolicy: () => request('/api/v1/plugins/rollout-policy'),
  updateRolloutPolicy: (data) => request('/api/v1/plugins/rollout-policy', { method: 'PUT', body: JSON.stringify(data) }),
  rolloutAudit: (params) => request('/api/v1/plugins/rollout-audit?' + new URLSearchParams(params)),

  // 报表
  slaOverview: () => request('/api/v1/reports/sla/overview'),
  slaTrend: (params) => request('/api/v1/reports/sla/trend?' + new URLSearchParams(params)),
  vulnSummary: () => request('/api/v1/reports/vuln/summary'),
  exportCsv: () => request('/api/v1/reports/vuln/export.csv'),

  // 通知
  dispatchNotification: (data) => request('/api/v1/notifications/dispatch', { method: 'POST', body: JSON.stringify(data) }),
  notifyPolicy: () => request('/api/v1/notifications/policy'),
  updateNotifyPolicy: (data) => request('/api/v1/notifications/policy', { method: 'PUT', body: JSON.stringify(data) }),
  notifyTemplates: () => request('/api/v1/notifications/templates'),
  createNotifyTemplate: (data) => request('/api/v1/notifications/templates', { method: 'POST', body: JSON.stringify(data) }),
  deleteNotifyTemplate: (id) => request('/api/v1/notifications/templates/' + id, { method: 'DELETE' }),
  webhookSubs: () => request('/api/v1/notifications/webhooks'),
  createWebhookSub: (data) => request('/api/v1/notifications/webhooks', { method: 'POST', body: JSON.stringify(data) }),
  deleteWebhookSub: (id) => request('/api/v1/notifications/webhooks/' + id, { method: 'DELETE' }),
  scheduledReports: () => request('/api/v1/reports/scheduled'),
  createScheduledReport: (data) => request('/api/v1/reports/scheduled', { method: 'POST', body: JSON.stringify(data) }),
  deleteScheduledReport: (id) => request('/api/v1/reports/scheduled/' + id, { method: 'DELETE' }),

  // 运维
  opsLogs: (params) => request('/api/v1/ops/logs?' + new URLSearchParams(params)),
  alertRules: () => request('/api/v1/ops/alert-rules'),
  createAlertRule: (data) => request('/api/v1/ops/alert-rules', { method: 'POST', body: JSON.stringify(data) }),
  deleteAlertRule: (id) => request('/api/v1/ops/alert-rules/' + id, { method: 'DELETE' }),
  backups: () => request('/api/v1/ops/backups'),
  createBackup: () => request('/api/v1/ops/backups', { method: 'POST' }),

  // 异步任务
  jobStatus: (params) => request('/api/v1/jobs/status?' + new URLSearchParams(params)),
  retryJob: (data) => request('/api/v1/jobs/retry', { method: 'POST', body: JSON.stringify(data) }),
  retryPolicy: () => request('/api/v1/jobs/retry-policy'),
  updateRetryPolicy: (data) => request('/api/v1/jobs/retry-policy', { method: 'PUT', body: JSON.stringify(data) }),
  retryHistory: (params) => request('/api/v1/jobs/retries?' + new URLSearchParams(params)),
  retryOverview: () => request('/api/v1/jobs/retries/overview'),
};

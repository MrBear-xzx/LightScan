const BASE = '';

async function request(url, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const res = await fetch(BASE + url, { ...options, headers });
  if (res.status === 401 && !url.startsWith('/api/v1/auth/')) {
    localStorage.removeItem('token');
    window.location.href = '/';
    throw new Error('登录已过期，请重新登录');
  }
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
  // ??
  login: (data) => request('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  register: (data) => request('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request('/api/v1/auth/me'),
  permissions: () => request('/api/v1/auth/permissions'),

  // ??
  createTask: (data) => request('/api/v1/discovery/tasks', { method: 'POST', body: JSON.stringify(data) }),
  batchScan: (data) => request('/api/v1/scan/batch', { method: 'POST', body: JSON.stringify(data) }),
  scanProgress: (params) => request('/api/v1/scan/progress?' + new URLSearchParams(params)),
  cancelTask: (taskId, tenantId) => request('/api/v1/scan/' + taskId + '/cancel?tenant_id=' + tenantId, { method: 'POST' }),
  taskDetail: (id, tenantId) => request("/api/v1/scan/tasks/" + id + "?tenant_id=" + tenantId),
  scanAggregation: (tenantId) => request('/api/v1/scan/aggregation?tenant_id=' + tenantId),
  scanPolicies: (tenantId) => request('/api/v1/scan/policies?tenant_id=' + tenantId),

  // ??
  vulnCases: (params) => request('/api/v1/vuln-cases?' + new URLSearchParams(params)),
  updateState: (caseId, data) => request('/api/v1/vuln-cases/' + caseId + '/state', { method: 'PATCH', body: JSON.stringify(data) }),
  assignCase: (caseId, data) => request('/api/v1/vuln-cases/' + caseId + '/assign', { method: 'PATCH', body: JSON.stringify(data) }),
  vulnTags: (tenantId) => request('/api/v1/vuln-cases/tags?tenant_id=' + tenantId),
  createTag: (data) => request('/api/v1/vuln-cases/tags', { method: 'POST', body: JSON.stringify(data) }),
  deleteTag: (tagId, tenantId) => request('/api/v1/vuln-cases/tags/' + tagId + '?tenant_id=' + tenantId, { method: 'DELETE' }),
  caseTags: (caseId, tenantId) => request('/api/v1/vuln-cases/' + caseId + '/tags?tenant_id=' + tenantId),
  assignTags: (caseId, data) => request('/api/v1/vuln-cases/' + caseId + '/tags?tenant_id=' + data.tenant_id, { method: 'POST', body: JSON.stringify(data) }),
  correlation: (tenantId) => request('/api/v1/vuln-cases/correlation?tenant_id=' + tenantId),
  lifecycle: (tenantId) => request('/api/v1/reports/vuln/lifecycle?tenant_id=' + tenantId),
  riskRules: (tenantId) => request('/api/v1/risk/rules?tenant_id=' + tenantId),
  updateRiskRules: (tenantId, data) => request('/api/v1/risk/rules?tenant_id=' + tenantId, { method: 'PUT', body: JSON.stringify(data) }),

  // ??
  plugins: (params) => request('/api/v1/plugins?' + new URLSearchParams(params)),
  pluginHealth: (tenantId) => request('/api/v1/plugins/health?tenant_id=' + tenantId),
  rolloutPolicy: (tenantId) => request('/api/v1/plugins/rollout-policy?tenant_id=' + tenantId),
  updateRolloutPolicy: (data) => request('/api/v1/plugins/rollout-policy', { method: 'PUT', body: JSON.stringify(data) }),
  rolloutAudit: (params) => request('/api/v1/plugins/rollout-audit?' + new URLSearchParams(params)),

  // ??
  slaOverview: (tenantId) => request('/api/v1/reports/sla/overview?tenant_id=' + tenantId),
  slaTrend: (params) => request('/api/v1/reports/sla/trend?' + new URLSearchParams(params)),
  vulnSummary: (tenantId) => request('/api/v1/reports/vuln/summary?tenant_id=' + tenantId),
  exportCsv: (tenantId) => request('/api/v1/reports/vuln/export.csv?tenant_id=' + tenantId),

  // ??
  dispatchNotification: (data) => request('/api/v1/notifications/dispatch', { method: 'POST', body: JSON.stringify(data) }),
  notifyPolicy: (tenantId) => request('/api/v1/notifications/policy?tenant_id=' + tenantId),
  updateNotifyPolicy: (data) => request('/api/v1/notifications/policy', { method: 'PUT', body: JSON.stringify(data) }),
  notifyTemplates: (tenantId) => request('/api/v1/notifications/templates?tenant_id=' + tenantId),
  createNotifyTemplate: (tenantId, data) => request('/api/v1/notifications/templates?tenant_id=' + tenantId, { method: 'POST', body: JSON.stringify(data) }),
  deleteNotifyTemplate: (id, tenantId) => request('/api/v1/notifications/templates/' + id + '?tenant_id=' + tenantId, { method: 'DELETE' }),
  webhookSubs: (tenantId) => request('/api/v1/notifications/webhooks?tenant_id=' + tenantId),
  createWebhookSub: (tenantId, data) => request('/api/v1/notifications/webhooks?tenant_id=' + tenantId, { method: 'POST', body: JSON.stringify(data) }),
  deleteWebhookSub: (id, tenantId) => request('/api/v1/notifications/webhooks/' + id + '?tenant_id=' + tenantId, { method: 'DELETE' }),
  scheduledReports: (tenantId) => request('/api/v1/reports/scheduled?tenant_id=' + tenantId),
  createScheduledReport: (tenantId, data) => request('/api/v1/reports/scheduled?tenant_id=' + tenantId, { method: 'POST', body: JSON.stringify(data) }),
  deleteScheduledReport: (id, tenantId) => request('/api/v1/reports/scheduled/' + id + '?tenant_id=' + tenantId, { method: 'DELETE' }),

  users: (tenantId) => request('/api/v1/auth/users?tenant_id=' + tenantId),
  opsLogs: (params) => request('/api/v1/ops/logs?' + new URLSearchParams(params)),
  alertRules: (tenantId) => request('/api/v1/ops/alert-rules?tenant_id=' + tenantId),
  createAlertRule: (tenantId, data) => request('/api/v1/ops/alert-rules?tenant_id=' + tenantId, { method: 'POST', body: JSON.stringify(data) }),
  deleteAlertRule: (id, tenantId) => request('/api/v1/ops/alert-rules/' + id + '?tenant_id=' + tenantId, { method: 'DELETE' }),
  backups: (tenantId) => request('/api/v1/ops/backups?tenant_id=' + tenantId),
  createBackup: (tenantId) => request('/api/v1/ops/backups?tenant_id=' + tenantId, { method: 'POST' }),
  projects: (tenantId) => request('/api/v1/projects?tenant_id=' + tenantId),
  createProject: (data) => request('/api/v1/projects', { method: 'POST', body: JSON.stringify(data) }),
  deleteProject: (id, tenantId) => request('/api/v1/projects/' + id + '?tenant_id=' + tenantId, { method: 'DELETE' }),

  // ??
  jobStatus: (params) => request('/api/v1/jobs/status?' + new URLSearchParams(params)),
  retryJob: (data) => request('/api/v1/jobs/retry', { method: 'POST', body: JSON.stringify(data) }),
  retryPolicy: (tenantId) => request('/api/v1/jobs/retry-policy?tenant_id=' + tenantId),
  updateRetryPolicy: (data) => request('/api/v1/jobs/retry-policy', { method: 'PUT', body: JSON.stringify(data) }),
  retryHistory: (params) => request('/api/v1/jobs/retries?' + new URLSearchParams(params)),
  retryOverview: (tenantId) => request('/api/v1/jobs/retries/overview?tenant_id=' + tenantId),
};

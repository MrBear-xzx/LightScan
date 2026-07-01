import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from './views/Dashboard.vue';
import Scans from './views/Scans.vue';
import Vulns from './views/Vulns.vue';
import Reports from './views/Reports.vue';
import Notifications from './views/Notifications.vue';
import Plugins from './views/Plugins.vue';
import Admin from './views/Admin.vue';

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/scans', name: 'Scans', component: Scans },
  { path: '/scans/:id', name: 'TaskDetail', component: () => import("./views/TaskDetail.vue") },
  { path: '/vulns', name: 'Vulns', component: Vulns },
  { path: '/reports', name: 'Reports', component: Reports },
  { path: '/notifications', name: 'Notifications', component: Notifications },
  { path: '/plugins', name: 'Plugins', component: Plugins },
  { path: '/admin', name: 'Admin', component: Admin },
];

const router = createRouter({ history: createWebHistory(), routes });

export default router;

import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from './views/Dashboard.vue';
import Scans from './views/Scans.vue';
import Vulns from './views/Vulns.vue';
import Reports from './views/Reports.vue';
import Notifications from './views/Notifications.vue';
import Plugins from './views/Plugins.vue';
import Admin from './views/Admin.vue';

const routes = [
  { path: '/', name: 'Login', component: () => import('./views/Login.vue') },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/scans', name: 'Scans', component: Scans, meta: { requiresAuth: true } },
  { path: '/scans/:id', name: 'TaskDetail', component: () => import("./views/TaskDetail.vue"), meta: { requiresAuth: true } },
  { path: '/vulns', name: 'Vulns', component: Vulns, meta: { requiresAuth: true } },
  { path: '/reports', name: 'Reports', component: Reports, meta: { requiresAuth: true } },
  { path: '/notifications', name: 'Notifications', component: Notifications, meta: { requiresAuth: true } },
  { path: '/plugins', name: 'Plugins', component: Plugins, meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: Admin, meta: { requiresAuth: true } },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (to.meta.requiresAuth && !token) next('/');
  else next();
});

export default router;

import { defineStore } from 'pinia';
import { api } from '../api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    tenantId: localStorage.getItem('tenant_id') || 'default',
    username: localStorage.getItem('username') || '',
    role: localStorage.getItem('role') || '',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.role === 'admin',
    isAnalyst: (state) => state.role === 'admin' || state.role === 'analyst',
  },
  actions: {
    async login(tenantId, username, password) {
      const data = await api.login({ tenant_id: tenantId, username, password });
      this.token = data.access_token;
      this.tenantId = data.tenant_id;
      this.username = data.username;
      this.role = data.role;
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('tenant_id', data.tenant_id);
      localStorage.setItem('username', data.username);
      localStorage.setItem('role', data.role);
    },
    async register(tenantId, username, password, role) {
      return await api.register({ tenant_id: tenantId, username, password, role });
    },
    logout() {
      this.token = '';
      this.tenantId = 'default';
      this.username = '';
      this.role = '';
      localStorage.removeItem('token');
      localStorage.removeItem('tenant_id');
      localStorage.removeItem('username');
      localStorage.removeItem('role');
      window.location.href = '/';
    },
  },
});

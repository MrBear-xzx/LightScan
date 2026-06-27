<template>
  <div class="login-page">
    <div class="login-card">
      <h1>LightScan</h1>
      <p class="subtitle">漏洞分析平台</p>

      <div class="tab-bar">
        <span :class="{ active: isLogin }" @click="isLogin = true">登录</span>
        <span :class="{ active: !isLogin }" @click="isLogin = false">注册</span>
      </div>

      <div v-if="isLogin">
        <div class="form-group">
          <label>租户 ID</label>
          <input v-model="loginTenant" placeholder="如 t1" />
        </div>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="loginUser" placeholder="输入用户名" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="loginPass" type="password" placeholder="输入密码" @keyup.enter="handleLogin" />
        </div>
        <p v-if="loginError" class="error-msg">{{ loginError }}</p>
        <button class="btn btn-primary btn-full" @click="handleLogin" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </div>

      <div v-else>
        <div class="form-group">
          <label>租户 ID</label>
          <input v-model="regTenant" placeholder="如 t1" />
        </div>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="regUser" placeholder="输入用户名" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="regPass" type="password" placeholder="至少 4 位" />
        </div>
        <div class="form-group">
          <label>角色</label>
          <select v-model="regRole">
            <option value="admin">管理员 (admin)</option>
            <option value="analyst" selected>分析师 (analyst)</option>
            <option value="viewer">观察者 (viewer)</option>
          </select>
        </div>
        <p v-if="regError" class="error-msg">{{ regError }}</p>
                <button class="btn btn-primary btn-full" @click="handleRegister" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { api } from '../api';

const router = useRouter();
const auth = useAuthStore();

const isLogin = ref(true);
const loading = ref(false);
const loginTenant = ref('t1');
const loginUser = ref('');
const loginPass = ref('');
const loginError = ref('');
const regTenant = ref('t1');
const regUser = ref('');
const regPass = ref('');
const regRole = ref('analyst');
const regError = ref('');
const regSuccess = ref('');

async function handleLogin() {
  loginError.value = '';
  loading.value = true;
  try {
    await auth.login(loginTenant.value, loginUser.value, loginPass.value);
    router.push('/dashboard');
  } catch (e) {
    loginError.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function handleRegister() {
  regError.value = '';
  loading.value = true;
  try {
    await auth.register(regTenant.value, regUser.value, regPass.value, regRole.value);
    await auth.login(regTenant.value, regUser.value, regPass.value);
    router.push('/dashboard');
  } catch (e) {
    regError.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
.login-card { background: #1e293b; border-radius: 16px; padding: 40px; width: 400px; box-shadow: 0 25px 50px rgba(0,0,0,0.4); }
h1 { font-size: 24px; text-align: center; }
h1 span { color: #3b82f6; }
.subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin: 4px 0 24px; }
.tab-bar { display: flex; gap: 0; margin-bottom: 24px; border-bottom: 1px solid #334155; }
.tab-bar span { flex: 1; text-align: center; padding: 8px; cursor: pointer; color: #94a3b8; font-size: 14px; border-bottom: 2px solid transparent; }
.tab-bar span.active { color: #3b82f6; border-bottom-color: #3b82f6; }
.btn-full { width: 100%; margin-top: 12px; }
.error-msg { color: #ef4444; font-size: 13px; margin-top: 8px; }
.success-msg { color: #22c55e; font-size: 13px; margin-top: 8px; }
</style>

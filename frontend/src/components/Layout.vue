<template>
  <div class="layout">
    <NavBar />
    <div class="main">
      <div class="topbar">
        <h2>{{ title }}</h2>
        <div class="user-info">
          <span>{{ authStore.username }}</span>
          <span class="role-badge">{{ authStore.role }}</span>
          <span class="logout-btn" @click="authStore.logout()">退出</span>
        </div>
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';
import NavBar from './NavBar.vue';
defineProps({ title: String });
const authStore = useAuthStore();
</script>

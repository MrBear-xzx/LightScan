<template>
  <div class="layout">
    <NavBar />
    <div class="main">
      <div class="topbar">
        <h2>{{ title }}</h2>
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup>
import NavBar from './NavBar.vue';
defineProps({ title: String });
</script>

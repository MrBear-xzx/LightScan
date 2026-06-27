<template>
  <Teleport to="body">
    <div v-if="visible" class="toast" :class="'toast-' + type">{{ message }}</div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue';
const visible = ref(false);
const message = ref('');
const type = ref('success');
let timer = null;

function show(msg, t = 'success') {
  message.value = msg;
  type.value = t;
  visible.value = true;
  clearTimeout(timer);
  timer = setTimeout(() => visible.value = false, 3000);
}
defineExpose({ show });
</script>

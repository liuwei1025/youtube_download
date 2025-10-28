<template>
  <div :class="['base-card', { 'base-card--hover': hover }]">
    <slot />
  </div>
</template>

<script setup>
defineProps({
  hover: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.base-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.base-card--hover:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
</style>


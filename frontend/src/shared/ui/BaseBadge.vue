<template>
  <span :class="['base-badge', `base-badge--${variant}`]">
    <slot />
  </span>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'warning', 'danger', 'info'].includes(value)
  }
})
</script>

<style scoped>
.base-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.base-badge--default {
  background: #f3f4f6;
  color: #374151;
}

.base-badge--success {
  background: #d1fae5;
  color: #065f46;
}

.base-badge--warning {
  background: #fef3c7;
  color: #92400e;
}

.base-badge--danger {
  background: #fee2e2;
  color: #991b1b;
}

.base-badge--info {
  background: #dbeafe;
  color: #1e40af;
}
</style>


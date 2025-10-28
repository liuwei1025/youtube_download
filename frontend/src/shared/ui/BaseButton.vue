<template>
  <button 
    :class="['base-button', `base-button--${variant}`, `base-button--${size}`, { 'base-button--disabled': disabled }]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'danger', 'warning'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.base-button:hover:not(.base-button--disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.base-button:active:not(.base-button--disabled) {
  transform: translateY(0);
}

.base-button--disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Sizes */
.base-button--small {
  padding: 6px 12px;
  font-size: 13px;
}

.base-button--medium {
  padding: 10px 20px;
  font-size: 14px;
}

.base-button--large {
  padding: 14px 28px;
  font-size: 16px;
}

/* Variants */
.base-button--primary {
  background: #3b82f6;
  color: white;
}

.base-button--primary:hover:not(.base-button--disabled) {
  background: #2563eb;
}

.base-button--secondary {
  background: #6b7280;
  color: white;
}

.base-button--secondary:hover:not(.base-button--disabled) {
  background: #4b5563;
}

.base-button--success {
  background: #10b981;
  color: white;
}

.base-button--success:hover:not(.base-button--disabled) {
  background: #059669;
}

.base-button--danger {
  background: #ef4444;
  color: white;
}

.base-button--danger:hover:not(.base-button--disabled) {
  background: #dc2626;
}

.base-button--warning {
  background: #f59e0b;
  color: white;
}

.base-button--warning:hover:not(.base-button--disabled) {
  background: #d97706;
}
</style>


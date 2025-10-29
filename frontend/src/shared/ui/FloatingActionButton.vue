<template>
  <button 
    :class="['fab', { 'fab--hidden': hidden }]"
    :title="title"
    @click="$emit('click', $event)"
  >
    <slot>
      <PlusIcon :size="32" class="fab-icon" />
    </slot>
  </button>
</template>

<script setup>
import { PlusIcon } from '@components/ui'

defineProps({
  hidden: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '创建任务'
  }
})

defineEmits(['click'])
</script>

<style scoped>
.fab {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4), 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  font-family: inherit;
}

.fab:hover {
  transform: scale(1.1) translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5), 0 12px 32px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.fab:active {
  transform: scale(1.05);
}

.fab--hidden {
  transform: scale(0) translateY(100px);
  opacity: 0;
  pointer-events: none;
}

.fab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .fab {
    right: 20px;
    bottom: 20px;
    width: 56px;
    height: 56px;
  }
  
}

/* 添加脉冲动画提示 */
@keyframes pulse {
  0% {
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4), 0 8px 24px rgba(0, 0, 0, 0.15);
  }
  50% {
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.6), 0 8px 24px rgba(0, 0, 0, 0.2), 0 0 0 10px rgba(59, 130, 246, 0.1);
  }
  100% {
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4), 0 8px 24px rgba(0, 0, 0, 0.15);
  }
}

.fab:not(:hover):not(.fab--hidden) {
  animation: pulse 2s ease-in-out infinite;
}
</style>


<template>
  <Badge :variant="mappedVariant">
    <slot />
  </Badge>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from '@components/ui'

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  size: {
    type: String,
    default: 'default'
  }
})

// 映射旧的 variant 到新的 shadcn-vue variant
const mappedVariant = computed(() => {
  const variantMap = {
    default: 'secondary',
    success: 'success',
    warning: 'warning',
    danger: 'destructive',
    info: 'info'
  }
  return variantMap[props.variant] || 'secondary'
})
</script>


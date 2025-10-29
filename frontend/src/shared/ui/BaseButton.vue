<template>
  <Button 
    :variant="mappedVariant"
    :size="mappedSize"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </Button>
</template>

<script setup>
import { computed } from 'vue'
import { Button } from '@components/ui'

const props = defineProps({
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

// 映射旧的 variant 到新的 shadcn-vue variant
const mappedVariant = computed(() => {
  const variantMap = {
    primary: 'default',
    secondary: 'secondary',
    success: 'default',
    danger: 'destructive',
    warning: 'default'
  }
  return variantMap[props.variant] || 'default'
})

// 映射旧的 size 到新的 shadcn-vue size
const mappedSize = computed(() => {
  const sizeMap = {
    small: 'sm',
    medium: 'default',
    large: 'lg'
  }
  return sizeMap[props.size] || 'default'
})

defineEmits(['click'])
</script>


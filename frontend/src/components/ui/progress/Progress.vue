<template>
  <ProgressRoot
    v-bind="forwarded"
    :class="cn('relative h-2 w-full overflow-hidden rounded-full bg-primary/20', props.class)"
  >
    <ProgressIndicator
      class="h-full w-full flex-1 bg-primary transition-all"
      :style="`transform: translateX(-${100 - (props.modelValue ?? 0)}%)`"
    />
  </ProgressRoot>
</template>

<script setup>
import { computed } from 'vue'
import { ProgressIndicator, ProgressRoot, useForwardPropsEmits } from 'radix-vue'
import { cn } from '@shared/lib'

const props = defineProps({
  modelValue: {
    type: Number,
    default: 0,
  },
  max: {
    type: Number,
    default: 100,
  },
  class: {
    type: String,
    default: '',
  },
})

const emits = defineEmits(['update:modelValue'])

const forwarded = useForwardPropsEmits(props, emits)
</script>


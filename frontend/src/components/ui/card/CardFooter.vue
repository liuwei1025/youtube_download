<template>
  <div :class="cn('flex items-center p-6 pt-0', props.class)">
    <slot />
  </div>
</template>

<script setup>
import { cn } from '@shared/lib'

const props = defineProps({
  class: {
    type: String,
    default: '',
  },
})
</script>


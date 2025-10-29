<template>
  <div :class="cn('flex flex-col space-y-1.5 p-6', props.class)">
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


<template>
  <div :class="cn('p-6 pt-0', props.class)">
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


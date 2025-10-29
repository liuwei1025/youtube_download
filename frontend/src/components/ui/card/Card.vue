<template>
  <div :class="cn('rounded-lg border bg-card text-card-foreground shadow', props.class)">
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


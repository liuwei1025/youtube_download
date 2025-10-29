<template>
  <tr :class="cn('border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted', props.class)">
    <slot />
  </tr>
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


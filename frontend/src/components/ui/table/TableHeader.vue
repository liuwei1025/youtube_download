<template>
  <thead :class="cn('[&_tr]:border-b', props.class)">
    <slot />
  </thead>
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


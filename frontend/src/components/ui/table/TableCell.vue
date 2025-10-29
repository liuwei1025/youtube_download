<template>
  <td :class="cn('p-2 align-middle [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]', props.class)">
    <slot />
  </td>
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


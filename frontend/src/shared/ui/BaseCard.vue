<template>
  <Card :class="hover ? 'transition-all hover:shadow-lg hover:-translate-y-0.5' : ''">
    <CardContent class="p-5">
      <slot />
    </CardContent>
  </Card>
</template>

<script setup>
import { Card, CardContent } from '@components/ui'

defineProps({
  hover: {
    type: Boolean,
    default: false
  }
})
</script>


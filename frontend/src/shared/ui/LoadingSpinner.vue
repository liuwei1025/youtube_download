<template>
  <div class="flex flex-col items-center justify-center p-10">
    <div class="w-10 h-10 border-4 border-muted border-t-primary rounded-full animate-spin"></div>
    <p v-if="text" class="mt-4 text-sm text-muted-foreground">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    default: ''
  }
})
</script>


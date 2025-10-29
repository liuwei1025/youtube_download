<template>
  <div class="flex flex-col min-h-screen">
    <header class="sticky top-0 z-50 bg-background border-b">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center">
          <router-link to="/" class="flex items-center gap-3 text-xl font-bold text-foreground hover:opacity-80 transition-opacity">
            <VideoIcon :size="32" class="text-primary" />
            <span class="hidden md:inline">YouTube 下载器</span>
          </router-link>
        </div>
      </div>
    </header>
    
    <main class="flex-1">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <footer class="bg-background border-t mt-16">
      <div class="container mx-auto px-6 py-6 text-center">
        <p class="text-sm text-muted-foreground">&copy; 2025 YouTube 下载器. Version 1.0.0</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { VideoIcon } from '@components/ui'
</script>

<style scoped>
/* Page transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>


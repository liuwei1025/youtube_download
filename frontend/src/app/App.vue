<template>
  <div class="flex flex-col min-h-screen">
    <header class="sticky top-0 z-50 bg-background border-b">
      <div class="container mx-auto px-6 py-4">
        <div class="flex justify-between items-center">
          <router-link to="/" class="flex items-center gap-3 text-xl font-bold text-foreground hover:opacity-80 transition-opacity">
            <span class="text-3xl">🎬</span>
            <span class="hidden md:inline">YouTube 下载器</span>
          </router-link>
          <nav class="flex items-center gap-6">
            <router-link 
              to="/" 
              class="text-muted-foreground font-medium hover:text-primary transition-colors router-link-active:text-primary"
            >
              任务列表
            </router-link>
            <Button @click="handleCreateTask" class="gap-2">
              <span class="text-lg font-bold leading-none">+</span>
              创建任务
            </Button>
          </nav>
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
import { useRouter } from 'vue-router'
import { Button } from '@components/ui'

const router = useRouter()

function handleCreateTask() {
  // 触发自定义事件或跳转到主页并展开表单
  if (router.currentRoute.value.path === '/') {
    // 已在主页，触发事件
    window.dispatchEvent(new CustomEvent('show-create-form'))
  } else {
    // 跳转到主页并显示创建表单
    router.push({ path: '/', query: { create: 'true' } })
  }
}
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


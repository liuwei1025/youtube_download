<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <router-link to="/" class="logo">
          <span class="logo-icon">🎬</span>
          <span class="logo-text">YouTube 下载器</span>
        </router-link>
        <nav class="nav">
          <router-link to="/" class="nav-link">任务列表</router-link>
          <button class="create-task-btn" @click="handleCreateTask">
            <span class="plus-icon">+</span>
            创建任务
          </button>
        </nav>
      </div>
    </header>
    
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 YouTube 下载器. Version 1.0.0</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

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
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  text-decoration: none;
  transition: opacity 0.2s;
}

.logo:hover {
  opacity: 0.8;
}

.logo-icon {
  font-size: 28px;
}

.nav {
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-link {
  color: #6b7280;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #3b82f6;
}

.create-task-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.create-task-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.create-task-btn:active {
  transform: translateY(0);
}

.plus-icon {
  font-size: 18px;
  font-weight: bold;
  line-height: 1;
}

.app-main {
  flex: 1;
  padding: 0;
}

.app-footer {
  background: white;
  border-top: 1px solid #e5e7eb;
  margin-top: 60px;
}

.app-footer .container {
  padding: 24px;
  text-align: center;
}

.app-footer p {
  color: #6b7280;
  font-size: 14px;
}

/* Page transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .logo-text {
    display: none;
  }
}
</style>


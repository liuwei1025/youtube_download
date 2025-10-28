<template>
  <div class="task-list-page">
    <div class="page-header">
      <div>
        <h1>任务管理</h1>
        <p class="subtitle">YouTube 视频下载任务</p>
      </div>
      <BaseButton variant="primary" @click="showCreateForm = !showCreateForm">
        {{ showCreateForm ? '隐藏' : '创建任务' }}
      </BaseButton>
    </div>

    <div v-if="showCreateForm" class="create-form-section">
      <CreateTaskForm 
        :on-success="handleTaskCreated"
        :on-cancel="() => showCreateForm = false"
      />
    </div>

    <div class="filters">
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: currentFilter === null }]"
          @click="setFilter(null)"
        >
          全部 ({{ taskStore.tasks.length }})
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'pending' }]"
          @click="setFilter('pending')"
        >
          等待中 ({{ taskStore.pendingTasks.length }})
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'processing' }]"
          @click="setFilter('processing')"
        >
          处理中 ({{ taskStore.processingTasks.length }})
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'completed' }]"
          @click="setFilter('completed')"
        >
          已完成 ({{ taskStore.completedTasks.length }})
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'failed' }]"
          @click="setFilter('failed')"
        >
          失败 ({{ taskStore.failedTasks.length }})
        </button>
      </div>
      
      <BaseButton size="small" variant="secondary" @click="loadTasks">
        刷新
      </BaseButton>
    </div>

    <div v-if="taskStore.loading" class="loading-container">
      <LoadingSpinner text="加载中..." />
    </div>

    <div v-else-if="taskStore.error" class="error-container">
      <p class="error-text">{{ taskStore.error }}</p>
      <BaseButton variant="primary" @click="loadTasks">重试</BaseButton>
    </div>

    <div v-else-if="filteredTasks.length === 0" class="empty-container">
      <p class="empty-text">暂无任务</p>
    </div>

    <div v-else class="tasks-grid">
      <TaskCard
        v-for="task in filteredTasks"
        :key="task.task_id"
        :task="task"
        @view-details="viewTaskDetail"
        @refresh="loadTasks"
      />
    </div>

    <!-- 浮动操作按钮 -->
    <FloatingActionButton 
      :hidden="showCreateForm"
      title="快速创建任务"
      @click="showCreateForm = true"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { BaseButton, LoadingSpinner, FloatingActionButton } from '@shared/ui'
import { CreateTaskForm } from '@features/task-management'
import { TaskCard } from '@widgets/task-card'
import { useTaskStore } from '@entities/task'

const router = useRouter()
const route = useRoute()
const taskStore = useTaskStore()

const showCreateForm = ref(false)
const currentFilter = ref(null)
let autoRefreshInterval = null

// 监听全局创建任务事件
function handleShowCreateForm() {
  showCreateForm.value = true
  // 滚动到表单
  setTimeout(() => {
    const formSection = document.querySelector('.create-form-section')
    if (formSection) {
      formSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, 100)
}

const filteredTasks = computed(() => {
  if (!currentFilter.value) {
    return taskStore.tasks
  }
  return taskStore.tasks.filter(task => task.status === currentFilter.value)
})

async function loadTasks() {
  try {
    await taskStore.fetchTasks({
      status: currentFilter.value,
      limit: 50
    })
  } catch (err) {
    console.error('Failed to load tasks:', err)
  }
}

function setFilter(status) {
  currentFilter.value = status
  loadTasks()
}

function handleTaskCreated() {
  showCreateForm.value = false
  loadTasks()
}

function viewTaskDetail(task) {
  router.push(`/tasks/${task.task_id}`)
}

// 自动刷新（每10秒）
function startAutoRefresh() {
  autoRefreshInterval = setInterval(() => {
    // 只在有处理中或等待中的任务时自动刷新
    if (taskStore.processingTasks.length > 0 || taskStore.pendingTasks.length > 0) {
      loadTasks()
    }
  }, 10000)
}

function stopAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval)
    autoRefreshInterval = null
  }
}

onMounted(() => {
  loadTasks()
  startAutoRefresh()
  
  // 监听全局创建任务事件
  window.addEventListener('show-create-form', handleShowCreateForm)
  
  // 检查 URL 查询参数
  if (route.query.create === 'true') {
    handleShowCreateForm()
    // 清除查询参数
    router.replace({ path: '/', query: {} })
  }
})

onUnmounted(() => {
  stopAutoRefresh()
  // 移除事件监听
  window.removeEventListener('show-create-form', handleShowCreateForm)
})
</script>

<style scoped>
.task-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  color: #111827;
}

.subtitle {
  margin: 8px 0 0 0;
  color: #6b7280;
  font-size: 16px;
}

.create-form-section {
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.filter-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.filter-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.loading-container,
.error-container,
.empty-container {
  text-align: center;
  padding: 60px 20px;
}

.error-text {
  color: #ef4444;
  margin-bottom: 16px;
  font-size: 16px;
}

.empty-text {
  color: #6b7280;
  font-size: 16px;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
}
</style>


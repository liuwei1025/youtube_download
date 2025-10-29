<template>
  <div class="task-list-page">
    <div class="page-header">
      <div>
        <h1>任务管理</h1>
        <p class="subtitle">YouTube 视频下载任务</p>
      </div>
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
          全部 ({{ total }})
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'pending' }]"
          @click="setFilter('pending')"
        >
          等待中
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'processing' }]"
          @click="setFilter('processing')"
        >
          处理中
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'completed' }]"
          @click="setFilter('completed')"
        >
          已完成
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'failed' }]"
          @click="setFilter('failed')"
        >
          失败
        </button>
      </div>
      
      <BaseButton size="small" variant="secondary" @click="loadTasks">
        刷新
      </BaseButton>
    </div>

    <div v-if="loading" class="loading-container">
      <LoadingSpinner text="加载中..." />
    </div>

    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <BaseButton variant="primary" @click="loadTasks">重试</BaseButton>
    </div>

    <div v-else-if="tasks.length === 0" class="empty-container">
      <p class="empty-text">暂无任务</p>
    </div>

    <div v-else class="table-container">
      <table class="tasks-table">
        <thead>
          <tr>
            <th style="width: 100px;">状态</th>
            <th style="width: 150px;">视频ID</th>
            <th>URL</th>
            <th style="width: 120px;">资源</th>
            <th style="width: 100px;">进度</th>
            <th style="width: 160px;">创建时间</th>
            <th style="width: 160px;">完成时间</th>
            <th style="width: 200px;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.task_id">
            <td>
              <BaseBadge :variant="getStatusVariant(task.status)">
                {{ formatTaskStatus(task.status) }}
              </BaseBadge>
            </td>
            <td>
              <span class="video-id" :title="task.video_id || task.task_id">
                {{ task.video_id || task.task_id.slice(0, 8) }}
              </span>
            </td>
            <td>
              <a :href="task.url" target="_blank" class="task-url" :title="task.url">
                {{ task.url }}
              </a>
            </td>
            <td>
              <div class="resource-tags">
                <BaseBadge v-if="task.download_video" variant="info" size="small">🎬 视频</BaseBadge>
                <BaseBadge v-if="task.download_audio" variant="success" size="small">🎵 音频</BaseBadge>
                <BaseBadge v-if="task.download_subtitles" variant="warning" size="small">📝 字幕</BaseBadge>
              </div>
            </td>
            <td>
              <div class="progress-cell">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: `${task.progress_percentage}%` }"
                  ></div>
                </div>
                <span class="progress-text">{{ task.progress_percentage }}%</span>
              </div>
            </td>
            <td>
              <span class="time-text">{{ formatDateTime(task.created_at, 'MM-DD HH:mm') }}</span>
            </td>
            <td>
              <span v-if="task.completed_at" class="time-text">
                {{ formatDateTime(task.completed_at, 'MM-DD HH:mm') }}
              </span>
              <span v-else class="time-text text-muted">-</span>
            </td>
            <td>
              <div class="action-buttons">
                <BaseButton 
                  size="small" 
                  variant="primary" 
                  @click="viewTaskDetail(task)"
                >
                  详情
                </BaseButton>
                <BaseButton
                  v-if="task.status === 'failed' || task.status === 'cancelled'"
                  size="small"
                  variant="primary"
                  @click="handleRetry(task)"
                >
                  重试
                </BaseButton>
                <BaseButton
                  size="small"
                  variant="danger"
                  @click="handleDelete(task)"
                >
                  删除
                </BaseButton>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页控件 -->
      <div class="pagination">
        <div class="pagination-info">
          显示 {{ offset + 1 }}-{{ Math.min(offset + limit, total) }} / 共 {{ total }} 条
        </div>
        <div class="pagination-controls">
          <BaseButton 
            size="small" 
            variant="secondary"
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
          >
            上一页
          </BaseButton>
          
          <div class="page-numbers">
            <button
              v-for="page in visiblePages"
              :key="page"
              :class="['page-btn', { active: page === currentPage }]"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </div>
          
          <BaseButton 
            size="small" 
            variant="secondary"
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
          >
            下一页
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { BaseButton, BaseBadge, LoadingSpinner } from '@shared/ui'
import { CreateTaskForm } from '@features/task-management'
import { useTaskStore } from '@entities/task'
import { formatDateTime, formatTaskStatus } from '@shared/lib'
import { tasksApi } from '@shared/api'

const router = useRouter()
const route = useRoute()
const taskStore = useTaskStore()

const showCreateForm = ref(false)
const currentFilter = ref(null)
const tasks = ref([])
const total = ref(0)
const limit = ref(10)
const offset = ref(0)
const loading = ref(false)
const error = ref(null)
let autoRefreshInterval = null

// 分页计算
const currentPage = computed(() => Math.floor(offset.value / limit.value) + 1)
const totalPages = computed(() => Math.ceil(total.value / limit.value))

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// 监听全局创建任务事件
function handleShowCreateForm() {
  showCreateForm.value = true
  setTimeout(() => {
    const formSection = document.querySelector('.create-form-section')
    if (formSection) {
      formSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, 100)
}

function getStatusVariant(status) {
  const variants = {
    pending: 'default',
    processing: 'info',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return variants[status] || 'default'
}

async function loadTasks() {
  loading.value = true
  error.value = null
  try {
    const response = await tasksApi.getTasks({
      status: currentFilter.value,
      limit: limit.value,
      offset: offset.value
    })
    
    tasks.value = response.tasks || []
    total.value = response.total || 0
  } catch (err) {
    console.error('Failed to load tasks:', err)
    error.value = err.message
    tasks.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function setFilter(status) {
  currentFilter.value = status
  offset.value = 0 // 重置到第一页
  loadTasks()
}

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  offset.value = (page - 1) * limit.value
  loadTasks()
}

function handleTaskCreated() {
  showCreateForm.value = false
  offset.value = 0
  loadTasks()
}

function viewTaskDetail(task) {
  router.push(`/tasks/${task.task_id}`)
}

async function handleRetry(task) {
  if (!confirm('确定要重试这个任务吗？')) {
    return
  }

  try {
    const result = await taskStore.retryTask(task.task_id)
    alert(`任务已重新创建！新任务ID: ${result.task_id}`)
    loadTasks()
  } catch (err) {
    alert(`重试失败: ${err.message}`)
  }
}

async function handleDelete(task) {
  if (!confirm('确定要删除这个任务及其文件吗？')) {
    return
  }

  try {
    await taskStore.deleteTask(task.task_id, true)
    loadTasks()
  } catch (err) {
    alert(`删除失败: ${err.message}`)
  }
}

// 自动刷新（每10秒）
function startAutoRefresh() {
  autoRefreshInterval = setInterval(() => {
    // 检查是否有进行中或等待中的任务
    const hasActiveTask = tasks.value.some(t => 
      t.status === 'pending' || t.status === 'processing'
    )
    if (hasActiveTask) {
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
  
  window.addEventListener('show-create-form', handleShowCreateForm)
  
  if (route.query.create === 'true') {
    handleShowCreateForm()
    router.replace({ path: '/', query: {} })
  }
})

onUnmounted(() => {
  stopAutoRefresh()
  window.removeEventListener('show-create-form', handleShowCreateForm)
})
</script>

<style scoped>
.task-list-page {
  max-width: 1400px;
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

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tasks-table {
  width: 100%;
  border-collapse: collapse;
}

.tasks-table thead {
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
}

.tasks-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.tasks-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.2s;
}

.tasks-table tbody tr:hover {
  background: #f9fafb;
}

.tasks-table tbody tr:last-child {
  border-bottom: none;
}

.tasks-table td {
  padding: 12px 16px;
  font-size: 13px;
  color: #374151;
}

.video-id {
  display: inline-block;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: monospace;
  color: #6b7280;
}

.task-url {
  display: inline-block;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #3b82f6;
  text-decoration: none;
}

.task-url:hover {
  text-decoration: underline;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  min-width: 40px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  min-width: 35px;
}

.time-text {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.time-text.text-muted {
  color: #9ca3af;
}

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
}

.resource-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.page-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .tasks-table {
    min-width: 900px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}
</style>


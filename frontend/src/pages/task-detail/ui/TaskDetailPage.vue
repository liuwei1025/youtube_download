<template>
  <div class="task-detail-page">
    <div class="page-header">
      <BaseButton variant="secondary" size="small" @click="$router.back()">
        ← 返回
      </BaseButton>
      <h1>任务详情</h1>
    </div>

    <div v-if="taskStore.loading" class="loading-container">
      <LoadingSpinner text="加载中..." />
    </div>

    <div v-else-if="taskStore.error" class="error-container">
      <p class="error-text">{{ taskStore.error }}</p>
      <BaseButton variant="primary" @click="loadTask">重试</BaseButton>
    </div>

    <div v-else-if="task" class="task-content">
      <BaseCard class="task-info-card">
        <div class="info-header">
          <h2>基本信息</h2>
          <BaseBadge :variant="getStatusVariant(task.status)">
            {{ formatTaskStatus(task.status) }}
          </BaseBadge>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <span class="label">任务ID:</span>
            <span class="value">{{ task.task_id }}</span>
          </div>

          <div v-if="task.video_id" class="info-item">
            <span class="label">视频ID:</span>
            <span class="value">{{ task.video_id }}</span>
          </div>

          <div class="info-item">
            <span class="label">视频URL:</span>
            <a :href="task.url" target="_blank" class="link">{{ task.url }}</a>
          </div>

          <div class="info-item">
            <span class="label">创建时间:</span>
            <span class="value">{{ formatDateTime(task.created_at) }}</span>
          </div>

          <div v-if="task.completed_at" class="info-item">
            <span class="label">完成时间:</span>
            <span class="value">{{ formatDateTime(task.completed_at) }}</span>
          </div>

          <div v-if="task.start_time" class="info-item">
            <span class="label">开始时间:</span>
            <span class="value">{{ task.start_time }}</span>
          </div>

          <div v-if="task.end_time" class="info-item">
            <span class="label">结束时间:</span>
            <span class="value">{{ task.end_time }}</span>
          </div>

          <div v-if="task.current_step" class="info-item">
            <span class="label">当前步骤:</span>
            <span class="value">{{ task.current_step }}</span>
          </div>
        </div>

        <div v-if="task.progress" class="progress-section">
          <div class="progress-info">
            <span class="progress-text">{{ task.progress }}</span>
            <span class="progress-percentage">{{ task.progress_percentage }}%</span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: `${task.progress_percentage}%` }"
            ></div>
          </div>
        </div>

        <div v-if="task.error_message" class="error-section">
          <h3>错误信息</h3>
          <p class="error-message">{{ task.error_message }}</p>
          <details v-if="task.error_trace" class="error-trace">
            <summary>查看堆栈信息</summary>
            <pre>{{ task.error_trace }}</pre>
          </details>
        </div>

        <div class="actions">
          <TaskActions :task="task" :on-success="handleActionSuccess" />
        </div>
      </BaseCard>

      <BaseCard v-if="task.files && task.files.length > 0" class="files-card">
        <h2>下载文件 ({{ task.files.length }})</h2>
        <div class="files-list">
          <div v-for="file in task.files" :key="file.file_id" class="file-card">
            <div class="file-icon">
              📄
            </div>
            <div class="file-info">
              <div class="file-header">
                <span class="file-name">{{ file.file_name }}</span>
                <BaseBadge variant="info">{{ formatFileType(file.file_type) }}</BaseBadge>
              </div>
              <div class="file-meta">
                <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
                <span class="file-mime">{{ file.mime_type }}</span>
              </div>
            </div>
            <a 
              :href="getDownloadUrl(task.task_id, file.file_type)"
              :download="file.file_name"
              class="download-button"
            >
              <BaseButton variant="primary" size="small">下载</BaseButton>
            </a>
          </div>
        </div>
      </BaseCard>

      <BaseCard class="logs-card">
        <div class="logs-header">
          <h2>任务日志</h2>
          <BaseButton size="small" variant="secondary" @click="loadLogs">
            刷新日志
          </BaseButton>
        </div>
        
        <div v-if="logsLoading" class="logs-loading">
          <LoadingSpinner text="加载日志..." />
        </div>
        
        <div v-else-if="logs.length === 0" class="logs-empty">
          暂无日志
        </div>
        
        <div v-else class="logs-list">
          <div 
            v-for="log in logs" 
            :key="log.log_id" 
            :class="['log-item', `log-${log.level.toLowerCase()}`]"
          >
            <span class="log-time">{{ formatDateTime(log.created_at, 'HH:mm:ss') }}</span>
            <span class="log-level">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BaseCard, BaseBadge, BaseButton, LoadingSpinner } from '@shared/ui'
import { formatDateTime, formatFileSize, formatTaskStatus, formatFileType } from '@shared/lib'
import { TaskActions } from '@features/task-management'
import { useTaskStore } from '@entities/task'
import { tasksApi } from '@shared/api'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()

const logs = ref([])
const logsLoading = ref(false)
let autoRefreshInterval = null

const task = computed(() => taskStore.currentTask)

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

function getDownloadUrl(taskId, fileType) {
  return tasksApi.getFileDownloadUrl(taskId, fileType)
}

async function loadTask() {
  try {
    await taskStore.fetchTask(route.params.id)
    await loadLogs()
  } catch (err) {
    console.error('Failed to load task:', err)
  }
}

async function loadLogs() {
  if (!route.params.id) return
  
  logsLoading.value = true
  try {
    logs.value = await tasksApi.getTaskLogs(route.params.id, 100)
  } catch (err) {
    console.error('Failed to load logs:', err)
  } finally {
    logsLoading.value = false
  }
}

function handleActionSuccess(action) {
  if (action === 'deleted') {
    router.push('/')
  } else {
    loadTask()
  }
}

function startAutoRefresh() {
  autoRefreshInterval = setInterval(() => {
    if (task.value && (task.value.status === 'pending' || task.value.status === 'processing')) {
      loadTask()
    }
  }, 5000)
}

function stopAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval)
    autoRefreshInterval = null
  }
}

onMounted(() => {
  loadTask()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  taskStore.clearCurrentTask()
})
</script>

<style scoped>
.task-detail-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #111827;
}

.loading-container,
.error-container {
  text-align: center;
  padding: 60px 20px;
}

.error-text {
  color: #ef4444;
  margin-bottom: 16px;
  font-size: 16px;
}

.task-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.task-info-card h2,
.files-card h2,
.logs-card h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
}

.value {
  font-size: 14px;
  color: #111827;
}

.link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
  word-break: break-all;
}

.link:hover {
  text-decoration: underline;
}

.progress-section {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 20px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-text {
  font-size: 14px;
  color: #374151;
}

.progress-percentage {
  font-size: 14px;
  font-weight: 600;
  color: #3b82f6;
}

.progress-bar {
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  transition: width 0.3s;
}

.error-section {
  padding: 16px;
  background: #fee2e2;
  border-radius: 8px;
  margin-bottom: 20px;
}

.error-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #991b1b;
}

.error-message {
  margin: 0 0 12px 0;
  color: #991b1b;
  font-size: 14px;
}

.error-trace {
  margin-top: 12px;
}

.error-trace summary {
  cursor: pointer;
  color: #991b1b;
  font-weight: 500;
  font-size: 13px;
}

.error-trace pre {
  margin-top: 8px;
  padding: 12px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  color: #374151;
}

.actions {
  display: flex;
  gap: 8px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  transition: background 0.2s;
}

.file-card:hover {
  background: #f3f4f6;
}

.file-icon {
  font-size: 32px;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.file-name {
  font-weight: 500;
  color: #111827;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #6b7280;
}

.download-button {
  text-decoration: none;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.logs-loading,
.logs-empty {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.logs-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.log-item {
  display: grid;
  grid-template-columns: 80px 60px 1fr;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 13px;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #6b7280;
  font-family: monospace;
}

.log-level {
  font-weight: 600;
}

.log-info .log-level {
  color: #3b82f6;
}

.log-warning .log-level {
  color: #f59e0b;
}

.log-error .log-level {
  color: #ef4444;
}

.log-message {
  color: #374151;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .log-item {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>


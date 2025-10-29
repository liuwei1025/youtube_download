<template>
  <div class="task-detail-page">
    <div class="page-header">
      <BaseButton variant="secondary" size="small" @click="$router.back()">
        ← 返回
      </BaseButton>
      <div style="display: flex; align-items: center; gap: 12px;">
        <h1>任务详情</h1>
        <span v-if="isAutoRefreshing" class="auto-refresh-indicator" title="正在自动刷新...">🔄</span>
      </div>
    </div>

    <div v-if="taskStore.loading && !isAutoRefreshing" class="loading-container">
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
        
        <!-- 视频播放器 -->
        <div v-if="videoFile" class="media-player-section">
          <h3>视频预览</h3>
          <video 
            :src="`/api/tasks/${task.task_id}/files/${videoFile.file_type}`"
            controls
            class="video-player"
            controlsList="nodownload"
          >
            您的浏览器不支持视频播放。
          </video>
        </div>

        <!-- 音频播放器 -->
        <div v-if="audioFile && !videoFile" class="media-player-section">
          <h3>音频预览</h3>
          <audio 
            :src="`/api/tasks/${task.task_id}/files/${audioFile.file_type}`"
            controls
            class="audio-player"
            controlsList="nodownload"
          >
            您的浏览器不支持音频播放。
          </audio>
        </div>

        <!-- 字幕查看器 -->
        <div v-if="task.download_subtitles" class="subtitle-viewer-section">
          <div class="subtitle-header">
            <h3>字幕内容</h3>
            <BaseButton 
              v-if="subtitleFile" 
              size="small" 
              variant="secondary" 
              @click="loadSubtitles"
            >
              刷新字幕
            </BaseButton>
          </div>
          
          <div v-if="subtitleFile">
            <div v-if="subtitlesLoading" class="subtitles-loading">
              <LoadingSpinner text="加载字幕中..." />
            </div>
            
            <div v-else-if="subtitles.length > 0" class="subtitles-timeline">
              <div 
                v-for="(subtitle, index) in subtitles" 
                :key="index"
                class="subtitle-item"
              >
                <div class="subtitle-time">{{ subtitle.time }}</div>
                <div class="subtitle-text">{{ subtitle.text }}</div>
              </div>
            </div>
            
            <div v-else class="subtitles-empty">
              正在加载字幕...
            </div>
          </div>
          
          <div v-else class="subtitles-empty">
            <div class="subtitle-error">
              <span class="error-icon">⚠️</span>
              <span class="error-text">字幕下载失败或不可用</span>
            </div>
          </div>
        </div>

        <!-- 文件列表 -->
        <div class="files-list-section">
          <h3>所有文件</h3>
          <div class="files-list">
            <div v-for="file in task.files" :key="file.file_id" class="file-card">
              <div>
                <div class="file-icon">
                  {{ getFileIcon(file.file_type) }}
                </div>
                <div class="file-info">
                  <div class="file-header">
                    <span class="file-name">{{ file.file_name }}</span>
                    <div style="display: flex; gap: 6px;">
                      <BaseBadge variant="info">{{ formatFileType(file.file_type) }}</BaseBadge>
                      <BaseBadge 
                        v-if="file.status" 
                        :variant="getFileStatusVariant(file.status)"
                      >
                        {{ formatFileStatus(file.status) }}
                      </BaseBadge>
                    </div>
                  </div>
                  <div class="file-meta">
                    <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
                    <span class="file-mime">{{ file.mime_type }}</span>
                  </div>
                </div>
                <div class="file-actions">
                <!-- 失败状态显示重新下载按钮 -->
                <BaseButton 
                  v-if="file.status === 'failed'" 
                  variant="danger" 
                  size="small"
                  @click="retryFileDownload(file.file_type)"
                  :disabled="file.status === 'processing'"
                >
                  重新下载
                </BaseButton>
                
                <!-- 处理中状态 -->
                <BaseBadge v-if="file.status === 'processing'" variant="info" size="small">
                  下载中...
                </BaseBadge>
                
                <!-- 成功状态显示预览和下载按钮 -->
                <template v-if="file.status === 'completed'">
                  <BaseButton 
                    v-if="canPreview(file.file_type)" 
                    variant="secondary" 
                    size="small"
                    @click="scrollToPreview(file.file_type)"
                  >
                    预览
                  </BaseButton>
                  <a 
                    :href="getDownloadUrl(task.task_id, file.file_type)"
                    :download="file.file_name"
                    class="download-button"
                  >
                    <BaseButton variant="primary" size="small">下载</BaseButton>
                  </a>
                </template>
              </div>
            </div>
              
              <!-- 失败时显示错误信息 -->
              <div v-if="file.status === 'failed' && file.error_message" class="file-error">
                <span class="error-icon">⚠️</span>
                <span class="error-text">{{ file.error_message }}</span>
              </div>
            </div>
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
const subtitles = ref([])
const subtitlesLoading = ref(false)
const isAutoRefreshing = ref(false)
let autoRefreshInterval = null

const task = computed(() => taskStore.currentTask)

// 找到不同类型的文件
const videoFile = computed(() => {
  if (!task.value?.files) return null
  return task.value.files.find(f => 
    f.file_type === 'video_with_subs' || f.file_type === 'video'
  )
})

const audioFile = computed(() => {
  if (!task.value?.files) return null
  return task.value.files.find(f => f.file_type === 'audio')
})

const subtitleFile = computed(() => {
  if (!task.value?.files) return null
  return task.value.files.find(f => f.file_type === 'subtitles')
})

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

function getFileIcon(fileType) {
  const icons = {
    video: '🎬',
    video_with_subs: '🎥',
    audio: '🎵',
    subtitles: '📝'
  }
  return icons[fileType] || '📄'
}

function getFileStatusVariant(status) {
  const variants = {
    pending: 'default',
    processing: 'info',
    completed: 'success',
    failed: 'danger'
  }
  return variants[status] || 'default'
}

function formatFileStatus(status) {
  const labels = {
    pending: '等待中',
    processing: '下载中',
    completed: '已完成',
    failed: '失败'
  }
  return labels[status] || status
}

function canPreview(fileType) {
  return ['video', 'video_with_subs', 'audio', 'subtitles'].includes(fileType)
}

function scrollToPreview(fileType) {
  let selector = ''
  if (fileType === 'video' || fileType === 'video_with_subs') {
    selector = '.video-player'
  } else if (fileType === 'audio') {
    selector = '.audio-player'
  } else if (fileType === 'subtitles') {
    selector = '.subtitle-viewer-section'
  }
  
  if (selector) {
    const element = document.querySelector(selector)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      // 如果是音频或视频，尝试播放
      if (fileType === 'audio' || fileType === 'video' || fileType === 'video_with_subs') {
        setTimeout(() => {
          const mediaElement = element.querySelector('video, audio')
          if (mediaElement) {
            mediaElement.play().catch(err => {
              console.log('自动播放被阻止:', err)
            })
          }
        }, 500)
      }
    } else {
      console.warn(`找不到预览元素: ${selector}`)
    }
  }
}

async function retryFileDownload(fileType) {
  if (!confirm(`确定要重新下载 ${formatFileType(fileType)} 吗？`)) {
    return
  }
  
  try {
    await tasksApi.retryFileDownload(route.params.id, fileType)
    alert('已开始重新下载，请稍后刷新查看结果')
    // 刷新任务数据
    loadTask()
  } catch (err) {
    console.error('重新下载失败:', err)
    alert('重新下载失败: ' + err.message)
  }
}

// 解析VTT字幕格式
function parseVTT(vttContent) {
  const lines = vttContent.split('\n')
  const subtitles = []
  let currentSubtitle = null
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    // 跳过空行和WEBVTT头
    if (!line || line.startsWith('WEBVTT') || line.startsWith('NOTE')) {
      continue
    }
    
    // 时间轴行 (00:00:00.000 --> 00:00:05.000)
    if (line.includes('-->')) {
      const timeMatch = line.match(/(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})/)
      if (timeMatch) {
        if (currentSubtitle) {
          subtitles.push(currentSubtitle)
        }
        currentSubtitle = {
          time: `${timeMatch[1]} --> ${timeMatch[2]}`,
          text: ''
        }
      }
    }
    // 字幕文本
    else if (currentSubtitle) {
      if (currentSubtitle.text) {
        currentSubtitle.text += '\n' + line
      } else {
        currentSubtitle.text = line
      }
    }
  }
  
  // 添加最后一条字幕
  if (currentSubtitle) {
    subtitles.push(currentSubtitle)
  }
  
  return subtitles
}

async function loadSubtitles() {
  if (!subtitleFile.value || !route.params.id) return
  
  subtitlesLoading.value = true
  try {
    const content = await tasksApi.getFileContent(
      route.params.id, 
      subtitleFile.value.file_type
    )
    subtitles.value = parseVTT(content)
  } catch (err) {
    console.error('Failed to load subtitles:', err)
    alert('加载字幕失败: ' + err.message)
  } finally {
    subtitlesLoading.value = false
  }
}

async function loadTask(isAutoRefresh = false) {
  try {
    isAutoRefreshing.value = isAutoRefresh
    await taskStore.fetchTask(route.params.id)
    
    // 自动刷新时只加载日志，避免页面抖动
    if (isAutoRefresh) {
      await loadLogs()
    } else {
      await loadLogs()
      
      // 等待下一个tick，确保computed已更新
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // 自动加载字幕
      if (subtitleFile.value && !subtitlesLoading.value && subtitles.value.length === 0) {
        loadSubtitles()
      }
    }
  } catch (err) {
    console.error('Failed to load task:', err)
  } finally {
    isAutoRefreshing.value = false
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
      loadTask(true)  // 传递true表示自动刷新
    }
  }, 10000)  // 从5秒改为10秒，降低刷新频率
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

.auto-refresh-indicator {
  font-size: 16px;
  animation: spin 2s linear infinite;
  display: inline-block;
  opacity: 0.7;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

.media-player-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.media-player-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.video-player {
  width: 100%;
  max-height: 500px;
  border-radius: 8px;
  background: #000;
}

.audio-player {
  width: 100%;
  border-radius: 8px;
}

.subtitle-viewer-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.subtitle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.subtitle-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.subtitles-loading,
.subtitles-empty {
  text-align: center;
  padding: 40px;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 8px;
}

.subtitle-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
}

.subtitle-error .error-icon {
  font-size: 18px;
}

.subtitle-error .error-text {
  font-size: 14px;
  font-weight: 500;
}

.subtitles-timeline {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.subtitle-item {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.2s;
}

.subtitle-item:hover {
  background: #f3f4f6;
}

.subtitle-item:last-child {
  border-bottom: none;
}

.subtitle-time {
  font-size: 12px;
  font-weight: 600;
  color: #3b82f6;
  font-family: monospace;
  margin-bottom: 6px;
}

.subtitle-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  white-space: pre-wrap;
}

.files-list-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  transition: background 0.2s;
}

.file-card:hover {
  background: #f3f4f6;
}

.file-card > div:first-child {
  display: flex;
  align-items: center;
  gap: 16px;
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

.file-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 13px;
}

.error-icon {
  font-size: 16px;
}

.error-text {
  color: #dc2626;
  flex: 1;
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


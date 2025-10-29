<template>
  <div class="container mx-auto px-6 py-8 max-w-5xl">
    <!-- 页面头部 -->
    <div class="flex items-center gap-4 mb-8">
      <Button variant="outline" size="sm" @click="$router.back()">
        ← 返回
      </Button>
      <div class="flex items-center gap-3">
        <h1 class="text-2xl font-bold">任务详情</h1>
        <RefreshIcon v-if="isAutoRefreshing" :size="20" class="animate-spin text-primary" title="正在自动刷新..." />
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="taskStore.loading && !isAutoRefreshing" class="text-center py-16">
      <LoadingSpinner text="加载中..." />
    </div>

    <!-- 错误状态 -->
    <Card v-else-if="taskStore.error" class="text-center py-16">
      <CardContent>
        <p class="text-destructive mb-4">{{ taskStore.error }}</p>
        <Button variant="default" @click="loadTask">重试</Button>
      </CardContent>
    </Card>

    <!-- 任务内容 -->
    <div v-else-if="task" class="space-y-6">
      <!-- 基本信息卡片 -->
      <Card>
        <CardHeader>
          <div class="flex justify-between items-start">
            <CardTitle>基本信息</CardTitle>
            <Badge :variant="getStatusVariant(task.status)">
              {{ formatTaskStatus(task.status) }}
            </Badge>
          </div>
        </CardHeader>
        <CardContent class="space-y-4">
          <!-- 信息网格 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div class="text-sm font-medium text-muted-foreground mb-1">任务ID:</div>
              <div class="text-sm">{{ task.task_id }}</div>
            </div>

            <div v-if="task.video_id">
              <div class="text-sm font-medium text-muted-foreground mb-1">视频ID:</div>
              <div class="text-sm">{{ task.video_id }}</div>
            </div>

            <div class="md:col-span-2">
              <div class="text-sm font-medium text-muted-foreground mb-1">视频URL:</div>
              <a :href="task.url" target="_blank" class="text-sm text-primary hover:underline break-all">
                {{ task.url }}
              </a>
            </div>

            <div>
              <div class="text-sm font-medium text-muted-foreground mb-1">创建时间:</div>
              <div class="text-sm">{{ formatDateTime(task.created_at) }}</div>
            </div>

            <div v-if="task.completed_at">
              <div class="text-sm font-medium text-muted-foreground mb-1">完成时间:</div>
              <div class="text-sm">{{ formatDateTime(task.completed_at) }}</div>
            </div>

            <div v-if="task.start_time">
              <div class="text-sm font-medium text-muted-foreground mb-1">开始时间:</div>
              <div class="text-sm">{{ task.start_time }}</div>
            </div>

            <div v-if="task.end_time">
              <div class="text-sm font-medium text-muted-foreground mb-1">结束时间:</div>
              <div class="text-sm">{{ task.end_time }}</div>
            </div>

            <div v-if="task.current_step" class="md:col-span-2">
              <div class="text-sm font-medium text-muted-foreground mb-1">当前步骤:</div>
              <div class="text-sm">{{ task.current_step }}</div>
            </div>
          </div>

          <!-- 进度条 -->
          <div v-if="task.progress" class="space-y-2 p-4 bg-muted rounded-lg">
            <div class="flex justify-between text-sm">
              <span>{{ task.progress }}</span>
              <span class="font-semibold text-primary">{{ task.progress_percentage }}%</span>
            </div>
            <Progress :model-value="task.progress_percentage" />
          </div>

          <!-- 错误信息 -->
          <div v-if="task.error_message" class="space-y-3 p-4 bg-destructive/10 border border-destructive/30 rounded-lg">
            <h3 class="text-sm font-semibold text-destructive">错误信息</h3>
            <p class="text-sm text-destructive">{{ task.error_message }}</p>
            <details v-if="task.error_trace" class="text-sm">
              <summary class="cursor-pointer text-destructive font-medium hover:underline">查看堆栈信息</summary>
              <pre class="mt-2 p-3 bg-background rounded text-xs overflow-x-auto">{{ task.error_trace }}</pre>
            </details>
          </div>
        </CardContent>
        <CardFooter class="border-t pt-6">
          <TaskActions :task="task" :on-success="handleActionSuccess" />
        </CardFooter>
      </Card>

      <!-- 下载选项与文件卡片 -->
      <Card v-if="task.files && task.files.length > 0">
        <CardHeader>
          <div class="flex flex-wrap items-center gap-2">
            <CardTitle>下载选项与文件</CardTitle>
            <Badge v-if="task.download_video" class="text-xs bg-primary/10 text-primary border-primary/20 flex items-center gap-1 px-2 py-0.5">
              <VideoIcon :size="12" />
              视频
            </Badge>
            <Badge v-if="task.download_audio" class="text-xs bg-secondary/10 text-secondary border-secondary/20 flex items-center gap-1 px-2 py-0.5">
              <AudioIcon :size="12" />
              音频
            </Badge>
            <Badge v-if="task.download_subtitles" class="text-xs bg-accent/10 text-accent border-accent/20 flex items-center gap-1 px-2 py-0.5">
              <SubtitleIcon :size="12" />
              字幕
            </Badge>
            <Badge v-if="task.burn_subtitles" class="text-xs bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20 flex items-center gap-1 px-2 py-0.5">
              <VideoIcon :size="12" />
              硬编码字幕
            </Badge>
            <span v-if="task.subtitle_langs" class="text-xs text-muted-foreground">
              字幕语言: <span class="font-medium">{{ task.subtitle_langs }}</span>
            </span>
          </div>
        </CardHeader>
        <CardContent class="space-y-6">
          <!-- 视频播放器 - 支持多个视频 -->
          <div v-if="videoFiles.length > 0" class="space-y-4">
            <div 
              v-for="(file, index) in videoFiles" 
              :key="file.file_id"
              class="space-y-2"
              :class="{ 'pt-4 border-t': index > 0 }"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-2">
                  <h3 class="text-base font-semibold">视频预览</h3>
                  <div class="flex items-center gap-2 text-sm text-muted-foreground">
                    <VideoIcon :size="16" />
                    <span class="font-medium">{{ file.file_name }}</span>
                    <Badge variant="info" class="text-xs">{{ formatFileType(file.file_type) }}</Badge>
                  </div>
                </div>
              </div>
              <video 
                :src="`/api/tasks/${task.task_id}/files/${file.file_type}`"
                :data-file-id="file.file_id"
                controls
                class="w-full max-h-[500px] rounded-lg bg-black"
                controlsList="nodownload"
              >
                您的浏览器不支持视频播放。
              </video>
            </div>
          </div>

          <!-- 音频播放器 -->
          <div v-if="audioFile" class="space-y-3 border-t pt-6">
            <div class="flex items-center gap-2">
              <h3 class="text-base font-semibold">音频预览</h3>
              <div class="flex items-center gap-2 text-sm text-muted-foreground">
                <AudioIcon :size="16" />
                <span class="font-medium">{{ audioFile.file_name }}</span>
              </div>
            </div>
            <audio 
              :src="`/api/tasks/${task.task_id}/files/${audioFile.file_type}`"
              controls
              class="w-full rounded-lg"
              controlsList="nodownload"
            >
              您的浏览器不支持音频播放。
            </audio>
          </div>

          <!-- 字幕查看器 -->
          <div v-if="task.download_subtitles" class="space-y-3 border-t pt-6">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <h3 class="text-base font-semibold">字幕内容</h3>
                <div v-if="subtitleFile" class="flex items-center gap-2 text-sm text-muted-foreground">
                  <SubtitleIcon :size="16" />
                  <span class="font-medium">{{ subtitleFile.file_name }}</span>
                </div>
              </div>
              <Button 
                v-if="subtitleFile" 
                size="sm" 
                variant="outline" 
                @click="loadSubtitles"
              >
                刷新字幕
              </Button>
            </div>
            
            <div v-if="subtitleFile">
              <div v-if="subtitlesLoading" class="text-center py-10">
                <LoadingSpinner text="加载字幕中..." />
              </div>
              
              <div v-else-if="subtitles.length > 0" class="max-h-96 overflow-y-auto border rounded-lg bg-muted">
                <div 
                  v-for="(subtitle, index) in subtitles" 
                  :key="index"
                  class="p-3 border-b last:border-b-0 hover:bg-background transition-colors"
                >
                  <div class="text-xs font-semibold text-primary font-mono mb-1">{{ subtitle.time }}</div>
                  <div class="text-sm whitespace-pre-wrap">{{ subtitle.text }}</div>
                </div>
              </div>
              
              <div v-else class="text-center py-10 text-muted-foreground">
                正在加载字幕...
              </div>
            </div>
            
            <div v-else class="flex items-center justify-center gap-2 py-10 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive">
              <span class="text-lg">⚠️</span>
              <span class="text-sm font-medium">字幕下载失败或不可用</span>
            </div>
          </div>

          <!-- 文件列表 -->
          <div class="space-y-3 border-t pt-6">
            <h3 class="text-base font-semibold">所有文件 ({{ task.files.length }})</h3>
            <div class="grid grid-cols-1 gap-3">
              <div 
                v-for="file in task.files" 
                :key="file.file_id" 
                class="p-4 bg-muted hover:bg-muted/80 rounded-lg transition-colors"
              >
                <div class="flex items-start gap-4">
                  <component :is="getFileIconComponent(file.file_type)" :size="28" class="text-primary flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="flex flex-wrap items-center gap-2 mb-1">
                      <span class="font-medium text-sm truncate">{{ file.file_name }}</span>
                      <Badge variant="info">{{ formatFileType(file.file_type) }}</Badge>
                      <Badge 
                        v-if="file.status" 
                        :variant="getFileStatusVariant(file.status)"
                      >
                        {{ formatFileStatus(file.status) }}
                      </Badge>
                    </div>
                    <div class="flex gap-3 text-xs text-muted-foreground">
                      <span>{{ formatFileSize(file.file_size) }}</span>
                      <span>{{ file.mime_type }}</span>
                    </div>
                  </div>
                  <div class="flex gap-2 flex-shrink-0">
                    <!-- 失败状态显示重新下载按钮 -->
                    <Button 
                      v-if="file.status === 'failed'" 
                      variant="destructive" 
                      size="sm"
                      @click="retryFileDownload(file.file_type)"
                      :disabled="file.status === 'processing'"
                    >
                      重新下载
                    </Button>
                    
                    <!-- 处理中状态 -->
                    <Badge v-if="file.status === 'processing'" variant="info">
                      下载中...
                    </Badge>
                    
                    <!-- 成功状态显示预览和下载按钮 -->
                    <template v-if="file.status === 'completed'">
                      <Button 
                        v-if="canPreview(file.file_type)" 
                        variant="outline" 
                        size="sm"
                        @click="scrollToPreview(file.file_type, file.file_id)"
                      >
                        预览
                      </Button>
                      <a 
                        :href="getDownloadUrl(task.task_id, file.file_type)"
                        :download="file.file_name"
                      >
                        <Button variant="default" size="sm">下载</Button>
                      </a>
                    </template>
                  </div>
                </div>
                
                <!-- 失败时显示错误信息 -->
                <div v-if="file.status === 'failed' && file.error_message" class="flex items-center gap-2 mt-3 p-3 bg-destructive/10 border border-destructive/30 rounded text-sm">
                  <span>⚠️</span>
                  <span class="text-destructive flex-1">{{ file.error_message }}</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- 日志卡片 -->
      <Card>
        <CardHeader>
          <div class="flex justify-between items-center">
            <CardTitle>任务日志</CardTitle>
            <Button size="sm" variant="outline" @click="loadLogs">
              刷新日志
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div v-if="logsLoading" class="text-center py-10">
            <LoadingSpinner text="加载日志..." />
          </div>
          
          <div v-else-if="logs.length === 0" class="text-center py-10 text-muted-foreground">
            暂无日志
          </div>
          
          <div v-else class="max-h-96 overflow-y-auto border rounded-lg">
            <div 
              v-for="log in logs" 
              :key="log.log_id" 
              :class="[
                'grid grid-cols-[80px_60px_1fr] gap-3 p-3 border-b last:border-b-0 text-sm',
                log.level.toLowerCase() === 'error' && 'bg-destructive/5',
                log.level.toLowerCase() === 'warning' && 'bg-yellow-50'
              ]"
            >
              <span class="text-muted-foreground font-mono text-xs">{{ formatDateTime(log.created_at, 'HH:mm:ss') }}</span>
              <span 
                :class="[
                  'font-semibold text-xs',
                  log.level.toLowerCase() === 'info' && 'text-blue-600',
                  log.level.toLowerCase() === 'warning' && 'text-yellow-600',
                  log.level.toLowerCase() === 'error' && 'text-destructive'
                ]"
              >
                {{ log.level }}
              </span>
              <span class="text-xs">{{ log.message }}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Badge, Card, CardHeader, CardTitle, CardContent, CardFooter, Progress, VideoIcon, AudioIcon, SubtitleIcon, DownloadIcon, RefreshIcon } from '@components/ui'
import { LoadingSpinner } from '@shared/ui'
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
const videoFiles = computed(() => {
  if (!task.value?.files) return []
  return task.value.files.filter(f => 
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
    pending: 'secondary',
    processing: 'info',
    completed: 'success',
    failed: 'destructive',
    cancelled: 'warning'
  }
  return variants[status] || 'secondary'
}

function getDownloadUrl(taskId, fileType) {
  return tasksApi.getFileDownloadUrl(taskId, fileType)
}

function getFileIconComponent(fileType) {
  const iconMap = {
    video: VideoIcon,
    video_with_subs: VideoIcon,
    audio: AudioIcon,
    subtitles: SubtitleIcon
  }
  return iconMap[fileType] || VideoIcon
}

function getFileStatusVariant(status) {
  const variants = {
    pending: 'secondary',
    processing: 'info',
    completed: 'success',
    failed: 'destructive'
  }
  return variants[status] || 'secondary'
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

function scrollToPreview(fileType, fileId) {
  let element = null
  
  if (fileType === 'video' || fileType === 'video_with_subs') {
    // 使用 data-file-id 属性精确定位视频元素
    if (fileId) {
      element = document.querySelector(`video[data-file-id="${fileId}"]`)
    }
    // 如果没有找到特定的视频，使用第一个视频元素
    if (!element) {
      element = document.querySelector('video')
    }
  } else if (fileType === 'audio') {
    element = document.querySelector('audio')
  } else if (fileType === 'subtitles') {
    // 滚动到字幕区域
    const subtitleSection = document.querySelector('.subtitle-viewer-section')
    if (subtitleSection) {
      element = subtitleSection
    } else {
      // 如果没有找到特定的字幕区域，找到包含字幕的父容器
      const subtitleContainer = Array.from(document.querySelectorAll('h3'))
        .find(h3 => h3.textContent.includes('字幕内容'))
      if (subtitleContainer) {
        element = subtitleContainer.parentElement
      }
    }
  }
  
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    // 如果是音频或视频，尝试播放
    if ((fileType === 'audio' || fileType === 'video' || fileType === 'video_with_subs') && 
        (element.tagName === 'VIDEO' || element.tagName === 'AUDIO')) {
      setTimeout(() => {
        element.play().catch(err => {
          console.log('自动播放被阻止:', err)
        })
      }, 500)
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
    
    if (!line || line.startsWith('WEBVTT') || line.startsWith('NOTE')) {
      continue
    }
    
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
    } else if (currentSubtitle) {
      if (currentSubtitle.text) {
        currentSubtitle.text += '\n' + line
      } else {
        currentSubtitle.text = line
      }
    }
  }
  
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
    
    if (isAutoRefresh) {
      await loadLogs()
    } else {
      await loadLogs()
      await new Promise(resolve => setTimeout(resolve, 100))
      
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
      loadTask(true)
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
  loadTask()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  taskStore.clearCurrentTask()
})
</script>

<template>
  <div class="space-y-6">
    <!-- 基本信息卡片 -->
    <Card class="mb-4">
      <CardHeader>
        <div class="flex justify-between items-start">
          <CardTitle class="text-lg">基本信息</CardTitle>
          <Badge :class="getStatusColor(task.status)">
            {{ formatTaskStatus(task.status) }}
          </Badge>
        </div>
      </CardHeader>
      <CardContent class="space-y-3">
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div class="text-muted-foreground mb-1">任务ID</div>
            <div class="font-mono">{{ task.task_id }}</div>
          </div>
          <div v-if="task.video_id">
            <div class="text-muted-foreground mb-1">视频ID</div>
            <div class="font-mono">{{ task.video_id }}</div>
          </div>
        </div>
        
        <div class="text-sm">
          <div class="text-muted-foreground mb-1">视频URL</div>
          <a :href="task.url" target="_blank" class="text-primary hover:underline break-all text-xs">
            {{ task.url }}
          </a>
        </div>

        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div class="text-muted-foreground mb-1">创建时间</div>
            <div class="text-xs">{{ formatDateTime(task.created_at) }}</div>
          </div>
          <div v-if="task.completed_at">
            <div class="text-muted-foreground mb-1">完成时间</div>
            <div class="text-xs">{{ formatDateTime(task.completed_at) }}</div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 text-sm">
          <div v-if="task.start_time">
            <div class="text-muted-foreground mb-1">片段开始</div>
            <div>{{ task.start_time }}</div>
          </div>
          <div v-if="task.end_time">
            <div class="text-muted-foreground mb-1">片段结束</div>
            <div>{{ task.end_time }}</div>
          </div>
        </div>

        <!-- 进度条（仅在处理中时显示） -->
        <div v-if="task.progress && task.status !== 'completed'" class="space-y-2 p-3 bg-muted/50 rounded-lg">
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">{{ task.progress }}</span>
            <span class="font-semibold text-primary">{{ task.progress_percentage }}%</span>
          </div>
          <Progress :model-value="task.progress_percentage" />
        </div>

        <!-- 错误信息 -->
        <div v-if="task.error_message" class="space-y-2 p-3 bg-destructive/10 border border-destructive/30 rounded-lg">
          <h3 class="text-sm font-semibold text-destructive">错误信息</h3>
          <p class="text-sm text-destructive">{{ task.error_message }}</p>
        </div>
      </CardContent>
    </Card>

    <!-- 下载选项与文件 -->
    <Card class="mb-4">
      <CardHeader>
        <div class="flex flex-wrap items-center gap-2">
          <CardTitle class="text-lg">下载选项与文件</CardTitle>
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
      <CardContent>
        <!-- 下载文件列表 -->
        <div v-if="!loading && task.files && task.files.length > 0" class="space-y-2">
          <h3 class="text-sm font-semibold">所有文件 ({{ task.files.length }})</h3>
          <div class="space-y-2">
            <div 
              v-for="file in task.files" 
              :key="file.file_path || file.file_id"
              class="flex items-start gap-3 p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
            >
              <component :is="getFileIconComponent(file.file_type)" :size="24" class="flex-shrink-0 text-primary" />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <div class="text-sm font-medium truncate">{{ getFileName(file.file_path || file.file_name) }}</div>
                  <Badge v-if="file.status" variant="secondary" class="text-xs">
                    {{ formatFileStatus(file.status) }}
                  </Badge>
                </div>
                <div class="flex gap-2 text-xs text-muted-foreground">
                  <span>{{ file.file_type }}</span>
                  <span v-if="file.file_size">{{ formatFileSize(file.file_size) }}</span>
                </div>
              </div>
              <Button 
                size="sm" 
                variant="outline"
                @click="downloadFile(file)"
                class="flex-shrink-0 flex items-center gap-2"
              >
                <DownloadIcon :size="16" />
                下载
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- 媒体预览 -->
    <Card v-if="shouldShowMediaPreview" class="mb-4">
      <CardHeader>
        <CardTitle class="text-lg">媒体预览</CardTitle>
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
            <div class="flex items-center gap-2">
              <h3 class="text-sm font-semibold">视频预览</h3>
              <div class="flex items-center gap-2 text-sm text-muted-foreground">
                <VideoIcon :size="14" />
                <span class="font-medium text-xs">{{ file.file_name }}</span>
                <Badge variant="secondary" class="text-xs">{{ file.file_type }}</Badge>
              </div>
            </div>
            <video 
              :src="`/api/tasks/${task.task_id}/files/${file.file_type}`"
              :data-file-id="file.file_id"
              controls
              :class="compact ? 'w-full max-h-[300px] rounded-lg bg-black' : 'w-full max-h-[500px] rounded-lg bg-black'"
              controlsList="nodownload"
            >
              您的浏览器不支持视频播放。
            </video>
          </div>
        </div>

        <!-- 音频播放器 -->
        <div v-if="audioFile" class="space-y-3" :class="{ 'border-t pt-6': videoFiles.length > 0 }">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-semibold">音频预览</h3>
            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <AudioIcon :size="14" />
              <span class="font-medium text-xs">{{ audioFile.file_name }}</span>
            </div>
          </div>
          <audio 
            :src="`/api/tasks/${task.task_id}/files/${audioFile.file_type}`"
            controls
            class="w-full"
            controlsList="nodownload"
          >
            您的浏览器不支持音频播放。
          </audio>
        </div>

        <!-- 字幕查看器 -->
        <div v-if="subtitleFile" class="space-y-2" :class="{ 'border-t pt-4': videoFiles.length > 0 || audioFile }">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <h3 class="text-sm font-semibold">字幕内容</h3>
              <div class="flex items-center gap-2 text-sm text-muted-foreground">
                <SubtitleIcon :size="14" />
                <span class="font-medium text-xs">{{ subtitleFile.file_name }}</span>
              </div>
            </div>
            <div class="flex gap-2">
              <Button 
                size="sm" 
                variant="outline" 
                @click="copyAllSubtitles"
                :disabled="subtitles.length === 0"
              >
                复制全部
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                @click="loadSubtitles"
                :disabled="subtitlesLoading"
              >
                {{ subtitlesLoading ? '加载中...' : '刷新字幕' }}
              </Button>
            </div>
          </div>
          
          <div v-if="subtitlesLoading" class="text-center py-6">
            <LoadingSpinner text="加载字幕中..." />
          </div>
          
          <div v-else-if="subtitles.length > 0" class="max-h-64 overflow-y-auto border rounded-lg bg-muted/30">
            <div 
              v-for="(subtitle, index) in subtitles" 
              :key="index"
              class="group p-2 border-b last:border-b-0 hover:bg-muted/50 transition-colors"
            >
              <div class="flex justify-between items-start gap-2">
                <div class="flex-1">
                  <div class="text-xs font-semibold text-primary font-mono mb-1">{{ subtitle.time }}</div>
                  <div class="text-sm whitespace-pre-wrap">{{ subtitle.text }}</div>
                </div>
                <Button 
                  size="sm" 
                  variant="ghost" 
                  class="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                  @click="copySubtitle(subtitle.text)"
                >
                  复制
                </Button>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-6 text-sm text-muted-foreground">
            点击"刷新字幕"加载字幕内容
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- 加载状态 -->
    <Card v-if="loading" class="mb-4">
      <CardContent class="py-10 text-center">
        <LoadingSpinner text="加载任务详情..." />
      </CardContent>
    </Card>

    <!-- 任务操作 -->
    <Card :class="compact ? 'sticky bottom-0 bg-background/95 backdrop-blur' : ''">
      <CardContent class="p-4">
        <div class="flex justify-between items-center">
          <span class="text-sm text-muted-foreground">任务操作</span>
          <TaskActions :task="task" :on-success="handleTaskAction" />
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Button, Badge, Card, CardContent, CardHeader, CardTitle, Progress, VideoIcon, AudioIcon, SubtitleIcon, DownloadIcon } from '@components/ui'
import { LoadingSpinner } from '@shared/ui'
import { TaskActions } from '@features/task-management'
import { formatDateTime, formatTaskStatus, formatFileSize } from '@shared/lib'
import { tasksApi } from '@shared/api'

const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  },
  mediaReady: {
    type: Boolean,
    default: true
  },
  onAction: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['action'])

const subtitles = ref([])
const subtitlesLoading = ref(false)

// 找到不同类型的文件
const videoFiles = computed(() => {
  if (!props.task?.files) return []
  return props.task.files.filter(f => 
    f.file_type === 'video_with_subs' || f.file_type === 'video'
  )
})

const audioFile = computed(() => {
  if (!props.task?.files) return null
  return props.task.files.find(f => f.file_type === 'audio')
})

const subtitleFile = computed(() => {
  if (!props.task?.files) return null
  return props.task.files.find(f => f.file_type === 'subtitles')
})

const shouldShowMediaPreview = computed(() => {
  return props.mediaReady && !props.loading && (videoFiles.value.length > 0 || audioFile.value || subtitleFile.value)
})

function getStatusColor(status) {
  const colors = {
    pending: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20',
    processing: 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20',
    completed: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20',
    failed: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20',
    cancelled: 'bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20'
  }
  return colors[status] || 'bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20'
}

function getFileName(filePath) {
  return filePath ? filePath.split('/').pop() : ''
}

function downloadFile(file) {
  if (!props.task) {
    console.error('无法下载：任务信息不存在')
    return
  }
  
  // 使用正确的API端点：/api/tasks/{task_id}/files/{file_type}
  const baseUrl = import.meta.env.VITE_API_URL || ''
  const url = `${baseUrl}/api/tasks/${props.task.task_id}/files/${file.file_type}`
  
  // 创建临时链接并触发下载
  const link = document.createElement('a')
  link.href = url
  link.download = file.file_name || getFileName(file.file_path)
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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

function formatFileStatus(status) {
  const labels = {
    pending: '等待中',
    processing: '下载中',
    completed: '已完成',
    failed: '失败'
  }
  return labels[status] || status
}

// 解析VTT字幕格式
function parseVTT(vttContent) {
  const lines = vttContent.split('\n')
  const result = []
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
          result.push(currentSubtitle)
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
    result.push(currentSubtitle)
  }
  
  return result
}

async function loadSubtitles() {
  if (!subtitleFile.value || !props.task) return
  
  subtitlesLoading.value = true
  try {
    const content = await tasksApi.getFileContent(
      props.task.task_id, 
      subtitleFile.value.file_type
    )
    subtitles.value = parseVTT(content)
  } catch (err) {
    console.error('Failed to load subtitles:', err)
    subtitles.value = []
  } finally {
    subtitlesLoading.value = false
  }
}

function copySubtitle(text) {
  navigator.clipboard.writeText(text).then(() => {
    console.log('字幕已复制')
  }).catch(err => {
    console.error('复制失败:', err)
  })
}

function copyAllSubtitles() {
  if (subtitles.value.length === 0) return
  
  const allText = subtitles.value.map(s => `${s.time}\n${s.text}`).join('\n\n')
  navigator.clipboard.writeText(allText).then(() => {
    alert('所有字幕已复制到剪贴板')
  }).catch(err => {
    console.error('复制失败:', err)
    alert('复制失败，请手动复制')
  })
}

function handleTaskAction(action) {
  if (props.onAction) {
    props.onAction(action)
  }
  emit('action', action)
  
  // 如果有字幕文件，自动加载
  if (action === 'regenerated' && subtitleFile.value) {
    nextTick(() => {
      loadSubtitles()
    })
  }
}

// 监听任务变化，如果有字幕文件自动加载
watch(() => props.task, async (newTask) => {
  if (newTask?.files?.some(f => f.file_type === 'subtitles') && !subtitlesLoading.value && subtitles.value.length === 0) {
    await nextTick()
    loadSubtitles()
  }
}, { immediate: true })
</script>


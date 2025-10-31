<template>
  <div class="container mx-auto px-6 py-8 max-w-7xl">
    <!-- 创建任务 Drawer -->
    <Drawer :open="showCreateForm" @update:open="showCreateForm = $event" direction="right" :dismissible="true" :modal="true">
      <DrawerContent class="h-full w-full sm:w-[600px]" :disable-outside-pointer-events="true">
        <DrawerHeader>
          <DrawerTitle>创建下载任务</DrawerTitle>
          <DrawerDescription>填写 YouTube 视频信息和下载选项</DrawerDescription>
        </DrawerHeader>
        
        <div class="overflow-y-auto flex-1 px-6 pb-6">
          <CreateTaskForm 
            :on-success="handleTaskCreated"
            :on-cancel="() => showCreateForm = false"
          />
        </div>
      </DrawerContent>
    </Drawer>

    <!-- 过滤器和操作 -->
    <Card class="mb-6 border-primary/20">
      <CardContent class="p-4">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div class="flex flex-wrap gap-2">
            <Button
              :variant="currentFilter === null ? 'default' : 'outline'"
              size="sm"
              @click="setFilter(null)"
              class="flex items-center gap-2"
            >
              <ListIcon :size="16" />
              全部
            </Button>
            <Button
              :variant="currentFilter === 'pending' ? 'default' : 'outline'"
              size="sm"
              @click="setFilter('pending')"
              class="flex items-center gap-2"
            >
              <ClockIcon :size="16" />
              等待中
            </Button>
            <Button
              :variant="currentFilter === 'processing' ? 'default' : 'outline'"
              size="sm"
              @click="setFilter('processing')"
              class="flex items-center gap-2"
            >
              <SettingsIcon :size="16" />
              处理中
            </Button>
            <Button
              :variant="currentFilter === 'completed' ? 'default' : 'outline'"
              size="sm"
              @click="setFilter('completed')"
              class="flex items-center gap-2"
            >
              <CheckIcon :size="16" />
              已完成
            </Button>
            <Button
              :variant="currentFilter === 'failed' ? 'default' : 'outline'"
              size="sm"
              @click="setFilter('failed')"
              class="flex items-center gap-2"
            >
              <XIcon :size="16" />
              失败
            </Button>
          </div>
          
          <div class="flex gap-2">
            <Button size="sm" variant="outline" @click="loadTasks" class="flex items-center gap-2">
              <RefreshIcon :size="16" />
              刷新
            </Button>
            <Button size="sm" variant="default" @click="showCreateForm = true" class="flex items-center gap-2">
              <PlusIcon :size="16" />
              新建任务
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-16">
      <LoadingSpinner text="加载中..." />
    </div>

    <!-- 错误状态 -->
    <Card v-else-if="error" class="text-center py-16">
      <CardContent>
        <p class="text-destructive mb-4">{{ error }}</p>
        <Button variant="default" @click="loadTasks">重试</Button>
      </CardContent>
    </Card>

    <!-- 空状态 -->
    <Card v-else-if="tasks.length === 0" class="text-center py-16">
      <CardContent>
        <p class="text-muted-foreground">暂无任务</p>
      </CardContent>
    </Card>

    <!-- 任务表格 -->
    <Card v-else>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead class="w-[100px]">状态</TableHead>
            <TableHead class="w-[130px]">视频ID</TableHead>
            <TableHead class="w-[120px]">资源</TableHead>
            <TableHead class="w-[100px]">进度</TableHead>
            <TableHead class="w-[160px]">创建时间</TableHead>
            <TableHead class="w-[160px]">完成时间</TableHead>
            <TableHead class="w-[200px]">操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="task in tasks" :key="task.task_id">
            <TableCell>
              <Badge :class="getStatusColor(task.status)">
                {{ formatTaskStatus(task.status) }}
              </Badge>
            </TableCell>
            <TableCell>
              <a 
                :href="task.url" 
                target="_blank" 
                class="font-mono text-xs text-primary hover:underline" 
                :title="task.url"
              >
                {{ getVideoIdFromTask(task) }}
              </a>
            </TableCell>
            <TableCell>
              <div class="flex gap-2 whitespace-nowrap">
                <VideoIcon v-if="task.download_video" :size="18" class="text-primary" title="视频" />
                <AudioIcon v-if="task.download_audio" :size="18" class="text-secondary" title="音频" />
                <SubtitleIcon v-if="task.download_subtitles" :size="18" class="text-accent" title="字幕" />
              </div>
            </TableCell>
            <TableCell>
              <div class="flex items-center gap-2">
                <Progress :model-value="task.progress_percentage" class="w-16" />
                <span class="text-xs text-muted-foreground whitespace-nowrap">{{ task.progress_percentage }}%</span>
              </div>
            </TableCell>
            <TableCell>
              <span class="text-xs text-muted-foreground whitespace-nowrap">
                {{ formatDateTime(task.created_at, 'MM-DD HH:mm') }}
              </span>
            </TableCell>
            <TableCell>
              <span v-if="task.completed_at" class="text-xs text-muted-foreground whitespace-nowrap">
                {{ formatDateTime(task.completed_at, 'MM-DD HH:mm') }}
              </span>
              <span v-else class="text-xs text-muted-foreground">-</span>
            </TableCell>
            <TableCell>
              <div class="flex gap-2">
                <Button 
                  size="sm" 
                  variant="outline" 
                  @click="viewTaskDetail(task)"
                >
                  查看
                </Button>
                <Button
                  v-if="task.status === 'failed' || task.status === 'cancelled'"
                  size="sm"
                  variant="secondary"
                  @click="handleRetry(task)"
                >
                  重试
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  class="text-destructive hover:text-destructive hover:bg-destructive/10"
                  @click="handleDelete(task)"
                >
                  删除
                </Button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>

      <!-- 分页控件 -->
      <div class="flex flex-col sm:flex-row justify-between items-center gap-4 p-4 border-t">
        <div class="text-sm text-muted-foreground">
          显示 {{ offset + 1 }}-{{ Math.min(offset + limit, total) }} / 共 {{ total }} 条
        </div>
        <div class="flex items-center gap-3">
          <Button 
            size="sm" 
            variant="outline"
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
          >
            上一页
          </Button>
          
          <div class="flex gap-1">
            <Button
              v-for="page in visiblePages"
              :key="page"
              size="sm"
              :variant="page === currentPage ? 'default' : 'outline'"
              @click="goToPage(page)"
              class="min-w-[2rem]"
            >
              {{ page }}
            </Button>
          </div>
          
          <Button 
            size="sm" 
            variant="outline"
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
          >
            下一页
          </Button>
        </div>
      </div>
    </Card>

    <!-- 任务详情 Drawer -->
    <Drawer :open="drawerOpen" @update:open="drawerOpen = $event" direction="right" :dismissible="true" :modal="true">
      <DrawerContent class="h-full w-full sm:w-[600px]" :disable-outside-pointer-events="true">
        <DrawerHeader>
          <DrawerTitle>任务详情</DrawerTitle>
          <DrawerDescription v-if="selectedTask">
            任务 ID: {{ selectedTask.task_id }}
          </DrawerDescription>
        </DrawerHeader>
        
        <div v-if="selectedTask" class="overflow-y-auto flex-1 px-6 pb-6">
          <TaskDetailContent
            :task="selectedTask"
            :loading="taskDetailLoading"
            :compact="true"
            :media-ready="mediaResourcesReady"
            :on-action="handleTaskAction"
          />
        </div>
      </DrawerContent>
    </Drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Button, Badge, Card, CardContent, CardHeader, CardTitle, Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Progress, Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerDescription, VideoIcon, AudioIcon, SubtitleIcon, DownloadIcon, RefreshIcon, PlusIcon, CheckIcon, XIcon, ClockIcon, SettingsIcon, ListIcon } from '@components/ui'
import { LoadingSpinner } from '@shared/ui'
import { CreateTaskForm, TaskActions } from '@features/task-management'
import { TaskDetailContent } from '@features/task-detail'
import { useTaskStore } from '@entities/task'
import { formatDateTime, formatTaskStatus, formatFileSize } from '@shared/lib'
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
const drawerOpen = ref(false)
const selectedTask = ref(null)
const taskDetailLoading = ref(false)
const mediaResourcesReady = ref(false) // 控制媒体资源是否可以加载
let autoRefreshInterval = null

// 监听 Drawer 打开状态,延迟加载媒体资源
watch(drawerOpen, async (isOpen) => {
  if (isOpen) {
    // Drawer 打开时,延迟一段时间后再加载媒体资源,避免渲染冲突
    mediaResourcesReady.value = false
    await nextTick()
    // 等待 Drawer 动画完成 (通常为 300-500ms)
    setTimeout(() => {
      if (drawerOpen.value) { // 确保 Drawer 仍然是打开状态
        mediaResourcesReady.value = true
      }
    }, 400)
  } else {
    // Drawer 关闭时,立即重置状态
    mediaResourcesReady.value = false
  }
})

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
    pending: 'secondary',
    processing: 'default',
    completed: 'default',
    failed: 'destructive',
    cancelled: 'secondary'
  }
  return variants[status] || 'secondary'
}

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

function handleTaskAction(action) {
  // 关闭 drawer
  drawerOpen.value = false
  selectedTask.value = null
  
  // 刷新任务列表
  if (action === 'deleted' || action === 'retried' || action === 'regenerated') {
    loadTasks()
  }
}

function getVideoIdFromTask(task) {
  // 如果有 video_id 字段，直接返回
  if (task.video_id) {
    return task.video_id
  }
  
  // 从 URL 中提取视频ID
  try {
    const url = task.url
    
    // 匹配 youtube.com/watch?v=VIDEO_ID
    const watchMatch = url.match(/[?&]v=([^&]+)/)
    if (watchMatch) {
      return watchMatch[1]
    }
    
    // 匹配 youtu.be/VIDEO_ID
    const shortMatch = url.match(/youtu\.be\/([^?]+)/)
    if (shortMatch) {
      return shortMatch[1]
    }
    
    // 如果无法提取，返回任务ID的前8位
    return task.task_id.slice(0, 8)
  } catch (e) {
    return task.task_id.slice(0, 8)
  }
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

async function viewTaskDetail(task) {
  // 先显示基本信息
  selectedTask.value = task
  drawerOpen.value = true
  taskDetailLoading.value = true
  
  // 然后加载完整的任务详情
  try {
    const fullTask = await tasksApi.getTask(task.task_id)
    // 只在 drawer 仍然打开且是同一个任务时更新
    if (drawerOpen.value && selectedTask.value?.task_id === task.task_id) {
      selectedTask.value = fullTask
    }
  } catch (err) {
    console.error('Failed to load task details:', err)
  } finally {
    taskDetailLoading.value = false
  }
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

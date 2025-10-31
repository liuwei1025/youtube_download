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
    <div v-if="taskDetailLoading && !isAutoRefreshing" class="text-center py-16">
      <LoadingSpinner text="加载任务详情..." />
    </div>

    <!-- 错误状态 -->
    <Card v-else-if="error" class="text-center py-16">
      <CardContent>
        <p class="text-destructive mb-4">{{ error }}</p>
        <Button variant="default" @click="loadTask">重试</Button>
      </CardContent>
    </Card>

    <!-- 任务详情内容 -->
    <TaskDetailContent
      v-else-if="task"
      :task="task"
      :loading="taskDetailLoading"
      :compact="false"
      :media-ready="true"
      :on-action="handleTaskAction"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Button, Badge, Card, CardContent, RefreshIcon } from '@components/ui'
import { LoadingSpinner } from '@shared/ui'
import { TaskDetailContent } from '@features/task-detail'
import { tasksApi } from '@shared/api'

const router = useRouter()
const route = useRoute()

const task = ref(null)
const taskDetailLoading = ref(false)
const error = ref(null)
const isAutoRefreshing = ref(false)
let autoRefreshInterval = null

function handleTaskAction(action) {
  if (action === 'deleted') {
    // 删除后返回任务列表
    router.push('/')
  } else {
    // 其他操作后刷新任务详情
    loadTask()
  }
}

async function loadTask(isAutoRefresh = false) {
  if (!route.params.id) {
    error.value = '任务ID不存在'
    return
  }

  taskDetailLoading.value = true
  error.value = null
  isAutoRefreshing.value = isAutoRefresh

  try {
    const fullTask = await tasksApi.getTask(route.params.id)
    task.value = fullTask
  } catch (err) {
    console.error('Failed to load task details:', err)
    error.value = err.message || '加载任务详情失败'
  } finally {
    taskDetailLoading.value = false
    isAutoRefreshing.value = false
  }
}

// 自动刷新（每10秒）
function startAutoRefresh() {
  autoRefreshInterval = setInterval(() => {
    // 检查任务是否在进行中或等待中
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
})
</script>

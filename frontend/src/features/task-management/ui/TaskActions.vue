<template>
  <div class="flex gap-2">
    <Button
      v-if="task.status === 'pending' || task.status === 'processing'"
      size="sm"
      variant="outline"
      @click="handleCancel"
      :disabled="loading"
    >
      取消
    </Button>
    
    <Button
      v-if="task.status === 'failed' || task.status === 'cancelled'"
      size="sm"
      variant="default"
      @click="handleRetry"
      :disabled="loading"
    >
      重试
    </Button>
    
    <Button
      v-if="task.status === 'completed'"
      size="sm"
      variant="default"
      @click="handleRegenerate"
      :disabled="loading"
    >
      重新生成
    </Button>
    
    <Button
      size="sm"
      variant="destructive"
      @click="handleDelete"
      :disabled="loading"
    >
      删除
    </Button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button } from '@components/ui'
import { useTaskStore } from '@entities/task'

const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  onSuccess: {
    type: Function,
    default: null
  }
})

const taskStore = useTaskStore()
const loading = ref(false)

async function handleCancel() {
  if (!confirm('确定要取消这个任务吗？')) {
    return
  }

  loading.value = true
  try {
    await taskStore.cancelTask(props.task.task_id)
    if (props.onSuccess) {
      props.onSuccess('cancelled')
    }
  } catch (err) {
    alert(`取消失败: ${err.message}`)
  } finally {
    loading.value = false
  }
}

async function handleRetry() {
  if (!confirm('确定要重试这个任务吗？')) {
    return
  }

  loading.value = true
  try {
    const result = await taskStore.retryTask(props.task.task_id)
    alert(`任务已重新创建！新任务ID: ${result.task_id}`)
    if (props.onSuccess) {
      props.onSuccess('retried')
    }
  } catch (err) {
    alert(`重试失败: ${err.message}`)
  } finally {
    loading.value = false
  }
}

async function handleRegenerate() {
  if (!confirm('确定要重新生成这个任务吗？这将创建一个新任务使用相同的配置。')) {
    return
  }

  loading.value = true
  try {
    const result = await taskStore.retryTask(props.task.task_id)
    alert(`任务已重新创建！新任务ID: ${result.task_id}`)
    if (props.onSuccess) {
      props.onSuccess('regenerated')
    }
  } catch (err) {
    alert(`重新生成失败: ${err.message}`)
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!confirm('确定要删除这个任务及其文件吗？')) {
    return
  }

  loading.value = true
  try {
    await taskStore.deleteTask(props.task.task_id, true)
    if (props.onSuccess) {
      props.onSuccess('deleted')
    }
  } catch (err) {
    alert(`删除失败: ${err.message}`)
  } finally {
    loading.value = false
  }
}
</script>


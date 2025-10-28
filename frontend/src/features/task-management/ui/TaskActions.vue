<template>
  <div class="task-actions">
    <BaseButton
      v-if="task.status === 'pending' || task.status === 'processing'"
      size="small"
      variant="warning"
      @click="handleCancel"
      :disabled="loading"
    >
      取消
    </BaseButton>
    
    <BaseButton
      size="small"
      variant="danger"
      @click="handleDelete"
      :disabled="loading"
    >
      删除
    </BaseButton>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BaseButton } from '@shared/ui'
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

<style scoped>
.task-actions {
  display: flex;
  gap: 8px;
}
</style>


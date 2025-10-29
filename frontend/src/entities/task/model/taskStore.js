import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tasksApi } from '@shared/api'

export const useTaskStore = defineStore('task', () => {
  // State
  const tasks = ref([])
  const currentTask = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const pendingTasks = computed(() => 
    tasks.value.filter(t => t.status === 'pending')
  )
  
  const processingTasks = computed(() => 
    tasks.value.filter(t => t.status === 'processing')
  )
  
  const completedTasks = computed(() => 
    tasks.value.filter(t => t.status === 'completed')
  )
  
  const failedTasks = computed(() => 
    tasks.value.filter(t => t.status === 'failed')
  )

  // Actions
  async function fetchTasks(params = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await tasksApi.getTasks(params)
      // 确保 data 是数组
      tasks.value = Array.isArray(data) ? data : []
      return data
    } catch (err) {
      error.value = err.message
      // 出错时设置为空数组，避免 filter 错误
      tasks.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTask(taskId) {
    loading.value = true
    error.value = null
    try {
      const data = await tasksApi.getTask(taskId)
      currentTask.value = data
      
      // 更新列表中的任务
      const index = tasks.value.findIndex(t => t.task_id === taskId)
      if (index !== -1) {
        tasks.value[index] = data
      }
      
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTask(taskData) {
    loading.value = true
    error.value = null
    try {
      const data = await tasksApi.createTask(taskData)
      // 刷新任务列表
      await fetchTasks()
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function cancelTask(taskId) {
    try {
      await tasksApi.cancelTask(taskId)
      // 刷新任务详情
      await fetchTask(taskId)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function retryTask(taskId) {
    loading.value = true
    error.value = null
    try {
      const data = await tasksApi.retryTask(taskId)
      // 刷新任务列表
      await fetchTasks()
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteTask(taskId, deleteFiles = true) {
    try {
      await tasksApi.deleteTask(taskId, deleteFiles)
      // 从列表中移除
      tasks.value = tasks.value.filter(t => t.task_id !== taskId)
      if (currentTask.value?.task_id === taskId) {
        currentTask.value = null
      }
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  function clearCurrentTask() {
    currentTask.value = null
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    tasks,
    currentTask,
    loading,
    error,
    
    // Getters
    pendingTasks,
    processingTasks,
    completedTasks,
    failedTasks,
    
    // Actions
    fetchTasks,
    fetchTask,
    createTask,
    cancelTask,
    retryTask,
    deleteTask,
    clearCurrentTask,
    clearError
  }
})


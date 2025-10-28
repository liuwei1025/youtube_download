import { apiClient } from './client'

/**
 * 任务相关 API
 */
export const tasksApi = {
  /**
   * 获取任务列表
   */
  getTasks(params = {}) {
    return apiClient.get('/tasks', { params })
  },

  /**
   * 获取任务详情
   */
  getTask(taskId) {
    return apiClient.get(`/tasks/${taskId}`)
  },

  /**
   * 创建下载任务
   */
  createTask(data) {
    return apiClient.post('/download', data)
  },

  /**
   * 获取任务日志
   */
  getTaskLogs(taskId, limit = 100) {
    return apiClient.get(`/tasks/${taskId}/logs`, { params: { limit } })
  },

  /**
   * 获取任务文件列表
   */
  getTaskFiles(taskId) {
    return apiClient.get(`/tasks/${taskId}/files`)
  },

  /**
   * 获取文件下载URL
   */
  getFileDownloadUrl(taskId, fileType) {
    return `/api/tasks/${taskId}/files/${fileType}`
  },

  /**
   * 取消任务
   */
  cancelTask(taskId) {
    return apiClient.post(`/tasks/${taskId}/cancel`)
  },

  /**
   * 删除任务
   */
  deleteTask(taskId, deleteFiles = true) {
    return apiClient.delete(`/tasks/${taskId}`, {
      params: { delete_files: deleteFiles }
    })
  },

  /**
   * 获取统计信息
   */
  getStats() {
    return apiClient.get('/stats')
  },

  /**
   * 健康检查
   */
  healthCheck() {
    return apiClient.get('/health')
  }
}


import { apiClient } from './client'

/**
 * 任务相关 API
 */
export const tasksApi = {
  /**
   * 获取任务列表
   */
  getTasks(params = {}) {
    return apiClient.get('/api/tasks', { params })
  },

  /**
   * 获取任务详情
   */
  getTask(taskId) {
    return apiClient.get(`/api/tasks/${taskId}`)
  },

  /**
   * 创建下载任务
   */
  createTask(data) {
    return apiClient.post('/api/download', data)
  },

  /**
   * 获取任务日志
   */
  getTaskLogs(taskId, limit = 100) {
    return apiClient.get(`/api/tasks/${taskId}/logs`, { params: { limit } })
  },

  /**
   * 获取任务文件列表
   */
  getTaskFiles(taskId) {
    return apiClient.get(`/api/tasks/${taskId}/files`)
  },

  /**
   * 获取文件下载URL
   */
  getFileDownloadUrl(taskId, fileType) {
    return `/api/tasks/${taskId}/files/${fileType}`
  },

  /**
   * 获取文件内容（用于字幕文件）
   */
  async getFileContent(taskId, fileType) {
    const response = await fetch(`/api/tasks/${taskId}/files/${fileType}`)
    return await response.text()
  },

  /**
   * 取消任务
   */
  cancelTask(taskId) {
    return apiClient.post(`/api/tasks/${taskId}/cancel`)
  },

  /**
   * 重试任务
   */
  retryTask(taskId) {
    return apiClient.post(`/api/tasks/${taskId}/retry`)
  },

  /**
   * 删除任务
   */
  deleteTask(taskId, deleteFiles = true) {
    return apiClient.delete(`/api/tasks/${taskId}`, {
      params: { delete_files: deleteFiles }
    })
  },

  /**
   * 获取统计信息
   */
  getStats() {
    return apiClient.get('/api/stats')
  },

  /**
   * 健康检查
   */
  healthCheck() {
    return apiClient.get('/api/health')
  },

  /**
   * 重新下载单个文件
   */
  retryFileDownload(taskId, fileType) {
    return apiClient.post(`/api/tasks/${taskId}/files/${fileType}/retry`)
  }
}


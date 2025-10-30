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
   * 获取完整字幕内容
   */
  async getFullSubtitleContent(taskId, subtitleFileName) {
    // 从截取的字幕文件名中提取语言代码
    // 例如: subtitles_00_00-00_30.en.vtt -> en
    const match = subtitleFileName.match(/\.([a-z]{2,3})\.vtt$/i)
    const lang = match ? match[1] : 'en'

    // 构造完整字幕文件名
    const fullSubtitleFileName = `subtitles_full.${lang}.vtt`

    // 直接通过构造的URL获取完整字幕
    // 注意：这需要后端支持通过文件名访问，或者我们使用特殊的file_type
    const response = await fetch(`/api/tasks/${taskId}/files/subtitles_full/${lang}`)
    if (!response.ok) {
      throw new Error('获取完整字幕失败')
    }
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


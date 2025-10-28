<template>
  <BaseCard hover class="task-card">
    <div class="task-header">
      <div class="task-info">
        <h3 class="task-title">{{ task.video_id || task.task_id.slice(0, 8) }}</h3>
        <a v-if="task.url" :href="task.url" target="_blank" class="task-url">
          {{ task.url }}
        </a>
      </div>
      <BaseBadge :variant="getStatusVariant(task.status)">
        {{ formatTaskStatus(task.status) }}
      </BaseBadge>
    </div>

    <div class="task-details">
      <div class="detail-item">
        <span class="label">创建时间:</span>
        <span class="value">{{ formatDateTime(task.created_at) }}</span>
      </div>
      
      <div v-if="task.completed_at" class="detail-item">
        <span class="label">完成时间:</span>
        <span class="value">{{ formatDateTime(task.completed_at) }}</span>
      </div>

      <div v-if="task.progress" class="detail-item">
        <span class="label">进度:</span>
        <span class="value">{{ task.progress }}</span>
      </div>

      <div v-if="task.progress_percentage !== null" class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${task.progress_percentage}%` }"
        ></div>
      </div>
    </div>

    <div v-if="task.files && task.files.length > 0" class="task-files">
      <div class="files-header">文件 ({{ task.files.length }})</div>
      <div class="files-list">
        <div v-for="file in task.files" :key="file.file_id" class="file-item">
          <span class="file-info">
            <BaseBadge variant="info">{{ formatFileType(file.file_type) }}</BaseBadge>
            <span class="file-name">{{ file.file_name }}</span>
            <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
          </span>
          <a 
            :href="getDownloadUrl(task.task_id, file.file_type)"
            :download="file.file_name"
            class="download-link"
          >
            下载
          </a>
        </div>
      </div>
    </div>

    <div v-if="task.error_message" class="task-error">
      <strong>错误:</strong> {{ task.error_message }}
    </div>

    <div class="task-footer">
      <BaseButton 
        size="small" 
        variant="primary" 
        @click="$emit('view-details', task)"
      >
        查看详情
      </BaseButton>
      <TaskActions :task="task" :on-success="handleActionSuccess" />
    </div>
  </BaseCard>
</template>

<script setup>
import { BaseCard, BaseBadge, BaseButton } from '@shared/ui'
import { formatDateTime, formatFileSize, formatTaskStatus, formatFileType } from '@shared/lib'
import { TaskActions } from '@features/task-management'
import { tasksApi } from '@shared/api'

defineProps({
  task: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['view-details', 'refresh'])

function getStatusVariant(status) {
  const variants = {
    pending: 'default',
    processing: 'info',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return variants[status] || 'default'
}

function getDownloadUrl(taskId, fileType) {
  return tasksApi.getFileDownloadUrl(taskId, fileType)
}

function handleActionSuccess() {
  emit('refresh')
}
</script>

<style scoped>
.task-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.task-url {
  display: block;
  color: #3b82f6;
  text-decoration: none;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-url:hover {
  text-decoration: underline;
}

.task-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.label {
  color: #6b7280;
  font-weight: 500;
}

.value {
  color: #111827;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 4px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  transition: width 0.3s;
}

.task-files {
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
}

.files-header {
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 14px;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
  font-size: 13px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.file-name {
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #6b7280;
}

.download-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  padding: 4px 12px;
  border-radius: 4px;
  transition: background 0.2s;
}

.download-link:hover {
  background: #dbeafe;
}

.task-error {
  padding: 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 6px;
  font-size: 13px;
}

.task-footer {
  display: flex;
  gap: 8px;
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
}
</style>


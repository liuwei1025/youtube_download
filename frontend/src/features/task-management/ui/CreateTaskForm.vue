<template>
  <div class="create-task-form">
    <div class="form-header">
      <h2>创建下载任务</h2>
      <button type="button" class="example-btn" @click="fillExample">
        📝 填充示例
      </button>
    </div>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="url">YouTube URL *</label>
        <input
          id="url"
          v-model="formData.url"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          required
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="start_time">开始时间 *</label>
          <input
            id="start_time"
            v-model="formData.start_time"
            type="text"
            placeholder="00:30 或 30"
            required
          />
          <small>格式: HH:MM:SS, MM:SS 或秒数</small>
        </div>

        <div class="form-group">
          <label for="end_time">结束时间 *</label>
          <input
            id="end_time"
            v-model="formData.end_time"
            type="text"
            placeholder="01:30 或 90"
            required
          />
          <small>格式: HH:MM:SS, MM:SS 或秒数</small>
        </div>
      </div>

      <div class="form-group">
        <label>下载选项</label>
        <div class="checkbox-group">
          <label>
            <input v-model="formData.download_video" type="checkbox" />
            下载视频
          </label>
          <label>
            <input v-model="formData.download_audio" type="checkbox" />
            下载音频
          </label>
          <label>
            <input v-model="formData.download_subtitles" type="checkbox" />
            下载字幕
          </label>
          <label>
            <input v-model="formData.burn_subtitles" type="checkbox" />
            字幕硬编码
          </label>
        </div>
      </div>

      <div class="form-group">
        <label for="subtitle_langs">字幕语言</label>
        <input
          id="subtitle_langs"
          v-model="formData.subtitle_langs"
          type="text"
          placeholder="zh,en,it"
        />
        <small>多个语言用逗号分隔</small>
      </div>

      <div class="form-group">
        <label for="proxy">代理服务器（可选）</label>
        <input
          id="proxy"
          v-model="formData.proxy"
          type="text"
          placeholder="http://127.0.0.1:7890"
        />
      </div>

      <div class="form-actions">
        <BaseButton type="submit" variant="primary" :disabled="loading">
          {{ loading ? '创建中...' : '创建任务' }}
        </BaseButton>
        <BaseButton v-if="onCancel" type="button" variant="secondary" @click="onCancel">
          取消
        </BaseButton>
      </div>
    </form>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BaseButton } from '@shared/ui'
import { useTaskStore } from '@entities/task'

const props = defineProps({
  onSuccess: {
    type: Function,
    default: null
  },
  onCancel: {
    type: Function,
    default: null
  }
})

const taskStore = useTaskStore()

const formData = ref({
  url: '',
  start_time: '',
  end_time: '',
  download_video: true,
  download_audio: true,
  download_subtitles: true,
  burn_subtitles: false,
  subtitle_langs: 'zh,en',
  proxy: ''
})

const loading = ref(false)
const error = ref(null)

async function handleSubmit() {
  loading.value = true
  error.value = null

  try {
    const taskData = {
      ...formData.value,
      proxy: formData.value.proxy || null
    }
    
    const result = await taskStore.createTask(taskData)
    
    // 重置表单
    formData.value = {
      url: '',
      start_time: '',
      end_time: '',
      download_video: true,
      download_audio: true,
      download_subtitles: true,
      burn_subtitles: false,
      subtitle_langs: 'zh,en',
      proxy: ''
    }
    
    if (props.onSuccess) {
      props.onSuccess(result)
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function fillExample() {
  formData.value = {
    url: 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
    start_time: '0:10',
    end_time: '0:30',
    download_video: true,
    download_audio: true,
    download_subtitles: true,
    burn_subtitles: true,
    subtitle_langs: 'zh,en,it',
    proxy: ''
  }
}
</script>

<style scoped>
.create-task-form {
  max-width: 600px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

h2 {
  margin: 0;
  color: #111827;
}

.example-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.example-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
  transform: translateY(-1px);
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

input[type="url"],
input[type="text"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

input[type="url"]:focus,
input[type="text"]:focus {
  outline: none;
  border-color: #3b82f6;
}

small {
  display: block;
  margin-top: 4px;
  color: #6b7280;
  font-size: 12px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  margin-bottom: 0;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  margin-right: 8px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 6px;
  font-size: 14px;
}
</style>


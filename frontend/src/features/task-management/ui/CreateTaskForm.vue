<template>
  <div class="max-w-2xl">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">创建下载任务</h2>
      <Button variant="outline" size="sm" @click="fillExample">
        📝 填充示例
      </Button>
    </div>
    
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <div class="space-y-2">
        <label for="url" class="text-sm font-medium">YouTube URL *</label>
        <Input
          id="url"
          v-model="formData.url"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          required
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <label for="start_time" class="text-sm font-medium">开始时间 *</label>
          <Input
            id="start_time"
            v-model="formData.start_time"
            type="text"
            placeholder="00:30 或 30"
            required
          />
          <p class="text-xs text-muted-foreground">格式: HH:MM:SS, MM:SS 或秒数</p>
        </div>

        <div class="space-y-2">
          <label for="end_time" class="text-sm font-medium">结束时间 *</label>
          <Input
            id="end_time"
            v-model="formData.end_time"
            type="text"
            placeholder="01:30 或 90"
            required
          />
          <p class="text-xs text-muted-foreground">格式: HH:MM:SS, MM:SS 或秒数</p>
        </div>
      </div>

      <div class="space-y-3">
        <label class="text-sm font-medium">下载选项</label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="formData.download_video" type="checkbox" class="w-4 h-4 rounded border-input" />
            <span class="text-sm">下载视频</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="formData.download_audio" type="checkbox" class="w-4 h-4 rounded border-input" />
            <span class="text-sm">下载音频</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="formData.download_subtitles" type="checkbox" class="w-4 h-4 rounded border-input" />
            <span class="text-sm">下载字幕</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="formData.burn_subtitles" type="checkbox" class="w-4 h-4 rounded border-input" />
            <span class="text-sm">字幕硬编码</span>
          </label>
        </div>
      </div>

      <div class="space-y-2">
        <label for="subtitle_langs" class="text-sm font-medium">字幕语言</label>
        <Input
          id="subtitle_langs"
          v-model="formData.subtitle_langs"
          type="text"
          placeholder="zh,en,it"
        />
        <p class="text-xs text-muted-foreground">多个语言用逗号分隔</p>
      </div>

      <div class="space-y-2">
        <label for="proxy" class="text-sm font-medium">代理服务器（可选）</label>
        <Input
          id="proxy"
          v-model="formData.proxy"
          type="text"
          placeholder="http://127.0.0.1:7890"
        />
      </div>

      <div class="flex gap-3 pt-4">
        <Button type="submit" variant="default" :disabled="loading">
          {{ loading ? '创建中...' : '创建任务' }}
        </Button>
        <Button v-if="onCancel" type="button" variant="outline" @click="onCancel">
          取消
        </Button>
      </div>
    </form>

    <div v-if="error" class="mt-4 p-3 bg-destructive/10 border border-destructive/30 rounded-lg text-sm text-destructive">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, Input } from '@components/ui'
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

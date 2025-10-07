# API 参考文档

YouTube 下载器 HTTP API 完整参考文档。

## 基础信息

- **Base URL**: `https://your-app.up.railway.app`
- **API 版本**: v2.0.0
- **内容类型**: `application/json`

## 端点总览

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | API 信息 |
| GET | `/health` | 健康检查 |
| GET | `/docs` | Swagger 文档 |
| POST | `/download` | 创建下载任务 |
| GET | `/tasks` | 获取任务列表 |
| GET | `/tasks/{task_id}` | 获取任务状态 |
| GET | `/tasks/{task_id}/files/{file_type}` | 下载文件 |
| DELETE | `/tasks/{task_id}` | 删除任务 |
| POST | `/cleanup` | 清理旧任务 |

## 详细说明

### 1. 根路径

获取 API 基本信息。

**请求**
```http
GET /
```

**响应**
```json
{
  "service": "YouTube下载器 API",
  "version": "2.0.0",
  "status": "running",
  "endpoints": {
    "docs": "/docs",
    "health": "/health",
    "download": "/download",
    "tasks": "/tasks",
    "task_status": "/tasks/{task_id}"
  }
}
```

### 2. 健康检查

检查服务运行状态。

**请求**
```http
GET /health
```

**响应**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-07T12:34:56.789012",
  "tasks_count": 5,
  "downloads_dir": "/tmp/downloads"
}
```

### 3. 创建下载任务

创建一个新的视频下载任务。

**请求**
```http
POST /download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "start_time": "1:00",
  "end_time": "2:00",
  "proxy": "http://127.0.0.1:7890",
  "subtitle_langs": "zh,en",
  "download_video": true,
  "download_audio": true,
  "download_subtitles": true,
  "video_quality": "best[height<=480]",
  "audio_quality": "192K",
  "max_retries": 3
}
```

**请求参数**

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `url` | string | 是 | - | YouTube 视频 URL |
| `start_time` | string | 是 | - | 开始时间（HH:MM:SS, MM:SS 或秒数） |
| `end_time` | string | 是 | - | 结束时间（HH:MM:SS, MM:SS 或秒数） |
| `proxy` | string | 否 | null | 代理服务器地址 |
| `subtitle_langs` | string | 否 | "zh,en" | 字幕语言代码，逗号分隔 |
| `download_video` | boolean | 否 | true | 是否下载视频 |
| `download_audio` | boolean | 否 | true | 是否下载音频 |
| `download_subtitles` | boolean | 否 | true | 是否下载字幕 |
| `video_quality` | string | 否 | "best[height<=480]" | 视频质量 |
| `audio_quality` | string | 否 | "192K" | 音频质量 |
| `max_retries` | integer | 否 | 3 | 最大重试次数 |

**响应**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "任务已创建，正在处理中",
  "created_at": "2025-10-07T12:34:56.789012"
}
```

**状态码**
- `200`: 成功创建任务
- `400`: 请求参数错误
- `500`: 服务器内部错误

### 4. 获取任务列表

获取所有任务或按状态筛选。

**请求**
```http
GET /tasks?status=completed&limit=10
```

**查询参数**

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `status` | string | 否 | - | 过滤状态：pending, processing, completed, failed |
| `limit` | integer | 否 | 50 | 返回数量限制（1-100） |

**响应**
```json
[
  {
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "completed",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "video_id": "dQw4w9WgXcQ",
    "created_at": "2025-10-07T12:34:56.789012",
    "completed_at": "2025-10-07T12:35:23.456789",
    "error": null,
    "files": {
      "video": "segment_1_00-2_00.mp4",
      "audio": "audio_1_00-2_00.mp3"
    },
    "progress": "下载完成"
  }
]
```

### 5. 获取任务状态

查询指定任务的详细状态。

**请求**
```http
GET /tasks/{task_id}
```

**路径参数**
- `task_id`: 任务 ID（UUID 格式）

**响应**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "video_id": "dQw4w9WgXcQ",
  "created_at": "2025-10-07T12:34:56.789012",
  "completed_at": "2025-10-07T12:35:23.456789",
  "error": null,
  "files": {
    "video": "segment_1_00-2_00.mp4",
    "audio": "audio_1_00-2_00.mp3",
    "subtitles": "subtitles_1_00-2_00.zh.vtt"
  },
  "progress": "下载完成"
}
```

**任务状态说明**

| 状态 | 描述 |
|------|------|
| `pending` | 任务已创建，等待处理 |
| `processing` | 正在下载和处理 |
| `completed` | 任务完成，文件可下载 |
| `failed` | 任务失败，查看 error 字段 |

**状态码**
- `200`: 成功
- `404`: 任务不存在

### 6. 下载文件

下载任务生成的文件。

**请求**
```http
GET /tasks/{task_id}/files/{file_type}
```

**路径参数**
- `task_id`: 任务 ID
- `file_type`: 文件类型（video, audio, subtitles）

**响应**
- 成功时返回文件二进制数据
- Content-Type: `application/octet-stream`
- Content-Disposition: 包含文件名

**状态码**
- `200`: 成功
- `400`: 任务未完成
- `404`: 任务或文件不存在

**示例**
```bash
# 使用 curl 下载
curl -O -J "https://your-app.up.railway.app/tasks/a1b2c3d4.../files/video"

# 使用 wget 下载
wget --content-disposition "https://your-app.up.railway.app/tasks/a1b2c3d4.../files/audio"
```

### 7. 删除任务

删除任务及其关联的所有文件。

**请求**
```http
DELETE /tasks/{task_id}
```

**路径参数**
- `task_id`: 任务 ID

**响应**
```json
{
  "message": "任务已删除",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**状态码**
- `200`: 成功删除
- `404`: 任务不存在

### 8. 清理旧任务

手动清理超过指定时间的旧任务。

**请求**
```http
POST /cleanup?max_age_hours=24
```

**查询参数**
- `max_age_hours`: 清理多少小时前的任务（默认 24）

**响应**
```json
{
  "message": "已清理 24 小时前的旧任务",
  "current_tasks": 3
}
```

## 错误响应

所有端点在出错时返回统一格式：

```json
{
  "detail": "错误描述信息"
}
```

**常见状态码**

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 使用示例

### Python 示例

```python
import requests
import time

# API 基础 URL
BASE_URL = "https://your-app.up.railway.app"

# 1. 创建下载任务
response = requests.post(f"{BASE_URL}/download", json={
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "1:00",
    "end_time": "2:00",
    "download_video": True,
    "download_audio": True,
    "download_subtitles": False
})

task = response.json()
task_id = task["task_id"]
print(f"任务创建成功: {task_id}")

# 2. 轮询任务状态
while True:
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    status_data = response.json()
    
    status = status_data["status"]
    print(f"当前状态: {status}")
    
    if status == "completed":
        print("下载完成！")
        break
    elif status == "failed":
        print(f"下载失败: {status_data['error']}")
        break
    
    time.sleep(5)  # 等待 5 秒后再次查询

# 3. 下载文件
if status == "completed":
    # 下载视频
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}/files/video",
        stream=True
    )
    with open("downloaded_video.mp4", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("视频已保存")
    
    # 下载音频
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}/files/audio",
        stream=True
    )
    with open("downloaded_audio.mp3", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("音频已保存")
```

### JavaScript 示例

```javascript
const BASE_URL = "https://your-app.up.railway.app";

// 1. 创建下载任务
async function createDownloadTask() {
    const response = await fetch(`${BASE_URL}/download`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            start_time: "1:00",
            end_time: "2:00",
            download_video: true,
            download_audio: true,
            download_subtitles: false
        })
    });
    
    const task = await response.json();
    return task.task_id;
}

// 2. 查询任务状态
async function checkTaskStatus(taskId) {
    const response = await fetch(`${BASE_URL}/tasks/${taskId}`);
    return await response.json();
}

// 3. 等待任务完成
async function waitForCompletion(taskId) {
    while (true) {
        const status = await checkTaskStatus(taskId);
        console.log(`当前状态: ${status.status}`);
        
        if (status.status === "completed") {
            return status;
        } else if (status.status === "failed") {
            throw new Error(status.error);
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
}

// 4. 使用示例
(async () => {
    try {
        const taskId = await createDownloadTask();
        console.log(`任务创建成功: ${taskId}`);
        
        const result = await waitForCompletion(taskId);
        console.log("下载完成！", result.files);
        
        // 下载文件
        const videoUrl = `${BASE_URL}/tasks/${taskId}/files/video`;
        console.log(`视频下载地址: ${videoUrl}`);
        
    } catch (error) {
        console.error("错误:", error);
    }
})();
```

### cURL 示例

```bash
#!/bin/bash

BASE_URL="https://your-app.up.railway.app"

# 1. 创建下载任务
RESPONSE=$(curl -s -X POST "$BASE_URL/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "1:00",
    "end_time": "2:00",
    "download_video": true,
    "download_audio": true,
    "download_subtitles": false
  }')

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "任务创建成功: $TASK_ID"

# 2. 轮询任务状态
while true; do
  STATUS_RESPONSE=$(curl -s "$BASE_URL/tasks/$TASK_ID")
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
  
  echo "当前状态: $STATUS"
  
  if [ "$STATUS" == "completed" ]; then
    echo "下载完成！"
    break
  elif [ "$STATUS" == "failed" ]; then
    ERROR=$(echo $STATUS_RESPONSE | jq -r '.error')
    echo "下载失败: $ERROR"
    exit 1
  fi
  
  sleep 5
done

# 3. 下载文件
curl -O -J "$BASE_URL/tasks/$TASK_ID/files/video"
curl -O -J "$BASE_URL/tasks/$TASK_ID/files/audio"

echo "文件下载完成！"
```

## 速率限制

目前 API 没有硬性速率限制，但建议：
- 不要同时创建超过 5 个任务
- 任务间隔至少 1 秒
- 避免频繁轮询（建议 5 秒间隔）

## 最佳实践

1. **任务管理**
   - 完成后及时下载文件
   - 下载后删除不需要的任务
   - 定期清理旧任务

2. **错误处理**
   - 实现重试机制
   - 捕获所有可能的异常
   - 记录错误日志

3. **性能优化**
   - 使用合理的视频质量
   - 下载较短的片段
   - 避免并发过多任务

4. **安全性**
   - 验证 URL 有效性
   - 不要暴露敏感信息
   - 使用 HTTPS 连接

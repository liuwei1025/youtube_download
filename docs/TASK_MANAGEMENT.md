# 任务管理系统文档

## 概述

YouTube 下载器现在支持完整的任务管理系统，使用 PostgreSQL 数据库持久化存储任务信息，支持查看任务进度、下载文件、查看日志等功能。

## 功能特性

✅ **任务持久化存储** - 使用 PostgreSQL 数据库存储任务信息  
✅ **任务进度跟踪** - 实时查看任务执行进度和当前步骤  
✅ **文件管理** - 自动记录生成的文件信息（视频、音频、字幕）  
✅ **日志系统** - 详细记录任务执行过程中的所有日志  
✅ **任务统计** - 查看所有任务的统计信息  
✅ **任务操作** - 支持取消、删除任务  
✅ **自动清理** - 自动清理过期的旧任务  

## 快速开始

### 1. 启动服务

```bash
# 启动所有服务（包括数据库）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f youtube-dl-api
```

### 2. 访问 API 文档

启动后访问：http://localhost:8000/docs

## API 端点

### 基础端点

- `GET /` - API 信息
- `GET /health` - 健康检查（包含数据库状态）
- `GET /stats` - 任务统计信息

### 任务管理

#### 创建任务

```bash
POST /download
```

请求示例：
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "start_time": "00:10",
  "end_time": "01:30",
  "subtitle_langs": "zh,en",
  "download_video": true,
  "download_audio": true,
  "download_subtitles": true,
  "burn_subtitles": true,
  "video_quality": "best[height<=480]",
  "audio_quality": "192K"
}
```

响应示例：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "任务已创建，正在处理中",
  "created_at": "2025-10-27T10:30:00+08:00"
}
```

#### 查看任务列表

```bash
GET /tasks?status=processing&limit=50&offset=0
```

参数：
- `status` (可选): 过滤状态 (pending, processing, completed, failed, cancelled)
- `limit` (可选): 返回数量，默认 50
- `offset` (可选): 偏移量，默认 0

响应示例：
```json
[
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "video_id": "VIDEO_ID",
    "video_title": "视频标题",
    "progress": "正在下载视频...",
    "progress_percentage": 60,
    "created_at": "2025-10-27T10:30:00+08:00",
    "completed_at": null,
    "error_message": null
  }
]
```

#### 查看任务详情

```bash
GET /tasks/{task_id}
```

响应示例：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "video_id": "VIDEO_ID",
  "video_title": "视频标题",
  "start_time": "00:10",
  "end_time": "01:30",
  "progress": "下载完成",
  "progress_percentage": 100,
  "current_step": "完成",
  "created_at": "2025-10-27T10:30:00+08:00",
  "updated_at": "2025-10-27T10:35:00+08:00",
  "started_at": "2025-10-27T10:30:05+08:00",
  "completed_at": "2025-10-27T10:35:00+08:00",
  "files": [
    {
      "file_type": "video",
      "file_name": "segment_00_10-01_30.mp4",
      "file_path": "/app/downloads/VIDEO_ID/segment_00_10-01_30.mp4",
      "file_size": 15728640,
      "mime_type": "video/mp4",
      "created_at": "2025-10-27T10:35:00+08:00"
    },
    {
      "file_type": "audio",
      "file_name": "audio_00_10-01_30.mp3",
      "file_path": "/app/downloads/VIDEO_ID/audio_00_10-01_30.mp3",
      "file_size": 1966080,
      "mime_type": "audio/mpeg",
      "created_at": "2025-10-27T10:35:00+08:00"
    }
  ],
  "metadata": {}
}
```

#### 查看任务文件列表

```bash
GET /tasks/{task_id}/files
```

#### 下载任务文件

```bash
GET /tasks/{task_id}/files/{file_type}
```

文件类型：
- `video` - 视频文件
- `audio` - 音频文件
- `subtitles` - 字幕文件
- `video_with_subs` - 带字幕的视频文件

#### 查看任务日志

```bash
GET /tasks/{task_id}/logs?limit=100
```

响应示例：
```json
[
  {
    "level": "INFO",
    "message": "任务已创建: https://www.youtube.com/watch?v=VIDEO_ID",
    "created_at": "2025-10-27T10:30:00+08:00"
  },
  {
    "level": "INFO",
    "message": "开始处理任务: https://www.youtube.com/watch?v=VIDEO_ID",
    "created_at": "2025-10-27T10:30:05+08:00"
  },
  {
    "level": "INFO",
    "message": "任务完成",
    "created_at": "2025-10-27T10:35:00+08:00"
  }
]
```

#### 取消任务

```bash
POST /tasks/{task_id}/cancel
```

#### 删除任务

```bash
DELETE /tasks/{task_id}?delete_files=true
```

参数：
- `delete_files` (可选): 是否删除相关文件，默认 true

### 统计信息

```bash
GET /stats
```

响应示例：
```json
{
  "total": 100,
  "pending": 5,
  "processing": 2,
  "completed": 85,
  "failed": 6,
  "cancelled": 2
}
```

### 清理旧任务

```bash
POST /cleanup?max_age_hours=24
```

参数：
- `max_age_hours`: 清理多少小时前的任务，默认 24

## 使用示例

### Python 客户端示例

```python
import requests
import time

API_BASE = "http://localhost:8000"

# 创建下载任务
response = requests.post(f"{API_BASE}/download", json={
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "00:10",
    "end_time": "01:00",
    "subtitle_langs": "zh,en"
})

task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

# 轮询任务状态
while True:
    response = requests.get(f"{API_BASE}/tasks/{task_id}")
    task = response.json()
    
    print(f"状态: {task['status']}")
    print(f"进度: {task['progress']} ({task['progress_percentage']}%)")
    
    if task['status'] in ['completed', 'failed', 'cancelled']:
        break
    
    time.sleep(5)

# 下载完成后获取文件
if task['status'] == 'completed':
    for file in task['files']:
        file_type = file['file_type']
        response = requests.get(
            f"{API_BASE}/tasks/{task_id}/files/{file_type}",
            stream=True
        )
        
        with open(file['file_name'], 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"已下载: {file['file_name']}")
```

### curl 示例

```bash
# 创建任务
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "00:10",
    "end_time": "01:00"
  }'

# 查看任务状态
curl "http://localhost:8000/tasks/550e8400-e29b-41d4-a716-446655440000"

# 下载文件
curl -o video.mp4 \
  "http://localhost:8000/tasks/550e8400-e29b-41d4-a716-446655440000/files/video"
```

## 数据库管理

### 连接数据库

```bash
# 进入 PostgreSQL 容器
docker exec -it youtube-postgres psql -U youtube -d youtube_tasks

# 或者从宿主机连接
psql -h localhost -p 5432 -U youtube -d youtube_tasks
```

密码: `youtube_pass_2024`

### 常用查询

```sql
-- 查看所有任务
SELECT task_id, status, url, progress_percentage, created_at 
FROM tasks 
ORDER BY created_at DESC 
LIMIT 10;

-- 查看任务统计
SELECT status, COUNT(*) 
FROM tasks 
GROUP BY status;

-- 查看最近的错误
SELECT task_id, url, error_message, created_at 
FROM tasks 
WHERE status = 'failed' 
ORDER BY created_at DESC 
LIMIT 10;

-- 清理旧任务
SELECT cleanup_old_tasks(24);

-- 查看任务文件
SELECT t.task_id, t.url, f.file_type, f.file_name, f.file_size
FROM tasks t
JOIN task_files f ON t.task_id = f.task_id
WHERE t.status = 'completed'
ORDER BY t.created_at DESC;
```

## 数据库架构

### 主要表结构

#### tasks 表
- `task_id` - 任务唯一标识
- `status` - 任务状态 (pending, processing, completed, failed, cancelled)
- `url` - YouTube 视频链接
- `video_id` - 视频ID
- `video_title` - 视频标题
- `progress` - 进度描述
- `progress_percentage` - 进度百分比
- `current_step` - 当前步骤
- `created_at` - 创建时间
- `updated_at` - 更新时间
- `started_at` - 开始时间
- `completed_at` - 完成时间
- `error_message` - 错误信息

#### task_files 表
- `task_id` - 关联的任务ID
- `file_type` - 文件类型
- `file_name` - 文件名
- `file_path` - 文件路径
- `file_size` - 文件大小
- `mime_type` - MIME类型

#### task_logs 表
- `task_id` - 关联的任务ID
- `level` - 日志级别
- `message` - 日志内容
- `created_at` - 创建时间

## 环境变量

在 `docker-compose.yaml` 中配置：

```yaml
# 数据库配置
DATABASE_URL: "postgresql://youtube:youtube_pass_2024@postgres:5432/youtube_tasks"
DB_HOST: "postgres"
DB_PORT: "5432"
DB_NAME: "youtube_tasks"
DB_USER: "youtube"
DB_PASSWORD: "youtube_pass_2024"
```

## 故障排查

### 数据库连接失败

1. 检查数据库容器是否运行：
```bash
docker ps | grep postgres
```

2. 查看数据库日志：
```bash
docker-compose logs postgres
```

3. 测试数据库连接：
```bash
docker exec -it youtube-postgres pg_isready -U youtube
```

### 任务卡在 processing 状态

查看任务日志了解详情：
```bash
curl "http://localhost:8000/tasks/{task_id}/logs"
```

### 文件下载失败

1. 检查任务状态是否为 completed
2. 检查文件是否存在：
```bash
docker exec -it youtube-dl-api ls -la /app/downloads/{video_id}/
```

## 性能优化

### 数据库索引

已自动创建以下索引：
- `idx_tasks_status` - 按状态查询
- `idx_tasks_created_at` - 按创建时间排序
- `idx_tasks_video_id` - 按视频ID查询
- `idx_task_files_task_id` - 文件查询
- `idx_task_logs_task_id` - 日志查询

### 定期清理

建议定期清理旧任务：
```bash
# 每天清理 7 天前的已完成任务
curl -X POST "http://localhost:8000/cleanup?max_age_hours=168"
```

或者设置 cron 任务：
```bash
0 3 * * * curl -X POST "http://localhost:8000/cleanup?max_age_hours=168"
```

## 安全建议

1. **修改默认密码**：更改 `docker-compose.yaml` 中的数据库密码
2. **限制访问**：使用防火墙限制数据库端口访问
3. **备份数据**：定期备份 PostgreSQL 数据卷
4. **使用 HTTPS**：生产环境中使用反向代理配置 SSL

## 数据备份与恢复

### 备份

```bash
# 备份数据库
docker exec youtube-postgres pg_dump -U youtube youtube_tasks > backup.sql

# 备份文件
tar -czf downloads_backup.tar.gz downloads/
```

### 恢复

```bash
# 恢复数据库
docker exec -i youtube-postgres psql -U youtube youtube_tasks < backup.sql

# 恢复文件
tar -xzf downloads_backup.tar.gz
```

## 更新日志

### v3.0.0 (2025-10-27)
- ✨ 新增 PostgreSQL 数据库支持
- ✨ 新增任务进度跟踪功能
- ✨ 新增任务日志系统
- ✨ 新增文件管理功能
- ✨ 新增任务统计功能
- ✨ 新增取消任务功能
- 🔧 改进任务状态管理
- 🔧 优化 API 响应结构

## 相关文档

- [API 参考文档](API_REFERENCE.md)
- [项目结构说明](PROJECT_STRUCTURE.md)
- [Cookie 设置指南](COOKIES_SETUP.md)
- [FFmpeg 安装指南](FFMPEG_SETUP.md)


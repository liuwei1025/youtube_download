# 系统架构概览

## 整体架构图

```
┌──────────────────────────────────────────────────────────────────────┐
│                           客户端应用                                   │
│  (Python/JavaScript/curl/浏览器等)                                    │
└─────────────────────────┬────────────────────────────────────────────┘
                          │ HTTP/REST API
                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FastAPI Web 应用 (Port 8000)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  API 端点    │  │  任务管理    │  │  文件服务    │              │
│  │  /download   │  │  TaskService │  │  下载管理    │              │
│  │  /tasks      │  │              │  │              │              │
│  │  /stats      │  │              │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└───────────┬──────────────────────┬──────────────────────────────────┘
            │                      │
            │                      │
            ▼                      ▼
┌─────────────────────┐  ┌────────────────────────┐
│  PostgreSQL 数据库  │  │  文件系统 (Downloads)  │
│  (Port 5432)        │  │                        │
│                     │  │  /downloads/           │
│  ┌───────────────┐ │  │    ├── video_id_1/     │
│  │ tasks         │ │  │    │   ├── video.mp4   │
│  │ task_files    │ │  │    │   ├── audio.mp3   │
│  │ task_logs     │ │  │    │   └── subs.vtt    │
│  └───────────────┘ │  │    └── video_id_2/     │
│                     │  │        └── ...         │
└─────────────────────┘  └────────────────────────┘
```

## 数据流程图

### 1. 创建下载任务

```
客户端
  │
  │ POST /download
  │ {url, start_time, end_time, ...}
  │
  ▼
FastAPI
  │
  ├─► TaskService.create_task()
  │   └─► 插入任务记录到数据库
  │       └─► tasks 表 (status: pending)
  │
  ├─► 创建后台任务
  │   └─► process_download_task()
  │
  └─► 返回 task_id 给客户端
```

### 2. 处理下载任务

```
后台任务 process_download_task()
  │
  ├─► 更新状态: processing
  │   └─► TaskService.update_task_status()
  │       └─► 数据库: tasks.status = 'processing'
  │
  ├─► 提取视频ID
  │   └─► extract_video_id()
  │
  ├─► 执行下载
  │   └─► process_single_url()
  │       ├─► 下载视频 (yt-dlp)
  │       ├─► 提取音频 (ffmpeg)
  │       └─► 下载字幕 (yt-dlp)
  │
  ├─► 保存文件信息
  │   └─► TaskService.add_task_file()
  │       └─► 数据库: task_files 表
  │
  ├─► 记录日志
  │   └─► TaskService.add_task_log()
  │       └─► 数据库: task_logs 表
  │
  └─► 更新状态: completed
      └─► TaskService.update_task_status()
          └─► 数据库: tasks.status = 'completed'
```

### 3. 查询任务状态

```
客户端
  │
  │ GET /tasks/{task_id}
  │
  ▼
FastAPI
  │
  └─► TaskService.get_task()
      │
      ├─► 查询任务信息 (tasks 表)
      │
      ├─► 查询文件列表 (task_files 表)
      │
      └─► 返回完整的任务详情
```

### 4. 下载文件

```
客户端
  │
  │ GET /tasks/{task_id}/files/{file_type}
  │
  ▼
FastAPI
  │
  ├─► 验证任务状态 (completed)
  │
  ├─► 查询文件信息 (task_files 表)
  │
  ├─► 检查文件是否存在
  │
  └─► FileResponse (流式传输文件)
```

## 数据库 Schema

### tasks 表（任务主表）

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE,
    status task_status,              -- 任务状态
    url TEXT,                         -- YouTube URL
    video_id VARCHAR(255),           -- 视频ID
    video_title TEXT,                -- 视频标题
    
    -- 配置信息
    start_time VARCHAR(50),
    end_time VARCHAR(50),
    proxy TEXT,
    subtitle_langs VARCHAR(255),
    download_video BOOLEAN,
    download_audio BOOLEAN,
    download_subtitles BOOLEAN,
    burn_subtitles BOOLEAN,
    video_quality VARCHAR(100),
    audio_quality VARCHAR(50),
    max_retries INTEGER,
    
    -- 进度信息
    progress VARCHAR(255),           -- 进度描述
    progress_percentage INTEGER,     -- 进度百分比
    current_step VARCHAR(255),       -- 当前步骤
    
    -- 时间戳
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- 错误信息
    error_message TEXT,
    error_trace TEXT,
    
    -- 元数据
    metadata JSONB
);
```

### task_files 表（文件记录表）

```sql
CREATE TABLE task_files (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) REFERENCES tasks(task_id),
    file_type VARCHAR(50),           -- video/audio/subtitles
    file_name TEXT,
    file_path TEXT,
    file_size BIGINT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP,
    
    UNIQUE(task_id, file_type)
);
```

### task_logs 表（日志表）

```sql
CREATE TABLE task_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) REFERENCES tasks(task_id),
    level VARCHAR(20),               -- INFO/WARNING/ERROR
    message TEXT,
    created_at TIMESTAMP
);
```

## 状态转换图

```
        pending
           │
           │ 开始处理
           ▼
      processing ─────────┐
           │              │
           │              │ 出错
           │              ▼
           │          failed
           │
           │ 完成
           ▼
      completed
           
           
      或者在任意时刻：
           
      pending/processing
           │
           │ 用户取消
           ▼
      cancelled
```

## 技术栈详解

### 后端框架
- **FastAPI**: 现代、高性能的 Python Web 框架
- **asyncio**: 异步编程支持
- **asyncpg**: PostgreSQL 异步驱动

### 数据库
- **PostgreSQL 15**: 强大的关系型数据库
- **连接池**: 高效的数据库连接管理
- **事务支持**: 保证数据一致性

### 下载引擎
- **yt-dlp**: YouTube 下载核心
- **FFmpeg**: 视频处理和转换
- **字幕处理**: 自动下载和烧录

### 容器化
- **Docker**: 应用容器化
- **Docker Compose**: 多容器编排
- **数据卷**: 持久化存储

## 性能特性

### 1. 异步处理
- 所有下载任务在后台异步执行
- 不阻塞 API 响应
- 支持并发处理多个任务

### 2. 数据库连接池
```python
pool = await asyncpg.create_pool(
    min_size=2,
    max_size=10,
    command_timeout=60
)
```

### 3. 资源限制
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### 4. 文件流式传输
- 使用 `FileResponse` 流式传输大文件
- 减少内存占用
- 支持断点续传

## 安全特性

### 1. 数据库安全
- 独立的数据库用户和密码
- 内部网络隔离
- 参数化查询防止 SQL 注入

### 2. 文件访问控制
- 验证任务所有权
- 路径遍历防护
- 文件类型验证

### 3. 错误处理
- 全局异常捕获
- 详细的错误日志
- 用户友好的错误信息

## 扩展性设计

### 1. 水平扩展
```yaml
# 可以轻松增加 API 实例
youtube-dl-api:
  deploy:
    replicas: 3
```

### 2. 数据库扩展
- 支持主从复制
- 支持读写分离
- 可以添加 Redis 缓存层

### 3. 存储扩展
- 可以替换为对象存储 (S3, MinIO)
- 支持 CDN 加速
- 支持多区域存储

## 监控与日志

### 1. 应用日志
```python
logger.info(f"任务 {task_id} 完成")
logger.error(f"任务 {task_id} 失败: {error}")
```

### 2. 数据库日志
- PostgreSQL 慢查询日志
- 连接池监控
- 查询性能分析

### 3. 健康检查
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "..."]
  interval: 30s
  timeout: 10s
```

### 4. 统计指标
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

## 部署架构

### 开发环境
```
本地机器
  ├── docker-compose up
  ├── API: http://localhost:8000
  └── DB: localhost:5432
```

### 生产环境（推荐）
```
┌─────────────────┐
│   Load Balancer │
│    (Nginx)      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────┐   ┌─────┐
│ API │   │ API │  (多实例)
│  1  │   │  2  │
└──┬──┘   └──┬──┘
   │         │
   └────┬────┘
        │
        ▼
┌──────────────┐
│  PostgreSQL  │
│   (Primary)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│   (Replica)  │
└──────────────┘
```

## 故障恢复

### 1. 数据库故障
- 自动重连机制
- 连接池健康检查
- 从备库恢复

### 2. 下载失败
- 自动重试机制 (max_retries)
- 详细的错误日志
- 任务状态追踪

### 3. 文件丢失
- 数据库记录保留
- 可以重新下载
- 定期备份

## 最佳实践

### 1. 任务管理
- 定期清理旧任务
- 监控失败任务
- 合理设置重试次数

### 2. 存储管理
- 定期清理下载文件
- 监控磁盘使用
- 设置存储配额

### 3. 性能优化
- 使用连接池
- 启用数据库索引
- 异步处理任务

### 4. 安全维护
- 定期更新依赖
- 修改默认密码
- 限制网络访问

## 相关文档

- [快速启动指南](../QUICKSTART.md)
- [任务管理文档](TASK_MANAGEMENT.md)
- [API 参考](API_REFERENCE.md)
- [项目结构](PROJECT_STRUCTURE.md)


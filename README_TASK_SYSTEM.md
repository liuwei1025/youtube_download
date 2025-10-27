# YouTube 下载器 - 任务管理系统

## 系统概述

这是一个功能完整的 YouTube 视频下载服务，现已集成强大的任务管理系统，支持：

- 📊 **实时进度跟踪** - 查看每个任务的详细进度和状态
- 💾 **数据库持久化** - 使用 PostgreSQL 存储任务信息
- 📁 **文件管理** - 自动记录和管理下载的文件
- 📝 **日志系统** - 详细的任务执行日志
- 📈 **统计分析** - 任务执行统计和分析
- 🎯 **任务控制** - 取消、删除、重试任务

## 快速开始

### 1. 启动服务

```bash
# 克隆项目
git clone <your-repo>
cd youtube

# 启动所有服务（API + PostgreSQL）
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 2. 验证服务

```bash
# 检查健康状态
curl http://localhost:8000/health

# 查看 API 文档
open http://localhost:8000/docs
```

### 3. 创建第一个任务

```bash
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "00:00",
    "end_time": "01:00",
    "subtitle_langs": "zh,en"
  }'
```

## 系统架构

```
┌─────────────────┐
│   FastAPI App   │  ← HTTP API 服务
└────────┬────────┘
         │
         ├─────────────┐
         │             │
         ▼             ▼
┌─────────────┐  ┌──────────────┐
│  PostgreSQL │  │  Downloads   │  ← 文件存储
│   Database  │  │  Directory   │
└─────────────┘  └──────────────┘
```

## 核心功能

### 1. 任务创建与管理

创建下载任务后，系统自动：
- 分配唯一任务ID
- 记录到数据库
- 异步执行下载
- 更新进度状态

### 2. 进度跟踪

实时查看任务进度：
```json
{
  "progress": "正在下载视频...",
  "progress_percentage": 60,
  "current_step": "下载中"
}
```

### 3. 文件管理

自动记录所有生成的文件：
- 视频文件 (MP4)
- 音频文件 (MP3)
- 字幕文件 (VTT)
- 带字幕视频

### 4. 日志系统

完整的任务执行日志：
```bash
GET /tasks/{task_id}/logs
```

## API 端点总览

| 端点 | 方法 | 功能 |
|------|------|------|
| `/download` | POST | 创建下载任务 |
| `/tasks` | GET | 获取任务列表 |
| `/tasks/{task_id}` | GET | 获取任务详情 |
| `/tasks/{task_id}/files` | GET | 获取任务文件列表 |
| `/tasks/{task_id}/files/{type}` | GET | 下载指定文件 |
| `/tasks/{task_id}/logs` | GET | 获取任务日志 |
| `/tasks/{task_id}/cancel` | POST | 取消任务 |
| `/tasks/{task_id}` | DELETE | 删除任务 |
| `/stats` | GET | 获取统计信息 |
| `/cleanup` | POST | 清理旧任务 |

## 使用示例

### Python 完整示例

```python
import requests
import time

API_BASE = "http://localhost:8000"

# 1. 创建任务
print("创建下载任务...")
response = requests.post(f"{API_BASE}/download", json={
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "00:10",
    "end_time": "01:30",
    "subtitle_langs": "zh,en",
    "download_video": True,
    "download_audio": True,
    "download_subtitles": True
})

task = response.json()
task_id = task["task_id"]
print(f"✅ 任务创建成功: {task_id}")

# 2. 监控进度
print("\n监控任务进度...")
while True:
    response = requests.get(f"{API_BASE}/tasks/{task_id}")
    task = response.json()
    
    status = task['status']
    progress = task['progress']
    percentage = task['progress_percentage']
    
    print(f"状态: {status} | 进度: {progress} ({percentage}%)")
    
    if status in ['completed', 'failed', 'cancelled']:
        break
    
    time.sleep(2)

# 3. 查看日志
print("\n查看任务日志...")
response = requests.get(f"{API_BASE}/tasks/{task_id}/logs")
logs = response.json()
for log in logs[:5]:  # 显示最近5条
    print(f"[{log['level']}] {log['message']}")

# 4. 下载文件
if task['status'] == 'completed':
    print("\n下载文件...")
    files_response = requests.get(f"{API_BASE}/tasks/{task_id}/files")
    files_data = files_response.json()
    
    for file in files_data['files']:
        file_type = file['file_type']
        file_name = file['file_name']
        
        print(f"下载: {file_name}...")
        response = requests.get(
            f"{API_BASE}/tasks/{task_id}/files/{file_type}",
            stream=True
        )
        
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 已保存: {file_name}")
    
    print("\n✨ 所有文件下载完成！")
else:
    print(f"\n❌ 任务失败: {task.get('error_message')}")
```

### JavaScript/Node.js 示例

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:8000';

async function downloadVideo() {
    // 创建任务
    const { data: task } = await axios.post(`${API_BASE}/download`, {
        url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        start_time: '00:10',
        end_time: '01:30',
        subtitle_langs: 'zh,en'
    });
    
    console.log(`任务创建: ${task.task_id}`);
    
    // 轮询状态
    while (true) {
        const { data: status } = await axios.get(
            `${API_BASE}/tasks/${task.task_id}`
        );
        
        console.log(`进度: ${status.progress} (${status.progress_percentage}%)`);
        
        if (['completed', 'failed', 'cancelled'].includes(status.status)) {
            break;
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    console.log('任务完成！');
}

downloadVideo().catch(console.error);
```

## 数据库管理

### 连接数据库

```bash
# 使用 docker
docker exec -it youtube-postgres psql -U youtube -d youtube_tasks

# 从宿主机
psql -h localhost -p 5432 -U youtube -d youtube_tasks
# 密码: youtube_pass_2024
```

### 常用查询

```sql
-- 查看所有任务
SELECT task_id, status, url, progress_percentage, created_at 
FROM tasks 
ORDER BY created_at DESC;

-- 查看统计
SELECT status, COUNT(*) 
FROM tasks 
GROUP BY status;

-- 查看失败的任务
SELECT task_id, url, error_message 
FROM tasks 
WHERE status = 'failed';

-- 清理旧任务
SELECT cleanup_old_tasks(24);
```

## 配置说明

### 数据库配置

在 `docker-compose.yaml` 中：

```yaml
environment:
  DB_HOST: "postgres"
  DB_PORT: "5432"
  DB_NAME: "youtube_tasks"
  DB_USER: "youtube"
  DB_PASSWORD: "youtube_pass_2024"
```

### 应用配置

```yaml
environment:
  DOWNLOADS_DIR: "/app/downloads"
  HTTP_PROXY: "http://host.docker.internal:7890"
  PYTHONUNBUFFERED: "1"
```

## 监控与维护

### 查看服务状态

```bash
# 查看所有容器
docker-compose ps

# 查看日志
docker-compose logs -f youtube-dl-api

# 查看数据库日志
docker-compose logs -f postgres
```

### 健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# 数据库健康检查
docker exec youtube-postgres pg_isready -U youtube
```

### 统计信息

```bash
# 获取任务统计
curl http://localhost:8000/stats
```

### 清理旧任务

```bash
# 清理 24 小时前的旧任务
curl -X POST "http://localhost:8000/cleanup?max_age_hours=24"

# 清理 7 天前的旧任务
curl -X POST "http://localhost:8000/cleanup?max_age_hours=168"
```

## 故障排查

### 问题：数据库连接失败

```bash
# 检查数据库容器
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

### 问题：任务一直处于 processing

```bash
# 查看任务日志
curl http://localhost:8000/tasks/{task_id}/logs

# 查看应用日志
docker-compose logs youtube-dl-api
```

### 问题：文件下载失败

```bash
# 检查文件是否存在
docker exec youtube-dl-api ls -la /app/downloads/{video_id}/

# 检查任务状态
curl http://localhost:8000/tasks/{task_id}
```

## 数据备份

### 备份数据库

```bash
# 导出数据库
docker exec youtube-postgres pg_dump -U youtube youtube_tasks > backup.sql

# 备份下载文件
tar -czf downloads_backup.tar.gz downloads/
```

### 恢复数据库

```bash
# 导入数据库
docker exec -i youtube-postgres psql -U youtube youtube_tasks < backup.sql

# 恢复文件
tar -xzf downloads_backup.tar.gz
```

## 性能优化

1. **数据库索引** - 已自动创建必要的索引
2. **连接池** - 使用 asyncpg 连接池管理
3. **异步处理** - 所有下载任务异步执行
4. **资源限制** - Docker 资源限制防止过度占用

## 安全建议

1. **修改默认密码** - 更改数据库默认密码
2. **使用环境变量** - 敏感信息使用环境变量
3. **限制访问** - 使用防火墙限制端口访问
4. **定期备份** - 定期备份数据库和文件
5. **HTTPS** - 生产环境使用 HTTPS

## 项目结构

```
youtube/
├── app.py                 # FastAPI 应用主文件
├── docker-compose.yaml    # Docker 编排文件
├── init_db.sql           # 数据库初始化脚本
├── requirements.txt      # Python 依赖
├── src/
│   ├── database.py       # 数据库连接管理
│   ├── models.py         # 数据模型定义
│   ├── task_service.py   # 任务服务逻辑
│   └── downloader/       # 下载器核心模块
├── downloads/            # 下载文件目录
└── docs/
    └── TASK_MANAGEMENT.md  # 详细文档
```

## 技术栈

- **Web框架**: FastAPI 
- **数据库**: PostgreSQL 15
- **异步库**: asyncpg, asyncio
- **下载器**: yt-dlp
- **视频处理**: FFmpeg
- **容器化**: Docker, Docker Compose

## 相关链接

- 📚 [完整 API 文档](http://localhost:8000/docs)
- 📖 [详细使用文档](docs/TASK_MANAGEMENT.md)
- 🐛 [问题反馈](https://github.com/your-repo/issues)

## 更新日志

### v3.0.0 (2025-10-27)
- ✨ 新增完整的任务管理系统
- ✨ 集成 PostgreSQL 数据库
- ✨ 新增实时进度跟踪
- ✨ 新增任务日志系统
- ✨ 新增文件管理功能
- ✨ 新增任务统计分析
- 🔧 优化 API 结构
- 🔧 改进错误处理

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！


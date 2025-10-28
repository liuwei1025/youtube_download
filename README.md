# YouTube 视频片段下载器 v3.0

一个功能完整的 YouTube 视频下载工具，支持时间段裁剪、音频提取、字幕下载和 HTTP API 服务。**现已支持完整的任务管理系统和数据库持久化！**

## 🌟 主要特性

### 核心功能
- ✅ **精确时间段裁剪** - 使用两阶段下载策略，先下载完整视频再精确切割
- ✅ **音频提取** - 自动提取音频并保存为MP3格式（可配置质量）
- ✅ **字幕下载与烧录** - 支持多语言字幕下载和烧录到视频（中/英/日等）
- ✅ **HTTP代理支持** - 智能代理配置，支持环境变量和自定义设置
- ✅ **批量处理** - 支持从文件读取多个URL批量下载

### 🆕 任务管理系统 (v3.0)
- 📊 **实时进度跟踪** - 实时查看任务进度和状态
- 💾 **数据库持久化** - 使用 PostgreSQL 存储任务信息
- 📁 **文件管理** - 自动记录和管理所有下载的文件
- 📝 **日志系统** - 详细的任务执行日志
- 📈 **统计分析** - 任务执行统计和分析
- 🎯 **任务控制** - 取消、删除、查询任务
- 🔄 **异步处理** - 所有任务异步执行，支持并发

### 🎨 前端管理界面 (NEW!)
- 🖥️ **现代化UI** - 基于 Vue 3 + Vite 构建的响应式界面
- 📋 **任务管理** - 可视化任务列表、状态筛选、实时刷新
- 📥 **文件下载** - 直接从浏览器下载生成的文件
- 📊 **详情查看** - 查看完整任务信息、进度和日志
- 🎯 **Feature-Sliced Design** - 清晰的代码架构，易于维护和扩展

### 技术特性
- ✅ **RESTful API** - 完整的 HTTP API 服务
- ✅ **Docker 支持** - 完整的容器化部署方案
- ✅ **配置灵活** - 支持多种配置方式

## 📦 安装

### 依赖安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/youtube_download.git
cd youtube_download

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 ffmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载并添加到 PATH
```

## ⚡ 快速开始

### 🚀 一键启动（推荐）

```bash
# 1. 启动所有服务（API + 数据库）
docker-compose up -d

# 2. 验证服务
curl http://localhost:8000/health

# 3. 访问 API 文档
open http://localhost:8000/docs
```

详细指南：📖 [快速启动指南](QUICKSTART.md)

---

## 🚀 使用方法

### 方式一：命令行工具

```bash
# 基本用法
./ytdl "https://www.youtube.com/watch?v=VIDEO_ID" --start 1:00 --end 2:00

# 或使用 Python
python src/youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" \
    --start 1:00 --end 2:00

# 批量下载
python src/youtube_downloader.py --batch urls.txt --start 1:00 --end 2:00

# 使用配置文件
python src/youtube_downloader.py URL --start 1:00 --end 2:00 --config config.json
```

**更多命令行选项请查看：** [docs/README.md](docs/README.md)

### 方式二：Web 管理界面（推荐）

#### 1. 构建前端项目

```bash
# 构建前端（首次使用）
./build_frontend.sh

# 或手动构建
cd frontend
pnpm install
pnpm build
cd ..
```

#### 2. 启动服务

```bash
# 启动后端服务（会自动提供前端界面）
python app.py

# 访问地址：
# - 前端界面: http://localhost:8000
# - API 文档: http://localhost:8000/docs
```

**前端界面功能：**
- ✅ 创建和管理下载任务
- ✅ 实时查看任务状态和进度
- ✅ 按状态筛选任务
- ✅ 查看任务详情和日志
- ✅ 直接下载生成的文件
- ✅ 取消和删除任务

详细说明：📖 [前端设置指南](FRONTEND_SETUP.md)

### 方式三：API 服务

#### 直接运行

```bash
# 启动服务
python app.py

# 服务将在 http://localhost:8000 运行
# 访问 http://localhost:8000/docs 查看 API 文档
```

#### 使用 Docker Compose（推荐）

```bash
# 启动服务
docker-compose up -d youtube-dl-api

# 查看日志
docker-compose logs -f youtube-dl-api

# 停止服务
docker-compose down
```

服务启动后：
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 下载文件保存在 `./downloads` 目录

#### Docker 环境配置

在启动前，可以修改 `docker-compose.yaml` 中的环境变量：

```yaml
environment:
  # 代理配置（如果需要）
  HTTP_PROXY: "http://host.docker.internal:7890"
  HTTPS_PROXY: "http://host.docker.internal:7890"
  # 下载目录
  DOWNLOADS_DIR: "/app/downloads"
```

#### 🆕 任务管理 API 示例

```bash
# 1. 创建下载任务
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "start_time": "1:00",
    "end_time": "2:00",
    "subtitle_langs": "zh,en"
  }'

# 响应示例：
# {
#   "task_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "pending",
#   "message": "任务已创建，正在处理中",
#   "created_at": "2025-10-27T10:30:00+08:00"
# }

# 2. 查看任务进度（实时）
curl "http://localhost:8000/tasks/TASK_ID"
# 返回详细的进度信息：progress_percentage, current_step, files 等

# 3. 查看任务列表
curl "http://localhost:8000/tasks?status=processing&limit=10"

# 4. 查看任务日志
curl "http://localhost:8000/tasks/TASK_ID/logs"

# 5. 下载文件
curl -O "http://localhost:8000/tasks/TASK_ID/files/video"
curl -O "http://localhost:8000/tasks/TASK_ID/files/audio"
curl -O "http://localhost:8000/tasks/TASK_ID/files/subtitles"

# 6. 取消任务
curl -X POST "http://localhost:8000/tasks/TASK_ID/cancel"

# 7. 删除任务
curl -X DELETE "http://localhost:8000/tasks/TASK_ID"

# 8. 查看统计
curl "http://localhost:8000/stats"
```

**详细文档：**
- 📖 [任务管理系统文档](docs/TASK_MANAGEMENT.md) - 完整功能说明
- 📖 [API 参考文档](docs/API_REFERENCE.md) - API 详细说明
- 📊 [系统架构文档](docs/SYSTEM_OVERVIEW.md) - 架构和技术细节

## 🧪 测试

项目包含完整的测试套件（67个测试用例），确保功能稳定可靠。

### 快速测试

```bash
# 运行所有测试
./run_tests.sh --fast

# 或使用 pytest
pytest tests/ -v
```

### 测试覆盖

- ✅ **单元测试** - 22个测试，覆盖所有API端点
- ✅ **模块测试** - 37个测试，覆盖核心下载逻辑
- ✅ **集成测试** - 8个测试，验证端到端流程
- ✅ **代码覆盖率** - API层 87%

详细信息请参考：
- [测试套件文档](tests/README.md) - 完整测试说明
- [测试摘要报告](TEST_SUMMARY.md) - 测试结果和统计

## 📖 文档

### 快速入门
- 📘 **[快速启动指南](QUICKSTART.md)** - 30秒上手
- 🎨 **[前端设置指南](FRONTEND_SETUP.md)** - Web界面开发和部署 🆕
- 📗 **[任务管理系统](docs/TASK_MANAGEMENT.md)** - 完整功能文档
- 📙 **[系统架构](docs/SYSTEM_OVERVIEW.md)** - 技术架构说明

### 详细文档
- [完整使用指南](docs/README.md) - 命令行工具详细说明
- [API 参考文档](docs/API_REFERENCE.md) - HTTP API 完整文档
- [Cookie 设置](docs/COOKIES_SETUP.md) - Chrome Cookie 配置
- [项目结构](docs/PROJECT_STRUCTURE.md) - 代码结构说明

## 🎯 使用场景

### 场景一：本地快速下载
适合个人使用，直接在本地运行命令行工具。

```bash
./ytdl "https://www.youtube.com/watch?v=..." --start 1:00 --end 2:00
```

### 场景二：本地 API 服务
使用 Docker 运行 API 服务，在本地应用中集成视频下载功能。

```python
import requests

# 创建下载任务
response = requests.post(
    'http://localhost:8000/download',
    json={
        'url': 'https://www.youtube.com/watch?v=...',
        'start_time': '1:00',
        'end_time': '2:00'
    }
)
task_id = response.json()['task_id']
print(f"任务创建: {task_id}")
```

### 场景三：批量自动化处理
在自动化脚本中批量处理视频。

```python
import requests
import time

# 批量下载
for video_url in video_urls:
    response = requests.post(
        'http://localhost:8000/download',
        json={'url': video_url, 'start_time': '0:00', 'end_time': '1:00'}
    )
    task_id = response.json()['task_id']
    
    # 等待任务完成
    while True:
        status = requests.get(f'http://localhost:8000/tasks/{task_id}').json()
        if status['status'] == 'completed':
            print(f"任务完成: {task_id}")
            break
        time.sleep(2)
```

## 🔧 配置

### 配置文件示例 (config.json)

```json
{
  "proxy": "http://127.0.0.1:7890",
  "subtitle_langs": "zh,en,ja",
  "video_quality": "best[height<=720]",
  "audio_quality": "256K",
  "max_retries": 5,
  "output_dir": "downloads"
}
```

### 环境变量

```bash
# API 服务
export PORT=8000
export HOST=0.0.0.0
export DOWNLOADS_DIR=/tmp/downloads

# 代理设置
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

## 📊 项目结构

```
youtube/
├── src/
│   ├── youtube_downloader.py      # 核心下载逻辑
│   ├── database.py                # 🆕 数据库连接管理
│   ├── models.py                  # 🆕 数据模型定义
│   ├── task_service.py            # 🆕 任务管理服务
│   └── downloader/                # 下载器模块
│       ├── video.py               # 视频下载
│       ├── audio.py               # 音频提取
│       ├── subtitle.py            # 字幕下载
│       └── processor.py           # 任务处理
├── app.py                         # FastAPI HTTP 服务
├── init_db.sql                    # 🆕 数据库初始化脚本
├── docker-compose.yaml            # Docker Compose 配置（含数据库）
├── Dockerfile                     # Docker 镜像配置
├── requirements.txt               # Python 依赖
├── QUICKSTART.md                  # 🆕 快速启动指南
├── scripts/                       # 🆕 工具脚本
│   ├── check_db.sh               # 数据库健康检查
│   └── test_api.sh               # API 功能测试
└── docs/                          # 文档目录
    ├── TASK_MANAGEMENT.md         # 🆕 任务管理文档
    ├── SYSTEM_OVERVIEW.md         # 🆕 系统架构文档
    ├── API_REFERENCE.md           # API 文档
    └── README.md                  # 使用指南
```

## ⚠️ 注意事项

1. **依赖要求**
   - Python 3.8+
   - ffmpeg
   - yt-dlp

2. **代理设置**
   - 某些地区可能需要代理访问 YouTube
   - 可通过参数、配置文件或环境变量设置
   - Docker 环境中使用 `host.docker.internal` 访问宿主机代理

3. **Cookie 要求**
   - YouTube 可能需要 Cookie 验证
   - 支持从 Chrome 浏览器导入 Cookie
   - 将 Cookie 文件放在 `cookies/` 目录

4. **YouTube 403 错误**
   - 如果遇到 `HTTP Error 403: Forbidden`,请查看 [403 错误解决方案](YOUTUBE_403_QUICK_FIX.md)
   - 本项目已自动处理此问题,会自动选择最佳客户端
   - 详细说明: [docs/YOUTUBE_403_FIX.md](docs/YOUTUBE_403_FIX.md)

5. **存储空间**
   - 下载文件默认保存在 `downloads/` 目录
   - Docker 环境中通过卷挂载持久化存储
   - 注意磁盘空间，定期清理旧文件

6. **版权问题**
   - 请遵守 YouTube 使用条款
   - 仅用于个人学习和研究
   - 不要用于商业用途

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 请自由使用和修改

## 🔗 相关链接

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 下载工具
- [FFmpeg](https://ffmpeg.org/) - 视频处理工具
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [Docker](https://www.docker.com/) - 容器化平台

## 📝 更新日志

### 🎉 v3.0.0 (2025-10-27) - 任务管理系统
- ✨ **新增完整的任务管理系统**
- ✨ **集成 PostgreSQL 数据库持久化**
- ✨ **实时任务进度跟踪**
- ✨ **任务日志系统**
- ✨ **文件管理和下载功能**
- ✨ **任务统计和分析**
- ✨ **任务控制（取消、删除）**
- 🔧 **重构 API 架构**
- 🔧 **改进错误处理和日志**
- 📚 **完善文档和示例**
- 🛠️ **新增工具脚本**

### v2.0.0 (2025-10-07)
- 🆕 添加 HTTP API 服务
- 🆕 异步任务处理
- 🆕 文件下载接口
- 🆕 Docker 和 Docker Compose 支持
- 📖 完善文档和使用指南

### v1.2.0
- 🆕 批量处理支持
- 🆕 配置文件支持
- 🔧 改进错误处理

### v1.0.0
- 🎉 初始版本发布
- ✅ 基本下载功能
- ✅ 时间段裁剪
- ✅ 音频提取
- ✅ 字幕下载

---

**Star ⭐ 本项目如果对你有帮助！**

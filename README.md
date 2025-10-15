# YouTube 视频片段下载器

一个功能完整的 YouTube 视频下载工具，支持时间段裁剪、音频提取、字幕下载和 HTTP API 服务。

## 🌟 主要特性

- ✅ **精确时间段裁剪** - 使用两阶段下载策略，先下载完整视频再精确切割
- ✅ **音频提取** - 自动提取音频并保存为MP3格式（可配置质量）
- ✅ **字幕下载** - 支持多语言字幕下载（中/英/日等）
- ✅ **HTTP API 服务** - 支持 RESTful API 调用，异步任务处理
- ✅ **HTTP代理支持** - 智能代理配置，支持环境变量和自定义设置
- ✅ **批量处理** - 支持从文件读取多个URL批量下载
- ✅ **配置文件** - 支持JSON配置文件，保存常用设置
- ✅ **Docker 支持** - 提供完整的 Docker 和 Docker Compose 配置
- ✅ **日志系统** - 完整的日志记录，支持文件和控制台输出

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

### 方式二：本地 API 服务

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

#### API 使用示例

```bash
# 1. 创建下载任务
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "start_time": "1:00",
    "end_time": "2:00",
    "download_video": true,
    "download_audio": true
  }'

# 响应示例：
# {
#   "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
#   "status": "pending",
#   "message": "任务已创建，正在处理中"
# }

# 2. 查询任务状态
curl "http://localhost:8000/tasks/TASK_ID"

# 3. 下载完成的文件
curl -O "http://localhost:8000/tasks/TASK_ID/files/video"
curl -O "http://localhost:8000/tasks/TASK_ID/files/audio"
```

**更多 API 详情请查看：** [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

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
youtube_download/
├── src/
│   ├── youtube_downloader.py      # 核心下载逻辑
│   └── downloader/                # 下载器模块
│       ├── video.py               # 视频下载
│       ├── audio.py               # 音频提取
│       ├── subtitle.py            # 字幕下载
│       └── processor.py           # 任务处理
├── app.py                         # FastAPI HTTP 服务
├── test_api.py                    # API 测试脚本
├── Dockerfile                     # Docker 镜像配置
├── docker-compose.yaml            # Docker Compose 配置
├── requirements.txt               # Python 依赖
├── config.json                    # 配置文件
└── docs/                          # 文档目录
    ├── README.md                  # 使用指南
    ├── API_REFERENCE.md           # API 文档
    └── COOKIES_SETUP.md           # Cookie 设置
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

4. **存储空间**
   - 下载文件默认保存在 `downloads/` 目录
   - Docker 环境中通过卷挂载持久化存储
   - 注意磁盘空间，定期清理旧文件

5. **版权问题**
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

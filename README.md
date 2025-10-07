# YouTube 视频片段下载器

一个功能完整的 YouTube 视频下载工具，支持时间段裁剪、音频提取、字幕下载。现已支持 HTTP API 服务，可部署到 Railway.com 等云平台。

## 🌟 主要特性

### 核心功能
- ✅ **精确时间段裁剪** - 使用两阶段下载策略，先下载完整视频再精确切割
- ✅ **音频提取** - 自动提取音频并保存为MP3格式（可配置质量）
- ✅ **字幕下载** - 支持多语言字幕下载（中/英/日等）
- ✅ **HTTP代理支持** - 智能代理配置，支持环境变量和自定义设置
- ✅ **视频ID组织** - 按视频ID创建目录，文件管理更有序

### 新增功能 (v2.0)
- 🆕 **HTTP API 服务** - 支持 RESTful API 调用，可云端部署
- 🆕 **Railway 部署支持** - 一键部署到 Railway.com
- 🆕 **异步任务处理** - 后台处理下载任务，支持并发
- 🆕 **任务状态查询** - 实时查询下载进度和状态
- 🆕 **文件下载接口** - 通过 API 下载处理完成的文件
- 🆕 **批量处理** - 支持从文件读取多个URL批量下载
- 🆕 **配置文件** - 支持JSON配置文件，保存常用设置
- 🆕 **进度条显示** - 批量处理时显示实时进度
- 🆕 **依赖检查** - 自动检查必要工具是否安装
- 🆕 **日志系统** - 完整的日志记录，支持文件和控制台输出
- 🆕 **错误重试** - 智能重试机制，提高下载成功率

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

### 方式一：命令行工具（本地使用）

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

### 方式二：HTTP API 服务（云端部署）

#### 本地运行 API 服务

```bash
# 启动服务
python app.py

# 服务将在 http://localhost:8000 运行
# 访问 http://localhost:8000/docs 查看 API 文档
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

#### 测试 API

```bash
# 快速测试
python test_api.py --quick

# 完整测试（包含下载）
python test_api.py

# 测试远程服务
python test_api.py --url https://your-app.up.railway.app
```

**更多 API 详情请查看：** [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

## ☁️ 云端部署

### 部署到 Railway.com

Railway 是一个现代化的云平台，支持一键部署。

#### 快速部署

1. **Fork 本仓库到你的 GitHub**

2. **访问 [Railway.com](https://railway.com/) 并登录**

3. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你 fork 的仓库

4. **等待部署完成**
   - Railway 会自动检测 Dockerfile
   - 构建和部署大约需要 2-5 分钟

5. **生成公开域名**
   - 在服务设置中点击 "Generate Domain"
   - 获得类似 `your-app.up.railway.app` 的域名

6. **开始使用**
   ```bash
   # 访问 API 文档
   https://your-app.up.railway.app/docs
   
   # 创建下载任务
   curl -X POST "https://your-app.up.railway.app/download" \
     -H "Content-Type: application/json" \
     -d '{"url": "...", "start_time": "1:00", "end_time": "2:00"}'
   ```

**详细部署指南：** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### 其他部署选项

本项目也可以部署到以下平台：
- **Heroku** - 支持 Dockerfile
- **Google Cloud Run** - 无服务器容器
- **AWS ECS/Fargate** - 容器服务
- **DigitalOcean App Platform** - 应用平台
- **Render** - 类似 Railway 的平台

## 📖 文档

- [完整使用指南](docs/README.md) - 命令行工具详细说明
- [API 参考文档](docs/API_REFERENCE.md) - HTTP API 完整文档
- [Railway 部署指南](docs/DEPLOYMENT.md) - 云端部署教程
- [Cookie 设置](docs/COOKIES_SETUP.md) - Chrome Cookie 配置
- [项目结构](docs/PROJECT_STRUCTURE.md) - 代码结构说明

## 🎯 使用场景

### 场景一：本地快速下载
适合个人使用，直接在本地运行命令行工具。

```bash
./ytdl "https://www.youtube.com/watch?v=..." --start 1:00 --end 2:00
```

### 场景二：Web 应用集成
将 API 部署到云端，在 Web 应用中集成视频下载功能。

```javascript
// 前端调用 API
const response = await fetch('https://your-app.up.railway.app/download', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: videoUrl,
    start_time: startTime,
    end_time: endTime
  })
});
const { task_id } = await response.json();
```

### 场景三：自动化工作流
在自动化脚本中使用 API，批量处理视频。

```python
import requests

# 批量下载
for video_url in video_urls:
    response = requests.post(
        'https://your-app.up.railway.app/download',
        json={'url': video_url, 'start_time': '0:00', 'end_time': '1:00'}
    )
    task_id = response.json()['task_id']
    print(f"任务创建: {task_id}")
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

## 📊 架构

```
youtube_download/
├── src/
│   └── youtube_downloader.py  # 核心下载逻辑
├── app.py                      # FastAPI HTTP 服务
├── test_api.py                 # API 测试脚本
├── Dockerfile                  # Docker 镜像配置
├── railway.json                # Railway 部署配置
├── requirements.txt            # Python 依赖
├── config.json                 # 配置文件
└── docs/                       # 文档目录
    ├── README.md               # 使用指南
    ├── API_REFERENCE.md        # API 文档
    ├── DEPLOYMENT.md           # 部署指南
    └── COOKIES_SETUP.md        # Cookie 设置
```

## ⚠️ 注意事项

1. **依赖要求**
   - Python 3.8+
   - ffmpeg
   - yt-dlp

2. **代理设置**
   - 某些地区可能需要代理访问 YouTube
   - 可通过参数、配置文件或环境变量设置

3. **Cookie 要求**
   - YouTube 可能需要 Cookie 验证
   - 支持从 Chrome 浏览器导入 Cookie

4. **存储空间**
   - Railway 等平台使用临时文件系统
   - 文件会在服务重启后丢失
   - 建议及时下载完成的文件

5. **资源限制**
   - 免费套餐有资源限制
   - 建议下载较短的视频片段
   - 注意并发任务数量

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
- [Railway](https://railway.com/) - 部署平台

## 📝 更新日志

### v2.0.0 (2025-10-07)
- 🆕 添加 HTTP API 服务
- 🆕 支持 Railway 一键部署
- 🆕 异步任务处理
- 🆕 文件下载接口
- 📖 完善文档和部署指南

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

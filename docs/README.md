# YouTube视频片段下载器

一个功能完整的YouTube视频下载工具，支持时间段裁剪、音频提取、字幕下载，使用改进的两阶段下载策略确保精确的时间段控制。

## 🌟 主要特性

### 核心功能
- ✅ **精确时间段裁剪** - 使用两阶段下载策略，先下载完整视频再精确切割
- ✅ **音频提取** - 自动提取音频并保存为MP3格式（可配置质量）
- ✅ **字幕下载** - 支持多语言字幕下载（中/英/日等）
- ✅ **HTTP代理支持** - 智能代理配置，支持环境变量和自定义设置
- ✅ **视频ID组织** - 按视频ID创建目录，文件管理更有序

### 新增功能 (v2.0)
- 🆕 **批量处理** - 支持从文件读取多个URL批量下载
- 🆕 **配置文件** - 支持JSON配置文件，保存常用设置
- 🆕 **进度条显示** - 批量处理时显示实时进度
- 🆕 **依赖检查** - 自动检查必要工具是否安装
- 🆕 **日志系统** - 完整的日志记录，支持文件和控制台输出
- 🆕 **错误重试** - 智能重试机制，提高下载成功率
- 🆕 **磁盘空间检查** - 下载前检查可用存储空间

### 技术改进
- ✅ **Cookie支持** - 支持浏览器Cookie验证
- ✅ **多格式支持** - 支持多种时间格式输入
- ✅ **质量配置** - 可配置视频和音频质量
- ✅ **安全增强** - 改进代理配置安全性

## 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 或者手动安装
pip install yt-dlp tqdm

# 安装 ffmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载并添加到 PATH
```

## 使用方法

### 基本用法

```bash
# 一键执行 - 最简单的方式
./ytdl "https://www.youtube.com/watch?v=yJqOe-tKj-U" --start 2:00 --end 3:00

# 或者直接使用Python
python src/youtube_downloader.py "https://www.youtube.com/watch?v=yJqOe-tKj-U" \
    --start 2:00 --end 3:00

# 查看帮助
./ytdl --help
```

### 新功能使用

#### 批量下载
```bash
# 从文件批量下载（需要指定时间段）
python src/youtube_downloader.py --batch urls.txt --start 1:00 --end 2:00

# 使用配置文件
python src/youtube_downloader.py --batch urls.txt --config config.json
```

#### 配置文件
创建 `config.json` 文件：
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

#### 高级选项
```bash
# 自定义质量和重试次数
python src/youtube_downloader.py "URL" --start 1:00 --end 2:00 \
    --video-quality "best[height<=720]" \
    --audio-quality "256K" \
    --max-retries 5

# 只下载音频
python src/youtube_downloader.py "URL" --start 1:00 --end 2:00 --no-video

# 自定义代理
python src/youtube_downloader.py "URL" --start 1:00 --end 2:00 \
    --proxy "http://your-proxy:port"
```

### 改进特性

- **两阶段下载策略**: 先下载完整视频，再使用ffmpeg精确切割，确保时间段准确
- **HTTP代理支持**: 默认使用 `http://127.0.0.1:7890`，兼容性更好
- **视频质量优化**: 限制在480p以下，加快下载速度
- **文件组织**: 按视频ID创建目录，文件管理更有序

### 时间格式

支持以下时间格式：
- `HH:MM:SS` - 小时:分钟:秒 (例如: `00:01:30`)
- `MM:SS` - 分钟:秒 (例如: `1:30`)
- 纯秒数 (例如: `90`)

### 示例

```bash
# 下载视频第1分钟到第2分钟的片段（推荐方式）
./ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 00:01:00 --end 00:02:00

# 使用分钟格式
./ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 1:00 --end 2:00

# 使用纯秒数
./ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 60 --end 120

# 指定输出目录
./ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 1:00 --end 2:00 --output-dir ./videos

# 只下载音频，不下载视频
./ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 1:00 --end 2:00 --no-video

# 只下载视频，不下载字幕
./ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 1:00 --end 2:00 --no-subtitles

# 指定字幕语言（仅英文字幕）
./ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 1:00 --end 2:00 --sub-langs en

# 指定多种字幕语言（英文和日文）
./ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 1:00 --end 2:00 --sub-langs en,ja

# 直接使用Python脚本
python src/youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 1:00 --end 2:00
```

## 输出文件

文件按视频ID组织，每个视频创建独立目录：

```
downloads/
└── {视频ID}/
    ├── segment_{时间段}.mp4          # 视频文件
    ├── audio_{时间段}.mp3            # 音频文件
    └── subtitles_{时间段}.{语言}.vtt  # 字幕文件
```

### 示例输出：
```
downloads/
└── yJqOe-tKj-U/
    ├── segment_2_00-3_00.mp4        # 视频片段
    ├── audio_2_00-3_00.mp3          # 音频片段
    ├── subtitles_2_00-3_00.en.vtt   # 英文字幕
    └── subtitles_2_00-3_00.zh.vtt   # 中文字幕
```

## 字幕支持

- 自动下载自动生成字幕
- 默认语言：中文、英文（可通过 `--sub-langs` 自定义）
- 支持 VTT 格式
- 按时间段自动命名

## 注意事项

1. **依赖要求**: 确保已安装 Python 3、ffmpeg 和 yt-dlp
2. **代理设置**: 默认使用 `http://127.0.0.1:7890`，可通过 `--proxy` 参数自定义
3. **视频质量**: 默认限制在480p以下，如需更高质量请修改源代码
4. **存储空间**: 确保有足够的存储空间
5. **版权问题**: 请遵守 YouTube 的使用条款和版权规定
6. **Cookie要求**: YouTube需要cookie验证，请查看 [Cookie设置指南](COOKIES_SETUP.md)

## 常见问题

### Q: 下载速度很慢怎么办？
A: 可以尝试使用代理或VPN，或者选择较低的视频质量。

### Q: 字幕下载失败怎么办？
A: 并非所有视频都有自动字幕，可以尝试手动上传字幕或使用语音识别工具。

### Q: 音频提取失败怎么办？
A: 确保 ffmpeg 正确安装并添加到系统 PATH 中。

### Q: 时间截取不准确？
A: 视频编码的关键帧可能影响截取精度，建议前后增加几秒钟的缓冲时间。

## 故障排除

### 检查依赖安装

```bash
# 检查 yt-dlp
yt-dlp --version

# 检查 ffmpeg
ffmpeg -version
```

### 调试模式

```bash
# 添加 -v 参数获取详细输出
python youtube_segment_downloader.py <URL> --start <start> --end <end>
```

## 更新日志

- v1.0.0: 初始版本，支持基本功能
- v1.1.0: 改进字幕处理，支持多种格式
- v1.2.0: 优化时间戳处理逻辑

## 许可证

MIT License - 请自由使用和修改

## 贡献

欢迎提交 Issue 和 Pull Request！
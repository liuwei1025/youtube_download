# YouTube视频片段下载器

一个功能完整的YouTube视频下载工具，支持时间段裁剪、音频提取、字幕下载，完美适配SOCKS代理环境。

## 🌟 主要特性

- ✅ **时间段裁剪** - 精确下载指定时间段的视频片段
- ✅ **音频提取** - 自动提取音频并保存为MP3格式
- ✅ **字幕下载** - 支持多语言字幕下载（中/英/日等）
- ✅ **SOCKS代理** - 完美支持SOCKS5代理环境
- ✅ **视频ID命名** - 按视频ID自动命名文件，便于管理
- ✅ **Cookie支持** - 支持浏览器Cookie和Cookie文件
- ✅ **多格式支持** - 支持多种时间格式输入
- ✅ 自动处理字幕时间戳偏移

## 安装依赖

```bash
# 安装 Python 依赖
pip install yt-dlp

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

所有下载文件按视频ID自动命名，格式统一：

```
{视频ID}_{类型}_{时间段}.{扩展名}
```

### 示例输出：
1. **视频文件**: `yJqOe-tKj-U_segment_2:00-3:00_20241007_143022.mp4`
2. **音频文件**: `yJqOe-tKj-U_audio_2:00-3:00_20241007_143022.mp3`
3. **字幕文件**: `yJqOe-tKj-U_subtitles_2:00-3:00.en.vtt`

### 当前下载示例：
```
downloads/completed/
├── yJqOe-tKj-U_subtitles_2:00-3:00.en.vtt  # 英文，320KB
└── yJqOe-tKj-U_subtitles_2:00-3:00.ja.vtt  # 日文，408KB
```

## 字幕支持

- 自动下载自动生成字幕
- 优先下载中文简体字幕，然后是英文、日文
- 自动截取对应时间段的字幕内容
- 支持 VTT、SRT、ASS 格式

## 注意事项

1. **网络要求**: 需要稳定的网络连接
2. **存储空间**: 确保有足够的存储空间
3. **版权问题**: 请遵守 YouTube 的使用条款和版权规定
4. **时间精度**: 时间截取精度取决于视频的关键帧
5. **Cookie要求**: YouTube现在需要cookie验证，请查看 [Cookie设置指南](COOKIES_SETUP.md)

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
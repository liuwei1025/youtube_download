# YouTube 下载器使用指南

## 快速开始

项目提供了两个版本的下载器：
- `ytdl`: 原始版本
- `ytdl2`: 改进版本（推荐）

### 基本用法

```bash
# 下载 2:00-3:00 的视频片段
./ytdl2 "https://www.youtube.com/watch?v=VIDEO_ID" --start 2:00 --end 3:00

# 只下载音频
./ytdl2 "VIDEO_URL" --start 2:00 --end 3:00 --no-video

# 下载指定语言的字幕
./ytdl2 "VIDEO_URL" --start 2:00 --end 3:00 --sub-langs en,ja
```

### 改进版本（ytdl2）的特点

1. 更精确的时间段控制
   - 使用两阶段下载策略
   - 先下载稍长的片段
   - 使用 ffmpeg 精确切割

2. 更好的代理支持
   - 使用 HTTP 代理替代 SOCKS5
   - 默认代理地址：http://127.0.0.1:7890

3. 优化的下载设置
   - 视频质量限制在 480p 以下
   - 音频质量保持 192K
   - 自动清理临时文件

### 命令行选项

```bash
选项:
  --output-dir DIR     输出目录 (默认: downloads)
  --no-video          不下载视频
  --no-audio          不下载音频
  --no-subtitles      不下载字幕
  --sub-langs LANGS   字幕语言，逗号分隔 (默认: zh-CN,zh,en,ja)
                      例如: en,ja 或 zh-CN,en
```

### 时间格式支持

支持以下时间格式：
- `HH:MM:SS`: 例如 `01:30:45`
- `MM:SS`: 例如 `05:30`
- 秒数: 例如 `90`

### 输出文件

下载的文件会保存在 `downloads` 目录（可通过 `--output-dir` 修改），文件名格式：
- 视频：`VIDEO_ID_segment_START-END.mp4`
- 音频：`VIDEO_ID_audio_START-END.mp3`
- 字幕：`VIDEO_ID_subtitles_START-END.LANG.vtt`

### 注意事项

1. 确保系统已安装：
   - Python 3
   - ffmpeg
   - yt-dlp（会自动安装）

2. 代理设置：
   - 默认使用 http://127.0.0.1:7890
   - 如需修改，请编辑源代码中的 `setup_proxy()` 函数

3. 视频质量：
   - 默认限制在 480p 以下，以加快下载速度
   - 如需更高质量，可修改源代码中的 `format` 参数
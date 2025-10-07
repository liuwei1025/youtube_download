# YouTube下载器项目结构

## 📁 目录结构

```
youtube_download/
├── src/                          # 源代码目录
│   └── youtube_downloader.py    # 主要下载器脚本（改进版）
├── docs/                         # 文档目录
│   ├── README.md                 # 项目主要说明
│   ├── COOKIES_SETUP.md          # Cookie设置指南
│   └── PROJECT_STRUCTURE.md      # 项目结构说明
├── downloads/                    # 下载文件目录（按视频ID组织）
│   └── {VIDEO_ID}/               # 每个视频的独立目录
│       ├── segment_*.mp4         # 视频片段
│       ├── audio_*.mp3           # 音频片段
│       └── subtitles_*.vtt       # 字幕文件
├── ytdl                          # 一键执行脚本
└── requirements.txt              # Python依赖
```

## 🎯 文件命名规范

### 下载文件命名格式
文件按视频ID组织在独立目录中，命名格式：

```
{类型}_{时间段}.{扩展名}
```

#### 示例：
- **视频文件**: `segment_2_00-3_00.mp4`
- **音频文件**: `audio_2_00-3_00.mp3`
- **字幕文件**: `subtitles_2_00-3_00.en.vtt`

### 目录组织
每个视频ID创建独立目录，便于管理：
```
downloads/
├── yJqOe-tKj-U/
│   ├── segment_2_00-3_00.mp4
│   ├── audio_2_00-3_00.mp3
│   └── subtitles_2_00-3_00.en.vtt
└── dQw4w9WgXcQ/
    ├── segment_1_00-2_00.mp4
    └── audio_1_00-2_00.mp3
```

## 🚀 核心脚本说明

### 1. `youtube_downloader.py`
- **功能**: 改进版下载器，支持时间片段裁剪、音频提取、字幕下载
- **特点**: 
  - 两阶段下载策略（先下载完整视频，再精确切割）
  - HTTP代理支持（默认 http://127.0.0.1:7890）
  - 视频质量限制在480p以下
  - 按视频ID组织文件目录
- **用法**: `python src/youtube_downloader.py URL --start TIME --end TIME`

### 2. `ytdl`
- **功能**: 一键执行脚本
- **特点**: 
  - 简化参数输入
  - 自动调用主脚本
  - 支持所有主脚本参数
- **用法**: `./ytdl URL --start TIME --end TIME [选项]`

## 🎯 使用示例

### 基础使用
```bash
# 一键执行
./ytdl "https://www.youtube.com/watch?v=yJqOe-tKj-U" --start 2:00 --end 3:00

# 指定输出目录
./ytdl "URL" --start 2:00 --end 3:00 --output-dir ./my_videos

# 只下载音频
./ytdl "URL" --start 2:00 --end 3:00 --no-video

# 指定字幕语言
./ytdl "URL" --start 2:00 --end 3:00 --sub-langs en,ja

# 自定义代理
./ytdl "URL" --start 2:00 --end 3:00 --proxy http://127.0.0.1:8080
```

### 常用语言代码
- `zh` - 中文
- `en` - 英语  
- `ja` - 日语
- `ko` - 韩语
- `es` - 西班牙语
- `fr` - 法语

## 🎯 特色功能

1. **两阶段下载策略**: 先下载完整视频，再使用ffmpeg精确切割，确保时间段准确
2. **视频ID目录组织**: 每个视频创建独立目录，文件管理更有序
3. **HTTP代理支持**: 默认支持HTTP代理，兼容性更好
4. **质量优化**: 视频限制在480p以下，加快下载速度
5. **多语言字幕**: 支持多语言字幕下载
6. **时间格式灵活**: 支持多种时间格式 (HH:MM:SS, MM:SS, 秒数)

## 📋 文件管理

### 清理缓存
```bash
# 清理Python缓存
rm -rf __pycache__/
```

### 查看下载历史
```bash
# 查看所有下载的视频
ls -la downloads/

# 查看特定视频的文件
ls -la downloads/VIDEO_ID/
```

这个改进的结构确保了更好的文件组织和更精确的时间段控制！🚀
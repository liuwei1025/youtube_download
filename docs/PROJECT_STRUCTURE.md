# YouTube下载器项目结构

## 📁 目录结构

```
YouTube/
├── src/                          # 源代码目录
│   ├── youtube_segment_downloader.py    # 主要下载器脚本
│   ├── youtube_downloader_cli.py       # SOCKS代理命令行工具
│   ├── test_cookie_functionality.py    # Cookie功能测试
│   ├── test_script.py                  # 综合测试脚本
│   └── download_segment_proxy.sh       # SOCKS代理专用脚本
├── docs/                         # 文档目录
│   ├── README.md                 # 项目主要说明
│   ├── COOKIES_SETUP.md          # Cookie设置指南
│   ├── socks_download_solution.md # SOCKS代理解决方案
│   ├── PROJECT_STRUCTURE.md      # 项目结构说明
│   └── quick_start_guide.md      # 快速开始指南
├── examples/                     # 示例和使用案例
├── downloads/                    # 下载文件目录
│   ├── completed/                # 已完成的下载
│   └── temp/                     # 临时下载文件
└── requirements.txt              # Python依赖
```

## 🎯 文件命名规范

### 下载文件命名格式
所有下载的文件都按照以下格式命名：

```
{视频ID}_{类型}_{时间段}.{扩展名}
```

#### 示例：
- **视频文件**: `yJqOe-tKj-U_segment_2:00-3:00_20241007_143022.mp4`
- **音频文件**: `yJqOe-tKj-U_audio_2:00-3:00_20241007_143022.mp3`
- **字幕文件**: `yJqOe-tKj-U_subtitles_2:00-3:00.en.vtt`

### 类型标识
- `segment`: 视频片段
- `audio`: 音频片段
- `subtitles`: 字幕文件

## 🚀 核心脚本说明

### 1. `youtube_downloader.py`
- **功能**: 主要下载器，支持时间片段裁剪、音频提取、字幕下载
- **特点**: SOCKS代理优化、字幕语言指定、按视频ID命名
- **用法**: `python src/youtube_downloader.py URL --start TIME --end TIME`

### 2. `ytdl`
- **功能**: 一键执行脚本，自动配置SOCKS代理
- **特点**: 简化参数，自动代理检测
- **用法**: `./ytdl URL --start TIME --end TIME`
- **命名**: 统一按视频ID命名格式

## 🎯 使用示例

### 基础使用
```bash
# 一键执行
./ytdl "https://www.youtube.com/watch?v=yJqOe-tKj-U" --start 2:00 --end 3:00

# 指定字幕语言
./ytdl "https://www.youtube.com/watch?v=yJqOe-tKj-U" --start 2:00 --end 3:00 --sub-langs en

# 多种字幕语言
./ytdl "https://www.youtube.com/watch?v=yJqOe-tKj-U" --start 2:00 --end 3:00 --sub-langs en,ja
```

### 字幕语言指定
```bash
# 仅英文字幕
./ytdl "URL" --start 2:00 --end 3:00 --sub-langs en

# 英文和日文字幕
./ytdl "URL" --start 2:00 --end 3:00 --sub-langs en,ja

# 中文简体和繁体字幕
./ytdl "URL" --start 2:00 --end 3:00 --sub-langs zh-CN,zh-TW
```

### 常用语言代码
- `en` - 英语
- `ja` - 日语
- `zh-CN` - 中文简体
- `zh-TW` - 中文繁体
- `ko` - 韩语
- `es` - 西班牙语
- `fr` - 法语
- `de` - 德语

## 📊 当前下载示例

### 已完成的下载 (downloads/completed/)
```
yJqOe-tKj-U_subtitles_2:00-3:00.en.vtt      # 英文，320KB
yJqOe-tKj-U_subtitles_2:00-3:00.ja.vtt      # 日文，408KB
```

### 文件内容预览
**2-3分钟时间段包含内容：**
- 02:30-02:33: "Good evening. We're live."
- 02:33-02:34: "live on YouTube,"
- 02:34-02:37: "Instagram, and Facebook. I'm very"

## 🔧 使用示例

### 基础使用
```bash
# 使用主要下载器
python src/youtube_segment_downloader.py "URL" --start 2:00 --end 3:00 --cookies-from-browser chrome

# 使用SOCKS代理CLI
python src/youtube_downloader_cli.py "URL" --start 2:00 --end 3:00

# 使用一键脚本
./src/download_segment_proxy.sh "URL" 120 180
```

### 文件输出
所有输出文件将保存在 `downloads/completed/` 目录，按照视频ID和时间命名：
- `{video_id}_segment_{start}-{end}_{timestamp}.mp4`
- `{video_id}_audio_{start}-{end}_{timestamp}.mp3`
- `{video_id}_subtitles_{start}-{end}.{lang}.vtt`

## 📋 文件管理

### 清理临时文件
```bash
# 清理临时下载文件
rm -rf downloads/temp/*

# 清理缓存
rm -rf __pycache__/
```

### 查看下载历史
```bash
ls -la downloads/completed/
```

## 🎯 特色功能

1. **视频ID识别**: 自动从URL提取视频ID用于文件命名
2. **时间格式化**: 支持多种时间格式 (HH:MM:SS, MM:SS, 秒数)
3. **代理支持**: 完美支持SOCKS5代理环境
4. **多语言字幕**: 自动下载中英日等多语言字幕
5. **文件整理**: 按视频ID和时间自动组织文件结构

这个结构确保了每个下载的文件都能通过文件名快速识别其来源和内容！🚀
# 字幕烧录功能使用指南

## 功能简介

YouTube下载器现在支持自动将字幕烧录到下载的视频中，让您获得带有内嵌字幕的视频文件。

## 快速开始

### 基本使用（默认启用字幕烧录）

```bash
python src/youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" \
  --start 00:30 \
  --end 02:00
```

这将生成：
- `segment_00_30-02_00.mp4` - 原始视频
- `segment_00_30-02_00_with_subs.mp4` - **带字幕的视频**（新增）
- `audio_00_30-02_00.mp3` - 音频
- `subtitles_00_30-02_00.en.vtt` - 字幕文件

### 指定字幕语言

```bash
# 下载中文和英文字幕
python src/youtube_downloader.py "YOUR_VIDEO_URL" \
  --start 00:30 --end 02:00 \
  --sub-langs zh,en

# 仅下载英文字幕
python src/youtube_downloader.py "YOUR_VIDEO_URL" \
  --start 00:30 --end 02:00 \
  --sub-langs en
```

### 禁用字幕烧录

如果您只需要原始视频和独立的字幕文件：

```bash
python src/youtube_downloader.py "YOUR_VIDEO_URL" \
  --start 00:30 --end 02:00 \
  --no-burn-subtitles
```

## 功能特性

### ✅ 自动化处理
- 下载视频后自动烧录字幕
- 无需手动操作
- 保留原始视频和字幕文件

### ✅ 智能容错
- 自动检测FFmpeg功能
- 支持两种烧录方式（详见下方）
- 烧录失败时保留原始文件

### ✅ 灵活配置
- 可选择是否烧录字幕
- 支持多种字幕语言
- 自定义输出目录

## 技术实现

### 方式1: 字幕滤镜（推荐）

**要求**: FFmpeg需要包含libass支持

**效果**: 字幕直接烧录到视频画面上

**优点**:
- ✅ 字幕永久显示在画面上
- ✅ 所有播放器都能正常播放
- ✅ 支持自定义字幕样式
- ✅ 适合分享和上传到平台

**命令示例**:
```bash
ffmpeg -i video.mp4 \
  -vf "subtitles=subtitle.vtt:force_style='FontSize=20,PrimaryColour=&H00FFFFFF'" \
  -c:a copy output.mp4
```

### 方式2: 嵌入字幕流（备用）

**要求**: 标准FFmpeg即可

**效果**: 字幕作为subtitle track嵌入

**优点**:
- ✅ 无需特殊FFmpeg版本
- ✅ 文件体积略小
- ✅ 可以控制字幕开关

**限制**:
- ⚠️ 需要播放器支持字幕流
- ⚠️ 某些平台可能不显示

**命令示例**:
```bash
ffmpeg -i video.mp4 -i subtitle.vtt \
  -c:v libx264 -c:a copy -c:s mov_text \
  output.mp4
```

### 自动切换逻辑

程序会自动检测FFmpeg功能并选择最佳方式：

```python
# 伪代码
if subtitles_filter_available:
    使用方式1（字幕烧录到画面）
else:
    自动降级到方式2（嵌入字幕流）
    输出提示信息
```

## 查看生成的文件

### 查看文件列表

```bash
# 查看下载的所有文件
ls -lh downloads/VIDEO_ID/

# 示例输出:
# segment_00_30-02_00.mp4           1.5M  原始视频
# segment_00_30-02_00_with_subs.mp4 1.8M  带字幕视频
# audio_00_30-02_00.mp3             500K  音频
# subtitles_00_30-02_00.en.vtt      10K   字幕
```

### 验证字幕是否嵌入

```bash
# 查看视频信息
ffmpeg -i downloads/VIDEO_ID/segment_*_with_subs.mp4

# 如果有字幕，会看到类似输出:
# Stream #0:2(eng): Subtitle: mov_text
```

### 测试播放

```bash
# 使用VLC播放器
vlc downloads/VIDEO_ID/segment_*_with_subs.mp4

# 使用mpv播放器
mpv downloads/VIDEO_ID/segment_*_with_subs.mp4
```

## 高级配置

### 批量处理

创建URL列表文件 `urls.txt`:
```
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

批量下载并烧录字幕:
```bash
python src/youtube_downloader.py \
  --batch urls.txt \
  --start 00:30 --end 02:00
```

### 使用配置文件

创建 `config.json`:
```json
{
  "start_time": "00:30",
  "end_time": "02:00",
  "proxy": "http://127.0.0.1:7890",
  "subtitle_langs": "zh,en",
  "burn_subtitles": true,
  "video_quality": "best[height<=720]",
  "audio_quality": "192K"
}
```

使用配置文件:
```bash
python src/youtube_downloader.py "YOUR_VIDEO_URL" --config config.json
```

### 字幕样式自定义

如果使用支持libass的FFmpeg，可以自定义字幕样式：

修改 `src/youtube_downloader.py` 中的字幕样式参数:
```python
# 当前默认样式
force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=1,Shadow=1'

# 可以修改为:
# 大字体黄色字幕
force_style='FontSize=24,PrimaryColour=&H00FFFF00,OutlineColour=&H00000000,Outline=2'

# 粗体红色字幕
force_style='FontSize=22,PrimaryColour=&H000000FF,Bold=1,Outline=2'
```

颜色格式说明:
- `&H00FFFFFF` - 白色
- `&H00000000` - 黑色  
- `&H00FFFF00` - 黄色
- `&H000000FF` - 红色
- `&H0000FF00` - 绿色

## 性能考虑

### 处理时间

字幕烧录需要重新编码视频：

| 视频时长 | 分辨率 | 预估时间 |
|---------|--------|---------|
| 1分钟   | 480p   | ~30秒   |
| 1分钟   | 720p   | ~60秒   |
| 5分钟   | 480p   | ~2.5分钟 |
| 10分钟  | 720p   | ~10分钟 |

### 存储空间

- 原始视频: 基准
- 带字幕视频: +10-30%（取决于编码设置）
- 字幕文件: 可忽略不计（通常<100KB）

### 优化建议

1. **并行处理**: 批量下载时会自动并行处理多个视频
2. **视频质量**: 使用较低分辨率可加快处理速度
3. **磁盘空间**: 确保有足够空间存储临时文件

## 故障排除

### 问题1: 字幕烧录失败

**症状**: 看到错误信息 "字幕烧录失败"

**可能原因**:
1. FFmpeg不支持字幕滤镜
2. 字幕文件损坏
3. 视频文件损坏

**解决方法**:
```bash
# 1. 检查FFmpeg功能
ffmpeg -filters | grep subtitles

# 2. 如果没有输出，安装完整版FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux

# 3. 查看详细日志
tail -f youtube_downloader.log
```

### 问题2: 字幕未显示

**症状**: 生成的视频没有字幕

**检查步骤**:
1. 确认字幕文件已下载: `ls downloads/VIDEO_ID/subtitles_*`
2. 检查视频流信息: `ffmpeg -i video_with_subs.mp4`
3. 使用支持字幕的播放器测试

### 问题3: 字幕乱码

**原因**: VTT字幕编码问题

**解决方法**:
```bash
# 转换字幕编码为UTF-8
iconv -f ISO-8859-1 -t UTF-8 subtitle.vtt > subtitle_utf8.vtt
```

### 问题4: 处理速度慢

**优化方法**:
1. 降低视频质量: `--video-quality "best[height<=480]"`
2. 使用硬件加速（需要支持的FFmpeg）
3. 关闭不需要的功能: `--no-audio`

## 完整示例

### 示例1: 下载会议录像片段

```bash
# 下载10分钟会议录像，包含中英文字幕
python src/youtube_downloader.py \
  "https://www.youtube.com/watch?v=conference_video" \
  --start 15:30 \
  --end 25:30 \
  --sub-langs zh,en \
  --video-quality "best[height<=720]" \
  --output-dir meetings
```

### 示例2: 下载教程视频

```bash
# 下载5分钟教程，仅英文字幕
python src/youtube_downloader.py \
  "https://www.youtube.com/watch?v=tutorial_video" \
  --start 2:00 \
  --end 7:00 \
  --sub-langs en \
  --no-audio  # 不需要单独的音频文件
```

### 示例3: 批量下载课程

```bash
# 创建课程URL列表
cat > course_videos.txt << EOF
https://www.youtube.com/watch?v=lesson1
https://www.youtube.com/watch?v=lesson2
https://www.youtube.com/watch?v=lesson3
EOF

# 批量下载
python src/youtube_downloader.py \
  --batch course_videos.txt \
  --start 0:00 \
  --end 10:00 \
  --sub-langs zh,en \
  --output-dir courses
```

## 相关文档

- [FFmpeg 安装指南](FFMPEG_SETUP.md) - 如何安装支持字幕烧录的FFmpeg
- [测试总结](../tests/SUBTITLE_BURN_TEST_SUMMARY.md) - 功能测试报告
- [API 参考](API_REFERENCE.md) - 完整的API文档

## 常见问题

**Q: 字幕烧录会降低视频质量吗？**  
A: 使用默认设置，视频会被重新编码，可能会有轻微质量损失。可以通过调整编码参数来保持质量。

**Q: 可以烧录自定义字幕文件吗？**  
A: 可以。将您的VTT字幕文件放在正确的位置，程序会自动使用它。

**Q: 支持其他字幕格式吗？**  
A: 当前主要支持VTT格式。SRT和ASS格式的支持正在开发中。

**Q: 能否只生成带字幕的视频，不保留原始视频？**  
A: 可以通过修改代码实现，或者在处理完成后手动删除原始视频。

**Q: 批量处理时如何提高速度？**  
A: 程序已经支持并行处理（默认3个并发），可以通过修改代码调整并发数量。

## 反馈与贡献

如果您遇到问题或有改进建议，欢迎：
1. 提交 Issue
2. 创建 Pull Request
3. 查看项目文档获取更多信息

---

**提示**: 为了获得最佳体验，建议安装包含libass支持的完整版FFmpeg。详见 [FFmpeg 安装指南](FFMPEG_SETUP.md)。


# 快速开始指南 - 处理YouTube视频2-3分钟片段

## 🎯 目标
处理视频 https://www.youtube.com/watch?v=yJqOe-tKj-U 的2分钟到3分钟片段（音视频+字幕）

## 🚀 最简单的方法

### 步骤1: 安装Chrome扩展
1. 打开Chrome浏览器
2. 访问Chrome网上应用店
3. 搜索"Get cookies.txt LOCALLY"
4. 点击"添加到Chrome"

### 步骤2: 导出Cookie
1. 在Chrome中访问 https://www.youtube.com/watch?v=yJqOe-tKj-U
2. 点击浏览器右上角的扩展图标（拼图形状）
3. 找到"Get cookies.txt LOCALLY"并点击
4. 点击"Export as Netscape"
5. 将内容保存为 `cookies.txt` 文件

### 步骤3: 运行下载脚本
```bash
python3 youtube_segment_downloader.py "https://www.youtube.com/watch?v=yJqOe-tKj-U" \
    --start 2:00 \
    --end 3:00 \
    --cookies cookies.txt \
    --output-dir downloads
```

## 📁 输出文件
脚本将在 `downloads/` 目录生成：
1. **视频文件**: `youtube_segment_*.mp4` (2-3分钟片段)
2. **音频文件**: `youtube_segment_*_audio.mp3` (提取的音频)
3. **字幕文件**: `youtube_segment_*_subtitles.vtt` (中文字幕优先)

## ⚡ 替代方案
如果上述方法遇到问题，你可以：

### 使用yt-dlp直接测试
```bash
# 先测试yt-dlp是否能通过Chrome访问
yt-dlp --cookies-from-browser chrome --get-title "https://www.youtube.com/watch?v=yJqOe-tKj-U"
```

### 简化版本（仅视频）
```bash
python3 youtube_segment_downloader.py "https://www.youtube.com/watch?v=yJqOe-tKj-U" \
    --start 2:00 --end 3:00 \
    --cookies cookies.txt \
    --no-audio --no-subtitles \
    --output-dir downloads
```

## 🔍 验证结果
运行成功后，检查下载目录：
```bash
ls -la downloads/
```

## 📞 遇到问题？
1. **Cookie导出失败** → 确保已在Chrome中登录YouTube
2. **下载超时** → 检查网络连接，重试几次
3. **字幕下载失败** → 并非所有视频都有自动字幕

我已经为你准备好了完整的脚本和环境，按照上述步骤操作即可成功下载指定片段！
# YouTube Cookie 设置指南

由于YouTube现在需要验证用户不是机器人，我们需要提供cookie才能下载视频。

## 🚀 最简单的方法：使用浏览器Cookie（推荐）

yt-dlp内置了从主流浏览器直接获取cookie的功能，无需手动导出：

```bash
# 使用Chrome浏览器cookie
python src/youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --start 0 --end 30

# 或者使用一键脚本
./ytdl "https://www.youtube.com/watch?v=VIDEO_ID" --start 0 --end 30
```

**要求**：确保在运行脚本前已经使用相应的浏览器访问过YouTube。

## 获取Cookie文件的方法（备选方案）

### 方法1: 使用浏览器扩展 (推荐)
1. 安装浏览器扩展:
   - Chrome: "Get cookies.txt LOCALLY"
   - Firefox: "Export Cookies"
   - Edge: "Cookie-Editor"

2. 访问YouTube.com并登录你的账户

3. 使用扩展导出cookie，保存为cookies.txt文件

### 方法2: 使用yt-dlp的cookies-from-browser选项
```bash
# 从Chrome浏览器获取cookie
yt-dlp --cookies-from-browser chrome "https://www.youtube.com/watch?v=VIDEO_ID"

# 从Firefox浏览器获取cookie
yt-dlp --cookies-from-browser firefox "https://www.youtube.com/watch?v=VIDEO_ID"

# 从Edge浏览器获取cookie
yt-dlp --cookies-from-browser edge "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 方法3: 手动创建cookie文件
创建一个名为`cookies.txt`的文件，内容格式如下:
```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1234567890	cookie_name	cookie_value
```

## 使用Cookie下载

### 使用下载器（推荐）
```bash
# 基本使用（自动使用Chrome cookie）
./ytdl "https://www.youtube.com/watch?v=jNQXAC9IVRw" --start 0 --end 5

# 或者直接使用Python脚本
python src/youtube_downloader.py "https://www.youtube.com/watch?v=jNQXAC9IVRw" --start 0 --end 5
```

### 高级选项:
```bash
# 指定输出目录
./ytdl "https://www.youtube.com/watch?v=jNQXAC9IVRw" --start 0 --end 5 --output-dir ./downloads

# 仅下载视频(不提取音频)
./ytdl "https://www.youtube.com/watch?v=jNQXAC9IVRw" --start 0 --end 5 --no-audio

# 不下载字幕
./ytdl "https://www.youtube.com/watch?v=jNQXAC9IVRw" --start 0 --end 5 --no-subtitles

# 指定字幕语言
./ytdl "https://www.youtube.com/watch?v=jNQXAC9IVRw" --start 0 --end 5 --sub-langs en,ja
```

## 注意事项

1. **Cookie有效期**: Cookie文件可能会过期，需要定期更新
2. **隐私安全**: 不要分享你的cookie文件，它包含你的登录信息
3. **浏览器兼容性**: 建议使用主流浏览器(Chrome, Firefox, Edge)
4. **网络环境**: 某些网络环境可能需要额外的代理设置

## 故障排除

### 问题: "Sign in to confirm you're not a bot"
**解决方案**: 确保cookie文件是最新的，并且是从已登录的YouTube账户导出的

### 问题: "Cookie file format invalid"
**解决方案**: 检查cookie文件格式是否正确，建议使用浏览器扩展导出

### 问题: 下载仍然失败
**解决方案**:
- 尝试更新yt-dlp: `pip install -U yt-dlp`
- 检查网络连接
- 尝试使用不同的浏览器导出cookie

## 替代方案

如果cookie方法仍然不工作，可以考虑:
1. 使用VPN更换IP地址
2. 等待一段时间后重试
3. 使用YouTube Data API (需要API密钥)
4. 使用其他YouTube下载工具作为备选
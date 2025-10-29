# YouTube Cookies 问题快速解决

## ❌ 当前问题

您遇到的错误：
```
ERROR: [youtube] Sign in to confirm you're not a bot
ERROR: HTTP Error 429: Too Many Requests
```

**原因**：YouTube 检测到自动化访问，您的 cookies 文件已失效。

---

## ✅ 快速解决（3步）

### 方案 A: 使用自动脚本（推荐）

```bash
cd /Users/liuwei/Github/youtube
./scripts/update_cookies.sh
```

按照脚本提示操作即可。

### 方案 B: 手动更新

#### 1️⃣ 安装浏览器扩展

**Chrome/Edge 用户**：
- 打开 Chrome 应用商店
- 搜索并安装：**"Get cookies.txt LOCALLY"**
- 扩展地址：https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc

**Firefox 用户**：
- 打开 Firefox 扩展商店
- 搜索并安装：**"cookies.txt"**

#### 2️⃣ 导出 Cookies（重要！）

1. 在浏览器中访问 https://www.youtube.com
2. **确保已登录**您的 YouTube 账户
3. 点击扩展图标（通常在地址栏右侧）
4. 点击 "Export" 或 "导出"
5. **直接保存为**：`/Users/liuwei/Github/youtube/cookies/Cookies`
   
   > 💡 **提示**：直接覆盖原文件即可，脚本会自动备份

#### 3️⃣ 运行更新脚本

```bash
cd /Users/liuwei/Github/youtube
./scripts/update_cookies.sh
# 选择选项 1（使用默认路径）
```

脚本会自动：
- ✅ 备份旧文件
- ✅ 验证新文件格式
- ✅ 测试 cookies 是否有效
- ✅ 重启 Docker 服务

---

## 🧪 验证 Cookies 是否有效

```bash
docker exec youtube-dl-api yt-dlp \
  --cookies /app/cookies/Cookies \
  --proxy http://host.docker.internal:7890 \
  --get-title \
  "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

如果能显示视频标题，说明 cookies 有效！

---

## ⚠️ 关于 429 错误

`HTTP Error 429: Too Many Requests` 表示请求过于频繁。

**解决方法**：
- 等待 **10-30 分钟**后再重试
- 减少并发下载任务
- 如果使用代理，可以尝试更换代理 IP

---

## 🔧 其他优化建议

### 1. 增加重试等待时间

当前代码中重试间隔较短（1-2秒），可以修改为更长时间：

```python
# 在 src/downloader/utils.py 中修改
# 将重试间隔改为 5-10 秒
time.sleep(2 ** attempt)  # 指数退避：2, 4, 8 秒
```

### 2. 添加请求限流

在下载前添加延迟，避免触发 YouTube 的速率限制：

```python
import time
time.sleep(3)  # 每次下载前等待 3 秒
```

### 3. 使用不同的下载客户端

yt-dlp 支持多种客户端，可以尝试：

```bash
# 使用 iOS 客户端（有时更稳定）
yt-dlp --extractor-args "youtube:player_client=ios" [URL]

# 使用 Android 客户端
yt-dlp --extractor-args "youtube:player_client=android" [URL]
```

---

## 💡 预防措施

### 1. 定期更新 Cookies
- Cookies 通常有效期为 **几周到几个月**
- 当出现认证错误时，立即更新
- 建议每月主动更新一次

### 2. 合理控制下载频率
- 不要短时间内下载大量视频
- 在下载之间添加延迟
- 避免并发下载同一视频的多个片段

### 3. 保持 yt-dlp 最新
```bash
docker exec youtube-dl-api pip install -U yt-dlp
```

---

## 🆘 紧急临时方案

如果更新 cookies 后仍然失败，可以：

### 选项 1: 仅下载音频
音频下载的成功率通常更高：

```bash
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=jSyShqcAGAE",
    "start_time": "1:30",
    "end_time": "2:00",
    "download_video": false,
    "download_subtitles": false,
    "download_audio": true
  }'
```

### 选项 2: 更换代理
如果使用的代理被 YouTube 限制，尝试更换代理服务器。

### 选项 3: 等待后重试
等待 **1-2 小时**，让 YouTube 的速率限制重置。

---

## 📞 需要帮助？

如果问题仍然存在，请检查：
1. ✅ 浏览器中是否已登录 YouTube
2. ✅ 导出的 cookies 文件格式是否正确（第一行应该是 `# Netscape HTTP Cookie File`）
3. ✅ 代理是否正常工作
4. ✅ yt-dlp 是否为最新版本

您可以运行以下命令进行全面检查：

```bash
# 检查 cookies 文件
head -1 cookies/Cookies

# 检查 yt-dlp 版本
docker exec youtube-dl-api yt-dlp --version

# 检查代理
docker exec youtube-dl-api curl -x http://host.docker.internal:7890 https://www.google.com
```


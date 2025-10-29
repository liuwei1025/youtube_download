# 更新 YouTube Cookies 指南

## 问题
遇到 "Sign in to confirm you're not a bot" 错误时，需要更新 cookies 文件。

## 解决步骤

### 方法 1: 使用浏览器扩展（最简单）

1. **安装浏览器扩展**
   - Chrome/Edge: 安装 "Get cookies.txt LOCALLY" 扩展
   - Firefox: 安装 "cookies.txt" 扩展

2. **导出 Cookies**
   - 在浏览器中访问 https://www.youtube.com 并确保已登录
   - 点击扩展图标
   - 选择 "Export" 或 "导出"
   - 保存为 `Cookies` 文件（无扩展名）

3. **替换现有文件**
   ```bash
   # 备份旧文件
   mv cookies/Cookies cookies/Cookies.backup
   
   # 将新导出的文件移动到 cookies 目录
   mv ~/Downloads/Cookies cookies/Cookies
   
   # 重启 Docker 服务
   docker-compose restart youtube-dl-api
   ```

### 方法 2: 使用 yt-dlp 从浏览器提取

```bash
# 进入 Docker 容器
docker exec -it youtube-dl-api bash

# 使用 yt-dlp 从 Chrome 提取 cookies（需要主机支持）
yt-dlp --cookies-from-browser chrome --write-pages "https://www.youtube.com/watch?v=jSyShqcAGAE"
```

### 方法 3: 手动更新（高级）

1. 使用浏览器开发者工具（F12）
2. 访问 YouTube 并登录
3. 在 Application/存储 → Cookies → https://www.youtube.com
4. 找到关键 cookies（如 `__Secure-3PSID`, `HSID`, `SSID` 等）
5. 更新 `cookies/Cookies` 文件中的对应值

## 验证 Cookies 是否有效

```bash
# 测试下载（在容器中）
docker exec youtube-dl-api yt-dlp \
  --cookies /app/cookies/Cookies \
  --proxy http://host.docker.internal:7890 \
  --get-title "https://www.youtube.com/watch?v=jSyShqcAGAE"
```

如果能正确获取标题，说明 cookies 有效。

## 额外建议

### 1. 避免 429 错误（请求过于频繁）
   - 在重试之间等待更长时间（目前已有重试机制）
   - 减少并发下载任务
   - 考虑使用 YouTube Data API 作为备选

### 2. 更新 yt-dlp
   ```bash
   docker exec youtube-dl-api pip install -U yt-dlp
   ```

### 3. 检查代理状态
   确保代理 `http://host.docker.internal:7890` 正常工作：
   ```bash
   # 测试代理
   docker exec youtube-dl-api curl -x http://host.docker.internal:7890 https://www.google.com
   ```

## 常见问题

**Q: Cookies 多久需要更新一次？**
A: 通常 YouTube cookies 有效期为几周到几个月，当出现认证错误时需要更新。

**Q: 为什么即使 cookies 没过期也会失败？**
A: YouTube 会检测异常访问模式（如频繁请求、使用代理等），可能会要求重新验证。

**Q: 429 错误如何解决？**
A: 等待一段时间（几分钟到几小时），或者更换 IP 地址（更换代理）。

## 紧急处理

如果持续失败，可以临时禁用某些功能：
```bash
# 只下载音频（音频下载成功率更高）
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


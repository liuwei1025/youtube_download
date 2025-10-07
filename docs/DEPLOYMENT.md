# Railway 部署指南

本文档介绍如何将 YouTube 下载器部署到 Railway.com。

## 📋 准备工作

### 1. 注册 Railway 账号
- 访问 [Railway.com](https://railway.com/)
- 使用 GitHub 账号登录

### 2. 准备代码仓库
确保你的代码已推送到 GitHub 仓库。

## 🚀 部署步骤

### 方式一：通过 Railway Dashboard 部署（推荐）

1. **创建新项目**
   - 登录 Railway Dashboard
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"

2. **选择仓库**
   - 授权 Railway 访问你的 GitHub
   - 选择 `youtube_download` 仓库

3. **配置服务**
   - Railway 会自动检测 `Dockerfile`
   - 等待构建和部署完成（约 2-5 分钟）

4. **配置环境变量**（可选）
   ```
   PORT=8000
   DOWNLOADS_DIR=/tmp/downloads
   HTTP_PROXY=你的代理地址（如需要）
   HTTPS_PROXY=你的代理地址（如需要）
   ```

5. **生成公开域名**
   - 在服务设置中点击 "Generate Domain"
   - 记录生成的域名，如 `your-app.up.railway.app`

### 方式二：使用 Railway CLI

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 部署
railway up

# 查看日志
railway logs
```

## 📡 API 使用

部署完成后，你可以通过以下端点使用服务：

### 1. 查看 API 文档
```
https://your-app.up.railway.app/docs
```

### 2. 健康检查
```bash
curl https://your-app.up.railway.app/health
```

### 3. 创建下载任务
```bash
curl -X POST "https://your-app.up.railway.app/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "1:00",
    "end_time": "2:00",
    "download_video": true,
    "download_audio": true,
    "download_subtitles": false
  }'
```

响应示例：
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "任务已创建，正在处理中",
  "created_at": "2025-10-07T12:34:56.789012"
}
```

### 4. 查询任务状态
```bash
curl "https://your-app.up.railway.app/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

响应示例：
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "video_id": "dQw4w9WgXcQ",
  "created_at": "2025-10-07T12:34:56.789012",
  "completed_at": "2025-10-07T12:35:23.456789",
  "files": {
    "video": "segment_1_00-2_00.mp4",
    "audio": "audio_1_00-2_00.mp3"
  }
}
```

### 5. 下载文件
```bash
# 下载视频
curl -O "https://your-app.up.railway.app/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890/files/video"

# 下载音频
curl -O "https://your-app.up.railway.app/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890/files/audio"
```

### 6. 查看所有任务
```bash
curl "https://your-app.up.railway.app/tasks"

# 只查看已完成的任务
curl "https://your-app.up.railway.app/tasks?status=completed"
```

## 🔧 环境变量配置

在 Railway Dashboard 中可以配置以下环境变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务端口 | `8000` |
| `DOWNLOADS_DIR` | 下载目录 | `/tmp/downloads` |
| `HTTP_PROXY` | HTTP 代理 | 无 |
| `HTTPS_PROXY` | HTTPS 代理 | 无 |

## ⚠️ 重要注意事项

### 1. 临时文件系统
- Railway 使用临时文件系统（ephemeral storage）
- 服务重启后文件会丢失
- 建议及时下载完成的文件

### 2. 资源限制
- Railway 免费套餐有资源限制
- 注意监控内存和 CPU 使用
- 大文件下载可能需要升级套餐

### 3. 代理配置
- 如果需要访问被限制的内容，配置代理
- 可以使用环境变量或在请求中指定

### 4. 超时设置
- 长时间下载可能触发超时
- 建议下载较短的视频片段（<5分钟）

### 5. 并发限制
- 避免同时创建大量下载任务
- 建议控制并发数量

## 📊 监控和日志

### 查看日志
在 Railway Dashboard 中：
1. 进入你的项目
2. 选择服务
3. 点击 "Logs" 标签

### 监控指标
- CPU 使用率
- 内存使用率
- 网络流量
- 请求数量

## 🐛 故障排除

### 1. 服务无法启动
- 检查日志中的错误信息
- 确认 `ffmpeg` 和 `yt-dlp` 正常安装
- 验证 Dockerfile 构建成功

### 2. 下载失败
- 检查视频 URL 是否有效
- 确认代理配置正确（如需要）
- 查看任务状态中的错误信息

### 3. 文件下载失败
- 确认任务状态为 `completed`
- 检查文件是否存在
- 验证文件路径正确

### 4. 内存不足
- 降低视频质量参数
- 减少并发任务数
- 考虑升级 Railway 套餐

## 🔐 安全建议

1. **API 访问控制**
   - 生产环境建议添加身份验证
   - 可以使用 API Key 或 JWT Token

2. **速率限制**
   - 建议添加速率限制防止滥用
   - 可以使用 `slowapi` 库

3. **输入验证**
   - 已内置基本验证
   - 根据需要添加额外的安全检查

## 💰 成本估算

### Railway 定价（截至 2025 年）
- **Hobby Plan**: $5/月
  - 500 小时执行时间
  - 适合轻度使用

- **Pro Plan**: 按使用量计费
  - 更高的资源配额
  - 更好的性能

建议先使用 Hobby Plan 测试，根据实际使用情况决定是否升级。

## 📚 相关资源

- [Railway 官方文档](https://docs.railway.app/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [yt-dlp 文档](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg 文档](https://ffmpeg.org/documentation.html)

## 🆘 获取帮助

如果遇到问题：
1. 查看本项目的 GitHub Issues
2. 访问 Railway Community 论坛
3. 查看 FastAPI 和 yt-dlp 的文档

## 📝 更新日志

- v2.0.0 (2025-10-07): 初始 Railway 部署版本
  - 添加 FastAPI HTTP 服务
  - 支持异步任务处理
  - 添加完整的 API 文档

# 快速启动指南 - 任务管理系统

## 1️⃣ 启动服务 (30秒)

```bash
# 启动所有服务
docker-compose up -d

# 等待服务就绪（约10-15秒）
docker-compose logs -f
```

看到以下信息表示启动成功：
```
youtube-dl-api  | ✅ 数据库连接成功
youtube-dl-api  | ✅ 依赖检查通过
youtube-postgres | database system is ready to accept connections
```

## 2️⃣ 验证服务 (10秒)

```bash
# 检查健康状态
curl http://localhost:8000/health

# 预期输出：
# {
#   "status": "healthy",
#   "database": "connected",
#   ...
# }
```

## 3️⃣ 创建第一个任务 (1分钟)

```bash
# 创建下载任务
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "00:00",
    "end_time": "00:30",
    "subtitle_langs": "en"
  }'

# 返回任务ID，例如：
# {"task_id": "550e8400-e29b-41d4-a716-446655440000", ...}
```

## 4️⃣ 查看任务进度 (实时)

```bash
# 替换成你的任务ID
TASK_ID="your-task-id-here"

# 查看任务状态
curl "http://localhost:8000/tasks/$TASK_ID"

# 或查看所有任务
curl "http://localhost:8000/tasks"
```

## 5️⃣ 访问 Web 界面

打开浏览器访问：**http://localhost:8000/docs**

这是交互式 API 文档，可以直接测试所有功能！

---

## 🎯 核心功能速览

### 查看统计
```bash
curl http://localhost:8000/stats
```

### 查看任务列表
```bash
# 所有任务
curl "http://localhost:8000/tasks"

# 只看进行中的
curl "http://localhost:8000/tasks?status=processing"

# 只看已完成的
curl "http://localhost:8000/tasks?status=completed"
```

### 查看任务详情
```bash
curl "http://localhost:8000/tasks/{task_id}"
```

### 查看任务日志
```bash
curl "http://localhost:8000/tasks/{task_id}/logs"
```

### 下载文件
```bash
# 下载视频
curl -o video.mp4 \
  "http://localhost:8000/tasks/{task_id}/files/video"

# 下载音频
curl -o audio.mp3 \
  "http://localhost:8000/tasks/{task_id}/files/audio"

# 下载字幕
curl -o subtitles.vtt \
  "http://localhost:8000/tasks/{task_id}/files/subtitles"
```

### 取消任务
```bash
curl -X POST "http://localhost:8000/tasks/{task_id}/cancel"
```

### 删除任务
```bash
curl -X DELETE "http://localhost:8000/tasks/{task_id}"
```

---

## 🔧 常用管理命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有日志
docker-compose logs -f

# 只看 API 日志
docker-compose logs -f youtube-dl-api

# 只看数据库日志
docker-compose logs -f postgres
```

### 重启服务
```bash
# 重启 API
docker-compose restart youtube-dl-api

# 重启数据库
docker-compose restart postgres

# 重启所有
docker-compose restart
```

### 停止服务
```bash
docker-compose down

# 同时删除数据卷（会清空数据库）
docker-compose down -v
```

---

## 📊 数据库管理

### 连接数据库
```bash
docker exec -it youtube-postgres psql -U youtube -d youtube_tasks
```

密码：`youtube_pass_2024`

### 常用 SQL 查询
```sql
-- 查看所有任务
SELECT task_id, status, url, progress_percentage 
FROM tasks 
ORDER BY created_at DESC 
LIMIT 10;

-- 统计
SELECT status, COUNT(*) 
FROM tasks 
GROUP BY status;

-- 清理旧任务
SELECT cleanup_old_tasks(24);

-- 退出
\q
```

---

## 🐛 故障排查

### 问题1: 端口被占用
```bash
# 查看占用端口的进程
lsof -i :8000
lsof -i :5432

# 修改 docker-compose.yaml 中的端口映射
```

### 问题2: 数据库连接失败
```bash
# 检查数据库是否就绪
docker exec youtube-postgres pg_isready -U youtube

# 查看数据库日志
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

### 问题3: 任务卡住不动
```bash
# 查看任务日志
curl "http://localhost:8000/tasks/{task_id}/logs"

# 查看应用日志
docker-compose logs youtube-dl-api

# 取消任务
curl -X POST "http://localhost:8000/tasks/{task_id}/cancel"
```

### 问题4: 磁盘空间不足
```bash
# 清理旧任务（24小时前）
curl -X POST "http://localhost:8000/cleanup?max_age_hours=24"

# 查看磁盘使用
du -sh downloads/*

# 手动清理下载目录
rm -rf downloads/old_video_id/
```

---

## 💡 使用技巧

### 1. 批量下载
创建一个脚本：
```bash
#!/bin/bash
for url in $(cat urls.txt); do
    curl -X POST "http://localhost:8000/download" \
      -H "Content-Type: application/json" \
      -d "{
        \"url\": \"$url\",
        \"start_time\": \"00:00\",
        \"end_time\": \"01:00\"
      }"
    sleep 2
done
```

### 2. 监控脚本
```bash
#!/bin/bash
TASK_ID=$1
while true; do
    STATUS=$(curl -s "http://localhost:8000/tasks/$TASK_ID" | jq -r '.status')
    PROGRESS=$(curl -s "http://localhost:8000/tasks/$TASK_ID" | jq -r '.progress_percentage')
    echo "$(date): $STATUS - $PROGRESS%"
    
    if [[ "$STATUS" == "completed" ]] || [[ "$STATUS" == "failed" ]]; then
        break
    fi
    sleep 5
done
```

### 3. 定时清理
添加到 crontab：
```bash
# 每天凌晨3点清理7天前的任务
0 3 * * * curl -X POST "http://localhost:8000/cleanup?max_age_hours=168"
```

---

## 📚 更多资源

- 📖 **详细文档**: [docs/TASK_MANAGEMENT.md](docs/TASK_MANAGEMENT.md)
- 🌐 **API 文档**: http://localhost:8000/docs
- 📊 **健康检查**: http://localhost:8000/health
- 📈 **统计信息**: http://localhost:8000/stats

---

## ⚡ 性能提示

1. **并发任务**: API 支持多个任务并发执行
2. **资源限制**: Docker 已配置资源限制（2核 2GB）
3. **代理设置**: 已配置代理，如需修改请编辑 `docker-compose.yaml`
4. **定期清理**: 建议每周清理一次旧任务

---

## 🔒 安全提示

1. **修改密码**: 生产环境请修改数据库默认密码
2. **网络隔离**: 数据库不要暴露到公网
3. **定期备份**: 重要数据请定期备份
4. **日志审计**: 定期检查任务日志

---

## ✅ 下一步

1. 阅读 [完整文档](docs/TASK_MANAGEMENT.md)
2. 探索 [API 接口](http://localhost:8000/docs)
3. 尝试编写自己的客户端脚本
4. 根据需求调整配置

祝使用愉快！🎉


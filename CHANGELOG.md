# 更新日志

本文档记录项目的所有重要变更。

## [2.0.0] - 2025-10-07

### 🎉 重大更新：HTTP API 服务

本次更新将项目从纯命令行工具升级为完整的 HTTP API 服务，支持云端部署。

### ✨ 新增功能

#### API 服务
- **FastAPI HTTP 服务** (`app.py`)
  - RESTful API 设计
  - 异步任务处理
  - 自动生成 API 文档（Swagger UI）
  - 健康检查端点
  - 任务状态查询
  - 文件下载接口
  - 任务管理（创建、查询、删除）

#### 云端部署
- **Railway 一键部署支持**
  - `Dockerfile` - Docker 容器配置
  - `railway.json` - Railway 平台配置
  - `.dockerignore` - Docker 构建优化
  - 自动健康检查
  - 环境变量配置

#### 文档和工具
- **完整的部署文档**
  - `docs/DEPLOYMENT.md` - Railway 部署指南
  - `docs/API_REFERENCE.md` - 完整 API 参考
  - `QUICKSTART.md` - 快速开始指南
  - `CHANGELOG.md` - 更新日志

- **测试和示例**
  - `test_api.py` - 完整的 API 测试脚本
  - `examples/client.py` - Python 客户端示例
  - `run_server.sh` - 本地启动脚本

#### 新增 API 端点
- `GET /` - API 信息
- `GET /health` - 健康检查
- `POST /download` - 创建下载任务
- `GET /tasks` - 获取任务列表
- `GET /tasks/{task_id}` - 查询任务状态
- `GET /tasks/{task_id}/files/{file_type}` - 下载文件
- `DELETE /tasks/{task_id}` - 删除任务
- `POST /cleanup` - 清理旧任务

### 🔧 改进

#### 代码结构
- 保持原有命令行功能完全兼容
- 模块化设计，易于维护和扩展
- 添加类型注解（Pydantic 模型）
- 完善的错误处理和日志记录

#### 依赖更新
- 添加 `fastapi>=0.104.0`
- 添加 `uvicorn[standard]>=0.24.0`
- 添加 `pydantic>=2.0.0`
- 添加 `python-multipart>=0.0.6`

#### 文档
- 完全重写 `README.md`
- 新增多个专业文档
- 添加详细的使用示例
- 支持中英文双语

### 📦 文件结构变化

```
新增文件:
├── app.py                       # FastAPI 主应用
├── Dockerfile                   # Docker 配置
├── railway.json                 # Railway 配置
├── .dockerignore                # Docker 忽略文件
├── run_server.sh                # 启动脚本
├── test_api.py                  # API 测试
├── QUICKSTART.md                # 快速开始
├── CHANGELOG.md                 # 更新日志
├── examples/
│   └── client.py                # Python 客户端
└── docs/
    ├── DEPLOYMENT.md            # 部署指南
    └── API_REFERENCE.md         # API 文档

更新文件:
├── README.md                    # 主文档（重写）
├── requirements.txt             # 依赖（新增 web 框架）
└── .gitignore                   # 忽略列表（更新）

保持不变:
├── src/
│   └── youtube_downloader.py    # 核心下载逻辑
├── config.json                  # 配置文件
└── docs/
    ├── README.md                # 命令行文档
    ├── COOKIES_SETUP.md         # Cookie 设置
    └── PROJECT_STRUCTURE.md     # 项目结构
```

### 🎯 使用方式

#### 方式一：命令行（保持兼容）
```bash
# 原有命令行方式完全保留
./ytdl "URL" --start 1:00 --end 2:00
```

#### 方式二：HTTP API（新增）
```bash
# 本地运行服务
python app.py

# 调用 API
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "...", "start_time": "1:00", "end_time": "2:00"}'
```

#### 方式三：云端部署（新增）
1. Fork 仓库到 GitHub
2. 在 Railway.com 创建新项目
3. 选择 GitHub 仓库部署
4. 获得公开 API 地址

### 🔄 迁移指南

#### 现有用户
- ✅ 命令行功能完全兼容，无需修改
- ✅ 可选择性启用 API 服务
- ✅ 配置文件格式保持不变

#### 新用户
- 推荐先查看 `QUICKSTART.md`
- 选择适合的使用方式
- 参考示例代码快速上手

### 📝 技术亮点

1. **向后兼容**
   - 保留所有原有功能
   - 命令行工具仍可独立使用

2. **云原生设计**
   - Docker 容器化
   - 健康检查和自动重启
   - 环境变量配置

3. **生产就绪**
   - 完整的错误处理
   - 日志记录系统
   - API 文档自动生成

4. **易于部署**
   - 一键部署到 Railway
   - 支持多种云平台
   - 详细的部署文档

### ⚠️ 注意事项

1. **临时文件系统**
   - Railway 等平台使用临时存储
   - 文件会在重启后丢失
   - 建议及时下载完成的文件

2. **资源限制**
   - 免费套餐有限制
   - 建议下载短视频片段
   - 控制并发任务数量

3. **代理配置**
   - 某些地区可能需要代理
   - 支持环境变量和 API 参数

### 🔜 未来计划

- [ ] 添加用户认证系统
- [ ] 支持 WebSocket 实时推送
- [ ] 添加任务队列（Redis/RabbitMQ）
- [ ] 支持更多云存储（S3, OSS）
- [ ] 添加 Web 管理界面
- [ ] 支持 Docker Compose 部署
- [ ] 添加性能监控和统计
- [ ] 支持批量 API 调用

---

## [1.2.0] - 2024

### 新增
- 批量处理支持
- 配置文件支持
- 进度条显示
- 依赖检查
- 日志系统

### 改进
- 错误处理优化
- 重试机制
- 磁盘空间检查

---

## [1.1.0] - 2024

### 新增
- 字幕下载功能
- 多语言支持
- 音频提取

### 改进
- 时间戳处理
- 文件命名规范

---

## [1.0.0] - 2024

### 首次发布
- 基本下载功能
- 时间段裁剪
- 代理支持
- 视频质量选择

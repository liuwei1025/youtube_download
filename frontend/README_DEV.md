# 前端开发指南

## 开发环境配置

### 连接Docker后端服务

1. 首先启动Docker后端服务：

```bash
# 在项目根目录
docker-compose up -d
```

2. 启动前端开发服务器：

```bash
cd frontend
pnpm install
pnpm dev
```

3. 访问前端开发服务器：

```
http://localhost:5173
```

### 环境变量配置

前端会通过 Vite 代理连接到后端服务。默认配置连接到 `http://localhost:8000`。

如果需要连接到不同的后端地址，可以修改 `.env.development` 文件：

```env
VITE_API_URL=http://your-backend-url:port
```

### 开发模式特性

- ✅ 热更新（HMR）
- ✅ 自动代理API请求到后端
- ✅ 表格展示任务列表
- ✅ 分页功能（每页10条）
- ✅ 任务重试功能
- ✅ 视频/音频播放器
- ✅ 字幕时间轴查看

### API代理配置

前端开发服务器会将以下路径代理到后端：

- `/api/*` - API接口
- `/tasks/*` - 任务相关接口
- `/download` - 下载接口
- `/health` - 健康检查
- `/stats` - 统计信息

### 构建生产版本

```bash
pnpm build
```

构建产物会输出到 `dist/` 目录，可以直接部署到静态服务器或与后端一起部署。

### 测试

```bash
# 运行测试
pnpm test

# 运行linter
pnpm lint
```

## 常见问题

### 1. 无法连接到后端

检查：
- Docker容器是否正在运行：`docker ps`
- 后端端口是否正确：默认8000
- 防火墙是否允许连接

### 2. 热更新不工作

尝试：
- 重启开发服务器
- 清除浏览器缓存
- 检查文件保存是否成功

### 3. API请求失败

检查：
- 浏览器控制台的网络请求
- 后端服务是否正常：访问 `http://localhost:8000/health`
- 代理配置是否正确


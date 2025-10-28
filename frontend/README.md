# YouTube 下载器前端

基于 Vue 3 + Vite + Feature-Sliced Design 架构的管理界面。

## 技术栈

- Vue 3 - 渐进式 JavaScript 框架
- Vite - 下一代前端构建工具
- Vue Router - 官方路由管理器
- Pinia - 状态管理
- Axios - HTTP 客户端
- Feature-Sliced Design - 架构方法论

## 项目结构

```
src/
├── app/          # 应用初始化层
│   ├── providers # 全局 providers（router, store等）
│   ├── styles    # 全局样式
│   └── config    # 全局配置
├── pages/        # 页面层
│   ├── task-list    # 任务列表页
│   └── task-detail  # 任务详情页
├── widgets/      # 组件层（复杂UI组件）
│   └── task-card    # 任务卡片组件
├── features/     # 功能层
│   └── task-management # 任务管理功能
├── entities/     # 实体层
│   └── task         # 任务实体
└── shared/       # 共享层
    ├── api          # API 客户端
    ├── ui           # 基础 UI 组件
    └── lib          # 工具函数
```

## 开发

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build
```

## API 代理

开发环境下，`/api` 路径会被代理到后端 API 服务器（http://localhost:8000）。


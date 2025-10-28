#!/bin/bash
# 前端开发服务器启动脚本

cd frontend

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    pnpm install
fi

echo "🚀 启动前端开发服务器..."
echo "访问: http://localhost:5173"
pnpm dev


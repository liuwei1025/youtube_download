#!/bin/bash
# 前端构建脚本

cd frontend

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    pnpm install
fi

echo "🔨 构建前端项目..."
pnpm build

echo "✅ 构建完成！"
echo "前端文件已生成到: frontend/dist/"
echo "现在可以启动后端服务器: python app.py"


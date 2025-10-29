#!/bin/bash

# 启动开发环境脚本

echo "======================================"
echo "启动 YouTube 下载器开发环境"
echo "======================================"
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

echo "1. 启动后端服务（Docker）..."
docker-compose up -d

# 等待后端启动
echo "   等待后端服务启动..."
sleep 3

# 检查后端是否正常
echo "   检查后端健康状态..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ 后端服务已就绪"
        break
    fi
    
    if [ $i -eq 10 ]; then
        echo "   ⚠️  后端服务启动超时，请检查 Docker 日志"
        docker-compose logs
        exit 1
    fi
    
    echo "   等待中... ($i/10)"
    sleep 2
done

echo ""
echo "2. 准备启动前端开发服务器..."
echo "   安装依赖（如果需要）..."
cd frontend

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "   首次运行，安装依赖..."
    pnpm install
fi

echo ""
echo "======================================"
echo "✅ 环境已准备就绪！"
echo ""
echo "服务地址："
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo "  前端（需要手动启动）: http://localhost:5173"
echo ""
echo "启动前端开发服务器："
echo "  cd frontend && pnpm dev"
echo ""
echo "停止后端服务："
echo "  docker-compose down"
echo ""
echo "查看后端日志："
echo "  docker-compose logs -f"
echo "======================================"


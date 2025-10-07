#!/bin/bash
# 启动 YouTube 下载器 API 服务

echo "🚀 启动 YouTube 下载器 API 服务..."
echo ""

# 检查端口
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

# 检查依赖
echo "📦 检查依赖..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  警告: ffmpeg 未安装，下载功能可能无法正常工作"
fi

# 检查 Python 包
echo "📦 检查 Python 包..."
python3 -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ FastAPI 或 Uvicorn 未安装"
    echo "   运行: pip install -r requirements.txt"
    exit 1
fi

# 启动服务
echo ""
echo "✅ 依赖检查完成"
echo ""
echo "🌐 服务将运行在: http://${HOST}:${PORT}"
echo "📖 API 文档: http://localhost:${PORT}/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 运行服务
python3 app.py

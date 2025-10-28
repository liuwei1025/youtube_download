#!/bin/bash
# YouTube 403 错误修复测试脚本

set -e

echo "=========================================="
echo "YouTube 403 错误修复测试"
echo "=========================================="
echo ""

# 测试视频 URL
TEST_URL="https://www.youtube.com/watch?v=jNQXAC9IVRw"
TEST_DIR="test_403_fix"

# 清理旧的测试目录
if [ -d "$TEST_DIR" ]; then
    echo "🧹 清理旧的测试目录..."
    rm -rf "$TEST_DIR"
fi

# 创建测试目录
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📋 测试信息:"
echo "  - 视频 URL: $TEST_URL"
echo "  - 测试目录: $TEST_DIR"
echo "  - yt-dlp 版本: $(yt-dlp --version)"
echo ""

# 测试 1: 使用 cookies (旧方法,可能失败)
echo "=========================================="
echo "测试 1: 使用 cookies + 默认客户端"
echo "=========================================="
echo ""

if yt-dlp \
    --proxy http://127.0.0.1:7890 \
    --cookies ../cookies/Cookies \
    --no-cache-dir \
    -f 'bestvideo[height<=480]+bestaudio/best[height<=480]' \
    --merge-output-format mp4 \
    -o "test1_with_cookies.%(ext)s" \
    --no-playlist \
    --fixup force \
    "$TEST_URL" 2>&1 | tail -20; then
    echo "✅ 测试 1 成功"
    TEST1_SUCCESS=true
else
    echo "❌ 测试 1 失败 (预期可能失败)"
    TEST1_SUCCESS=false
fi

echo ""

# 测试 2: 不使用 cookies (新方法,应该成功)
echo "=========================================="
echo "测试 2: 不使用 cookies,自动选择客户端"
echo "=========================================="
echo ""

if yt-dlp \
    --proxy http://127.0.0.1:7890 \
    --no-cache-dir \
    -f 'bestvideo[height<=480]+bestaudio/best[height<=480]' \
    --merge-output-format mp4 \
    -o "test2_no_cookies.%(ext)s" \
    --no-playlist \
    --fixup force \
    "$TEST_URL" 2>&1 | tail -20; then
    echo "✅ 测试 2 成功"
    TEST2_SUCCESS=true
else
    echo "❌ 测试 2 失败"
    TEST2_SUCCESS=false
fi

echo ""

# 测试 3: 使用 Python API
echo "=========================================="
echo "测试 3: Python API 调用"
echo "=========================================="
echo ""

cd ..

if python -c "
from src.downloader.video import download_segment
from src.downloader.config import DownloadConfig
from src.downloader.utils import setup_proxy, extract_video_id
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

config = DownloadConfig(
    url='$TEST_URL',
    start_time='00:00',
    end_time='00:05',
    video_quality='best[height<=480]',
    output_dir='$TEST_DIR',
    cookies_file='cookies/Cookies',
    max_retries=3
)

proxy = setup_proxy(config)
video_id = extract_video_id(config.url)
result = download_segment(config, 'video', video_id, proxy)

if result:
    print(f'✅ 下载成功: {result}')
    exit(0)
else:
    print('❌ 下载失败')
    exit(1)
"; then
    echo "✅ 测试 3 成功"
    TEST3_SUCCESS=true
else
    echo "❌ 测试 3 失败"
    TEST3_SUCCESS=false
fi

echo ""

# 总结
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo ""

if [ "$TEST1_SUCCESS" = true ]; then
    echo "✅ 测试 1: 使用 cookies - 成功"
else
    echo "⚠️  测试 1: 使用 cookies - 失败 (可能是预期的)"
fi

if [ "$TEST2_SUCCESS" = true ]; then
    echo "✅ 测试 2: 不使用 cookies - 成功"
else
    echo "❌ 测试 2: 不使用 cookies - 失败"
fi

if [ "$TEST3_SUCCESS" = true ]; then
    echo "✅ 测试 3: Python API - 成功"
else
    echo "❌ 测试 3: Python API - 失败"
fi

echo ""

# 检查下载的文件
echo "=========================================="
echo "下载的文件"
echo "=========================================="
echo ""

ls -lh "$TEST_DIR"/*.mp4 2>/dev/null || echo "没有找到下载的文件"

echo ""

# 清理
echo "=========================================="
echo "清理测试文件"
echo "=========================================="
echo ""

read -p "是否清理测试文件? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$TEST_DIR"
    echo "✅ 已清理测试文件"
else
    echo "ℹ️  测试文件保留在 $TEST_DIR 目录"
fi

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="


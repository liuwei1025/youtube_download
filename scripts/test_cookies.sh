#!/bin/bash
# 测试 YouTube Cookies 是否有效

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COOKIES_FILE="$PROJECT_DIR/cookies/Cookies"

echo "🧪 YouTube Cookies 测试工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查文件是否存在
if [ ! -f "$COOKIES_FILE" ]; then
    echo "❌ 错误: Cookies 文件不存在"
    echo "   路径: $COOKIES_FILE"
    echo ""
    echo "💡 请先运行: ./scripts/update_cookies.sh"
    exit 1
fi

# 检查文件格式
echo "📄 检查文件格式..."
FIRST_LINE=$(head -1 "$COOKIES_FILE")
if [[ "$FIRST_LINE" == *"Netscape HTTP Cookie File"* ]]; then
    echo "✅ 文件格式正确"
else
    echo "❌ 文件格式错误"
    echo "   第一行: $FIRST_LINE"
    echo "   期望: # Netscape HTTP Cookie File"
    exit 1
fi

# 检查文件大小
FILE_SIZE=$(wc -c < "$COOKIES_FILE" | tr -d ' ')
if [ "$FILE_SIZE" -lt 100 ]; then
    echo "⚠️  警告: 文件太小 (${FILE_SIZE} 字节)，可能不完整"
fi

# 显示文件信息
echo ""
echo "📊 文件信息:"
echo "   路径: $COOKIES_FILE"
echo "   大小: $FILE_SIZE 字节"
if [ "$(uname)" = "Darwin" ]; then
    # macOS
    MOD_TIME=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$COOKIES_FILE")
else
    # Linux
    MOD_TIME=$(stat -c "%y" "$COOKIES_FILE" | cut -d. -f1)
fi
echo "   修改时间: $MOD_TIME"

# 统计 cookie 数量
COOKIE_COUNT=$(grep -v '^#' "$COOKIES_FILE" | grep -v '^$' | wc -l | tr -d ' ')
echo "   Cookie 数量: $COOKIE_COUNT"

# 检查 Docker 服务是否运行
echo ""
echo "🐳 检查 Docker 服务..."
if ! docker ps | grep -q youtube-dl-api; then
    echo "⚠️  警告: youtube-dl-api 容器未运行"
    echo ""
    read -p "是否启动服务？(Y/n): " START_SERVICE
    if [[ ! "$START_SERVICE" =~ ^[Nn]$ ]]; then
        echo "🔄 启动服务..."
        cd "$PROJECT_DIR"
        docker-compose up -d youtube-dl-api
        echo "⏳ 等待服务就绪..."
        sleep 5
    else
        echo "❌ 无法测试，服务未运行"
        exit 1
    fi
fi

# 测试 cookies
echo ""
echo "🧪 测试 Cookies 有效性..."
echo "   测试视频: https://www.youtube.com/watch?v=jNQXAC9IVRw"
echo ""

TEST_OUTPUT=$(docker exec youtube-dl-api yt-dlp \
    --cookies /app/cookies/Cookies \
    --proxy http://host.docker.internal:7890 \
    --get-title \
    --get-duration \
    "https://www.youtube.com/watch?v=jNQXAC9IVRw" 2>&1)

if echo "$TEST_OUTPUT" | grep -q "Sign in to confirm"; then
    echo "❌ Cookies 验证失败：需要登录确认"
    echo ""
    echo "错误信息:"
    echo "$TEST_OUTPUT" | grep "ERROR" || echo "$TEST_OUTPUT"
    echo ""
    echo "💡 解决方法："
    echo "   1. 运行: ./scripts/update_cookies.sh"
    echo "   2. 确保在浏览器中已登录 YouTube"
    echo "   3. 重新导出 cookies"
    exit 1
elif echo "$TEST_OUTPUT" | grep -q "ERROR"; then
    echo "❌ 测试失败"
    echo ""
    echo "错误信息:"
    echo "$TEST_OUTPUT"
    exit 1
else
    echo "✅ Cookies 验证成功！"
    echo ""
    echo "📺 测试结果:"
    echo "$TEST_OUTPUT" | head -2
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 测试完成！Cookies 工作正常"
echo ""
echo "💡 提示："
echo "   • 如果将来出现认证错误，运行: ./scripts/update_cookies.sh"
echo "   • 建议每月主动更新一次 cookies"


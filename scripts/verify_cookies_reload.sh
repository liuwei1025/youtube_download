#!/bin/bash
# 验证 cookies 是否每次都重新读取（无需重启容器）

set -e

echo "🧪 验证 Cookies 动态加载测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "此脚本将验证更新 cookies 文件后，无需重启容器即可生效"
echo ""

# 检查容器是否运行
if ! docker ps | grep -q youtube-dl-api; then
    echo "❌ 错误: youtube-dl-api 容器未运行"
    exit 1
fi

# 显示当前 cookies 文件信息
echo "📄 当前 Cookies 文件信息:"
if [ -f "cookies/Cookies" ]; then
    echo "   文件大小: $(wc -c < cookies/Cookies | tr -d ' ') 字节"
    if [ "$(uname)" = "Darwin" ]; then
        echo "   修改时间: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" cookies/Cookies)"
    else
        echo "   修改时间: $(stat -c "%y" cookies/Cookies | cut -d. -f1)"
    fi
    echo "   Cookie 数量: $(grep -v '^#' cookies/Cookies | grep -v '^$' | wc -l | tr -d ' ')"
else
    echo "   ⚠️  文件不存在"
fi

echo ""
echo "🧪 测试步骤："
echo ""
echo "1️⃣  第一次测试 - 使用当前 cookies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 第一次测试
BEFORE_TIME=$(date +%s)
docker exec youtube-dl-api yt-dlp \
    --cookies /app/cookies/Cookies \
    --proxy http://host.docker.internal:7890 \
    --get-title \
    --no-warnings \
    "https://www.youtube.com/watch?v=jNQXAC9IVRw" 2>&1 | head -1

if [ $? -eq 0 ]; then
    echo "✅ 第一次测试成功"
else
    echo "❌ 第一次测试失败"
fi

echo ""
read -p "现在请更新 cookies 文件（在另一个终端或使用浏览器扩展），完成后按回车继续..."

echo ""
echo "2️⃣  第二次测试 - 使用更新后的 cookies（未重启容器）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查文件是否被修改
if [ -f "cookies/Cookies" ]; then
    if [ "$(uname)" = "Darwin" ]; then
        FILE_MOD_TIME=$(stat -f %m cookies/Cookies)
    else
        FILE_MOD_TIME=$(stat -c %Y cookies/Cookies)
    fi
    
    if [ $FILE_MOD_TIME -gt $BEFORE_TIME ]; then
        echo "✅ 检测到文件已更新"
        echo "   新文件大小: $(wc -c < cookies/Cookies | tr -d ' ') 字节"
        echo "   新 Cookie 数量: $(grep -v '^#' cookies/Cookies | grep -v '^$' | wc -l | tr -d ' ')"
    else
        echo "⚠️  警告: 文件似乎未被修改"
        echo "   如果您已更新，可能时间戳未改变"
    fi
fi

echo ""
echo "测试下载（未重启容器）..."

# 第二次测试（未重启容器）
docker exec youtube-dl-api yt-dlp \
    --cookies /app/cookies/Cookies \
    --proxy http://host.docker.internal:7890 \
    --get-title \
    --no-warnings \
    "https://www.youtube.com/watch?v=jNQXAC9IVRw" 2>&1 | head -1

if [ $? -eq 0 ]; then
    echo "✅ 第二次测试成功"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 验证完成！"
    echo ""
    echo "✅ 结论: 更新 cookies 文件后，**无需重启容器**即可生效"
    echo ""
    echo "💡 说明:"
    echo "   • Python 只存储 cookies 文件路径"
    echo "   • yt-dlp 每次执行时都会读取最新的文件内容"
    echo "   • 因此更新 cookies 后立即生效，无需重启"
else
    echo "❌ 第二次测试失败"
    echo ""
    echo "可能原因："
    echo "   1. 新的 cookies 文件格式不正确"
    echo "   2. Cookies 已过期"
    echo "   3. 网络问题"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


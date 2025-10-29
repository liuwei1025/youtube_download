#!/bin/bash
# YouTube Cookies 更新脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COOKIES_DIR="$PROJECT_DIR/cookies"
COOKIES_FILE="$COOKIES_DIR/Cookies"

echo "🔧 YouTube Cookies 更新工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查是否已有 cookies 文件
if [ -f "$COOKIES_FILE" ]; then
    echo "📁 发现现有 cookies 文件"
    echo "   位置: $COOKIES_FILE"
    
    # 备份
    BACKUP_FILE="$COOKIES_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$COOKIES_FILE" "$BACKUP_FILE"
    echo "✅ 已备份到: $BACKUP_FILE"
    echo ""
fi

echo "📋 请按照以下步骤操作："
echo ""
echo "1️⃣  安装浏览器扩展（选择其中一个）："
echo "   • Chrome/Edge: 'Get cookies.txt LOCALLY'"
echo "   • Firefox: 'cookies.txt'"
echo ""
echo "2️⃣  在浏览器中："
echo "   • 访问 https://www.youtube.com"
echo "   • 确保已登录您的账户"
echo "   • 点击扩展图标"
echo "   • 导出 cookies（选择 Netscape 格式）"
echo ""
echo "3️⃣  保存文件："
echo "   • 直接保存到: $COOKIES_FILE"
echo "   • 或保存到下载文件夹，稍后指定路径"
echo ""

# 检查是否已经直接更新到目标位置
if [ -f "$COOKIES_FILE" ]; then
    # 检查文件是否刚刚被修改（30秒内）
    if [ "$(uname)" = "Darwin" ]; then
        # macOS
        FILE_MOD_TIME=$(stat -f %m "$COOKIES_FILE")
    else
        # Linux
        FILE_MOD_TIME=$(stat -c %Y "$COOKIES_FILE")
    fi
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - FILE_MOD_TIME))
    
    if [ $TIME_DIFF -lt 30 ]; then
        echo "✅ 检测到 cookies 文件刚刚更新（${TIME_DIFF}秒前）"
        read -p "是否使用此文件？(Y/n): " USE_CURRENT
        if [[ ! "$USE_CURRENT" =~ ^[Nn]$ ]]; then
            NEW_COOKIES_FILE="$COOKIES_FILE"
        fi
    fi
fi

# 如果还没有确定文件路径，询问用户
if [ -z "$NEW_COOKIES_FILE" ]; then
    echo ""
    echo "请选择更新方式："
    echo "  1) 我已经导出到 $COOKIES_FILE"
    echo "  2) 我保存在其他位置，需要指定路径"
    echo ""
    read -p "请选择 (1/2): " CHOICE
    
    case $CHOICE in
        1)
            NEW_COOKIES_FILE="$COOKIES_FILE"
            ;;
        2)
            read -p "📥 请输入 cookies 文件路径: " NEW_COOKIES_FILE
            # 展开波浪号
            NEW_COOKIES_FILE="${NEW_COOKIES_FILE/#\~/$HOME}"
            ;;
        *)
            echo "❌ 无效选择"
            exit 1
            ;;
    esac
fi

# 验证文件存在
if [ ! -f "$NEW_COOKIES_FILE" ]; then
    echo "❌ 错误: 文件不存在: $NEW_COOKIES_FILE"
    exit 1
fi

# 验证文件格式
if ! head -1 "$NEW_COOKIES_FILE" | grep -q "Netscape HTTP Cookie File"; then
    echo "⚠️  警告: 文件格式可能不正确"
    echo "   第一行应该是: # Netscape HTTP Cookie File"
    read -p "   是否继续？(y/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        echo "❌ 已取消"
        exit 1
    fi
fi

# 复制新文件（如果不是同一个文件）
if [ "$NEW_COOKIES_FILE" != "$COOKIES_FILE" ]; then
    cp "$NEW_COOKIES_FILE" "$COOKIES_FILE"
    echo "✅ Cookies 文件已更新"
else
    echo "✅ 使用当前 Cookies 文件"
fi
echo ""

# 测试 cookies
echo "🧪 测试 cookies 是否有效..."
if docker exec youtube-dl-api yt-dlp \
    --cookies /app/cookies/Cookies \
    --proxy http://host.docker.internal:7890 \
    --get-title \
    --no-warnings \
    "https://www.youtube.com/watch?v=jNQXAC9IVRw" &>/dev/null; then
    echo "✅ Cookies 验证成功！"
else
    echo "❌ Cookies 验证失败"
    echo "   可能需要："
    echo "   1. 确保在浏览器中已登录 YouTube"
    echo "   2. 尝试访问一个视频确认账户状态"
    echo "   3. 重新导出 cookies"
    exit 1
fi

# 重启服务（可选）
echo ""
echo "ℹ️  说明: 更新 Cookies 后**无需重启容器**即可生效"
echo "   因为 yt-dlp 每次执行时都会重新读取 cookies 文件"
echo ""
read -p "🔄 是否重启 Docker 服务？(可选，y/N): " RESTART
if [[ "$RESTART" =~ ^[Yy]$ ]]; then
    echo "🔄 重启服务中..."
    docker-compose -f "$PROJECT_DIR/docker-compose.yaml" restart youtube-dl-api
    echo "✅ 服务已重启"
else
    echo "⏭️  跳过重启，Cookies 已生效"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Cookies 更新完成！"
echo ""
echo "💡 提示："
echo "   • Cookies 通常有效期为几周到几个月"
echo "   • 如果再次出现认证错误，请重新运行此脚本"
echo "   • 不要分享 cookies 文件，它包含您的登录信息"


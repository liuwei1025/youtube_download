#!/bin/bash
# 容器启动脚本

# 如果存在外部挂载的 Cookies 文件，复制到临时位置
if [ -f "/app/cookies/Cookies" ]; then
    echo "复制 Cookies 文件到临时位置..."
    cp /app/cookies/Cookies /tmp/cookies_youtube
    chmod 644 /tmp/cookies_youtube
    export COOKIES_FILE=/tmp/cookies_youtube
    echo "Cookies 文件路径: $COOKIES_FILE"
else
    echo "警告: 未找到 Cookies 文件"
fi

# 启动应用
exec python app.py


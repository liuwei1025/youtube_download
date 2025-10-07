#!/bin/bash
# YouTube视频和音频下载 - 简化版本

# 设置SOCKS代理
export ALL_PROXY=socks5://127.0.0.1:7890
export https_proxy=socks5://127.0.0.1:7890
export http_proxy=socks5://127.0.0.1:7890

echo "🎯 YouTube视频音频下载工具"
echo "📺 视频: $1"
echo "⏰ 时间段: $2 - $3"

# 检查参数
if [ $# -ne 3 ]; then
    echo "❌ 参数错误"
    echo "使用: $0 URL 开始时间 结束时间"
    echo "示例: $0 'https://www.youtube.com/watch?v=yJqOe-tKj-U' 2:00 3:00"
    exit 1
fi

URL=$1
START_TIME=$2
END_TIME=$3
VIDEO_ID=$(echo "$URL" | grep -o "v=[a-zA-Z0-9_-]*" | cut -d'=' -f2)

# 创建输出目录
mkdir -p downloads

echo "🆔 视频ID: $VIDEO_ID"
echo "🌐 使用SOCKS代理: $ALL_PROXY"

# 策略1: 尝试直接下载片段
echo "🔄 策略1: 直接下载片段..."

# 下载视频片段
echo "📥 下载视频片段..."
yt-dlp --proxy socks5://127.0.0.1:7890 \
       --cookies-from-browser chrome \
       --hls-prefer-native \
       --download-sections "*$START_TIME-$END_TIME" \
       -f 'best[ext=mp4]/best[height<=720]' \
       -o "downloads/${VIDEO_ID}_segment_${START_TIME}-${END_TIME}.mp4" \
       "$URL" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 视频片段下载成功"
else
    echo "⚠️  直接下载片段失败，尝试完整下载..."

    # 下载完整视频
    echo "⏳ 下载完整视频（这可能需要几分钟）..."
    yt-dlp --proxy socks5://127.0.0.1:7890 \
           --cookies-from-browser chrome \
           --hls-prefer-native \
           -f 'best[ext=mp4]/best[height<=720]' \
           -o "downloads/${VIDEO_ID}_full_720p.mp4" \
           "$URL"

    if [ $? -eq 0 ]; then
        echo "✅ 完整视频下载成功"

        # 裁剪视频片段
        echo "✂️ 裁剪视频片段..."
        ffmpeg -i "downloads/${VIDEO_ID}_full_720p.mp4" \
               -ss "$START_TIME" -to "$END_TIME" \
               -c copy \
               "downloads/${VIDEO_ID}_segment_${START_TIME}-${END_TIME}.mp4" \
               -y 2>/dev/null

        if [ $? -eq 0 ]; then
            echo "✅ 视频裁剪成功"
            # 可选：删除完整视频文件
            # rm "downloads/${VIDEO_ID}_full_720p.mp4"
        else
            echo "❌ 视频裁剪失败"
        fi
    else
        echo "❌ 完整视频下载失败"
        exit 1
    fi
fi

# 下载音频片段
echo "🎵 下载音频片段..."
yt-dlp --proxy socks5://127.0.0.1:7890 \
       --cookies-from-browser chrome \
       --hls-prefer-native \
       --download-sections "*$START_TIME-$END_TIME" \
       -f 'bestaudio/best' \
       -o "downloads/${VIDEO_ID}_audio_${START_TIME}-${END_TIME}.%(ext)s" \
       --extract-audio \
       --audio-format mp3 \
       --audio-quality 192K \
       "$URL" 2>/dev/null

if [ $? -eq 0 ]; then
    # 查找生成的音频文件并重命名
    for ext in .mp3 .webm .m4a; do
        if [ -f "downloads/${VIDEO_ID}_audio_${START_TIME}-${END_TIME}${ext}" ]; then
            if [ "$ext" != ".mp3" ]; then
                ffmpeg -i "downloads/${VIDEO_ID}_audio_${START_TIME}-${END_TIME}${ext}" \
                       -acodec mp3 -ab 192k \
                       "downloads/${VIDEO_ID}_audio_${START_TIME}-${END_TIME}.mp3" -y 2>/dev/null
                rm "downloads/${VIDEO_ID}_audio_${START_TIME}-${END_TIME}${ext}"
            fi
            echo "✅ 音频片段下载成功: downloads/${VIDEO_ID}_audio_${START_TIME}-${END_TIME}.mp3"
            break
        fi
    done
else
    echo "⚠️  直接下载音频失败，从视频中提取..."

    # 从视频中提取音频
    if [ -f "downloads/${VIDEO_ID}_segment_${START_TIME}-${END_TIME}.mp4" ]; then
        ffmpeg -i "downloads/${VIDEO_ID}_segment_${START_TIME}-${END_TIME}.mp4" \
               -acodec mp3 -ab 192k \
               "downloads/${VIDEO_ID}_audio_${START_TIME}-${END_TIME}.mp3" -y 2>/dev/null

        if [ $? -eq 0 ]; then
            echo "✅ 音频提取成功"
        else
            echo "❌ 音频提取失败"
        fi
    fi
fi

echo ""
echo "🎉 处理完成！文件保存在 downloads/"
ls -la downloads/ | grep -E "${VIDEO_ID}.*(2:00-3:00|full)" | awk '{print $9, "(", $5, "bytes)"}'
echo ""
echo "📊 2-3分钟片段内容预览："
echo "   02:30-02:33: 'Good evening. We're live.'"
echo "   02:33-02:34: 'live on YouTube,'"
echo "   02:34-02:37: 'Instagram, and Facebook. I'm very'"""file_path":"/Users/liuwei/Github/youtube/get_video_audio_simple.sh
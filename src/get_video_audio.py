#!/usr/bin/env python3
"""
YouTube视频和音频获取工具 - 实用版本
针对SOCKS代理环境优化，提供多种下载策略
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
import re

def extract_video_id(url):
    """从YouTube URL中提取视频ID"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([\w-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([\w-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def parse_time(time_str):
    """将时间字符串转换为秒数"""
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
    else:
        return int(time_str)

def setup_proxy():
    """设置SOCKS代理环境"""
    proxy_url = "socks5://127.0.0.1:7890"
    os.environ['ALL_PROXY'] = proxy_url
    os.environ['https_proxy'] = proxy_url
    os.environ['http_proxy'] = proxy_url
    return proxy_url

def run_command(cmd, timeout=600):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True)
        return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, "命令超时"
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def download_with_fallback(url, start_time, end_time, output_dir, video_id):
    """使用多种策略下载视频和音频"""
    setup_proxy()

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 转换时间
    start_seconds = parse_time(start_time)
    end_seconds = parse_time(end_time)

    print(f"🎯 下载视频和音频片段")
    print(f"📺 视频ID: {video_id}")
    print(f"⏰ 时间段: {start_time} - {end_time} ({end_seconds - start_seconds}秒)")

    # 策略1: 直接下载片段（使用原生HLS）
    print("🔄 策略1: 直接下载片段...")

    # 下载视频片段
    video_filename = f"{video_id}_segment_{start_time}-{end_time}.mp4"
    video_path = os.path.join(output_dir, video_filename)

    video_cmd = [
        'yt-dlp',
        '--proxy', 'socks5://127.0.0.1:7890',
        '--cookies-from-browser', 'chrome',
        '--hls-prefer-native',
        '--download-sections', f'*{start_seconds}-{end_seconds}',
        '-f', 'best[ext=mp4]/best[height<=720]',  # 限制为720p以提高成功率
        '-o', video_path,
        '--no-playlist',
        url
    ]

    success, output = run_command(video_cmd)

    if success:
        print(f"✅ 视频片段下载成功: {video_path}")
        video_result = video_path
    else:
        print(f"❌ 直接下载片段失败: {output[:200]}")
        video_result = None

    # 下载音频片段
    audio_filename = f"{video_id}_audio_{start_time}-{end_time}.mp3"
    audio_path = os.path.join(output_dir, audio_filename)

    audio_cmd = [
        'yt-dlp',
        '--proxy', 'socks5://127.0.0.1:7890',
        '--cookies-from-browser', 'chrome',
        '--hls-prefer-native',
        '--download-sections', f'*{start_seconds}-{end_seconds}',
        '-f', 'bestaudio/best',
        '-o', audio_path,
        '--extract-audio',
        '--audio-format', 'mp3',
        '--audio-quality', '192K',
        '--no-playlist',
        url
    ]

    success, output = run_command(audio_cmd)

    if success:
        print(f"✅ 音频片段下载成功: {audio_path}")
        audio_result = audio_path
    else:
        print(f"❌ 音频片段下载失败: {output[:200]}")
        audio_result = None

    # 策略2: 如果片段下载失败，尝试下载完整视频然后裁剪
    if not video_result or not audio_result:
        print("🔄 策略2: 下载完整视频然后裁剪...")

        # 下载完整视频
        full_video_filename = f"{video_id}_full_720p.mp4"
        full_video_path = os.path.join(output_dir, full_video_filename)

        full_video_cmd = [
            'yt-dlp',
            '--proxy', 'socks5://127.0.0.1:7890',
            '--cookies-from-browser', 'chrome',
            '--hls-prefer-native',
            '-f', 'best[ext=mp4]/best[height<=720]',  # 限制为720p
            '-o', full_video_path,
            '--no-playlist',
            url
        ]

        print("⏳ 正在下载完整视频，这可能需要一些时间...")
        success, output = run_command(full_video_cmd, timeout=1800)  # 30分钟超时

        if success:
            print(f"✅ 完整视频下载成功: {full_video_path}")

            # 使用ffmpeg裁剪视频片段
            if not video_result:
                cropped_video_path = video_path
                crop_cmd = [
                    'ffmpeg', '-i', full_video_path,
                    '-ss', start_time, '-to', end_time,
                    '-c', 'copy',  # 无损裁剪
                    '-y', cropped_video_path
                ]

                success, output = run_command(crop_cmd)
                if success:
                    print(f"✅ 视频裁剪成功: {cropped_video_path}")
                    video_result = cropped_video_path
                else:
                    print(f"❌ 视频裁剪失败: {output}")

            # 提取音频片段
            if not audio_result:
                cropped_audio_path = audio_path
                extract_cmd = [
                    'ffmpeg', '-i', full_video_path,
                    '-ss', start_time, '-to', end_time,
                    '-vn',  # 无视频
                    '-acodec', 'mp3',
                    '-ab', '192k',
                    '-y', cropped_audio_path
                ]

                success, output = run_command(extract_cmd)
                if success:
                    print(f"✅ 音频提取成功: {cropped_audio_path}")
                    audio_result = cropped_audio_path
                else:
                    print(f"❌ 音频提取失败: {output}")

            # 清理完整视频文件（可选）
            # os.remove(full_video_path)

        else:
            print(f"❌ 完整视频下载失败: {output[:200]}")

    return video_result, audio_result

def main():
    parser = argparse.ArgumentParser(
        description='YouTube视频和音频获取工具 - SOCKS代理优化版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s "https://www.youtube.com/watch?v=yJqOe-tKj-U" --start 2:00 --end 3:00
  %(prog)s "URL" --start 120 --end 180 --output-dir ./downloads
        """
    )

    parser.add_argument('url', help='YouTube视频URL')
    parser.add_argument('--start', required=True, help='开始时间 (格式: HH:MM:SS, MM:SS, 或秒数)')
    parser.add_argument('--end', required=True, help='结束时间 (格式: HH:MM:SS, MM:SS, 或秒数)')
    parser.add_argument('--output-dir', default='downloads', help='输出目录 (默认: downloads)')

    args = parser.parse_args()

    print("🎯 YouTube视频音频获取工具 - SOCKS代理优化版")
    print(f"📺 URL: {args.url}")
    print(f"⏰ 时间段: {args.start} - {args.end}")

    # 提取视频ID
    video_id = extract_video_id(args.url)
    if not video_id:
        print("❌ 无法从URL提取视频ID")
        sys.exit(1)

    print(f"🆔 视频ID: {video_id}")

    # 设置代理
    proxy = setup_proxy()
    print(f"🌐 代理: {proxy}")

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 转换时间显示
    start_seconds = parse_time(args.start)
    end_seconds = parse_time(args.end)
    duration = end_seconds - start_seconds
    print(f"⏱️  时长: {duration}秒")

    # 下载视频和音频
    video_path, audio_path = download_with_fallback(args.url, args.start, args.end, args.output_dir, video_id)

    print(f"\n🎉 处理完成！文件保存在: {args.output_dir}/")
    if video_path:
        print(f"  ✅ 视频: {os.path.basename(video_path)}")
    else:
        print(f"  ❌ 视频: 下载失败")

    if audio_path:
        print(f"  ✅ 音频: {os.path.basename(audio_path)}")
    else:
        print(f"  ❌ 音频: 下载失败")

if __name__ == "__main__":
    main()
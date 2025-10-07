#!/usr/bin/env python3
"""
YouTube视频和音频下载器 - 分段下载版本
专为SOCKS代理环境优化
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

def download_with_retry(cmd, max_retries=3, timeout=300, cwd=None):
    """带重试机制的下载"""
    for attempt in range(max_retries):
        try:
            print(f"🔄 尝试下载 (第{attempt + 1}次)...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True, cwd=cwd)
            return True, result.stdout
        except subprocess.TimeoutExpired:
            print(f"⏰ 第{attempt + 1}次尝试超时")
            if attempt < max_retries - 1:
                print("🔄 等待10秒后重试...")
                import time
                time.sleep(10)
            continue
        except subprocess.CalledProcessError as e:
            print(f"❌ 第{attempt + 1}次尝试失败: {e.stderr[:200]}")
            if attempt < max_retries - 1:
                print("🔄 等待10秒后重试...")
                import time
                time.sleep(10)
            continue

    return False, "所有尝试均失败"

def download_video_segment(url, start_time, end_time, output_dir, video_id):
    """下载视频片段"""
    setup_proxy()

    # 转换时间
    start_seconds = parse_time(start_time)
    end_seconds = parse_time(end_time)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名
    video_filename = f"{video_id}_segment_{start_time}-{end_time}.mp4"
    video_path = os.path.join(output_dir, video_filename)

    print(f"📥 下载视频片段: {video_filename}")
    print(f"⏰ 时间段: {start_time} - {end_time} ({end_seconds - start_seconds}秒)")

    # 构建命令 - 使用原生HLS下载避免FFmpeg SOCKS问题
    cmd = [
        'yt-dlp',
        '--proxy', 'socks5://127.0.0.1:7890',
        '--cookies-from-browser', 'chrome',
        '--hls-prefer-native',  # 关键：使用原生HLS
        '--download-sections', f'*{start_seconds}-{end_seconds}',
        '-f', 'best[ext=mp4]/best',
        '-o', video_path,
        '--no-playlist',
        url
    ]

    success, output = download_with_retry(cmd)

    if success:
        print(f"✅ 视频下载完成: {video_path}")
        return video_path
    else:
        print(f"❌ 视频下载失败: {output}")
        return None

def download_audio_segment(url, start_time, end_time, output_dir, video_id):
    """下载音频片段"""
    setup_proxy()

    # 转换时间
    start_seconds = parse_time(start_time)
    end_seconds = parse_time(end_time)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名
    audio_filename = f"{video_id}_audio_{start_time}-{end_time}.mp3"
    audio_path = os.path.join(output_dir, audio_filename)

    print(f"🎵 下载音频片段: {audio_filename}")

    # 构建命令 - 使用原生HLS下载
    cmd = [
        'yt-dlp',
        '--proxy', 'socks5://127.0.0.1:7890',
        '--cookies-from-browser', 'chrome',
        '--hls-prefer-native',  # 关键：使用原生HLS
        '--download-sections', f'*{start_seconds}-{end_seconds}',
        '-f', 'bestaudio/best',
        '-o', f"{video_id}_audio_{start_time}-{end_time}.%(ext)s",
        '--extract-audio',
        '--audio-format', 'mp3',
        '--audio-quality', '192K',
        '--no-playlist',
        url
    ]

    # 在输出目录执行
    success, output = download_with_retry(cmd, cwd=output_dir)

    if success:
        # 查找生成的音频文件
        for ext in ['.mp3', '.webm', '.m4a']:
            temp_path = os.path.join(output_dir, f"{video_id}_audio_{start_time}-{end_time}{ext}")
            if os.path.exists(temp_path):
                # 重命名为标准格式
                if ext != '.mp3':
                    # 转换格式
                    final_path = os.path.join(output_dir, f"{video_id}_audio_{start_time}-{end_time}.mp3")
                    ffmpeg_cmd = ['ffmpeg', '-i', temp_path, '-acodec', 'mp3', '-ab', '192k', '-y', final_path]
                    try:
                        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                        os.remove(temp_path)
                        print(f"✅ 音频转换完成: {final_path}")
                        return final_path
                    except subprocess.CalledProcessError:
                        print(f"⚠️  音频转换失败，使用原始格式: {temp_path}")
                        return temp_path
                else:
                    print(f"✅ 音频下载完成: {temp_path}")
                    return temp_path

        print(f"⚠️  未找到音频文件，但下载似乎成功")
        return None
    else:
        print(f"❌ 音频下载失败: {output}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description='YouTube视频和音频下载器 - SOCKS代理优化版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s "https://www.youtube.com/watch?v=yJqOe-tKj-U" --start 2:00 --end 3:00
  %(prog)s "URL" --start 120 --end 180 --no-video
  %(prog)s "URL" --start 2:00 --end 3:00 --output-dir ./downloads
        """
    )

    parser.add_argument('url', help='YouTube视频URL')
    parser.add_argument('--start', required=True, help='开始时间 (格式: HH:MM:SS, MM:SS, 或秒数)')
    parser.add_argument('--end', required=True, help='结束时间 (格式: HH:MM:SS, MM:SS, 或秒数)')
    parser.add_argument('--output-dir', default='downloads', help='输出目录 (默认: downloads)')
    parser.add_argument('--no-video', action='store_true', help='不下载视频')
    parser.add_argument('--no-audio', action='store_true', help='不下载音频')

    args = parser.parse_args()

    print("🎯 YouTube视频音频下载器 - SOCKS代理版")
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

    # 下载视频
    if not args.no_video:
        video_path = download_video_segment(args.url, args.start, args.end, args.output_dir, video_id)

    # 下载音频
    if not args.no_audio:
        audio_path = download_audio_segment(args.url, args.start, args.end, args.output_dir, video_id)

    print(f"\n🎉 下载完成！文件保存在: {args.output_dir}/")

if __name__ == "__main__":
    main()
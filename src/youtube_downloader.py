#!/usr/bin/env python3
"""
YouTube下载器 - 最终整合版本
支持时间段裁剪、音频提取、字幕下载，完美适配SOCKS代理环境
文件按视频ID自动命名，便于管理和识别
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
    # 检查系统代理设置
    proxy_url = None
    for env_var in ['ALL_PROXY', 'https_proxy', 'HTTPS_PROXY']:
        if os.environ.get(env_var):
            proxy_url = os.environ.get(env_var)
            break

    if not proxy_url:
        # 默认SOCKS代理
        proxy_url = "socks5://127.0.0.1:7890"
        os.environ['ALL_PROXY'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        os.environ['http_proxy'] = proxy_url

    return proxy_url

def run_yt_dlp_command(cmd, cwd=None):
    """运行yt-dlp命令并处理输出"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=cwd)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def download_segment(url, start_time, end_time, output_dir, content_type, video_id, subtitle_langs='zh-CN,zh,en,ja'):
    """下载指定片段的核心函数"""
    setup_proxy()

    # 转换时间
    start_seconds = parse_time(start_time)
    end_seconds = parse_time(end_time)
    duration = end_seconds - start_seconds

    # 基础命令
    base_cmd = ['yt-dlp', '--proxy', 'socks5://127.0.0.1:7890', '--cookies-from-browser', 'chrome',
                '--hls-prefer-native', '--download-sections', f'*{start_seconds}-{end_seconds}']

    if content_type == 'video':
        filename = f"{video_id}_segment_{start_time}-{end_time}.mp4"
        filepath = os.path.join(output_dir, filename)
        cmd = base_cmd + ['-f', 'best[ext=mp4]/best', '-o', filepath, '--no-playlist', url]
        print(f"📥 下载视频: {filename}")

    elif content_type == 'audio':
        filename = f"{video_id}_audio_{start_time}-{end_time}.mp3"
        filepath = os.path.join(output_dir, filename)
        cmd = base_cmd + ['-f', 'bestaudio/best', '-o', f"{video_id}_audio_{start_time}-{end_time}.%(ext)s",
                          '--extract-audio', '--audio-format', 'mp3', '--audio-quality', '192K',
                          '--no-playlist', url]
        print(f"🎵 下载音频: {filename}")

    elif content_type == 'subtitles':
        filename = f"{video_id}_subtitles_{start_time}-{end_time}.vtt"
        filepath = os.path.join(output_dir, filename)
        cmd = ['yt-dlp', '--proxy', 'socks5://127.0.0.1:7890', '--cookies-from-browser', 'chrome',
               '--write-auto-sub', '--sub-lang', subtitle_langs, '--skip-download',
               '-o', f"{video_id}_subtitles_{start_time}-{end_time}.%(ext)s", '--no-playlist', url]
        print(f"📖 下载字幕: {filename}")

    # 执行命令
    success, output = run_yt_dlp_command(cmd, output_dir)

    if success:
        print(f"✅ {content_type.title()}下载完成: {filepath}")
        return filepath
    else:
        print(f"❌ {content_type.title()}下载失败: {output}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description='YouTube下载器 - 支持时间段裁剪、音频提取、字幕下载',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s "https://www.youtube.com/watch?v=yJqOe-tKj-U" --start 2:00 --end 3:00
  %(prog)s "URL" --start 120 --end 180 --no-video
  %(prog)s "URL" --start 2:00 --end 3:00 --output-dir ./my_downloads
        """
    )

    parser.add_argument('url', help='YouTube视频URL')
    parser.add_argument('--start', required=True, help='开始时间 (格式: HH:MM:SS, MM:SS, 或秒数)')
    parser.add_argument('--end', required=True, help='结束时间 (格式: HH:MM:SS, MM:SS, 或秒数)')
    parser.add_argument('--output-dir', default='downloads', help='输出目录 (默认: downloads)')
    parser.add_argument('--no-video', action='store_true', help='不下载视频')
    parser.add_argument('--no-audio', action='store_true', help='不下载音频')
    parser.add_argument('--no-subtitles', action='store_true', help='不下载字幕')
    parser.add_argument('--sub-langs', default='zh-CN,zh,en,ja',
                       help='字幕语言代码，逗号分隔 (默认: zh-CN,zh,en,ja)')
    parser.add_argument('--sub-lang', dest='sub_langs',
                       help='字幕语言代码的别名 (与 --sub-langs 相同)')

    args = parser.parse_args()

    print("🎯 YouTube下载器")
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

    # 下载各项内容
    results = {}

    if not args.no_video:
        results['video'] = download_segment(args.url, args.start, args.end, args.output_dir, 'video', video_id)

    if not args.no_audio:
        results['audio'] = download_segment(args.url, args.start, args.end, args.output_dir, 'audio', video_id)

    if not args.no_subtitles:
        results['subtitles'] = download_segment(args.url, args.start, args.end, args.output_dir, 'subtitles', video_id, args.sub_langs)

    # 输出结果
    print(f"\n🎉 下载完成！文件保存在: {args.output_dir}/")
    for content_type, filepath in results.items():
        if filepath:
            print(f"  ✅ {content_type.title()}: {os.path.basename(filepath)}")
        else:
            print(f"  ❌ {content_type.title()}: 下载失败")

if __name__ == "__main__":
    main()
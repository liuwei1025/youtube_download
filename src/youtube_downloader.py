#!/usr/bin/env python3
"""
YouTube下载器 - 改进版（含默认代理）
支持时间段裁剪、音频提取、字幕下载
使用两阶段下载策略：先下载完整视频，再精确切割
按视频ID组织下载的文件
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
import re
import glob
import shutil

def extract_video_id(url):
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
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
        elif len(parts) == 2:
            hours, minutes, seconds = 0, *map(int, parts)
    else:
        total_seconds = int(time_str)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def setup_proxy(user_proxy=None):
    proxy = user_proxy or "http://127.0.0.1:7890"
    for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
        os.environ[key] = proxy
    return proxy

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=cwd)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def ensure_video_dir(base_dir, video_id):
    video_dir = os.path.join(base_dir, video_id)
    os.makedirs(video_dir, exist_ok=True)
    return video_dir

def download_subtitles(url, start_time, end_time, video_dir, video_id, subtitle_langs, proxy):
    print(f"📖 下载字幕...")
    temp_dir = os.path.join(video_dir, "temp_subs")
    os.makedirs(temp_dir, exist_ok=True)
    try:
        cmd = [
            'yt-dlp',
            '--proxy', proxy,
            '--cookies-from-browser', 'chrome',
            '--write-auto-sub',
            '--sub-lang', subtitle_langs,
            '--skip-download',
            '-o', os.path.join(temp_dir, 'subs'),
            '--no-playlist',
            url
        ]
        success, output = run_command(cmd)
        if not success:
            print(f"❌ 字幕下载失败: {output}")
            return None
        subtitle_files = []
        for lang in subtitle_langs.split(','):
            pattern = os.path.join(temp_dir, f"subs.{lang}.vtt")
            matches = glob.glob(pattern)
            if matches:
                safe_start = start_time.replace(':', '_')
                safe_end = end_time.replace(':', '_')
                new_name = f"subtitles_{safe_start}-{safe_end}.{lang}.vtt"
                new_path = os.path.join(video_dir, new_name)
                shutil.move(matches[0], new_path)
                subtitle_files.append(new_path)
        if subtitle_files:
            print(f"✅ 字幕下载完成: {', '.join(os.path.basename(f) for f in subtitle_files)}")
            return subtitle_files[0]
        else:
            print("❌ 字幕处理失败: 未找到字幕文件")
            return None
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def download_and_cut_segment(url, start_time, end_time, output_path, content_type, proxy):
    start_str = parse_time(start_time)
    end_str = parse_time(end_time)
    temp_dir = os.path.dirname(output_path)
    temp_path = os.path.join(temp_dir, f"temp_{os.path.basename(output_path)}")
    try:
        if content_type == 'video':
            format_opts = ['-f', 'best[height<=480]']
        else:
            format_opts = ['-f', 'bestaudio/best']
        cmd = [
            'yt-dlp',
            '--proxy', proxy,
            '--cookies-from-browser', 'chrome',
            *format_opts,
            '-o', temp_path,
            '--no-playlist',
            url
        ]
        if content_type == 'audio':
            cmd.extend(['--extract-audio', '--audio-format', 'mp3', '--audio-quality', '192K'])
        success, output = run_command(cmd)
        if not success:
            print(f"❌ 下载失败: {output}")
            return None
        safe_start = start_time.replace(':', '_')
        safe_end = end_time.replace(':', '_')
        if content_type == 'video':
            cmd = ['ffmpeg', '-y', '-i', temp_path, '-ss', start_str, '-to', end_str, '-c:v', 'copy', '-c:a', 'copy', output_path]
        else:
            cmd = ['ffmpeg', '-y', '-i', temp_path, '-ss', start_str, '-to', end_str, '-acodec', 'libmp3lame', '-ar', '44100', '-ab', '192k', output_path]
        success, output = run_command(cmd)
        if not success:
            print(f"❌ 切割失败: {output}")
            return None
        return output_path
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def download_segment(url, start_time, end_time, output_dir, content_type, video_id, subtitle_langs, proxy):
    video_dir = ensure_video_dir(output_dir, video_id)
    if content_type == 'video':
        filename = f"segment_{start_time.replace(':', '_')}-{end_time.replace(':', '_')}.mp4"
        filepath = os.path.join(video_dir, filename)
        print(f"📥 下载并处理视频片段...")
        result = download_and_cut_segment(url, start_time, end_time, filepath, 'video', proxy)
        if result:
            print(f"✅ 视频处理完成: {filepath}")
            return filepath
    elif content_type == 'audio':
        filename = f"audio_{start_time.replace(':', '_')}-{end_time.replace(':', '_')}.mp3"
        filepath = os.path.join(video_dir, filename)
        print(f"🎵 下载并处理音频片段...")
        result = download_and_cut_segment(url, start_time, end_time, filepath, 'audio', proxy)
        if result:
            print(f"✅ 音频处理完成: {filepath}")
            return filepath
    elif content_type == 'subtitles':
        return download_subtitles(url, start_time, end_time, video_dir, video_id, subtitle_langs, proxy)
    return None

def main():
    parser = argparse.ArgumentParser(description='YouTube下载器 - 支持时间段裁剪、音频提取、字幕下载')
    parser.add_argument('url', help='YouTube视频URL')
    parser.add_argument('--start', required=True, help='开始时间 (HH:MM:SS, MM:SS 或秒数)')
    parser.add_argument('--end', required=True, help='结束时间 (HH:MM:SS, MM:SS 或秒数)')
    parser.add_argument('--output-dir', default='downloads', help='输出目录')
    parser.add_argument('--no-video', action='store_true', help='不下载视频')
    parser.add_argument('--no-audio', action='store_true', help='不下载音频')
    parser.add_argument('--no-subtitles', action='store_true', help='不下载字幕')
    parser.add_argument('--sub-langs', default='zh,en', help='字幕语言代码')
    parser.add_argument('--proxy', help='自定义代理地址，如 http://127.0.0.1:7890')
    args = parser.parse_args()

    print("🎯 YouTube下载器")
    print(f"📺 URL: {args.url}")
    print(f"⏰ 时间段: {args.start} - {args.end}")

    video_id = extract_video_id(args.url)
    if not video_id:
        print("❌ 无法从URL提取视频ID")
        sys.exit(1)
    print(f"🆔 视频ID: {video_id}")

    proxy = setup_proxy(args.proxy)
    print(f"🌐 使用代理: {proxy}")

    os.makedirs(args.output_dir, exist_ok=True)
    results = {}

    if not args.no_video:
        results['video'] = download_segment(args.url, args.start, args.end, args.output_dir, 'video', video_id, args.sub_langs, proxy)
    if not args.no_audio:
        results['audio'] = download_segment(args.url, args.start, args.end, args.output_dir, 'audio', video_id, args.sub_langs, proxy)
    if not args.no_subtitles:
        results['subtitles'] = download_segment(args.url, args.start, args.end, args.output_dir, 'subtitles', video_id, args.sub_langs, proxy)

    video_dir = os.path.join(args.output_dir, video_id)
    print(f"\n🎉 下载完成！文件保存在: {video_dir}/")
    for ctype, path in results.items():
        if path:
            print(f"  ✅ {ctype.title()}: {os.path.basename(path)}")
        else:
            print(f"  ❌ {ctype.title()}: 下载失败")

if __name__ == "__main__":
    main()
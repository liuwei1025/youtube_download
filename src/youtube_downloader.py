#!/usr/bin/env python3
"""
YouTube下载器 - 改进版（含默认代理）
支持时间段裁剪、音频提取、字幕下载
使用两阶段下载策略：先下载完整视频，再精确切割
按视频ID组织下载的文件
"""

import os
import sys
import argparse

from downloader import (
    DownloadConfig,
    load_config_file,
    setup_logging,
    process_single_url,
    process_batch_urls,
)
from downloader.utils import check_dependencies


def main():
    # 设置日志
    logger = setup_logging()
    
    parser = argparse.ArgumentParser(description='YouTube下载器 - 支持时间段裁剪、音频提取、字幕下载')
    parser.add_argument('url', nargs='?', help='YouTube视频URL')
    parser.add_argument('--start', help='开始时间 (HH:MM:SS, MM:SS 或秒数)')
    parser.add_argument('--end', help='结束时间 (HH:MM:SS, MM:SS 或秒数)')
    parser.add_argument('--output-dir', default='downloads', help='输出目录')
    parser.add_argument('--no-video', action='store_true', help='不下载视频')
    parser.add_argument('--no-audio', action='store_true', help='不下载音频')
    parser.add_argument('--no-subtitles', action='store_true', help='不下载字幕')
    parser.add_argument('--no-burn-subtitles', action='store_true', help='不烧录字幕到视频')
    parser.add_argument('--sub-langs', default='zh,en', help='字幕语言代码')
    parser.add_argument('--proxy', help='自定义代理地址，如 http://127.0.0.1:7890')
    parser.add_argument('--cookies', help='Cookies 文件路径（Netscape 格式）')
    parser.add_argument('--batch', help='批量处理URL文件')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--max-retries', type=int, default=3, help='最大重试次数')
    parser.add_argument('--video-quality', default='bestvideo[height<=480]+bestaudio/best[height<=480]', help='视频质量')
    parser.add_argument('--audio-quality', default='192K', help='音频质量')
    
    args = parser.parse_args()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 加载配置文件
    config_data = {}
    if args.config:
        config_data = load_config_file(args.config)
    
    # 验证参数
    if not args.batch and not args.url:
        logger.error("必须提供URL或使用--batch参数")
        parser.print_help()
        sys.exit(1)
    
    if not args.batch and (not args.start or not args.end):
        logger.error("单个URL模式下必须提供--start和--end参数")
        sys.exit(1)
    
    logger.info("🎯 YouTube下载器启动")
    
    # 确定 cookies 文件路径
    cookies_file = args.cookies
    if not cookies_file:
        # 尝试使用默认路径
        default_cookies = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies', 'Cookies')
        if os.path.exists(default_cookies):
            cookies_file = default_cookies
            logger.info(f"使用默认 Cookies 文件: {cookies_file}")
        else:
            logger.warning("未找到 Cookies 文件，某些视频可能无法下载")
    
    # 创建配置对象
    config = DownloadConfig(
        url=args.url or '',
        start_time=args.start or config_data.get('start_time', ''),
        end_time=args.end or config_data.get('end_time', ''),
        output_dir=args.output_dir,
        proxy=args.proxy or config_data.get('proxy'),
        subtitle_langs=args.sub_langs,
        download_video=not args.no_video,
        download_audio=not args.no_audio,
        download_subtitles=not args.no_subtitles,
        burn_subtitles=not args.no_burn_subtitles,
        max_retries=args.max_retries,
        video_quality=args.video_quality,
        audio_quality=args.audio_quality,
        cookies_file=cookies_file
    )
    
    try:
        if args.batch:
            # 批量处理模式
            results = process_batch_urls(args.batch, config)
            success_count = sum(1 for r in results if r['success'])
            logger.info(f"批量处理完成: {success_count}/{len(results)} 个URL成功")
        else:
            # 单个URL模式
            logger.info(f"📺 URL: {config.url}")
            logger.info(f"⏰ 时间段: {config.start_time} - {config.end_time}")
            process_single_url(config)
            
    except KeyboardInterrupt:
        logger.info("用户中断下载")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

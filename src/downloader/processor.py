"""
下载处理器模块
"""

import os
import logging
import threading
from typing import Optional, List

from .config import DownloadConfig
from .utils import extract_video_id, setup_proxy
from .thread_manager import ThreadPoolManager, ThreadSafeProgress
from .video import download_segment
from .subtitle import burn_subtitles_to_video


def process_batch_urls(urls_file: str, config: DownloadConfig) -> List[dict]:
    """批量处理URL列表"""
    logger = logging.getLogger(__name__)
    results = []
    
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        logger.error(f"URL文件不存在: {urls_file}")
        return results
    
    logger.info(f"开始批量处理 {len(urls)} 个URL")
    
    # 创建线程安全的进度条
    progress = ThreadSafeProgress(total=len(urls), desc="处理URL", unit="个")
    success_count = 0
    
    def process_url(url: str) -> dict:
        """处理单个URL的包装函数"""
        nonlocal success_count
        progress.set_postfix_str(f"当前: {url[:50]}...")
        
        # 为每个URL创建独立配置
        url_config = DownloadConfig(
            url=url,
            start_time=config.start_time,
            end_time=config.end_time,
            output_dir=config.output_dir,
            proxy=config.proxy,
            subtitle_langs=config.subtitle_langs,
            download_video=config.download_video,
            download_audio=config.download_audio,
            download_subtitles=config.download_subtitles,
            burn_subtitles=config.burn_subtitles,
            max_retries=config.max_retries,
            video_quality=config.video_quality,
            audio_quality=config.audio_quality
        )
        
        result = process_single_url(url_config)
        success = result is not None
        
        with threading.Lock():
            if success:
                success_count += 1
            progress.set_postfix_str(f"成功: {success_count}/{len(urls)}")
            progress.update(1)
        
        return {
            'url': url,
            'success': success,
            'result': result
        }
    
    try:
        with ThreadPoolManager(max_workers=3) as pool:
            futures = [pool.executor.submit(process_url, url) for url in urls]
            results_dict = pool.wait_for_results(futures)
            results = list(results_dict.values())
    finally:
        progress.close()
    
    logger.info(f"批量处理完成: {success_count}/{len(urls)} 个URL成功")
    return results


def process_single_url(config: DownloadConfig) -> Optional[dict]:
    """处理单个URL，使用线程池并行下载各个组件"""
    logger = logging.getLogger(__name__)
    
    # 提取视频ID
    video_id = extract_video_id(config.url)
    if not video_id:
        logger.error(f"无法从URL提取视频ID: {config.url}")
        return None
    
    logger.info(f"🆔 视频ID: {video_id}")
    
    # 设置代理
    proxy = setup_proxy(config)
    if not proxy:
        logger.error("代理设置失败")
        return None
    
    # 创建输出目录
    os.makedirs(config.output_dir, exist_ok=True)
    
    # 第一阶段：并行下载视频和字幕（避免并行下载视频+音频导致 403 错误）
    download_tasks = {}
    if config.download_video:
        download_tasks['video'] = ('video', video_id, proxy)
    if config.download_subtitles:
        download_tasks['subtitles'] = ('subtitles', video_id, proxy)
    
    results = {}
    
    # 使用线程池并行下载视频和字幕
    if download_tasks:
        with ThreadPoolManager(max_workers=2) as pool:
            futures = {
                task_type: pool.executor.submit(download_segment, config, *task_args)
                for task_type, task_args in download_tasks.items()
            }
            results = pool.wait_for_results(futures)
    
    # 第二阶段：下载/提取音频（在视频下载完成后，可以从视频中提取音频）
    if config.download_audio:
        logger.info("开始处理音频...")
        audio_path = download_segment(config, 'audio', video_id, proxy)
        results['audio'] = audio_path
    
    # 输出结果
    video_dir = os.path.join(config.output_dir, video_id)
    logger.info(f"🎉 下载完成！文件保存在: {video_dir}/")
    
    for ctype, path in results.items():
        if path:
            logger.info(f"  ✅ {ctype.title()}: {os.path.basename(path)}")
        else:
            logger.warning(f"  ❌ {ctype.title()}: 下载失败")
    
    # 烧录字幕到视频
    if config.burn_subtitles and results.get('video') and results.get('subtitles'):
        video_path = results['video']
        subtitle_path = results['subtitles']
        
        # 生成带字幕的视频文件名
        video_basename = os.path.basename(video_path)
        video_name, video_ext = os.path.splitext(video_basename)
        output_with_subs = os.path.join(video_dir, f"{video_name}_with_subs{video_ext}")
        
        # 检查是否已经存在
        if os.path.exists(output_with_subs) and os.path.getsize(output_with_subs) > 0:
            logger.info(f"✅ 带字幕的视频已存在: {os.path.basename(output_with_subs)}")
            results['video_with_subtitles'] = output_with_subs
        else:
            # 执行字幕烧录
            burned_video = burn_subtitles_to_video(video_path, subtitle_path, output_with_subs)
            if burned_video:
                results['video_with_subtitles'] = burned_video
            else:
                logger.warning("字幕烧录失败，保留原始视频文件")
    
    return results


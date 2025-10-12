"""
字幕处理模块
"""

import os
import re
import glob
import shutil
import logging

from .config import DownloadConfig
from .utils import time_to_seconds, seconds_to_vtt_time, run_command


def adjust_subtitle_timestamps(subtitle_path, start_offset_seconds, end_offset_seconds):
    """调整字幕时间戳，使其与切割后的视频对齐
    
    Args:
        subtitle_path: 字幕文件路径
        start_offset_seconds: 起始时间偏移（秒）
        end_offset_seconds: 结束时间偏移（秒）
    
    Returns:
        调整后的字幕文件路径，失败返回None
    """
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(subtitle_path):
        logger.error(f"字幕文件不存在: {subtitle_path}")
        return None
    
    try:
        # 读取原始字幕文件
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        adjusted_lines = []
        skip_block = False
        in_header = True
        total_timestamps = 0
        kept_timestamps = 0
        
        for i, line in enumerate(lines):
            # 保留WEBVTT头部和元数据
            if in_header:
                if line.strip() == '' or line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                    adjusted_lines.append(line)
                    if line.strip() == '' and len(adjusted_lines) > 1:
                        in_header = False
                    continue
            
            # VTT时间戳格式: HH:MM:SS.mmm --> HH:MM:SS.mmm (可能带额外属性)
            time_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})(.*)'
            match = re.match(time_pattern, line)
            
            if match:
                total_timestamps += 1
                # 解析时间戳
                start_time_str = match.group(1)
                end_time_str = match.group(2)
                extra_attrs = match.group(3)  # 保留额外的属性，如 align:start position:0%
                
                # 转换为秒数
                start_parts = start_time_str.split(':')
                start_seconds = float(start_parts[0]) * 3600 + float(start_parts[1]) * 60 + float(start_parts[2])
                
                end_parts = end_time_str.split(':')
                end_seconds = float(end_parts[0]) * 3600 + float(end_parts[1]) * 60 + float(end_parts[2])
                
                # 检查字幕是否在指定时间范围内
                if end_seconds < start_offset_seconds or start_seconds > end_offset_seconds:
                    # 跳过不在范围内的字幕块
                    skip_block = True
                    continue
                
                kept_timestamps += 1
                if kept_timestamps == 1:
                    logger.debug(f"第一个保留的字幕在第 {i+1} 行: {start_time_str} --> {end_time_str}")
                
                # 调整时间戳（减去起始偏移量）
                adjusted_start = max(0, start_seconds - start_offset_seconds)
                adjusted_end = max(0, end_seconds - start_offset_seconds)
                
                # 转换回VTT格式，保留额外属性
                adjusted_line = f"{seconds_to_vtt_time(adjusted_start)} --> {seconds_to_vtt_time(adjusted_end)}{extra_attrs}"
                if not adjusted_line.endswith('\n'):
                    adjusted_line += '\n'
                adjusted_lines.append(adjusted_line)
                skip_block = False  # 找到有效时间戳，开始保留后续文本
            else:
                # 非时间戳行：只有在不跳过时才保留
                if not skip_block:
                    adjusted_lines.append(line)
        
        # 写回文件
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.writelines(adjusted_lines)
        
        logger.info(f"✅ 字幕时间戳已调整: {os.path.basename(subtitle_path)}")
        logger.info(f"   处理统计: 总时间戳 {total_timestamps} 个, 保留 {kept_timestamps} 个, 输出 {len(adjusted_lines)} 行")
        return subtitle_path
        
    except Exception as e:
        logger.error(f"调整字幕时间戳时出错: {e}")
        return None


def download_subtitles(config: DownloadConfig, video_dir: str, video_id: str, proxy: str):
    """下载字幕文件"""
    logger = logging.getLogger(__name__)
    logger.info("📖 开始下载字幕...")
    
    temp_dir = os.path.join(video_dir, "temp_subs")
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        cmd = [
            'yt-dlp',
            '--proxy', proxy,
            '--cookies-from-browser', 'chrome',
            '--write-auto-sub',
            '--sub-lang', config.subtitle_langs,
            '--skip-download',
            '-o', os.path.join(temp_dir, 'subs'),
            '--no-playlist',
            config.url
        ]
        
        success, output = run_command(cmd, max_retries=config.max_retries)
        if not success:
            logger.error(f"字幕下载失败: {output}")
            return None
            
        # 计算时间偏移量（秒）
        start_offset_seconds = time_to_seconds(config.start_time)
        end_offset_seconds = time_to_seconds(config.end_time)
            
        subtitle_files = []
        for lang in config.subtitle_langs.split(','):
            lang = lang.strip()
            pattern = os.path.join(temp_dir, f"subs.{lang}.vtt")
            matches = glob.glob(pattern)
            if matches:
                safe_start = config.start_time.replace(':', '_')
                safe_end = config.end_time.replace(':', '_')
                new_name = f"subtitles_{safe_start}-{safe_end}.{lang}.vtt"
                new_path = os.path.join(video_dir, new_name)
                shutil.move(matches[0], new_path)
                
                # 调整字幕时间戳，使其与切割后的视频对齐
                adjusted_path = adjust_subtitle_timestamps(new_path, start_offset_seconds, end_offset_seconds)
                if adjusted_path:
                    subtitle_files.append(adjusted_path)
                    logger.info(f"✅ {lang} 字幕下载并调整完成")
                else:
                    logger.warning(f"⚠️  {lang} 字幕时间戳调整失败，但文件已保存")
                    subtitle_files.append(new_path)
                
        if subtitle_files:
            logger.info(f"字幕下载完成: {', '.join(os.path.basename(f) for f in subtitle_files)}")
            return subtitle_files[0]
        else:
            logger.warning("未找到可用的字幕文件")
            return None
            
    except Exception as e:
        logger.error(f"字幕下载过程中出错: {e}")
        return None
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def burn_subtitles_to_video(video_path: str, subtitle_path: str, output_path: str):
    """将字幕烧录到视频上
    
    Args:
        video_path: 原始视频文件路径
        subtitle_path: 字幕文件路径
        output_path: 输出视频文件路径
    
    Returns:
        成功返回输出文件路径，失败返回None
    """
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(video_path):
        logger.error(f"视频文件不存在: {video_path}")
        return None
    
    if not os.path.exists(subtitle_path):
        logger.error(f"字幕文件不存在: {subtitle_path}")
        return None
    
    try:
        logger.info(f"🎬 开始烧录字幕到视频...")
        logger.info(f"  视频: {os.path.basename(video_path)}")
        logger.info(f"  字幕: {os.path.basename(subtitle_path)}")
        
        # 方法1: 尝试使用subtitles滤镜（需要libass支持）
        subtitle_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')
        
        ffmpeg_cmd_with_filter = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f"subtitles={subtitle_path_escaped}:force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=1,Shadow=1'",
            '-c:a', 'copy',
            '-preset', 'fast',
            output_path
        ]
        
        # 方法2: 使用overlay方式（备用方案）
        ffmpeg_cmd_with_overlay = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', subtitle_path,
            '-c:v', 'libx264',
            '-c:a', 'copy',
            '-c:s', 'mov_text',
            '-metadata:s:s:0', 'language=eng',
            '-disposition:s:0', 'default',
            '-preset', 'fast',
            output_path
        ]
        
        # 先尝试方法1
        success, output = run_command(ffmpeg_cmd_with_filter, max_retries=1)
        
        # 如果方法1失败（可能是因为缺少subtitles滤镜），尝试方法2
        if not success and 'No such filter' in output:
            logger.info("字幕滤镜不可用，尝试使用备用方案...")
            success, output = run_command(ffmpeg_cmd_with_overlay, max_retries=2)
        elif not success:
            # 如果方法1因其他原因失败，重试一次
            logger.info("重试字幕烧录...")
            success, output = run_command(ffmpeg_cmd_with_filter, max_retries=1)
        if not success:
            logger.error(f"字幕烧录失败: {output}")
            return None
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info(f"✅ 字幕烧录完成: {os.path.basename(output_path)}")
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"  文件大小: {file_size_mb:.2f} MB")
            return output_path
        else:
            logger.error("烧录后的视频文件无效")
            return None
            
    except Exception as e:
        logger.error(f"烧录字幕时出错: {e}")
        return None


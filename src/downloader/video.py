"""
视频/音频下载模块
"""

import os
import glob
import logging

from .config import DownloadConfig
from .utils import parse_time, check_disk_space, run_command, ensure_video_dir
from .subtitle import download_subtitles


def download_and_cut_segment(config: DownloadConfig, output_path: str, content_type: str, proxy: str):
    """下载并切割视频/音频片段"""
    logger = logging.getLogger(__name__)
    start_str = parse_time(config.start_time)
    end_str = parse_time(config.end_time)
    
    # 计算持续时间（秒）
    def time_to_seconds(time_str):
        parts = time_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + float(parts[1])
        else:  # SS
            return float(parts[0])
    
    duration = time_to_seconds(end_str) - time_to_seconds(start_str)
    duration_str = str(duration)
    
    temp_dir = os.path.dirname(output_path)
    temp_path = os.path.join(temp_dir, f"temp_{os.path.basename(output_path)}")
    
    try:
        # 检查磁盘空间
        if not check_disk_space(temp_dir):
            return None
            
        # 设置下载格式
        if content_type == 'video':
            format_opts = ['-f', config.video_quality]
        else:
            format_opts = ['-f', 'bestaudio/best']
            
        # 构建下载命令
        cmd = [
            'yt-dlp',
            '--proxy', proxy,
            '--cookies-from-browser', 'chrome',
            *format_opts,
            '-o', temp_path,
            '--no-playlist',
            config.url
        ]
        
        if content_type == 'audio':
            cmd.extend(['--extract-audio', '--audio-format', 'mp3', '--audio-quality', config.audio_quality])
            
        logger.info(f"开始下载 {content_type}...")
        success, output = run_command(cmd, max_retries=config.max_retries)
        if not success:
            logger.error(f"下载失败: {output}")
            return None
            
        # 检查下载的文件是否存在
        if not os.path.exists(temp_path):
            # 尝试查找实际下载的文件
            base_name = os.path.splitext(temp_path)[0]
            possible_files = glob.glob(f"{base_name}.*")
            if possible_files:
                temp_path = possible_files[0]
                logger.info(f"找到下载文件: {temp_path}")
            else:
                logger.error("下载的文件不存在")
                return None
        
        # 使用ffmpeg切割
        logger.info(f"开始切割 {content_type} 片段: {start_str} - {end_str} (时长: {duration:.2f}秒)")
        if content_type == 'video':
            # 使用两阶段切割策略实现精确切割：
            # 1. -ss 放在 -i 之前：快速定位到目标时间附近（可能不精确）
            # 2. 使用 -t 指定持续时间：确保切割的视频长度正确
            # 3. 使用重新编码：确保从精确的时间点开始，避免关键帧导致的画面静止问题
            # 注意：虽然重新编码较慢，但能确保视频从第一帧就是动态的
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-ss', start_str,    # 输入seek：快速定位到开始时间
                '-i', temp_path,
                '-t', duration_str,  # 指定输出视频的持续时间
                '-c:v', 'libx264',   # 重新编码以实现精确切割
                '-preset', 'fast',   # 使用快速预设平衡速度和质量
                '-crf', '23',        # 恒定质量模式（23是默认值，质量较好）
                '-c:a', 'aac',       # 音频也重新编码以保持同步
                '-b:a', '128k',      # 音频比特率
                output_path
            ]
        else:
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-ss', start_str,    # 定位到开始时间
                '-i', temp_path, 
                '-t', duration_str,  # 指定持续时间
                '-acodec', 'libmp3lame', '-ar', '44100', '-ab', config.audio_quality, 
                output_path
            ]
            
        success, output = run_command(ffmpeg_cmd, max_retries=2)
        if not success:
            logger.error(f"切割失败: {output}")
            return None
            
        logger.info(f"✅ {content_type} 处理完成: {os.path.basename(output_path)}")
        return output_path
        
    except Exception as e:
        logger.error(f"处理 {content_type} 时出错: {e}")
        return None
    finally:
        # 清理临时文件
        for pattern in [temp_path, f"{os.path.splitext(temp_path)[0]}.*"]:
            for file_path in glob.glob(pattern):
                if os.path.exists(file_path) and file_path != output_path:
                    try:
                        os.remove(file_path)
                        logger.debug(f"清理临时文件: {file_path}")
                    except Exception as e:
                        logger.warning(f"清理临时文件失败: {e}")


def download_segment(config: DownloadConfig, content_type: str, video_id: str, proxy: str):
    """下载指定类型的媒体片段"""
    logger = logging.getLogger(__name__)
    video_dir = ensure_video_dir(config.output_dir, video_id)
    
    safe_start = config.start_time.replace(':', '_')
    safe_end = config.end_time.replace(':', '_')
    
    if content_type == 'video':
        filename = f"segment_{safe_start}-{safe_end}.mp4"
        filepath = os.path.join(video_dir, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            logger.info(f"✅ 视频片段已存在，跳过下载: {filename}")
            return filepath
        logger.info("📥 开始下载并处理视频片段...")
        result = download_and_cut_segment(config, filepath, 'video', proxy)
        return result
        
    elif content_type == 'audio':
        filename = f"audio_{safe_start}-{safe_end}.mp3"
        filepath = os.path.join(video_dir, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            logger.info(f"✅ 音频片段已存在，跳过下载: {filename}")
            return filepath
        logger.info("🎵 开始下载并处理音频片段...")
        result = download_and_cut_segment(config, filepath, 'audio', proxy)
        return result
        
    elif content_type == 'subtitles':
        safe_start = config.start_time.replace(':', '_')
        safe_end = config.end_time.replace(':', '_')
        # 检查所有配置的语言的字幕是否都已存在
        all_subtitles_exist = True
        for lang in config.subtitle_langs.split(','):
            lang = lang.strip()
            filename = f"subtitles_{safe_start}-{safe_end}.{lang}.vtt"
            filepath = os.path.join(video_dir, filename)
            if not (os.path.exists(filepath) and os.path.getsize(filepath) > 0):
                all_subtitles_exist = False
                break
        
        if all_subtitles_exist:
            logger.info(f"✅ 所有字幕文件已存在，跳过下载")
            return os.path.join(video_dir, f"subtitles_{safe_start}-{safe_end}.{config.subtitle_langs.split(',')[0].strip()}.vtt")
        
        return download_subtitles(config, video_dir, video_id, proxy)
        
    else:
        logger.error(f"不支持的内容类型: {content_type}")
        return None


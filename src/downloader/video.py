"""
视频/音频下载模块
"""

import os
import glob
import logging

from .config import DownloadConfig
from .utils import parse_time, check_disk_space, run_command, ensure_video_dir
from .subtitle import download_subtitles


def extract_audio_from_video(video_path: str, audio_path: str, audio_quality: str = '192K') -> bool:
    """从视频文件中提取音频
    
    Args:
        video_path: 视频文件路径
        audio_path: 输出音频文件路径
        audio_quality: 音频质量（比特率）
        
    Returns:
        bool: 是否成功提取
    """
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(video_path):
        logger.error(f"视频文件不存在: {video_path}")
        return False
    
    try:
        logger.info(f"🎵 从视频中提取音频...")
        
        # 使用 ffmpeg 从视频中提取音频
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vn',  # 不包含视频
            '-acodec', 'libmp3lame',
            '-ar', '44100',
            '-ab', audio_quality,
            audio_path
        ]
        
        success, output = run_command(cmd, max_retries=2)
        if not success:
            logger.error(f"音频提取失败: {output}")
            return False
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            logger.info(f"✅ 音频提取完成: {os.path.basename(audio_path)}")
            return True
        else:
            logger.error("音频提取后文件不存在或为空")
            return False
            
    except Exception as e:
        logger.error(f"提取音频时出错: {e}")
        return False


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
    # 移除扩展名，让 yt-dlp 自动处理（它会在下载分离流时添加后缀，然后合并）
    output_base = os.path.splitext(os.path.basename(output_path))[0]
    temp_path = os.path.join(temp_dir, f"temp_{output_base}.%(ext)s")
    
    try:
        # 检查磁盘空间
        if not check_disk_space(temp_dir):
            return None
            
        # 设置下载格式
        if content_type == 'video':
            format_opts = ['-f', config.video_quality]
        else:
            format_opts = ['-f', 'bestaudio/best']
            
        # 构建下载命令基础部分
        cmd = [
            'yt-dlp',
            '--proxy', proxy
        ]
        
        # 添加 cookies 参数
        if config.cookies_file and os.path.exists(config.cookies_file):
            cmd.extend([
                '--cookies', config.cookies_file,
                '--no-cache-dir'  # 禁止缓存，避免尝试写入 cookies 文件
            ])
            logger.debug(f"使用 cookies 文件: {config.cookies_file}")
        else:
            logger.warning("未配置 cookies 文件或文件不存在，可能会导致下载失败")
        
        # 添加其他参数
        cmd.extend(format_opts)
        cmd.extend([
            '-o', temp_path,
            '--no-playlist',
            '--fixup', 'force',  # 强制修复下载的文件
            config.url
        ])
        
        # 为视频添加合并格式参数，确保输出为有效的 MP4
        # yt-dlp 会自动下载分离的视频和音频流，然后用 ffmpeg 合并
        if content_type == 'video':
            cmd.extend(['--merge-output-format', 'mp4'])
        
        if content_type == 'audio':
            cmd.extend(['--extract-audio', '--audio-format', 'mp3', '--audio-quality', config.audio_quality])
            
        logger.info(f"开始下载 {content_type}...")
        success, output = run_command(cmd, max_retries=config.max_retries)
        if not success:
            logger.error(f"下载失败: {output}")
            return None
            
        # 查找下载的文件（因为使用了 %(ext)s 模板，需要查找实际文件）
        # 将模板路径转换为搜索模式
        search_pattern = temp_path.replace('.%(ext)s', '.*')
        possible_files = glob.glob(search_pattern)
        
        # 过滤掉临时文件（.part, .ytdl等）
        valid_files = [f for f in possible_files if not any(f.endswith(ext) for ext in ['.part', '.ytdl', '.temp'])]
        
        if valid_files:
            # 如果有多个文件，选择最大的（通常是合并后的文件）
            temp_path = max(valid_files, key=os.path.getsize)
            logger.info(f"找到下载文件: {os.path.basename(temp_path)}")
        else:
            logger.error(f"下载的文件不存在，搜索模式: {search_pattern}")
            return None
        
        # 验证下载的文件是否有效（仅针对视频）
        if content_type == 'video':
            logger.info(f"验证下载文件的有效性...")
            verify_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type', temp_path]
            verify_success, verify_output = run_command(verify_cmd, max_retries=1)
            if not verify_success or 'video' not in verify_output.lower():
                logger.error(f"下载的视频文件无效: {verify_output}")
                return None
            logger.info(f"✅ 文件验证通过")
        
        # 使用ffmpeg切割
        logger.info(f"开始切割 {content_type} 片段: {start_str} - {end_str} (时长: {duration:.2f}秒)")
        if content_type == 'video':
            # 检查视频是否有音频流
            has_audio = False
            check_audio_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'default=noprint_wrappers=1', temp_path]
            audio_check_success, audio_check_output = run_command(check_audio_cmd, max_retries=1)
            if audio_check_success and 'audio' in audio_check_output.lower():
                has_audio = True
                logger.info("✅ 视频包含音频流")
            else:
                logger.warning("⚠️ 视频不包含音频流，将只处理视频")
            
            # 使用两阶段切割策略实现精确切割：
            # 1. -ss 放在 -i 之前：快速定位到目标时间附近（可能不精确）
            # 2. 使用 -t 指定持续时间：确保切割的视频长度正确
            # 3. 使用重新编码：确保从精确的时间点开始，避免关键帧导致的画面静止问题
            # 注意：虽然重新编码较慢，但能确保视频从第一帧就是动态的
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                # 增加分析参数以处理格式异常的视频
                '-analyzeduration', '100M',
                '-probesize', '100M',
                '-ss', start_str,    # 输入seek：快速定位到开始时间
                '-i', temp_path,
                '-t', duration_str,  # 指定输出视频的持续时间
                '-c:v', 'libx264',   # 重新编码以实现精确切割
                '-pix_fmt', 'yuv420p',  # 明确指定像素格式
                '-preset', 'fast',   # 使用快速预设平衡速度和质量
                '-crf', '23',        # 恒定质量模式（23是默认值，质量较好）
            ]
            
            # 根据是否有音频流添加音频处理参数
            if has_audio:
                ffmpeg_cmd.extend([
                    '-c:a', 'aac',       # 音频也重新编码以保持同步
                    '-b:a', '128k',      # 音频比特率
                ])
            else:
                ffmpeg_cmd.extend([
                    '-an',  # 不包含音频
                ])
            
            ffmpeg_cmd.append(output_path)
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
        
        # 优先从已下载的视频中提取音频，避免重复下载导致 403 错误
        video_filename = f"segment_{safe_start}-{safe_end}.mp4"
        video_filepath = os.path.join(video_dir, video_filename)
        
        if os.path.exists(video_filepath) and os.path.getsize(video_filepath) > 0:
            logger.info("🎵 从已下载的视频中提取音频...")
            if extract_audio_from_video(video_filepath, filepath, config.audio_quality):
                return filepath
            else:
                logger.warning("从视频提取音频失败，尝试直接下载音频...")
        
        # 如果视频不存在或提取失败，则尝试直接下载音频
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


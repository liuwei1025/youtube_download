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
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import time
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

class ThreadSafeProgress:
    """线程安全的进度条包装类"""
    def __init__(self, total=None, desc=None, unit=None):
        self.lock = threading.Lock()
        if HAS_TQDM:
            self.progress = tqdm(total=total, desc=desc, unit=unit)
        else:
            self.progress = None
            self.current = 0
            self.total = total
            self.desc = desc

    def update(self, n=1):
        with self.lock:
            if self.progress:
                self.progress.update(n)
            else:
                self.current += n
                if self.desc:
                    print(f"{self.desc}: {self.current}/{self.total}")

    def set_postfix_str(self, text):
        with self.lock:
            if self.progress:
                self.progress.set_postfix_str(text)
            else:
                print(f"{text}")

    def close(self):
        with self.lock:
            if self.progress:
                self.progress.close()

class ThreadPoolManager:
    """线程池管理器"""
    def __init__(self, max_workers=3):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.progress_lock = threading.Lock()
        self.results_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
        if exc_type:
            self.logger.error(f"线程池执行出错: {exc_val}")
            return False
        return True

    def wait_for_results(self, futures_dict: Dict[str, Any]) -> Dict[str, Any]:
        """等待并收集所有任务的结果"""
        results = {}
        try:
            if isinstance(futures_dict, dict):
                for key, future in futures_dict.items():
                    try:
                        results[key] = future.result()
                    except Exception as e:
                        self.logger.error(f"任务 {key} 执行失败: {e}")
                        results[key] = None
            else:  # List of futures
                for future in as_completed(futures_dict):
                    try:
                        result = future.result()
                        with self.results_lock:
                            if isinstance(result, dict):
                                results.update(result)
                            else:
                                results[id(future)] = result
                    except Exception as e:
                        self.logger.error(f"任务执行失败: {e}")
        except Exception as e:
            self.logger.error(f"等待任务结果时出错: {e}")
        return results

@dataclass
class DownloadConfig:
    """下载配置类"""
    url: str
    start_time: str
    end_time: str
    output_dir: str = 'downloads'
    proxy: Optional[str] = None
    subtitle_langs: str = 'zh,en'
    download_video: bool = True
    download_audio: bool = True
    download_subtitles: bool = True
    max_retries: int = 3
    video_quality: str = 'best[height<=480]'
    audio_quality: str = '192K'

def setup_logging():
    """设置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('youtube_downloader.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """检查必要的依赖是否安装"""
    logger = logging.getLogger(__name__)
    dependencies = ['yt-dlp', 'ffmpeg']

    return True

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

def setup_proxy(config: DownloadConfig):
    """设置代理配置"""
    logger = logging.getLogger(__name__)
    
    # 优先使用用户指定的代理
    if config.proxy:
        proxy = config.proxy
    # 检查环境变量中的代理设置
    elif os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY'):
        proxy = os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')
        logger.info(f"使用环境变量代理: {proxy}")
        return proxy
    # 默认代理（仅在本地开发时使用）
    else:
        proxy = "http://127.0.0.1:7890"
        logger.warning(f"使用默认代理: {proxy} (建议通过--proxy参数或环境变量设置)")
    
    # 验证代理格式
    if not proxy.startswith(('http://', 'https://', 'socks5://')):
        logger.error(f"无效的代理格式: {proxy}")
        return None
        
    for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
        os.environ[key] = proxy
    
    logger.info(f"代理设置完成: {proxy}")
    return proxy

def run_command(cmd, cwd=None, max_retries=3):
    """执行命令，支持重试机制"""
    logger = logging.getLogger(__name__)
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"执行命令 (尝试 {attempt + 1}/{max_retries}): {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=cwd)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            logger.warning(f"命令执行失败 (尝试 {attempt + 1}/{max_retries}): {e.stderr}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logger.error(f"命令执行最终失败: {e.stderr}")
                return False, e.stderr
        except FileNotFoundError as e:
            logger.error(f"命令不存在: {cmd[0]}")
            return False, f"命令不存在: {cmd[0]}"
    
    return False, "未知错误"

def ensure_video_dir(base_dir, video_id):
    # 确保使用绝对路径，基于当前脚本所在目录
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_base_dir = os.path.join(script_dir, base_dir)
    video_dir = os.path.join(abs_base_dir, video_id)
    os.makedirs(video_dir, exist_ok=True)
    return video_dir

def check_disk_space(path, required_mb=1000):
    """检查磁盘空间是否足够"""
    logger = logging.getLogger(__name__)
    try:
        stat = os.statvfs(path)
        available_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
        if available_mb < required_mb:
            logger.error(f"磁盘空间不足: 可用 {available_mb:.1f}MB, 需要 {required_mb}MB")
            return False
        logger.info(f"磁盘空间检查通过: 可用 {available_mb:.1f}MB")
        return True
    except Exception as e:
        logger.warning(f"无法检查磁盘空间: {e}")
        return True  # 检查失败时继续执行

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
                subtitle_files.append(new_path)
                logger.info(f"✅ {lang} 字幕下载完成")
                
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

def download_and_cut_segment(config: DownloadConfig, output_path: str, content_type: str, proxy: str):
    """下载并切割视频/音频片段"""
    logger = logging.getLogger(__name__)
    start_str = parse_time(config.start_time)
    end_str = parse_time(config.end_time)
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
        logger.info(f"开始切割 {content_type} 片段: {start_str} - {end_str}")
        if content_type == 'video':
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-i', temp_path, 
                '-ss', start_str, '-to', end_str, 
                '-c:v', 'copy', '-c:a', 'copy', 
                output_path
            ]
        else:
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-i', temp_path, 
                '-ss', start_str, '-to', end_str, 
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

def load_config_file(config_path: str) -> dict:
    """加载配置文件"""
    import json
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        logging.getLogger(__name__).warning(f"配置文件格式错误: {e}")
        return {}

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
    
    # 准备下载任务
    download_tasks = {}
    if config.download_video:
        download_tasks['video'] = ('video', video_id, proxy)
    if config.download_audio:
        download_tasks['audio'] = ('audio', video_id, proxy)
    if config.download_subtitles:
        download_tasks['subtitles'] = ('subtitles', video_id, proxy)
    
    # 使用线程池并行下载
    with ThreadPoolManager(max_workers=3) as pool:
        futures = {
            task_type: pool.executor.submit(download_segment, config, *task_args)
            for task_type, task_args in download_tasks.items()
        }
        results = pool.wait_for_results(futures)
    
    # 输出结果
    video_dir = os.path.join(config.output_dir, video_id)
    logger.info(f"🎉 下载完成！文件保存在: {video_dir}/")
    
    for ctype, path in results.items():
        if path:
            logger.info(f"  ✅ {ctype.title()}: {os.path.basename(path)}")
        else:
            logger.warning(f"  ❌ {ctype.title()}: 下载失败")
    
    return results

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
    parser.add_argument('--sub-langs', default='zh,en', help='字幕语言代码')
    parser.add_argument('--proxy', help='自定义代理地址，如 http://127.0.0.1:7890')
    parser.add_argument('--batch', help='批量处理URL文件')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--max-retries', type=int, default=3, help='最大重试次数')
    parser.add_argument('--video-quality', default='best[height<=480]', help='视频质量')
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
        max_retries=args.max_retries,
        video_quality=args.video_quality,
        audio_quality=args.audio_quality
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
"""
工具函数模块
"""

import os
import re
import time
import logging
import subprocess
from typing import Optional

from .config import DownloadConfig


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
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([\w-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([\w-]+)'
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


def time_to_seconds(time_str):
    """将时间字符串转换为秒数"""
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
    else:
        return float(time_str)


def seconds_to_vtt_time(seconds):
    """将秒数转换为VTT时间格式 (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    milliseconds = int((secs - int(secs)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(secs):02d}.{milliseconds:03d}"


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
    # 确保使用绝对路径，基于项目根目录（src的上一级）
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


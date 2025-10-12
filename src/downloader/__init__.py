"""
YouTube下载器模块
支持时间段裁剪、音频提取、字幕下载
"""

from .config import DownloadConfig, load_config_file
from .processor import process_single_url, process_batch_urls
from .utils import setup_logging

__all__ = [
    'DownloadConfig',
    'load_config_file',
    'process_single_url',
    'process_batch_urls',
    'setup_logging',
]


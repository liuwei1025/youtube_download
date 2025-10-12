"""
配置管理模块
"""

import logging
from dataclasses import dataclass
from typing import Optional


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
    burn_subtitles: bool = True
    max_retries: int = 3
    video_quality: str = 'best[height<=480]'
    audio_quality: str = '192K'


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


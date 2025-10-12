#!/usr/bin/env python3
"""
YouTube下载器模块使用示例
演示如何在Python代码中使用重构后的下载器模块
"""

import sys
import os

# 添加src目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

# 示例1: 使用主要的公共API
print("=" * 60)
print("示例1: 使用主要的公共API")
print("=" * 60)

from downloader import (
    DownloadConfig,
    process_single_url,
    setup_logging
)

# 设置日志
logger = setup_logging()

# 创建下载配置
config = DownloadConfig(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    start_time="0:10",
    end_time="0:30",
    output_dir="downloads",
    subtitle_langs="en,zh",
    download_video=True,
    download_audio=True,
    download_subtitles=True,
    burn_subtitles=True
)

print(f"配置创建成功: {config.url}")
print(f"时间段: {config.start_time} - {config.end_time}")

# 处理下载（这里只是演示，不实际执行）
# results = process_single_url(config)


# 示例2: 使用工具函数
print("\n" + "=" * 60)
print("示例2: 使用工具函数")
print("=" * 60)

from downloader.utils import (
    extract_video_id,
    parse_time,
    time_to_seconds
)

# 提取视频ID
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "www.youtube.com/watch?v=dQw4w9WgXcQ"
]

print("\n视频ID提取:")
for url in urls:
    video_id = extract_video_id(url)
    print(f"  {url} -> {video_id}")

# 时间格式转换
print("\n时间格式转换:")
times = ["1:30", "01:30:45", "90"]
for t in times:
    formatted = parse_time(t)
    seconds = time_to_seconds(t)
    print(f"  {t} -> {formatted} ({seconds}秒)")


# 示例3: 使用配置加载
print("\n" + "=" * 60)
print("示例3: 加载配置文件")
print("=" * 60)

from downloader import load_config_file

# 演示加载配置（文件可能不存在）
config_path = "config.json"
config_data = load_config_file(config_path)
if config_data:
    print(f"配置文件加载成功: {config_data}")
else:
    print(f"配置文件不存在或为空: {config_path}")


# 示例4: 批量处理URL
print("\n" + "=" * 60)
print("示例4: 批量处理URL (不实际执行)")
print("=" * 60)

from downloader import process_batch_urls

# 创建一个示例URL文件内容
urls_example = """
# YouTube视频下载列表
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0

# 注释行会被忽略
"""

print("批量处理URL列表的示例:")
print(urls_example)
print("使用方式:")
print("  results = process_batch_urls('urls.txt', config)")


# 示例5: 自定义下载配置
print("\n" + "=" * 60)
print("示例5: 自定义下载配置")
print("=" * 60)

# 只下载音频
audio_only_config = DownloadConfig(
    url="https://www.youtube.com/watch?v=example",
    start_time="0:00",
    end_time="1:00",
    download_video=False,
    download_audio=True,
    download_subtitles=False
)
print("音频专用配置:")
print(f"  下载视频: {audio_only_config.download_video}")
print(f"  下载音频: {audio_only_config.download_audio}")
print(f"  下载字幕: {audio_only_config.download_subtitles}")

# 高质量视频
hq_config = DownloadConfig(
    url="https://www.youtube.com/watch?v=example",
    start_time="0:00",
    end_time="1:00",
    video_quality="best[height<=1080]",
    audio_quality="320K"
)
print("\n高质量配置:")
print(f"  视频质量: {hq_config.video_quality}")
print(f"  音频质量: {hq_config.audio_quality}")


print("\n" + "=" * 60)
print("示例完成！")
print("=" * 60)


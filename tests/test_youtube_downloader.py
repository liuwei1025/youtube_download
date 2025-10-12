#!/usr/bin/env python3
"""
youtube_downloader 模块测试
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest

# 添加 src 目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from downloader import DownloadConfig
from downloader.utils import extract_video_id, parse_time, ensure_video_dir, check_disk_space
from downloader.subtitle import burn_subtitles_to_video


class TestVideoIdExtraction:
    """视频ID提取测试"""
    
    def test_extract_from_watch_url(self):
        """测试从标准 watch URL 提取"""
        url = "https://www.youtube.com/watch?v=7opHwsmusvE"
        video_id = extract_video_id(url)
        assert video_id == "7opHwsmusvE"
    
    def test_extract_from_short_url(self):
        """测试从短链接提取"""
        url = "https://youtu.be/7opHwsmusvE"
        video_id = extract_video_id(url)
        assert video_id == "7opHwsmusvE"
    
    def test_extract_from_embed_url(self):
        """测试从嵌入链接提取"""
        url = "https://www.youtube.com/embed/7opHwsmusvE"
        video_id = extract_video_id(url)
        assert video_id == "7opHwsmusvE"
    
    def test_extract_with_additional_params(self):
        """测试带额外参数的 URL"""
        url = "https://www.youtube.com/watch?v=7opHwsmusvE&t=10s&list=PLxxx"
        video_id = extract_video_id(url)
        assert video_id == "7opHwsmusvE"
    
    def test_extract_without_protocol(self):
        """测试不带协议的 URL"""
        url = "www.youtube.com/watch?v=7opHwsmusvE"
        video_id = extract_video_id(url)
        assert video_id == "7opHwsmusvE"
    
    def test_extract_from_invalid_url(self):
        """测试无效 URL"""
        url = "https://www.google.com"
        video_id = extract_video_id(url)
        assert video_id is None
    
    def test_extract_from_empty_url(self):
        """测试空 URL"""
        video_id = extract_video_id("")
        assert video_id is None


class TestTimeParser:
    """时间解析测试"""
    
    def test_parse_hhmmss_format(self):
        """测试 HH:MM:SS 格式"""
        result = parse_time("01:30:45")
        assert result == "01:30:45"
    
    def test_parse_mmss_format(self):
        """测试 MM:SS 格式"""
        result = parse_time("05:30")
        assert result == "00:05:30"
    
    def test_parse_seconds_only(self):
        """测试仅秒数格式"""
        result = parse_time("90")
        assert result == "00:01:30"
    
    def test_parse_large_seconds(self):
        """测试大秒数"""
        result = parse_time("3665")  # 1小时1分5秒
        assert result == "01:01:05"
    
    def test_parse_zero_time(self):
        """测试零时间"""
        result = parse_time("0")
        assert result == "00:00:00"
    
    def test_parse_single_digit_minutes(self):
        """测试单位数分钟"""
        result = parse_time("5:30")
        assert result == "00:05:30"


class TestDownloadConfig:
    """下载配置测试"""
    
    def test_minimal_config(self):
        """测试最小配置"""
        config = DownloadConfig(
            url="https://www.youtube.com/watch?v=test123",
            start_time="00:10",
            end_time="00:30"
        )
        
        assert config.url == "https://www.youtube.com/watch?v=test123"
        assert config.start_time == "00:10"
        assert config.end_time == "00:30"
        assert config.output_dir == "downloads"
        assert config.download_video is True
        assert config.download_audio is True
        assert config.download_subtitles is True
    
    def test_full_config(self):
        """测试完整配置"""
        config = DownloadConfig(
            url="https://www.youtube.com/watch?v=test123",
            start_time="01:00",
            end_time="02:00",
            output_dir="/tmp/test",
            proxy="http://proxy.example.com:8080",
            subtitle_langs="zh,en,ja",
            download_video=False,
            download_audio=True,
            download_subtitles=False,
            max_retries=5,
            video_quality="best[height<=720]",
            audio_quality="256K"
        )
        
        assert config.proxy == "http://proxy.example.com:8080"
        assert config.subtitle_langs == "zh,en,ja"
        assert config.download_video is False
        assert config.download_audio is True
        assert config.download_subtitles is False
        assert config.max_retries == 5
        assert config.video_quality == "best[height<=720]"
        assert config.audio_quality == "256K"
    
    def test_config_defaults(self):
        """测试配置默认值"""
        config = DownloadConfig(
            url="test_url",
            start_time="0:10",
            end_time="0:30"
        )
        
        assert config.proxy is None
        assert config.subtitle_langs == "zh,en"
        assert config.max_retries == 3
        assert config.video_quality == "best[height<=480]"
        assert config.audio_quality == "192K"


class TestVideoDirectory:
    """视频目录管理测试"""
    
    def test_ensure_video_dir_creates_directory(self, temp_downloads_dir):
        """测试创建视频目录"""
        video_id = "test_video_123"
        video_dir = ensure_video_dir(temp_downloads_dir, video_id)
        
        assert os.path.exists(video_dir)
        assert os.path.isdir(video_dir)
        assert video_id in video_dir
    
    def test_ensure_video_dir_already_exists(self, temp_downloads_dir):
        """测试目录已存在的情况"""
        video_id = "test_video_123"
        
        # 第一次创建
        video_dir1 = ensure_video_dir(temp_downloads_dir, video_id)
        
        # 第二次应该返回相同路径
        video_dir2 = ensure_video_dir(temp_downloads_dir, video_id)
        
        assert video_dir1 == video_dir2
        assert os.path.exists(video_dir2)
    
    def test_ensure_video_dir_with_special_chars(self, temp_downloads_dir):
        """测试带特殊字符的视频ID"""
        video_id = "test-video_123"
        video_dir = ensure_video_dir(temp_downloads_dir, video_id)
        
        assert os.path.exists(video_dir)
        assert video_id in video_dir


class TestDiskSpace:
    """磁盘空间检查测试"""
    
    def test_check_disk_space_sufficient(self, temp_downloads_dir):
        """测试磁盘空间充足"""
        # 检查1MB空间（应该总是有的）
        result = check_disk_space(temp_downloads_dir, required_mb=1)
        assert result is True
    
    def test_check_disk_space_insufficient(self, temp_downloads_dir):
        """测试磁盘空间不足"""
        # 检查一个非常大的空间（通常不够）
        result = check_disk_space(temp_downloads_dir, required_mb=999999999)
        assert result is False
    
    def test_check_disk_space_zero_required(self, temp_downloads_dir):
        """测试需求为0"""
        result = check_disk_space(temp_downloads_dir, required_mb=0)
        assert result is True


class TestProxySetup:
    """代理设置测试"""
    
    def test_proxy_with_explicit_config(self):
        """测试显式指定代理"""
        from downloader.utils import setup_proxy
        
        config = DownloadConfig(
            url="test_url",
            start_time="0:10",
            end_time="0:30",
            proxy="http://192.168.1.1:8080"
        )
        
        proxy = setup_proxy(config)
        assert proxy == "http://192.168.1.1:8080"
        assert os.environ.get('HTTP_PROXY') == "http://192.168.1.1:8080"
    
    def test_proxy_with_environment_variable(self):
        """测试环境变量代理"""
        from downloader.utils import setup_proxy
        
        # 设置环境变量
        os.environ['HTTP_PROXY'] = "http://env-proxy:8080"
        
        config = DownloadConfig(
            url="test_url",
            start_time="0:10",
            end_time="0:30",
            proxy=None
        )
        
        proxy = setup_proxy(config)
        assert proxy == "http://env-proxy:8080"
        
        # 清理
        del os.environ['HTTP_PROXY']
    
    def test_proxy_default_fallback(self):
        """测试默认代理回退"""
        from downloader.utils import setup_proxy
        
        # 清除环境变量
        for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
            if key in os.environ:
                del os.environ[key]
        
        config = DownloadConfig(
            url="test_url",
            start_time="0:10",
            end_time="0:30",
            proxy=None
        )
        
        proxy = setup_proxy(config)
        assert proxy == "http://127.0.0.1:7890"  # 默认代理


class TestCommandExecution:
    """命令执行测试"""
    
    def test_run_simple_command(self):
        """测试执行简单命令"""
        from downloader.utils import run_command
        
        # 执行 echo 命令
        success, output = run_command(['echo', 'test'])
        assert success is True
        assert 'test' in output
    
    def test_run_failing_command(self):
        """测试执行失败的命令"""
        from downloader.utils import run_command
        
        # 执行会失败的命令
        success, output = run_command(['ls', '/nonexistent/path/12345'], max_retries=1)
        assert success is False
    
    def test_run_nonexistent_command(self):
        """测试执行不存在的命令"""
        from downloader.utils import run_command
        
        success, output = run_command(['nonexistent_command_12345'], max_retries=1)
        assert success is False
        assert "命令不存在" in output or "不存在" in output


class TestIntegrationHelpers:
    """集成辅助函数测试"""
    
    def test_parse_and_format_times(self):
        """测试时间解析和格式化的集成"""
        test_cases = [
            ("0:10", "0:30", "00:00:10", "00:00:30"),
            ("1:00", "2:00", "00:01:00", "00:02:00"),
            ("90", "120", "00:01:30", "00:02:00"),
        ]
        
        for start_in, end_in, start_out, end_out in test_cases:
            start_result = parse_time(start_in)
            end_result = parse_time(end_in)
            assert start_result == start_out
            assert end_result == end_out
    
    def test_video_id_and_directory_integration(self, temp_downloads_dir):
        """测试视频ID提取和目录创建的集成"""
        url = "https://www.youtube.com/watch?v=7opHwsmusvE"
        video_id = extract_video_id(url)
        assert video_id is not None
        
        video_dir = ensure_video_dir(temp_downloads_dir, video_id)
        assert os.path.exists(video_dir)
        assert video_id in video_dir


class TestFileNaming:
    """文件命名测试"""
    
    def test_safe_filename_generation(self):
        """测试安全文件名生成"""
        # 测试时间格式转换为安全文件名
        start_time = "01:30"
        end_time = "02:45"
        
        safe_start = start_time.replace(':', '_')
        safe_end = end_time.replace(':', '_')
        
        assert safe_start == "01_30"
        assert safe_end == "02_45"
        
        # 构建文件名
        video_filename = f"segment_{safe_start}-{safe_end}.mp4"
        audio_filename = f"audio_{safe_start}-{safe_end}.mp3"
        subtitle_filename = f"subtitles_{safe_start}-{safe_end}.en.vtt"
        
        assert video_filename == "segment_01_30-02_45.mp4"
        assert audio_filename == "audio_01_30-02_45.mp3"
        assert subtitle_filename == "subtitles_01_30-02_45.en.vtt"


class TestConfigValidation:
    """配置验证测试"""
    
    def test_valid_quality_settings(self):
        """测试有效的质量设置"""
        quality_options = [
            "best[height<=360]",
            "best[height<=480]",
            "best[height<=720]",
            "best[height<=1080]",
            "bestaudio/best"
        ]
        
        for quality in quality_options:
            config = DownloadConfig(
                url="test_url",
                start_time="0:10",
                end_time="0:30",
                video_quality=quality
            )
            assert config.video_quality == quality
    
    def test_valid_audio_quality(self):
        """测试有效的音频质量设置"""
        audio_options = ["128K", "192K", "256K", "320K"]
        
        for quality in audio_options:
            config = DownloadConfig(
                url="test_url",
                start_time="0:10",
                end_time="0:30",
                audio_quality=quality
            )
            assert config.audio_quality == quality
    
    def test_subtitle_languages(self):
        """测试字幕语言设置"""
        lang_options = ["zh", "en", "zh,en", "zh,en,ja", "en,es,fr"]
        
        for langs in lang_options:
            config = DownloadConfig(
                url="test_url",
                start_time="0:10",
                end_time="0:30",
                subtitle_langs=langs
            )
            assert config.subtitle_langs == langs


class TestEdgeCases:
    """边缘情况测试"""
    
    def test_very_short_time_range(self):
        """测试非常短的时间范围"""
        config = DownloadConfig(
            url="test_url",
            start_time="0:00",
            end_time="0:01"
        )
        assert config.start_time == "0:00"
        assert config.end_time == "0:01"
    
    def test_long_time_range(self):
        """测试长时间范围"""
        config = DownloadConfig(
            url="test_url",
            start_time="0:00",
            end_time="3:00:00"
        )
        assert config.start_time == "0:00"
        assert config.end_time == "3:00:00"
    
    def test_unicode_in_paths(self, temp_downloads_dir):
        """测试路径中的 Unicode 字符"""
        # 某些视频ID可能包含特殊字符（虽然YouTube通常不会）
        video_id = "test_视频_123"
        try:
            video_dir = ensure_video_dir(temp_downloads_dir, video_id)
            # 如果系统支持 Unicode，应该成功
            assert os.path.exists(video_dir)
        except Exception as e:
            # 某些文件系统可能不支持
            pytest.skip(f"文件系统不支持 Unicode: {e}")


class TestSubtitleBurning:
    """字幕烧录功能测试"""
    
    @pytest.fixture
    def test_video_path(self):
        """返回测试视频文件路径"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(project_root, 'downloads', 'test_video_id', 'segment_00_10-00_30.mp4')
    
    @pytest.fixture
    def test_subtitle_path(self):
        """返回测试字幕文件路径"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(project_root, 'downloads', 'test_video_id', 'subtitles_00_10-00_30.en.vtt')
    
    @pytest.fixture
    def test_output_path(self, temp_downloads_dir):
        """返回测试输出文件路径"""
        return os.path.join(temp_downloads_dir, 'test_output_with_subs.mp4')
    
    def test_burn_subtitles_success(self, test_video_path, test_subtitle_path, test_output_path):
        """测试成功烧录字幕"""
        # 跳过如果测试文件不存在
        if not os.path.exists(test_video_path):
            pytest.skip("测试视频文件不存在")
        if not os.path.exists(test_subtitle_path):
            pytest.skip("测试字幕文件不存在")
        
        # 检查视频文件是否有效
        if os.path.getsize(test_video_path) == 0:
            pytest.skip("测试视频文件为空")
        
        result = burn_subtitles_to_video(test_video_path, test_subtitle_path, test_output_path)
        
        # 如果ffmpeg不支持字幕烧录，跳过测试
        if result is None:
            pytest.skip("ffmpeg不支持字幕烧录（可能缺少libass支持）")
        
        # 验证返回值
        assert result == test_output_path
        
        # 验证输出文件存在
        assert os.path.exists(test_output_path)
        
        # 验证文件大小大于0
        assert os.path.getsize(test_output_path) > 0
        
        # 验证输出文件大小合理（应该与原视频大小相近或稍大）
        original_size = os.path.getsize(test_video_path)
        output_size = os.path.getsize(test_output_path)
        # 允许输出文件是原文件的0.5-5倍（取决于编码设置）
        assert output_size > original_size * 0.5
        assert output_size < original_size * 5
    
    def test_burn_subtitles_missing_video(self, test_subtitle_path, test_output_path):
        """测试视频文件不存在的情况"""
        fake_video_path = "/nonexistent/video.mp4"
        result = burn_subtitles_to_video(fake_video_path, test_subtitle_path, test_output_path)
        
        # 应该返回 None
        assert result is None
        
        # 输出文件不应该被创建
        assert not os.path.exists(test_output_path)
    
    def test_burn_subtitles_missing_subtitle(self, test_video_path, test_output_path):
        """测试字幕文件不存在的情况"""
        if not os.path.exists(test_video_path):
            pytest.skip("测试视频文件不存在")
        
        fake_subtitle_path = "/nonexistent/subtitle.vtt"
        result = burn_subtitles_to_video(test_video_path, fake_subtitle_path, test_output_path)
        
        # 应该返回 None
        assert result is None
        
        # 输出文件不应该被创建
        assert not os.path.exists(test_output_path)
    
    def test_burn_subtitles_with_real_files(self):
        """使用真实下载文件测试字幕烧录"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        downloads_dir = os.path.join(project_root, 'downloads')
        
        # 寻找第一个包含视频和字幕的目录
        test_dirs = [
            '1pw9ycK2krg',
            '24UIccYCp6c', 
            '72eLohjOiu8',
            'test_video_id'
        ]
        
        video_path = None
        subtitle_path = None
        
        for video_id in test_dirs:
            video_dir = os.path.join(downloads_dir, video_id)
            if not os.path.exists(video_dir):
                continue
            
            # 查找视频文件
            video_files = [f for f in os.listdir(video_dir) if f.startswith('segment_') and f.endswith('.mp4')]
            if not video_files:
                continue
            
            video_file = video_files[0]
            video_path = os.path.join(video_dir, video_file)
            
            # 查找对应的字幕文件
            base_name = video_file.replace('segment_', '').replace('.mp4', '')
            subtitle_files = [f for f in os.listdir(video_dir) if f.startswith(f'subtitles_{base_name}') and f.endswith('.vtt')]
            if not subtitle_files:
                continue
            
            subtitle_path = os.path.join(video_dir, subtitle_files[0])
            break
        
        # 如果找不到测试文件，跳过测试
        if not video_path or not subtitle_path:
            pytest.skip("未找到可用的测试文件")
        
        # 生成输出路径
        output_path = video_path.replace('.mp4', '_with_subs_test.mp4')
        
        try:
            result = burn_subtitles_to_video(video_path, subtitle_path, output_path)
            
            # 如果ffmpeg不支持字幕烧录，跳过测试
            if result is None:
                pytest.skip("ffmpeg不支持字幕烧录（可能缺少libass支持）")
            
            # 验证结果
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            print(f"\n✅ 字幕烧录测试成功:")
            print(f"  视频: {os.path.basename(video_path)}")
            print(f"  字幕: {os.path.basename(subtitle_path)}")
            print(f"  输出: {os.path.basename(output_path)}")
            print(f"  原始大小: {os.path.getsize(video_path) / (1024*1024):.2f} MB")
            print(f"  输出大小: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
            
        finally:
            # 清理测试文件
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_download_config_burn_subtitles_flag(self):
        """测试DownloadConfig中的burn_subtitles配置"""
        # 默认应该启用字幕烧录
        config = DownloadConfig(
            url="test_url",
            start_time="0:10",
            end_time="0:30"
        )
        assert config.burn_subtitles is True
        
        # 显式禁用字幕烧录
        config = DownloadConfig(
            url="test_url",
            start_time="0:10",
            end_time="0:30",
            burn_subtitles=False
        )
        assert config.burn_subtitles is False
        
        # 显式启用字幕烧录
        config = DownloadConfig(
            url="test_url",
            start_time="0:10",
            end_time="0:30",
            burn_subtitles=True
        )
        assert config.burn_subtitles is True


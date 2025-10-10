#!/usr/bin/env python3
"""
pytest 配置和共享 fixtures
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))


@pytest.fixture
def test_client():
    """FastAPI 测试客户端"""
    # 导入 app 时需要先 mock 一些依赖
    with patch('app.check_dependencies', return_value=True):
        from app import app
        client = TestClient(app)
        yield client


@pytest.fixture
def temp_downloads_dir():
    """临时下载目录"""
    temp_dir = tempfile.mkdtemp(prefix="youtube_test_")
    yield temp_dir
    # 清理
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_youtube_downloader():
    """Mock youtube_downloader 模块的主要函数"""
    with patch('app.process_single_url') as mock_process, \
         patch('app.extract_video_id') as mock_extract:
        
        # 模拟 extract_video_id 返回测试 ID
        mock_extract.return_value = 'test_video_id'
        
        # 模拟 process_single_url 返回成功结果
        def mock_download(config):
            """模拟下载函数"""
            video_id = 'test_video_id'
            video_dir = os.path.join(config.output_dir, video_id)
            os.makedirs(video_dir, exist_ok=True)
            
            results = {}
            if config.download_video:
                video_path = os.path.join(video_dir, 'segment_00_10-00_30.mp4')
                Path(video_path).touch()
                results['video'] = video_path
            
            if config.download_audio:
                audio_path = os.path.join(video_dir, 'audio_00_10-00_30.mp3')
                Path(audio_path).touch()
                results['audio'] = audio_path
            
            if config.download_subtitles:
                subtitle_path = os.path.join(video_dir, 'subtitles_00_10-00_30.en.vtt')
                Path(subtitle_path).touch()
                results['subtitles'] = subtitle_path
            
            return results
        
        mock_process.side_effect = mock_download
        
        yield {
            'process_single_url': mock_process,
            'extract_video_id': mock_extract
        }


@pytest.fixture
def real_youtube_url():
    """真实的 YouTube 测试 URL"""
    return "https://www.youtube.com/watch?v=7opHwsmusvE"


@pytest.fixture
def test_video_params():
    """测试视频参数"""
    return {
        "url": "https://www.youtube.com/watch?v=7opHwsmusvE",
        "start_time": "00:10",
        "end_time": "00:30",
        "download_video": True,
        "download_audio": True,
        "download_subtitles": False,  # 集成测试时可以设为 False 加快速度
        "video_quality": "best[height<=360]",
        "audio_quality": "192K",
        "max_retries": 2
    }


@pytest.fixture(autouse=True)
def reset_tasks_db():
    """每个测试前重置任务数据库"""
    import app
    app.tasks_db.clear()
    yield
    app.tasks_db.clear()


@pytest.fixture
def sample_task_data():
    """示例任务数据"""
    return {
        'task_id': 'test-task-123',
        'status': 'completed',
        'url': 'https://www.youtube.com/watch?v=test123',
        'video_id': 'test123',
        'created_at': '2024-01-01T00:00:00',
        'completed_at': '2024-01-01T00:05:00',
        'files': {
            'video': 'segment_00_10-00_30.mp4',
            'audio': 'audio_00_10-00_30.mp3',
            'subtitles': 'subtitles_00_10-00_30.en.vtt'
        }
    }


@pytest.fixture
def skip_integration():
    """跳过集成测试的标记"""
    skip_integration = os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true'
    if skip_integration:
        pytest.skip("跳过集成测试（SKIP_INTEGRATION_TESTS=true）")


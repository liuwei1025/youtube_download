#!/usr/bin/env python3
"""
API 单元测试 - 使用 Mock 模拟外部依赖
"""

import os
import time
from pathlib import Path
from unittest.mock import patch, Mock
import pytest


class TestRootEndpoints:
    """根端点测试"""
    
    def test_root_endpoint(self, test_client):
        """测试根路径"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "YouTube下载器 API"
        assert data["version"] == "2.0.0"
        assert data["status"] == "running"
        assert "endpoints" in data
    
    def test_health_check(self, test_client):
        """测试健康检查"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "tasks_count" in data
        assert "downloads_dir" in data


class TestTaskCreation:
    """任务创建测试"""
    
    def test_create_download_task(self, test_client, mock_youtube_downloader, temp_downloads_dir):
        """测试创建下载任务"""
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            payload = {
                "url": "https://www.youtube.com/watch?v=test123",
                "start_time": "00:10",
                "end_time": "00:30",
                "download_video": True,
                "download_audio": True,
                "download_subtitles": False
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "pending"
            assert data["message"] == "任务已创建，正在处理中"
            assert "created_at" in data
    
    def test_create_task_with_all_options(self, test_client, mock_youtube_downloader, temp_downloads_dir):
        """测试使用所有选项创建任务"""
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            payload = {
                "url": "https://www.youtube.com/watch?v=test123",
                "start_time": "01:00",
                "end_time": "02:00",
                "proxy": "http://127.0.0.1:7890",
                "subtitle_langs": "zh,en,ja",
                "download_video": True,
                "download_audio": True,
                "download_subtitles": True,
                "video_quality": "best[height<=720]",
                "audio_quality": "256K",
                "max_retries": 5
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending"
    
    def test_create_task_video_only(self, test_client, mock_youtube_downloader, temp_downloads_dir):
        """测试仅下载视频"""
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            payload = {
                "url": "https://www.youtube.com/watch?v=test123",
                "start_time": "00:10",
                "end_time": "00:30",
                "download_video": True,
                "download_audio": False,
                "download_subtitles": False
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200
    
    def test_create_task_audio_only(self, test_client, mock_youtube_downloader, temp_downloads_dir):
        """测试仅下载音频"""
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            payload = {
                "url": "https://www.youtube.com/watch?v=test123",
                "start_time": "00:10",
                "end_time": "00:30",
                "download_video": False,
                "download_audio": True,
                "download_subtitles": False
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200


class TestTaskManagement:
    """任务管理测试"""
    
    def test_get_task_status(self, test_client, sample_task_data):
        """测试获取任务状态"""
        import app
        task_id = sample_task_data['task_id']
        app.tasks_db[task_id] = sample_task_data
        
        response = test_client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] == "completed"
        assert data["url"] == sample_task_data["url"]
    
    def test_get_nonexistent_task(self, test_client):
        """测试获取不存在的任务"""
        response = test_client.get("/tasks/nonexistent-task-id")
        assert response.status_code == 404
        assert "任务不存在" in response.json()["detail"]
    
    def test_list_all_tasks(self, test_client, sample_task_data):
        """测试获取任务列表"""
        import app
        # 添加多个任务
        for i in range(3):
            task_id = f"test-task-{i}"
            task_data = sample_task_data.copy()
            task_data['task_id'] = task_id
            task_data['created_at'] = f"2024-01-01T00:0{i}:00"
            app.tasks_db[task_id] = task_data
        
        response = test_client.get("/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert isinstance(data, list)
    
    def test_list_tasks_with_status_filter(self, test_client, sample_task_data):
        """测试按状态过滤任务"""
        import app
        # 添加不同状态的任务
        statuses = ['pending', 'processing', 'completed', 'failed']
        for i, status in enumerate(statuses):
            task_id = f"test-task-{i}"
            task_data = sample_task_data.copy()
            task_data['task_id'] = task_id
            task_data['status'] = status
            app.tasks_db[task_id] = task_data
        
        # 过滤已完成的任务
        response = test_client.get("/tasks?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"
    
    def test_list_tasks_with_limit(self, test_client, sample_task_data):
        """测试任务列表数量限制"""
        import app
        # 添加多个任务
        for i in range(10):
            task_id = f"test-task-{i}"
            task_data = sample_task_data.copy()
            task_data['task_id'] = task_id
            app.tasks_db[task_id] = task_data
        
        # 限制返回5个
        response = test_client.get("/tasks?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
    
    def test_delete_task(self, test_client, sample_task_data, temp_downloads_dir):
        """测试删除任务"""
        import app
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            task_id = sample_task_data['task_id']
            video_id = sample_task_data['video_id']
            
            # 创建测试文件
            video_dir = os.path.join(temp_downloads_dir, video_id)
            os.makedirs(video_dir, exist_ok=True)
            test_file = os.path.join(video_dir, 'test.mp4')
            Path(test_file).touch()
            
            # 添加任务到数据库
            app.tasks_db[task_id] = sample_task_data
            
            # 删除任务
            response = test_client.delete(f"/tasks/{task_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["task_id"] == task_id
            assert "已删除" in data["message"]
            
            # 验证任务已从数据库删除
            assert task_id not in app.tasks_db
            
            # 验证文件已删除
            assert not os.path.exists(video_dir)
    
    def test_delete_nonexistent_task(self, test_client):
        """测试删除不存在的任务"""
        response = test_client.delete("/tasks/nonexistent-task-id")
        assert response.status_code == 404


class TestFileDownload:
    """文件下载测试"""
    
    def test_download_video_file(self, test_client, sample_task_data, temp_downloads_dir):
        """测试下载视频文件"""
        import app
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            task_id = sample_task_data['task_id']
            video_id = sample_task_data['video_id']
            
            # 创建测试视频文件
            video_dir = os.path.join(temp_downloads_dir, video_id)
            os.makedirs(video_dir, exist_ok=True)
            video_file = os.path.join(video_dir, sample_task_data['files']['video'])
            with open(video_file, 'wb') as f:
                f.write(b'test video content')
            
            # 添加任务到数据库
            app.tasks_db[task_id] = sample_task_data
            
            # 下载文件
            response = test_client.get(f"/tasks/{task_id}/files/video")
            assert response.status_code == 200
            assert response.headers['content-type'] == 'application/octet-stream'
            assert len(response.content) > 0
    
    def test_download_audio_file(self, test_client, sample_task_data, temp_downloads_dir):
        """测试下载音频文件"""
        import app
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            task_id = sample_task_data['task_id']
            video_id = sample_task_data['video_id']
            
            # 创建测试音频文件
            video_dir = os.path.join(temp_downloads_dir, video_id)
            os.makedirs(video_dir, exist_ok=True)
            audio_file = os.path.join(video_dir, sample_task_data['files']['audio'])
            with open(audio_file, 'wb') as f:
                f.write(b'test audio content')
            
            app.tasks_db[task_id] = sample_task_data
            
            response = test_client.get(f"/tasks/{task_id}/files/audio")
            assert response.status_code == 200
    
    def test_download_file_task_not_completed(self, test_client, sample_task_data):
        """测试下载未完成任务的文件"""
        import app
        
        task_id = sample_task_data['task_id']
        sample_task_data['status'] = 'processing'
        app.tasks_db[task_id] = sample_task_data
        
        response = test_client.get(f"/tasks/{task_id}/files/video")
        assert response.status_code == 400
        assert "未完成" in response.json()["detail"]
    
    def test_download_nonexistent_file_type(self, test_client, sample_task_data, temp_downloads_dir):
        """测试下载不存在的文件类型"""
        import app
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            task_id = sample_task_data['task_id']
            sample_task_data['files'] = {'video': 'test.mp4'}  # 只有视频
            app.tasks_db[task_id] = sample_task_data
            
            response = test_client.get(f"/tasks/{task_id}/files/subtitles")
            assert response.status_code == 404


class TestCleanup:
    """清理功能测试"""
    
    def test_cleanup_endpoint(self, test_client, sample_task_data, temp_downloads_dir):
        """测试清理旧任务"""
        import app
        from datetime import datetime, timedelta
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            # 添加一个旧任务（25小时前）
            old_task_id = 'old-task'
            old_time = (datetime.now() - timedelta(hours=25)).isoformat()
            old_task = sample_task_data.copy()
            old_task['task_id'] = old_task_id
            old_task['created_at'] = old_time
            old_task['video_id'] = 'old_video'
            
            # 创建旧任务的文件
            old_video_dir = os.path.join(temp_downloads_dir, 'old_video')
            os.makedirs(old_video_dir, exist_ok=True)
            Path(os.path.join(old_video_dir, 'test.mp4')).touch()
            
            app.tasks_db[old_task_id] = old_task
            
            # 添加一个新任务（1小时前）
            new_task_id = 'new-task'
            new_time = (datetime.now() - timedelta(hours=1)).isoformat()
            new_task = sample_task_data.copy()
            new_task['task_id'] = new_task_id
            new_task['created_at'] = new_time
            app.tasks_db[new_task_id] = new_task
            
            # 执行清理
            response = test_client.post("/cleanup?max_age_hours=24")
            assert response.status_code == 200
            
            data = response.json()
            assert "已清理" in data["message"]
            
            # 验证旧任务被删除
            assert old_task_id not in app.tasks_db
            
            # 验证新任务保留
            assert new_task_id in app.tasks_db
            
            # 验证旧文件被删除
            assert not os.path.exists(old_video_dir)


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_task_id_format(self, test_client):
        """测试无效的任务ID格式"""
        # FastAPI 会自动重定向 /tasks/ 到 /tasks，所以这个测试实际上会返回任务列表
        # 改为测试一个明确不存在的任务ID
        response = test_client.get("/tasks/invalid-format-123")
        assert response.status_code == 404
    
    def test_missing_required_fields(self, test_client):
        """测试缺少必需字段"""
        # 缺少 URL
        payload = {
            "start_time": "00:10",
            "end_time": "00:30"
        }
        response = test_client.post("/download", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_time_format(self, test_client, mock_youtube_downloader):
        """测试无效的时间格式 - 注意：API层不验证格式，由下载器处理"""
        payload = {
            "url": "https://www.youtube.com/watch?v=test123",
            "start_time": "invalid",
            "end_time": "invalid"
        }
        # API 会接受请求，但下载时会失败
        response = test_client.post("/download", json=payload)
        # API 层面会成功创建任务
        assert response.status_code == 200


class TestConcurrency:
    """并发测试"""
    
    def test_multiple_concurrent_tasks(self, test_client, mock_youtube_downloader, temp_downloads_dir):
        """测试创建多个并发任务"""
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            task_ids = []
            
            # 创建5个任务
            for i in range(5):
                payload = {
                    "url": f"https://www.youtube.com/watch?v=test{i}",
                    "start_time": "00:10",
                    "end_time": "00:30"
                }
                response = test_client.post("/download", json=payload)
                assert response.status_code == 200
                task_ids.append(response.json()["task_id"])
            
            # 验证所有任务都已创建
            assert len(task_ids) == 5
            assert len(set(task_ids)) == 5  # 所有ID都是唯一的
            
            # 等待后台任务完成
            time.sleep(2)
            
            # 检查任务列表
            response = test_client.get("/tasks")
            assert response.status_code == 200
            tasks = response.json()
            assert len(tasks) == 5


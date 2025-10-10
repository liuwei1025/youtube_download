#!/usr/bin/env python3
"""
API 集成测试 - 使用真实 YouTube URL
"""

import os
import time
import pytest
from pathlib import Path


class TestRealDownload:
    """真实下载测试"""
    
    @pytest.mark.skipif(
        os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true',
        reason="跳过集成测试"
    )
    def test_full_download_workflow(self, test_client, real_youtube_url, temp_downloads_dir):
        """测试完整的下载工作流程"""
        from unittest.mock import patch
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            # 1. 创建下载任务
            payload = {
                "url": real_youtube_url,
                "start_time": "00:10",
                "end_time": "00:30",
                "download_video": True,
                "download_audio": True,
                "download_subtitles": False,  # 跳过字幕加快测试
                "video_quality": "best[height<=360]",
                "audio_quality": "128K",
                "max_retries": 3
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            task_id = data["task_id"]
            assert data["status"] == "pending"
            
            print(f"\n任务已创建: {task_id}")
            
            # 2. 轮询任务状态
            max_wait = 300  # 最多等待5分钟
            start_time = time.time()
            final_status = None
            
            while time.time() - start_time < max_wait:
                response = test_client.get(f"/tasks/{task_id}")
                assert response.status_code == 200
                
                task_data = response.json()
                status = task_data["status"]
                print(f"任务状态: {status} - {task_data.get('progress', '')}")
                
                if status == "completed":
                    final_status = "completed"
                    print("✅ 任务完成!")
                    break
                elif status == "failed":
                    final_status = "failed"
                    print(f"❌ 任务失败: {task_data.get('error', '')}")
                    break
                
                time.sleep(5)  # 每5秒检查一次
            
            assert final_status == "completed", "任务应该成功完成"
            
            # 3. 验证文件生成
            response = test_client.get(f"/tasks/{task_id}")
            task_data = response.json()
            files = task_data.get("files", {})
            
            assert "video" in files, "应该生成视频文件"
            assert "audio" in files, "应该生成音频文件"
            print(f"生成的文件: {files}")
            
            # 4. 下载并验证视频文件
            response = test_client.get(f"/tasks/{task_id}/files/video")
            assert response.status_code == 200
            video_content = response.content
            assert len(video_content) > 1000, "视频文件应该有实际内容"
            print(f"视频文件大小: {len(video_content)} 字节")
            
            # 5. 下载并验证音频文件
            response = test_client.get(f"/tasks/{task_id}/files/audio")
            assert response.status_code == 200
            audio_content = response.content
            assert len(audio_content) > 1000, "音频文件应该有实际内容"
            print(f"音频文件大小: {len(audio_content)} 字节")
            
            # 6. 清理任务
            response = test_client.delete(f"/tasks/{task_id}")
            assert response.status_code == 200
            print("任务已清理")
    
    @pytest.mark.skipif(
        os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true',
        reason="跳过集成测试"
    )
    def test_video_only_download(self, test_client, real_youtube_url, temp_downloads_dir):
        """测试仅下载视频"""
        from unittest.mock import patch
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            payload = {
                "url": real_youtube_url,
                "start_time": "00:10",
                "end_time": "00:25",
                "download_video": True,
                "download_audio": False,
                "download_subtitles": False,
                "video_quality": "best[height<=360]"
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200
            task_id = response.json()["task_id"]
            
            # 等待完成
            final_status = self._wait_for_task(test_client, task_id, max_wait=180)
            assert final_status == "completed"
            
            # 验证只有视频文件
            response = test_client.get(f"/tasks/{task_id}")
            files = response.json().get("files", {})
            assert "video" in files
            assert "audio" not in files
            
            # 清理
            test_client.delete(f"/tasks/{task_id}")
    
    @pytest.mark.skipif(
        os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true',
        reason="跳过集成测试"
    )
    def test_audio_only_download(self, test_client, real_youtube_url, temp_downloads_dir):
        """测试仅下载音频"""
        from unittest.mock import patch
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            payload = {
                "url": real_youtube_url,
                "start_time": "00:10",
                "end_time": "00:25",
                "download_video": False,
                "download_audio": True,
                "download_subtitles": False,
                "audio_quality": "128K"
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200
            task_id = response.json()["task_id"]
            
            # 等待完成
            final_status = self._wait_for_task(test_client, task_id, max_wait=180)
            assert final_status == "completed"
            
            # 验证只有音频文件
            response = test_client.get(f"/tasks/{task_id}")
            files = response.json().get("files", {})
            assert "audio" in files
            assert "video" not in files
            
            # 清理
            test_client.delete(f"/tasks/{task_id}")
    
    @pytest.mark.skipif(
        os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true',
        reason="跳过集成测试"
    )
    def test_invalid_url(self, test_client, temp_downloads_dir):
        """测试无效的 URL"""
        from unittest.mock import patch
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            payload = {
                "url": "https://www.youtube.com/watch?v=invalid_video_id_12345",
                "start_time": "00:10",
                "end_time": "00:30",
                "download_video": True,
                "download_audio": False,
                "download_subtitles": False
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200
            task_id = response.json()["task_id"]
            
            # 等待任务处理
            final_status = self._wait_for_task(test_client, task_id, max_wait=60)
            
            # 应该失败
            assert final_status == "failed"
            
            # 检查错误信息
            response = test_client.get(f"/tasks/{task_id}")
            task_data = response.json()
            assert "error" in task_data
            
            # 清理
            test_client.delete(f"/tasks/{task_id}")
    
    @pytest.mark.skipif(
        os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true',
        reason="跳过集成测试"
    )
    def test_different_time_ranges(self, test_client, real_youtube_url, temp_downloads_dir):
        """测试不同的时间范围"""
        from unittest.mock import patch
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            # 测试不同的时间格式
            test_cases = [
                ("00:05", "00:15"),  # MM:SS 格式
                ("0:10", "0:20"),    # 单个0
                ("10", "20"),         # 秒数格式
            ]
            
            for start, end in test_cases:
                payload = {
                    "url": real_youtube_url,
                    "start_time": start,
                    "end_time": end,
                    "download_video": False,
                    "download_audio": True,
                    "download_subtitles": False,
                    "audio_quality": "128K"
                }
                
                response = test_client.post("/download", json=payload)
                assert response.status_code == 200
                task_id = response.json()["task_id"]
                
                print(f"测试时间范围: {start} - {end}")
                
                # 等待完成
                final_status = self._wait_for_task(test_client, task_id, max_wait=180)
                assert final_status == "completed", f"时间范围 {start}-{end} 应该成功"
                
                # 清理
                test_client.delete(f"/tasks/{task_id}")
    
    def _wait_for_task(self, client, task_id, max_wait=300):
        """等待任务完成的辅助函数"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = client.get(f"/tasks/{task_id}")
            if response.status_code != 200:
                return None
            
            task_data = response.json()
            status = task_data["status"]
            
            if status in ["completed", "failed"]:
                return status
            
            time.sleep(5)
        
        return "timeout"


class TestTaskPersistence:
    """任务持久性测试"""
    
    @pytest.mark.skipif(
        os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true',
        reason="跳过集成测试"
    )
    def test_task_list_during_download(self, test_client, real_youtube_url, temp_downloads_dir):
        """测试下载过程中的任务列表"""
        from unittest.mock import patch
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            # 创建任务
            payload = {
                "url": real_youtube_url,
                "start_time": "00:10",
                "end_time": "00:25",
                "download_video": False,
                "download_audio": True,
                "download_subtitles": False
            }
            
            response = test_client.post("/download", json=payload)
            task_id = response.json()["task_id"]
            
            # 立即检查任务列表
            response = test_client.get("/tasks")
            assert response.status_code == 200
            tasks = response.json()
            assert len(tasks) >= 1
            
            # 找到我们的任务
            our_task = next((t for t in tasks if t["task_id"] == task_id), None)
            assert our_task is not None
            assert our_task["status"] in ["pending", "processing"]
            
            # 等待完成
            start_time = time.time()
            while time.time() - start_time < 180:
                response = test_client.get(f"/tasks/{task_id}")
                if response.json()["status"] in ["completed", "failed"]:
                    break
                time.sleep(5)
            
            # 再次检查任务列表
            response = test_client.get("/tasks")
            tasks = response.json()
            our_task = next((t for t in tasks if t["task_id"] == task_id), None)
            assert our_task is not None
            assert our_task["status"] in ["completed", "failed"]
            
            # 清理
            test_client.delete(f"/tasks/{task_id}")


class TestErrorRecovery:
    """错误恢复测试"""
    
    @pytest.mark.skipif(
        os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true',
        reason="跳过集成测试"
    )
    def test_invalid_time_range(self, test_client, real_youtube_url, temp_downloads_dir):
        """测试无效的时间范围（结束时间早于开始时间）"""
        from unittest.mock import patch
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            payload = {
                "url": real_youtube_url,
                "start_time": "00:30",
                "end_time": "00:10",  # 早于开始时间
                "download_video": False,
                "download_audio": True,
                "download_subtitles": False
            }
            
            response = test_client.post("/download", json=payload)
            assert response.status_code == 200
            task_id = response.json()["task_id"]
            
            # 等待处理
            start_time = time.time()
            while time.time() - start_time < 60:
                response = test_client.get(f"/tasks/{task_id}")
                status = response.json()["status"]
                if status in ["completed", "failed"]:
                    break
                time.sleep(3)
            
            # 应该失败或生成空文件
            response = test_client.get(f"/tasks/{task_id}")
            final_status = response.json()["status"]
            # 可能是 failed，也可能是 completed 但文件很小
            assert final_status in ["completed", "failed"]
            
            # 清理
            test_client.delete(f"/tasks/{task_id}")


class TestConcurrentDownloads:
    """并发下载测试"""
    
    @pytest.mark.skipif(
        os.environ.get('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true',
        reason="跳过集成测试"
    )
    def test_multiple_downloads(self, test_client, real_youtube_url, temp_downloads_dir):
        """测试同时进行多个下载"""
        from unittest.mock import patch
        
        with patch('app.DOWNLOADS_DIR', temp_downloads_dir):
            task_ids = []
            
            # 创建3个下载任务
            for i in range(3):
                start = 10 + i * 5
                end = start + 10
                
                payload = {
                    "url": real_youtube_url,
                    "start_time": f"00:{start:02d}",
                    "end_time": f"00:{end:02d}",
                    "download_video": False,
                    "download_audio": True,
                    "download_subtitles": False,
                    "audio_quality": "128K"
                }
                
                response = test_client.post("/download", json=payload)
                assert response.status_code == 200
                task_ids.append(response.json()["task_id"])
                
                print(f"创建任务 {i+1}/3: {task_ids[-1]}")
            
            # 等待所有任务完成
            max_wait = 300
            start_time = time.time()
            completed_tasks = set()
            
            while time.time() - start_time < max_wait:
                for task_id in task_ids:
                    if task_id in completed_tasks:
                        continue
                    
                    response = test_client.get(f"/tasks/{task_id}")
                    if response.status_code == 200:
                        status = response.json()["status"]
                        if status in ["completed", "failed"]:
                            completed_tasks.add(task_id)
                            print(f"任务完成: {task_id} - {status}")
                
                if len(completed_tasks) == len(task_ids):
                    break
                
                time.sleep(5)
            
            # 验证所有任务都完成了
            assert len(completed_tasks) == len(task_ids), "所有任务都应该完成"
            
            # 检查成功率
            success_count = 0
            for task_id in task_ids:
                response = test_client.get(f"/tasks/{task_id}")
                if response.json()["status"] == "completed":
                    success_count += 1
            
            print(f"成功率: {success_count}/{len(task_ids)}")
            assert success_count >= 2, "至少应该有2个任务成功"
            
            # 清理所有任务
            for task_id in task_ids:
                test_client.delete(f"/tasks/{task_id}")


#!/usr/bin/env python3
"""
YouTube 下载器 Python 客户端示例
演示如何使用 API 下载视频
"""

import requests
import time
import argparse
from typing import Optional, Dict


class YouTubeDownloaderClient:
    """YouTube 下载器 API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            base_url: API 基础 URL
        """
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict:
        """检查服务健康状态"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def create_task(
        self,
        url: str,
        start_time: str,
        end_time: str,
        proxy: Optional[str] = None,
        download_video: bool = True,
        download_audio: bool = True,
        download_subtitles: bool = False,
        video_quality: str = "bestvideo[height<=480]+bestaudio/best[height<=480]",
        audio_quality: str = "192K"
    ) -> Dict:
        """
        创建下载任务
        
        Args:
            url: YouTube 视频 URL
            start_time: 开始时间
            end_time: 结束时间
            proxy: 代理服务器（可选）
            download_video: 是否下载视频
            download_audio: 是否下载音频
            download_subtitles: 是否下载字幕
            video_quality: 视频质量
            audio_quality: 音频质量
            
        Returns:
            任务信息字典
        """
        payload = {
            "url": url,
            "start_time": start_time,
            "end_time": end_time,
            "download_video": download_video,
            "download_audio": download_audio,
            "download_subtitles": download_subtitles,
            "video_quality": video_quality,
            "audio_quality": audio_quality
        }
        
        if proxy:
            payload["proxy"] = proxy
        
        response = requests.post(
            f"{self.base_url}/download",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, task_id: str) -> Dict:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态字典
        """
        response = requests.get(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def list_tasks(self, status: Optional[str] = None, limit: int = 50) -> list:
        """
        获取任务列表
        
        Args:
            status: 过滤状态（pending, processing, completed, failed）
            limit: 返回数量限制
            
        Returns:
            任务列表
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        response = requests.get(f"{self.base_url}/tasks", params=params)
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 5,
        verbose: bool = True
    ) -> Dict:
        """
        等待任务完成
        
        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）
            verbose: 是否打印进度
            
        Returns:
            完成的任务状态
            
        Raises:
            TimeoutError: 等待超时
            Exception: 任务失败
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_data = self.get_task_status(task_id)
            status = status_data['status']
            
            if verbose:
                elapsed = int(time.time() - start_time)
                progress = status_data.get('progress', status)
                print(f"[{elapsed}s] 状态: {status} - {progress}")
            
            if status == 'completed':
                if verbose:
                    print("✅ 任务完成！")
                return status_data
            elif status == 'failed':
                error = status_data.get('error', '未知错误')
                raise Exception(f"任务失败: {error}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"等待任务完成超时（{timeout}秒）")
    
    def download_file(
        self,
        task_id: str,
        file_type: str,
        output_path: str,
        verbose: bool = True
    ) -> str:
        """
        下载文件
        
        Args:
            task_id: 任务 ID
            file_type: 文件类型（video, audio, subtitles）
            output_path: 输出文件路径
            verbose: 是否打印进度
            
        Returns:
            输出文件路径
        """
        if verbose:
            print(f"📥 下载 {file_type} 到 {output_path}...")
        
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}/files/{file_type}",
            stream=True,
            timeout=120
        )
        response.raise_for_status()
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            if total_size > 0 and verbose:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / total_size) * 100
                    print(f"\r进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
                print()  # 换行
            else:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        if verbose:
            print(f"✅ 下载完成: {output_path}")
        
        return output_path
    
    def delete_task(self, task_id: str) -> Dict:
        """
        删除任务及其文件
        
        Args:
            task_id: 任务 ID
            
        Returns:
            删除结果
        """
        response = requests.delete(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(description="YouTube 下载器 API 客户端")
    parser.add_argument("url", help="YouTube 视频 URL")
    parser.add_argument("--start", required=True, help="开始时间（HH:MM:SS 或 MM:SS）")
    parser.add_argument("--end", required=True, help="结束时间（HH:MM:SS 或 MM:SS）")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API 地址")
    parser.add_argument("--proxy", help="代理服务器地址")
    parser.add_argument("--output-dir", default=".", help="输出目录")
    parser.add_argument("--no-video", action="store_true", help="不下载视频")
    parser.add_argument("--no-audio", action="store_true", help="不下载音频")
    parser.add_argument("--subtitles", action="store_true", help="下载字幕")
    parser.add_argument("--video-quality", default="bestvideo[height<=480]+bestaudio/best[height<=480]", help="视频质量")
    parser.add_argument("--audio-quality", default="192K", help="音频质量")
    
    args = parser.parse_args()
    
    # 创建客户端
    client = YouTubeDownloaderClient(args.api_url)
    
    try:
        # 健康检查
        print("🔍 检查服务状态...")
        health = client.health_check()
        print(f"✅ 服务正常运行: {health['status']}")
        print()
        
        # 创建任务
        print("📤 创建下载任务...")
        task = client.create_task(
            url=args.url,
            start_time=args.start,
            end_time=args.end,
            proxy=args.proxy,
            download_video=not args.no_video,
            download_audio=not args.no_audio,
            download_subtitles=args.subtitles,
            video_quality=args.video_quality,
            audio_quality=args.audio_quality
        )
        
        task_id = task['task_id']
        print(f"✅ 任务已创建: {task_id}")
        print()
        
        # 等待完成
        print("⏳ 等待任务完成...")
        result = client.wait_for_completion(task_id, timeout=300)
        print()
        
        # 下载文件
        files = result.get('files', {})
        
        if 'video' in files and not args.no_video:
            video_path = f"{args.output_dir}/video.mp4"
            client.download_file(task_id, 'video', video_path)
        
        if 'audio' in files and not args.no_audio:
            audio_path = f"{args.output_dir}/audio.mp3"
            client.download_file(task_id, 'audio', audio_path)
        
        if 'subtitles' in files and args.subtitles:
            subtitle_path = f"{args.output_dir}/subtitles.vtt"
            client.download_file(task_id, 'subtitles', subtitle_path)
        
        print()
        print("🎉 全部完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

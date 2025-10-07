#!/usr/bin/env python3
"""
YouTube下载器 HTTP API 服务
使用 FastAPI 提供 RESTful API
"""

import os
import sys
import uuid
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import shutil

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# 导入原有的下载功能
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from youtube_downloader import (
    DownloadConfig, 
    process_single_url,
    setup_logging,
    check_dependencies,
    extract_video_id
)

# 全局变量
tasks_db: Dict[str, dict] = {}
DOWNLOADS_DIR = os.environ.get('DOWNLOADS_DIR', '/tmp/downloads')

# 确保下载目录存在
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# 设置日志
logger = setup_logging()


class DownloadRequest(BaseModel):
    """下载请求模型"""
    url: str = Field(..., description="YouTube视频URL")
    start_time: str = Field(..., description="开始时间 (HH:MM:SS, MM:SS 或秒数)")
    end_time: str = Field(..., description="结束时间 (HH:MM:SS, MM:SS 或秒数)")
    proxy: Optional[str] = Field(None, description="代理服务器地址")
    subtitle_langs: str = Field("zh,en", description="字幕语言代码，逗号分隔")
    download_video: bool = Field(True, description="是否下载视频")
    download_audio: bool = Field(True, description="是否下载音频")
    download_subtitles: bool = Field(True, description="是否下载字幕")
    video_quality: str = Field("best[height<=480]", description="视频质量")
    audio_quality: str = Field("192K", description="音频质量")
    max_retries: int = Field(3, description="最大重试次数")


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str
    status: str
    message: str
    created_at: str


class TaskStatus(BaseModel):
    """任务状态模型"""
    task_id: str
    status: str  # pending, processing, completed, failed
    url: str
    video_id: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    files: Optional[Dict[str, str]] = None
    progress: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时检查依赖
    logger.info("🚀 启动 YouTube 下载器 API 服务...")
    if not check_dependencies():
        logger.error("❌ 依赖检查失败，但服务将继续运行")
    else:
        logger.info("✅ 依赖检查通过")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 关闭服务...")
    cleanup_old_tasks()


app = FastAPI(
    title="YouTube下载器 API",
    description="支持时间段裁剪、音频提取、字幕下载的 YouTube 下载服务",
    version="2.0.0",
    lifespan=lifespan
)


def cleanup_old_tasks(max_age_hours: int = 24):
    """清理旧任务和文件"""
    logger.info("开始清理旧任务...")
    current_time = datetime.now()
    tasks_to_remove = []
    
    for task_id, task in tasks_db.items():
        created_at = datetime.fromisoformat(task['created_at'])
        age_hours = (current_time - created_at).total_seconds() / 3600
        
        if age_hours > max_age_hours:
            # 删除相关文件
            if task.get('video_id'):
                video_dir = os.path.join(DOWNLOADS_DIR, task['video_id'])
                if os.path.exists(video_dir):
                    shutil.rmtree(video_dir)
                    logger.info(f"删除旧任务文件: {video_dir}")
            tasks_to_remove.append(task_id)
    
    for task_id in tasks_to_remove:
        del tasks_db[task_id]
        logger.info(f"删除旧任务: {task_id}")
    
    logger.info(f"清理完成，删除了 {len(tasks_to_remove)} 个旧任务")


async def process_download_task(task_id: str, config: DownloadConfig):
    """异步处理下载任务"""
    try:
        tasks_db[task_id]['status'] = 'processing'
        tasks_db[task_id]['progress'] = '开始下载...'
        logger.info(f"开始处理任务 {task_id}: {config.url}")
        
        # 提取视频ID
        video_id = extract_video_id(config.url)
        if video_id:
            tasks_db[task_id]['video_id'] = video_id
        
        # 执行下载（在线程池中运行阻塞操作）
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, process_single_url, config)
        
        if result:
            tasks_db[task_id]['status'] = 'completed'
            tasks_db[task_id]['completed_at'] = datetime.now().isoformat()
            tasks_db[task_id]['progress'] = '下载完成'
            
            # 记录文件路径
            files = {}
            for content_type, file_path in result.items():
                if file_path and os.path.exists(file_path):
                    files[content_type] = os.path.basename(file_path)
            
            tasks_db[task_id]['files'] = files
            logger.info(f"任务 {task_id} 完成: {files}")
        else:
            tasks_db[task_id]['status'] = 'failed'
            tasks_db[task_id]['error'] = '下载失败，请检查日志'
            tasks_db[task_id]['completed_at'] = datetime.now().isoformat()
            logger.error(f"任务 {task_id} 失败")
            
    except Exception as e:
        tasks_db[task_id]['status'] = 'failed'
        tasks_db[task_id]['error'] = str(e)
        tasks_db[task_id]['completed_at'] = datetime.now().isoformat()
        logger.error(f"任务 {task_id} 异常: {e}", exc_info=True)


@app.get("/", response_model=dict)
async def root():
    """根路径 - API 信息"""
    return {
        "service": "YouTube下载器 API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "download": "/download",
            "tasks": "/tasks",
            "task_status": "/tasks/{task_id}"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tasks_count": len(tasks_db),
        "downloads_dir": DOWNLOADS_DIR
    }


@app.post("/download", response_model=TaskResponse)
async def create_download_task(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    """
    创建下载任务
    
    - **url**: YouTube视频URL
    - **start_time**: 开始时间
    - **end_time**: 结束时间
    - 其他可选参数见模型定义
    """
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建下载配置
        config = DownloadConfig(
            url=request.url,
            start_time=request.start_time,
            end_time=request.end_time,
            output_dir=DOWNLOADS_DIR,
            proxy=request.proxy,
            subtitle_langs=request.subtitle_langs,
            download_video=request.download_video,
            download_audio=request.download_audio,
            download_subtitles=request.download_subtitles,
            max_retries=request.max_retries,
            video_quality=request.video_quality,
            audio_quality=request.audio_quality
        )
        
        # 初始化任务状态
        tasks_db[task_id] = {
            'task_id': task_id,
            'status': 'pending',
            'url': request.url,
            'created_at': datetime.now().isoformat(),
            'config': request.dict()
        }
        
        # 添加后台任务
        background_tasks.add_task(process_download_task, task_id, config)
        
        logger.info(f"创建下载任务: {task_id} for {request.url}")
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            message="任务已创建，正在处理中",
            created_at=tasks_db[task_id]['created_at']
        )
        
    except Exception as e:
        logger.error(f"创建任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@app.get("/tasks", response_model=List[TaskStatus])
async def list_tasks(
    status: Optional[str] = Query(None, description="过滤状态: pending, processing, completed, failed"),
    limit: int = Query(50, description="返回数量限制", ge=1, le=100)
):
    """获取任务列表"""
    tasks = list(tasks_db.values())
    
    # 过滤状态
    if status:
        tasks = [t for t in tasks if t['status'] == status]
    
    # 按创建时间倒序
    tasks = sorted(tasks, key=lambda x: x['created_at'], reverse=True)
    
    # 限制数量
    tasks = tasks[:limit]
    
    return [TaskStatus(**task) for task in tasks]


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return TaskStatus(**tasks_db[task_id])


@app.get("/tasks/{task_id}/files/{file_type}")
async def download_file(task_id: str, file_type: str):
    """
    下载任务生成的文件
    
    - **file_type**: video, audio, subtitles
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_db[task_id]
    
    if task['status'] != 'completed':
        raise HTTPException(status_code=400, detail="任务未完成")
    
    if not task.get('files') or file_type not in task['files']:
        raise HTTPException(status_code=404, detail=f"文件类型 {file_type} 不存在")
    
    # 构建文件路径
    video_id = task.get('video_id')
    if not video_id:
        raise HTTPException(status_code=500, detail="视频ID缺失")
    
    file_name = task['files'][file_type]
    file_path = os.path.join(DOWNLOADS_DIR, video_id, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type='application/octet-stream'
    )


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务及其文件"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_db[task_id]
    
    # 删除文件
    if task.get('video_id'):
        video_dir = os.path.join(DOWNLOADS_DIR, task['video_id'])
        if os.path.exists(video_dir):
            shutil.rmtree(video_dir)
            logger.info(f"删除任务文件: {video_dir}")
    
    # 删除任务记录
    del tasks_db[task_id]
    logger.info(f"删除任务: {task_id}")
    
    return {"message": "任务已删除", "task_id": task_id}


@app.post("/cleanup")
async def cleanup_tasks(max_age_hours: int = Query(24, description="清理多少小时前的任务")):
    """手动清理旧任务"""
    cleanup_old_tasks(max_age_hours)
    return {
        "message": f"已清理 {max_age_hours} 小时前的旧任务",
        "current_tasks": len(tasks_db)
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"启动服务器: {host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

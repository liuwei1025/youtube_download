#!/usr/bin/env python3
"""
YouTube下载器 HTTP API 服务
使用 FastAPI 提供 RESTful API
支持数据库持久化存储任务
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Optional, List
from pathlib import Path
import shutil
import traceback

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 导入原有的下载功能
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from downloader import (
    DownloadConfig, 
    process_single_url,
    setup_logging
)
from downloader.utils import check_dependencies, extract_video_id

# 导入数据库和模型
from src.database import db
from src.models import (
    DownloadRequest,
    TaskResponse,
    TaskDetail,
    TaskList,
    TaskListResponse,
    TaskStatus,
    FileType,
    TaskStats,
    TaskLog,
)
from src.task_service import TaskService

# 默认保存在项目根目录的 downloads 文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.environ.get('DOWNLOADS_DIR', os.path.join(BASE_DIR, 'downloads'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')

# Cookies 文件路径配置（优先使用环境变量，否则使用默认路径）
COOKIES_FILE = os.environ.get('COOKIES_FILE', os.path.join(BASE_DIR, 'cookies', 'Cookies'))

# 确保下载目录存在
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# 设置日志
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库连接
    logger.info("🚀 启动 YouTube 下载器 API 服务...")
    try:
        await db.connect()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        raise
    
    if not check_dependencies():
        logger.error("❌ 依赖检查失败，但服务将继续运行")
    else:
        logger.info("✅ 依赖检查通过")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 关闭服务...")
    await db.disconnect()


app = FastAPI(
    title="YouTube下载器 API",
    description="支持时间段裁剪、音频提取、字幕下载的 YouTube 下载服务 (数据库版)",
    version="3.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def retry_single_file_download(
    task_id: str,
    file_type: str,
    url: str,
    start_time: Optional[str],
    end_time: Optional[str],
    subtitle_langs: Optional[str],
    proxy: Optional[str]
):
    """重新下载单个失败的文件"""
    try:
        await TaskService.add_log(task_id, 'INFO', f'开始重新下载文件: {file_type}')
        
        # 更新文件状态为processing
        await db.execute(
            """
            UPDATE task_files 
            SET status = 'processing'
            WHERE task_id = :task_id AND file_type = :file_type
            """,
            {"task_id": task_id, "file_type": file_type}
        )
        
        # 构建下载配置
        config = DownloadConfig(
            url=url,
            output_dir=DOWNLOADS_DIR,
            start_time=start_time,
            end_time=end_time,
            subtitle_langs=subtitle_langs,
            proxy=proxy,
            cookies_file=COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        # 根据文件类型设置下载选项
        download_video=(file_type in [FileType.VIDEO.value, FileType.VIDEO_WITH_SUBS.value]),
        download_audio=(file_type == FileType.AUDIO.value),
        download_subtitles=(file_type in [FileType.SUBTITLES.value, FileType.VIDEO_WITH_SUBS.value]),
        burn_subtitles=(file_type == FileType.VIDEO_WITH_SUBS.value)
        )
        
        # 执行下载
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, process_single_url, config)
        
        if result:
            # process_single_url 返回的是字典，key 是 FileType 枚举，value 是文件路径
            # 将字符串转换为 FileType 枚举进行比较（兼容历史数据）
            file_type_enum = None
            try:
                file_type_enum = FileType(file_type) if file_type in [ft.value for ft in FileType] else None
            except ValueError:
                file_type_enum = None
            
            # 根据文件类型获取对应的文件路径
            file_path = None
            file_name = None
            file_size = None
            mime_type = None
            
            if file_type_enum == FileType.VIDEO and result.get(FileType.VIDEO):
                file_path = result[FileType.VIDEO]
                mime_type = 'video/mp4'
            elif file_type_enum == FileType.AUDIO and result.get(FileType.AUDIO):
                file_path = result[FileType.AUDIO]
                mime_type = 'audio/mpeg'
            elif file_type_enum == FileType.SUBTITLES and result.get(FileType.SUBTITLES):
                file_path = result[FileType.SUBTITLES]
                mime_type = 'text/vtt'
            elif file_type_enum == FileType.VIDEO_WITH_SUBS and result.get(FileType.VIDEO_WITH_SUBS):
                file_path = result[FileType.VIDEO_WITH_SUBS]
                mime_type = 'video/mp4'
            
            if file_path and os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                # 更新文件记录
                await db.execute(
                    """
                    UPDATE task_files 
                    SET file_name = :file_name,
                        file_path = :file_path,
                        file_size = :file_size,
                        mime_type = :mime_type,
                        status = 'completed',
                        error_message = NULL
                    WHERE task_id = :task_id AND file_type = :file_type
                    """,
                    {
                        "task_id": task_id,
                        "file_type": file_type,
                        "file_name": file_name,
                        "file_path": file_path,
                        "file_size": file_size,
                        "mime_type": mime_type
                    }
                )
                
                await TaskService.add_log(
                    task_id, 
                    'INFO', 
                    f'文件重新下载成功: {file_type} -> {file_name}'
                )
                logger.info(f"任务 {task_id} 文件 {file_type} 重新下载成功")
            else:
                raise Exception(f"文件 {file_type} 下载后未找到")
        else:
            # process_single_url 返回 None 表示下载失败
            raise Exception(f"文件 {file_type} 下载失败")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"任务 {task_id} 文件 {file_type} 重新下载失败: {error_msg}", exc_info=True)
        
        # 更新文件状态为failed
        await db.execute(
            """
            UPDATE task_files 
            SET status = 'failed',
                error_message = :error_message
            WHERE task_id = :task_id AND file_type = :file_type
            """,
            {
                "task_id": task_id,
                "file_type": file_type,
                "error_message": error_msg[:500]  # 限制错误信息长度
            }
        )
        
        await TaskService.add_log(
            task_id,
            'ERROR',
            f'文件 {file_type} 重新下载失败: {error_msg}'
        )


async def process_download_task(task_id: str, config: DownloadConfig):
    """异步处理下载任务"""
    try:
        # 更新状态为处理中
        await TaskService.update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            progress='开始下载...',
            progress_percentage=10,
            current_step='初始化'
        )
        await TaskService.add_task_log(task_id, 'INFO', f'开始处理任务: {config.url}')
        logger.info(f"开始处理任务 {task_id}: {config.url}")
        
        # 提取视频ID
        video_id = extract_video_id(config.url)
        if video_id:
            await TaskService.update_task_status(
                task_id,
                TaskStatus.PROCESSING,
                video_id=video_id,
                progress='已提取视频ID',
                progress_percentage=20
            )
            await TaskService.add_task_log(task_id, 'INFO', f'视频ID: {video_id}')
        
        # 更新进度
        await TaskService.update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            progress='正在下载视频...',
            progress_percentage=30,
            current_step='下载中'
        )
        
        # 执行下载（在线程池中运行阻塞操作）
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, process_single_url, config)
        
        if result:
            # 下载成功，保存文件信息
            await TaskService.update_task_status(
                task_id,
                TaskStatus.PROCESSING,
                progress='正在保存文件信息...',
                progress_percentage=90,
                current_step='保存文件'
            )
            
            for content_type, file_path in result.items():
                if file_path and os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    
                    # 确定MIME类型，使用 FileType 枚举的值（字符串）
                    mime_type = 'application/octet-stream'
                    if content_type == FileType.VIDEO or content_type == FileType.VIDEO_WITH_SUBS:
                        mime_type = 'video/mp4'
                    elif content_type == FileType.AUDIO:
                        mime_type = 'audio/mpeg'
                    elif content_type == FileType.SUBTITLES:
                        mime_type = 'text/vtt'
                    
                    # 将枚举值转换为字符串存储到数据库
                    file_type_str = content_type.value if isinstance(content_type, FileType) else str(content_type)
                    
                    await TaskService.add_task_file(
                        task_id,
                        file_type_str,
                        file_name,
                        file_path,
                        file_size,
                        mime_type
                    )
                    await TaskService.add_task_log(
                        task_id,
                        'INFO',
                        f'已保存文件: {file_type_str} - {file_name}'
                    )
            
            # 更新为完成状态
            await TaskService.update_task_status(
                task_id,
                TaskStatus.COMPLETED,
                progress='下载完成',
                progress_percentage=100,
                current_step='完成'
            )
            await TaskService.add_task_log(task_id, 'INFO', '任务完成')
            logger.info(f"任务 {task_id} 完成")
        else:
            # 下载失败
            error_msg = '下载失败，请检查日志'
            await TaskService.update_task_status(
                task_id,
                TaskStatus.FAILED,
                progress='下载失败',
                progress_percentage=0,
                error_message=error_msg
            )
            await TaskService.add_task_log(task_id, 'ERROR', error_msg)
            logger.error(f"任务 {task_id} 失败")
            
    except Exception as e:
        # 捕获异常
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        await TaskService.update_task_status(
            task_id,
            TaskStatus.FAILED,
            progress='任务异常',
            progress_percentage=0,
            error_message=error_msg,
            error_trace=error_trace
        )
        await TaskService.add_task_log(task_id, 'ERROR', f'任务异常: {error_msg}')
        logger.error(f"任务 {task_id} 异常: {e}", exc_info=True)


@app.get("/api", response_model=dict)
async def api_root():
    """API 根路径 - API 信息"""
    return {
        "service": "YouTube下载器 API (数据库版)",
        "version": "3.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "download": "/download",
            "tasks": "/tasks",
            "task_status": "/tasks/{task_id}",
            "task_files": "/tasks/{task_id}/files",
            "task_logs": "/tasks/{task_id}/logs",
            "task_stats": "/stats"
        }
    }


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    try:
        # 测试数据库连接
        stats = await TaskService.get_task_stats()
        db_status = "connected"
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        db_status = "disconnected"
        stats = None
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "tasks_stats": stats.dict() if stats else None,
        "downloads_dir": DOWNLOADS_DIR
    }


@app.post("/api/download", response_model=TaskResponse)
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
        # 创建任务记录
        task_id = await TaskService.create_task(
            url=request.url,
            start_time=request.start_time,
            end_time=request.end_time,
            proxy=request.proxy,
            subtitle_langs=request.subtitle_langs,
            download_video=request.download_video,
            download_audio=request.download_audio,
            download_subtitles=request.download_subtitles,
            burn_subtitles=request.burn_subtitles,
            video_quality=request.video_quality,
            audio_quality=request.audio_quality,
            max_retries=request.max_retries
        )
        
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
            burn_subtitles=request.burn_subtitles,
            max_retries=request.max_retries,
            video_quality=request.video_quality,
            audio_quality=request.audio_quality,
            cookies_file=COOKIES_FILE if os.path.exists(COOKIES_FILE) else None
        )
        
        # 添加后台任务
        background_tasks.add_task(process_download_task, task_id, config)
        
        # 记录日志
        await TaskService.add_task_log(task_id, 'INFO', f'任务已创建: {request.url}')
        logger.info(f"创建下载任务: {task_id} for {request.url}")
        
        # 获取任务信息
        task = await TaskService.get_task(task_id)
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="任务已创建，正在处理中",
            created_at=task.created_at
        )
        
    except Exception as e:
        logger.error(f"创建任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@app.get("/api/tasks", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None, description="过滤状态: pending, processing, completed, failed, cancelled"),
    limit: int = Query(10, description="返回数量限制", ge=1, le=100),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """获取任务列表（带分页）"""
    try:
        tasks = await TaskService.list_tasks(status=status, limit=limit, offset=offset)
        total = await TaskService.get_tasks_count(status=status)
        
        return TaskListResponse(
            tasks=tasks,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@app.get("/api/tasks/{task_id}", response_model=TaskDetail)
async def get_task_status(task_id: str):
    """获取任务详情"""
    try:
        task = await TaskService.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@app.get("/api/tasks/{task_id}/logs", response_model=List[TaskLog])
async def get_task_logs(
    task_id: str,
    limit: int = Query(100, description="返回数量限制", ge=1, le=1000)
):
    """获取任务日志"""
    try:
        # 先检查任务是否存在
        task = await TaskService.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        logs = await TaskService.get_task_logs(task_id, limit=limit)
        return logs
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务日志失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取任务日志失败: {str(e)}")


@app.get("/api/tasks/{task_id}/files")
async def get_task_files(task_id: str):
    """获取任务的所有文件列表"""
    try:
        task = await TaskService.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "task_id": task_id,
            "status": task.status,
            "files": [f.dict() for f in task.files]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务文件列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取任务文件列表失败: {str(e)}")


@app.get("/api/tasks/{task_id}/files/{file_type}")
async def download_file(task_id: str, file_type: str):
    """
    下载任务生成的文件
    
    - **file_type**: video, audio, subtitles, video_with_subs
    """
    try:
        task = await TaskService.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="任务未完成")
        
        # 查找对应类型的文件
        target_file = None
        for f in task.files:
            if f.file_type == file_type:
                target_file = f
                break
        
        if not target_file:
            raise HTTPException(status_code=404, detail=f"文件类型 {file_type} 不存在")
        
        file_path = target_file.file_path
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=file_path,
            filename=target_file.file_name,
            media_type=target_file.mime_type or 'application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, delete_files: bool = Query(True, description="是否删除相关文件")):
    """删除任务及其文件"""
    try:
        task = await TaskService.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 删除文件
        if delete_files and task.video_id:
            video_dir = os.path.join(DOWNLOADS_DIR, task.video_id)
            if os.path.exists(video_dir):
                shutil.rmtree(video_dir)
                logger.info(f"删除任务文件: {video_dir}")
        
        # 删除数据库记录
        await TaskService.delete_task(task_id)
        logger.info(f"删除任务: {task_id}")
        
        return {"message": "任务已删除", "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """取消任务"""
    try:
        task = await TaskService.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail="任务已结束，无法取消")
        
        await TaskService.cancel_task(task_id)
        await TaskService.add_task_log(task_id, 'INFO', '任务已被用户取消')
        logger.info(f"取消任务: {task_id}")
        
        return {"message": "任务已取消", "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


@app.post("/api/tasks/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: str, background_tasks: BackgroundTasks):
    """重试失败的任务"""
    try:
        task = await TaskService.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status not in [TaskStatus.FAILED, TaskStatus.CANCELLED]:
            raise HTTPException(
                status_code=400,
                detail=f"只能重试失败或已取消的任务，当前状态: {task.status}"
            )
        
        # 创建新任务
        new_task_id = await TaskService.retry_task(task_id)
        
        # 创建下载配置
        config = DownloadConfig(
            url=task.url,
            start_time=task.start_time,
            end_time=task.end_time,
            output_dir=DOWNLOADS_DIR,
            proxy=task.proxy,
            subtitle_langs=task.subtitle_langs,
            download_video=task.download_video,
            download_audio=task.download_audio,
            download_subtitles=task.download_subtitles,
            burn_subtitles=task.burn_subtitles,
            max_retries=task.max_retries,
            video_quality=task.video_quality,
            audio_quality=task.audio_quality,
            cookies_file=COOKIES_FILE if os.path.exists(COOKIES_FILE) else None
        )
        
        # 添加后台任务
        background_tasks.add_task(process_download_task, new_task_id, config)
        
        logger.info(f"重试任务: {task_id} -> {new_task_id}")
        
        # 获取新任务信息
        new_task = await TaskService.get_task(new_task_id)
        
        return TaskResponse(
            task_id=new_task_id,
            status=TaskStatus.PENDING,
            message=f"任务已重新创建，正在处理中（原任务: {task_id}）",
            created_at=new_task.created_at
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"重试任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"重试任务失败: {str(e)}")


@app.get("/api/stats", response_model=TaskStats)
async def get_stats():
    """获取任务统计信息"""
    try:
        stats = await TaskService.get_task_stats()
        return stats
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@app.post("/api/cleanup")
async def cleanup_tasks(max_age_hours: int = Query(24, description="清理多少小时前的任务")):
    """手动清理旧任务"""
    try:
        deleted_count = await TaskService.cleanup_old_tasks(hours=max_age_hours)
        
        return {
            "message": f"已清理 {max_age_hours} 小时前的旧任务",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"清理任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"清理任务失败: {str(e)}")


@app.post("/api/tasks/{task_id}/files/{file_type}/retry")
async def retry_file_download(
    task_id: str, 
    file_type: str,
    background_tasks: BackgroundTasks
):
    """重新下载失败的单个文件
    
    Args:
        task_id: 任务ID
        file_type: 文件类型 (video, audio, subtitles, video_with_subs)
    """
    try:
        # 获取任务
        task = await TaskService.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
        
        # 检查文件类型是否有效
        valid_types = ['video', 'audio', 'subtitles', 'video_with_subs']
        if file_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的文件类型: {file_type}。有效类型: {', '.join(valid_types)}"
            )
        
        # 更新文件状态为pending
        await db.execute(
            """
            UPDATE task_files 
            SET status = 'pending', error_message = NULL
            WHERE task_id = :task_id AND file_type = :file_type
            """,
            {"task_id": task_id, "file_type": file_type}
        )
        
        # 记录日志
        await TaskService.add_log(
            task_id, 
            "INFO", 
            f"准备重新下载文件: {file_type}"
        )
        
        # 在后台重新下载该文件
        background_tasks.add_task(
            retry_single_file_download,
            task_id,
            file_type,
            task.url,
            task.start_time,
            task.end_time,
            task.subtitle_langs,
            task.proxy
        )
        
        return {
            "message": f"已开始重新下载文件: {file_type}",
            "task_id": task_id,
            "file_type": file_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新下载文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"重新下载文件失败: {str(e)}")


# 挂载前端静态文件（必须在最后，以免覆盖API路由）
if os.path.exists(FRONTEND_DIR):
    # 静态资源（CSS, JS等）
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")
    
    # SPA fallback - 所有未匹配的路由返回 index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """为 SPA 提供 fallback 路由"""
        # 如果请求的是文件且存在，直接返回
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # 否则返回 index.html（用于 Vue Router）
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        else:
            return JSONResponse(
                status_code=404,
                content={"detail": "前端文件未构建，请先运行: cd frontend && pnpm install && pnpm build"}
            )
    
    logger.info(f"✅ 前端静态文件已挂载: {FRONTEND_DIR}")
else:
    logger.warning(f"⚠️  前端构建目录不存在: {FRONTEND_DIR}")
    logger.warning("提示: 请先构建前端项目")
    logger.warning("  cd frontend")
    logger.warning("  pnpm install")
    logger.warning("  pnpm build")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"启动服务器: {host}:{port}")
    logger.info(f"API 文档: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    if os.path.exists(FRONTEND_DIR):
        logger.info(f"前端界面: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

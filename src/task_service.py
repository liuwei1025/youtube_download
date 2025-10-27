#!/usr/bin/env python3
"""
任务管理服务
提供任务的CRUD操作和业务逻辑
"""

import os
import json
import traceback
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from uuid import uuid4

from .database import db
from .models import TaskStatus, TaskDetail, TaskList, TaskStats, TaskFile, TaskLog


class TaskService:
    """任务管理服务类"""
    
    @staticmethod
    async def create_task(
        url: str,
        start_time: str,
        end_time: str,
        **config
    ) -> str:
        """
        创建新任务
        
        Args:
            url: YouTube视频URL
            start_time: 开始时间
            end_time: 结束时间
            **config: 其他配置参数
        
        Returns:
            task_id: 任务ID
        """
        task_id = str(uuid4())
        
        query = """
            INSERT INTO tasks (
                task_id, status, url, start_time, end_time,
                proxy, subtitle_langs, download_video, download_audio,
                download_subtitles, burn_subtitles, video_quality,
                audio_quality, max_retries, progress, metadata
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            RETURNING task_id
        """
        
        result = await db.fetchval(
            query,
            task_id,
            TaskStatus.PENDING.value,
            url,
            start_time,
            end_time,
            config.get('proxy'),
            config.get('subtitle_langs', 'zh,en'),
            config.get('download_video', True),
            config.get('download_audio', True),
            config.get('download_subtitles', True),
            config.get('burn_subtitles', True),
            config.get('video_quality', 'bestvideo[height<=480]+bestaudio/best[height<=480]'),
            config.get('audio_quality', '192K'),
            config.get('max_retries', 3),
            '任务已创建',
            json.dumps(config.get('metadata', {}))
        )
        
        return result
    
    @staticmethod
    async def get_task(task_id: str) -> Optional[TaskDetail]:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务详情或None
        """
        query = """
            SELECT 
                task_id, status, url, video_id, video_title,
                start_time, end_time, proxy, subtitle_langs,
                download_video, download_audio, download_subtitles, burn_subtitles,
                video_quality, audio_quality, max_retries,
                progress, progress_percentage, current_step,
                created_at, updated_at, started_at, completed_at,
                error_message, error_trace, metadata
            FROM tasks
            WHERE task_id = $1
        """
        
        row = await db.fetchrow(query, task_id)
        if not row:
            return None
        
        # 获取文件信息
        files_query = """
            SELECT file_type, file_name, file_path, file_size, mime_type, created_at
            FROM task_files
            WHERE task_id = $1
            ORDER BY created_at DESC
        """
        files_rows = await db.fetch(files_query, task_id)
        files = [TaskFile(**dict(f)) for f in files_rows]
        
        # 构建任务详情
        task_data = dict(row)
        task_data['files'] = files
        
        # 解析 metadata
        if task_data.get('metadata'):
            task_data['metadata'] = json.loads(task_data['metadata']) if isinstance(task_data['metadata'], str) else task_data['metadata']
        
        return TaskDetail(**task_data)
    
    @staticmethod
    async def list_tasks(
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TaskList]:
        """
        获取任务列表
        
        Args:
            status: 过滤状态
            limit: 返回数量限制
            offset: 偏移量
        
        Returns:
            任务列表
        """
        if status:
            query = """
                SELECT 
                    task_id, status, url, video_id, video_title,
                    progress, progress_percentage,
                    created_at, completed_at, error_message
                FROM tasks
                WHERE status = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """
            rows = await db.fetch(query, status, limit, offset)
        else:
            query = """
                SELECT 
                    task_id, status, url, video_id, video_title,
                    progress, progress_percentage,
                    created_at, completed_at, error_message
                FROM tasks
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            rows = await db.fetch(query, limit, offset)
        
        return [TaskList(**dict(row)) for row in rows]
    
    @staticmethod
    async def update_task_status(
        task_id: str,
        status: TaskStatus,
        progress: Optional[str] = None,
        progress_percentage: Optional[int] = None,
        current_step: Optional[str] = None,
        video_id: Optional[str] = None,
        video_title: Optional[str] = None,
        error_message: Optional[str] = None,
        error_trace: Optional[str] = None
    ):
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            progress: 进度描述
            progress_percentage: 进度百分比
            current_step: 当前步骤
            video_id: 视频ID
            video_title: 视频标题
            error_message: 错误信息
            error_trace: 错误堆栈
        """
        # 构建动态更新语句
        updates = ['status = $2', 'updated_at = CURRENT_TIMESTAMP']
        params = [task_id, status.value]
        param_count = 2
        
        if progress is not None:
            param_count += 1
            updates.append(f'progress = ${param_count}')
            params.append(progress)
        
        if progress_percentage is not None:
            param_count += 1
            updates.append(f'progress_percentage = ${param_count}')
            params.append(progress_percentage)
        
        if current_step is not None:
            param_count += 1
            updates.append(f'current_step = ${param_count}')
            params.append(current_step)
        
        if video_id is not None:
            param_count += 1
            updates.append(f'video_id = ${param_count}')
            params.append(video_id)
        
        if video_title is not None:
            param_count += 1
            updates.append(f'video_title = ${param_count}')
            params.append(video_title)
        
        if error_message is not None:
            param_count += 1
            updates.append(f'error_message = ${param_count}')
            params.append(error_message)
        
        if error_trace is not None:
            param_count += 1
            updates.append(f'error_trace = ${param_count}')
            params.append(error_trace)
        
        # 根据状态更新时间戳
        if status == TaskStatus.PROCESSING:
            updates.append('started_at = CURRENT_TIMESTAMP')
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            updates.append('completed_at = CURRENT_TIMESTAMP')
        
        query = f"""
            UPDATE tasks
            SET {', '.join(updates)}
            WHERE task_id = $1
        """
        
        await db.execute(query, *params)
    
    @staticmethod
    async def add_task_file(
        task_id: str,
        file_type: str,
        file_name: str,
        file_path: str,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None
    ):
        """
        添加任务文件记录
        
        Args:
            task_id: 任务ID
            file_type: 文件类型
            file_name: 文件名
            file_path: 文件路径
            file_size: 文件大小
            mime_type: MIME类型
        """
        query = """
            INSERT INTO task_files (task_id, file_type, file_name, file_path, file_size, mime_type)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (task_id, file_type)
            DO UPDATE SET
                file_name = EXCLUDED.file_name,
                file_path = EXCLUDED.file_path,
                file_size = EXCLUDED.file_size,
                mime_type = EXCLUDED.mime_type,
                created_at = CURRENT_TIMESTAMP
        """
        
        await db.execute(query, task_id, file_type, file_name, file_path, file_size, mime_type)
    
    @staticmethod
    async def add_task_log(
        task_id: str,
        level: str,
        message: str
    ):
        """
        添加任务日志
        
        Args:
            task_id: 任务ID
            level: 日志级别
            message: 日志消息
        """
        query = """
            INSERT INTO task_logs (task_id, level, message)
            VALUES ($1, $2, $3)
        """
        
        await db.execute(query, task_id, level, message)
    
    @staticmethod
    async def get_task_logs(task_id: str, limit: int = 100) -> List[TaskLog]:
        """
        获取任务日志
        
        Args:
            task_id: 任务ID
            limit: 返回数量限制
        
        Returns:
            日志列表
        """
        query = """
            SELECT level, message, created_at
            FROM task_logs
            WHERE task_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        
        rows = await db.fetch(query, task_id, limit)
        return [TaskLog(**dict(row)) for row in rows]
    
    @staticmethod
    async def delete_task(task_id: str):
        """
        删除任务（会级联删除文件记录和日志）
        
        Args:
            task_id: 任务ID
        """
        query = "DELETE FROM tasks WHERE task_id = $1"
        await db.execute(query, task_id)
    
    @staticmethod
    async def get_task_stats() -> TaskStats:
        """
        获取任务统计信息
        
        Returns:
            任务统计
        """
        query = """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'pending') as pending,
                COUNT(*) FILTER (WHERE status = 'processing') as processing,
                COUNT(*) FILTER (WHERE status = 'completed') as completed,
                COUNT(*) FILTER (WHERE status = 'failed') as failed,
                COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled
            FROM tasks
        """
        
        row = await db.fetchrow(query)
        return TaskStats(**dict(row))
    
    @staticmethod
    async def cleanup_old_tasks(hours: int = 24) -> int:
        """
        清理旧任务
        
        Args:
            hours: 清理多少小时前的任务
        
        Returns:
            删除的任务数量
        """
        query = """
            DELETE FROM tasks
            WHERE created_at < $1
            AND status IN ('completed', 'failed', 'cancelled')
        """
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        result = await db.execute(query, cutoff_time)
        
        # 从 'DELETE N' 中提取数字
        deleted_count = int(result.split()[-1]) if result else 0
        return deleted_count
    
    @staticmethod
    async def cancel_task(task_id: str):
        """
        取消任务
        
        Args:
            task_id: 任务ID
        """
        await TaskService.update_task_status(
            task_id,
            TaskStatus.CANCELLED,
            progress='任务已取消',
            progress_percentage=0
        )


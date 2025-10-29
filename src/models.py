#!/usr/bin/env python3
"""
数据库模型和 Pydantic 模型
"""

from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileType(str, Enum):
    """文件类型枚举"""
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLES = "subtitles"
    VIDEO_WITH_SUBS = "video_with_subs"


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
    burn_subtitles: bool = Field(True, description="是否烧录字幕到视频")
    video_quality: str = Field("bestvideo[height<=480]+bestaudio/best[height<=480]", description="视频质量")
    audio_quality: str = Field("192K", description="音频质量")
    max_retries: int = Field(3, description="最大重试次数")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """验证 URL 不能为空"""
        if not v or not v.strip():
            raise ValueError('URL 不能为空')
        if 'youtube.com/watch' not in v and 'youtu.be/' not in v:
            raise ValueError('请提供有效的 YouTube URL')
        return v.strip()
    
    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time(cls, v, info):
        """验证时间不能为空"""
        if not v or not v.strip():
            raise ValueError(f'{info.field_name} 不能为空')
        return v.strip()
    
    @field_validator('proxy')
    @classmethod
    def validate_proxy(cls, v):
        """验证代理地址"""
        if v and v.strip():
            return v.strip()
        return None


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str
    status: TaskStatus
    message: str
    created_at: datetime


class TaskFile(BaseModel):
    """任务文件模型"""
    file_type: str
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: str = 'completed'  # pending, processing, completed, failed
    error_message: Optional[str] = None
    created_at: datetime


class TaskLog(BaseModel):
    """任务日志模型"""
    level: str
    message: str
    created_at: datetime


class TaskDetail(BaseModel):
    """任务详情模型"""
    task_id: str
    status: TaskStatus
    url: str
    video_id: Optional[str] = None
    video_title: Optional[str] = None
    
    # 任务配置
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    proxy: Optional[str] = None
    subtitle_langs: Optional[str] = None
    download_video: bool = True
    download_audio: bool = True
    download_subtitles: bool = True
    burn_subtitles: bool = True
    video_quality: Optional[str] = None
    audio_quality: Optional[str] = None
    max_retries: int = 3
    
    # 任务进度
    progress: Optional[str] = None
    progress_percentage: int = 0
    current_step: Optional[str] = None
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 错误信息
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    
    # 文件信息
    files: List[TaskFile] = []
    
    # 元数据
    metadata: Dict = {}


class TaskList(BaseModel):
    """任务列表模型"""
    task_id: str
    status: TaskStatus
    url: str
    video_id: Optional[str] = None
    video_title: Optional[str] = None
    progress: Optional[str] = None
    progress_percentage: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    download_video: bool = True
    download_audio: bool = True
    download_subtitles: bool = True


class TaskListResponse(BaseModel):
    """任务列表响应模型（带分页）"""
    tasks: List[TaskList]
    total: int
    limit: int
    offset: int


class TaskStats(BaseModel):
    """任务统计模型"""
    total: int = 0
    pending: int = 0
    processing: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0


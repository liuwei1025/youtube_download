-- 初始化数据库脚本
-- 创建任务表

-- 设置时区
SET timezone = 'Asia/Shanghai';

-- 创建任务状态枚举类型
DO $$ BEGIN
    CREATE TYPE task_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 创建任务表
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255) UNIQUE NOT NULL,
    status task_status NOT NULL DEFAULT 'pending',
    url TEXT NOT NULL,
    video_id VARCHAR(255),
    video_title TEXT,
    
    -- 任务配置
    start_time VARCHAR(50),
    end_time VARCHAR(50),
    proxy TEXT,
    subtitle_langs VARCHAR(255),
    download_video BOOLEAN DEFAULT TRUE,
    download_audio BOOLEAN DEFAULT TRUE,
    download_subtitles BOOLEAN DEFAULT TRUE,
    burn_subtitles BOOLEAN DEFAULT TRUE,
    video_quality VARCHAR(100),
    audio_quality VARCHAR(50),
    max_retries INTEGER DEFAULT 3,
    
    -- 任务进度
    progress VARCHAR(255),
    progress_percentage INTEGER DEFAULT 0,
    current_step VARCHAR(255),
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- 错误信息
    error_message TEXT,
    error_trace TEXT,
    
    -- 其他信息
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 创建任务文件表
CREATE TABLE IF NOT EXISTS task_files (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    file_type VARCHAR(50) NOT NULL, -- video, audio, subtitles, video_with_subs
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(task_id, file_type)
);

-- 创建任务日志表
CREATE TABLE IF NOT EXISTS task_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL, -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_video_id ON tasks(video_id);
CREATE INDEX IF NOT EXISTS idx_task_files_task_id ON task_files(task_id);
CREATE INDEX IF NOT EXISTS idx_task_logs_task_id ON task_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_task_logs_created_at ON task_logs(created_at DESC);

-- 创建更新时间戳触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入一些测试注释
COMMENT ON TABLE tasks IS '任务主表，存储所有下载任务的信息';
COMMENT ON TABLE task_files IS '任务文件表，存储每个任务生成的文件信息';
COMMENT ON TABLE task_logs IS '任务日志表，存储任务执行过程中的日志';

-- 创建清理旧任务的函数
CREATE OR REPLACE FUNCTION cleanup_old_tasks(hours_old INTEGER DEFAULT 24)
RETURNS TABLE(deleted_count INTEGER) AS $$
DECLARE
    deleted INTEGER;
BEGIN
    DELETE FROM tasks
    WHERE created_at < CURRENT_TIMESTAMP - (hours_old || ' hours')::INTERVAL
    AND status IN ('completed', 'failed', 'cancelled');
    
    GET DIAGNOSTICS deleted = ROW_COUNT;
    RETURN QUERY SELECT deleted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_tasks IS '清理指定小时数之前的已完成、失败或取消的任务';


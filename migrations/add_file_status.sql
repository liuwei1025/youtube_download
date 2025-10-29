-- 添加文件状态字段
-- 执行日期: 2025-10-29

-- 创建文件状态枚举类型
DO $$ BEGIN
    CREATE TYPE file_status AS ENUM ('pending', 'processing', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 添加status列到task_files表
ALTER TABLE task_files 
ADD COLUMN IF NOT EXISTS status file_status DEFAULT 'completed';

-- 添加error_message列
ALTER TABLE task_files 
ADD COLUMN IF NOT EXISTS error_message TEXT;

-- 为已存在的记录设置状态为completed
UPDATE task_files SET status = 'completed' WHERE status IS NULL;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_task_files_status ON task_files(status);

COMMENT ON COLUMN task_files.status IS '文件状态: pending-等待, processing-处理中, completed-已完成, failed-失败';
COMMENT ON COLUMN task_files.error_message IS '文件下载失败时的错误信息';


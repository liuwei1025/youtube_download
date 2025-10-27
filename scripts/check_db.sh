#!/bin/bash
# 数据库健康检查脚本

echo "🔍 检查数据库状态..."
echo ""

# 检查容器是否运行
echo "1️⃣ 检查 PostgreSQL 容器..."
if docker ps | grep -q youtube-postgres; then
    echo "✅ PostgreSQL 容器运行中"
else
    echo "❌ PostgreSQL 容器未运行"
    exit 1
fi

echo ""

# 检查数据库连接
echo "2️⃣ 检查数据库连接..."
if docker exec youtube-postgres pg_isready -U youtube -d youtube_tasks > /dev/null 2>&1; then
    echo "✅ 数据库连接正常"
else
    echo "❌ 数据库连接失败"
    exit 1
fi

echo ""

# 查询任务统计
echo "3️⃣ 查询任务统计..."
docker exec youtube-postgres psql -U youtube -d youtube_tasks -c "
    SELECT 
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE status = 'pending') as pending,
        COUNT(*) FILTER (WHERE status = 'processing') as processing,
        COUNT(*) FILTER (WHERE status = 'completed') as completed,
        COUNT(*) FILTER (WHERE status = 'failed') as failed,
        COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled
    FROM tasks;
"

echo ""

# 查询最近的任务
echo "4️⃣ 最近的任务 (前5条)..."
docker exec youtube-postgres psql -U youtube -d youtube_tasks -c "
    SELECT 
        task_id,
        status,
        SUBSTRING(url, 1, 50) as url,
        progress_percentage,
        created_at
    FROM tasks
    ORDER BY created_at DESC
    LIMIT 5;
"

echo ""

# 查询数据库大小
echo "5️⃣ 数据库大小..."
docker exec youtube-postgres psql -U youtube -d youtube_tasks -c "
    SELECT 
        pg_size_pretty(pg_database_size('youtube_tasks')) as database_size;
"

echo ""
echo "✨ 检查完成！"


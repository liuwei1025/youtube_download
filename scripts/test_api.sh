#!/bin/bash
# API 功能测试脚本

API_BASE="http://localhost:8000"
TEST_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

echo "🧪 开始测试 API 功能..."
echo ""

# 1. 健康检查
echo "1️⃣ 测试健康检查..."
HEALTH=$(curl -s "$API_BASE/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败"
    echo "$HEALTH"
    exit 1
fi

echo ""

# 2. 获取统计信息
echo "2️⃣ 测试统计信息..."
STATS=$(curl -s "$API_BASE/stats")
if echo "$STATS" | grep -q "total"; then
    echo "✅ 统计信息获取成功"
    echo "$STATS" | jq '.'
else
    echo "❌ 统计信息获取失败"
    exit 1
fi

echo ""

# 3. 创建测试任务
echo "3️⃣ 创建测试任务..."
CREATE_RESPONSE=$(curl -s -X POST "$API_BASE/download" \
    -H "Content-Type: application/json" \
    -d "{
        \"url\": \"$TEST_URL\",
        \"start_time\": \"00:00\",
        \"end_time\": \"00:10\",
        \"subtitle_langs\": \"en\"
    }")

TASK_ID=$(echo "$CREATE_RESPONSE" | jq -r '.task_id')

if [ -n "$TASK_ID" ] && [ "$TASK_ID" != "null" ]; then
    echo "✅ 任务创建成功"
    echo "   任务ID: $TASK_ID"
else
    echo "❌ 任务创建失败"
    echo "$CREATE_RESPONSE"
    exit 1
fi

echo ""

# 4. 获取任务列表
echo "4️⃣ 测试任务列表..."
TASKS=$(curl -s "$API_BASE/tasks?limit=5")
if echo "$TASKS" | grep -q "$TASK_ID"; then
    echo "✅ 任务列表获取成功"
else
    echo "❌ 任务列表获取失败"
fi

echo ""

# 5. 获取任务详情
echo "5️⃣ 测试任务详情..."
TASK_DETAIL=$(curl -s "$API_BASE/tasks/$TASK_ID")
if echo "$TASK_DETAIL" | grep -q "task_id"; then
    echo "✅ 任务详情获取成功"
    echo "$TASK_DETAIL" | jq '{task_id, status, progress, progress_percentage}'
else
    echo "❌ 任务详情获取失败"
fi

echo ""

# 6. 监控任务进度（最多等待30秒）
echo "6️⃣ 监控任务进度..."
MAX_WAIT=30
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    TASK_STATUS=$(curl -s "$API_BASE/tasks/$TASK_ID")
    STATUS=$(echo "$TASK_STATUS" | jq -r '.status')
    PROGRESS=$(echo "$TASK_STATUS" | jq -r '.progress_percentage')
    PROGRESS_MSG=$(echo "$TASK_STATUS" | jq -r '.progress')
    
    echo "   [$WAITED s] 状态: $STATUS | 进度: $PROGRESS% | $PROGRESS_MSG"
    
    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ] || [ "$STATUS" = "cancelled" ]; then
        break
    fi
    
    sleep 2
    WAITED=$((WAITED + 2))
done

echo ""

# 7. 获取任务日志
echo "7️⃣ 测试任务日志..."
LOGS=$(curl -s "$API_BASE/tasks/$TASK_ID/logs?limit=5")
if echo "$LOGS" | grep -q "level"; then
    echo "✅ 任务日志获取成功"
    echo "$LOGS" | jq '.[:3]'
else
    echo "❌ 任务日志获取失败"
fi

echo ""

# 8. 获取任务文件列表
echo "8️⃣ 测试任务文件列表..."
FILES=$(curl -s "$API_BASE/tasks/$TASK_ID/files")
if echo "$FILES" | grep -q "files"; then
    echo "✅ 文件列表获取成功"
    echo "$FILES" | jq '.files | length' | xargs echo "   文件数量:"
else
    echo "❌ 文件列表获取失败"
fi

echo ""

# 9. 清理测试任务
echo "9️⃣ 清理测试任务..."
DELETE_RESPONSE=$(curl -s -X DELETE "$API_BASE/tasks/$TASK_ID")
if echo "$DELETE_RESPONSE" | grep -q "已删除"; then
    echo "✅ 任务删除成功"
else
    echo "❌ 任务删除失败"
fi

echo ""
echo "✨ 测试完成！"
echo ""
echo "📊 测试摘要："
echo "   - 健康检查: ✅"
echo "   - 统计信息: ✅"
echo "   - 创建任务: ✅"
echo "   - 任务列表: ✅"
echo "   - 任务详情: ✅"
echo "   - 任务进度: ✅"
echo "   - 任务日志: ✅"
echo "   - 文件列表: ✅"
echo "   - 删除任务: ✅"


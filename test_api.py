#!/usr/bin/env python3
"""
API 测试脚本
用于测试 YouTube 下载器 API 的各个端点
"""

import requests
import time
import sys
import json

# 配置
BASE_URL = "http://localhost:8000"  # 本地测试，部署后改为 Railway URL

def test_health():
    """测试健康检查端点"""
    print("\n🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ 服务健康: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_root():
    """测试根路径"""
    print("\n🔍 测试根路径...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ API 信息: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
        return False

def test_create_task():
    """测试创建下载任务"""
    print("\n🔍 测试创建下载任务...")
    try:
        # 使用一个短视频进行测试
        payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "start_time": "0:10",
            "end_time": "0:20",
            "download_video": True,
            "download_audio": True,
            "download_subtitles": False,
            "video_quality": "best[height<=360]",
            "max_retries": 2
        }
        
        response = requests.post(
            f"{BASE_URL}/download",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        task_id = data.get("task_id")
        print(f"✅ 任务创建成功!")
        print(f"   任务ID: {task_id}")
        print(f"   状态: {data.get('status')}")
        print(f"   创建时间: {data.get('created_at')}")
        
        return task_id
    except Exception as e:
        print(f"❌ 创建任务失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   响应内容: {e.response.text}")
        return None

def test_task_status(task_id):
    """测试查询任务状态"""
    print(f"\n🔍 测试查询任务状态 (ID: {task_id})...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/{task_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ 任务状态:")
        print(f"   状态: {data.get('status')}")
        print(f"   URL: {data.get('url')}")
        print(f"   视频ID: {data.get('video_id')}")
        print(f"   进度: {data.get('progress')}")
        
        if data.get('error'):
            print(f"   错误: {data.get('error')}")
        
        if data.get('files'):
            print(f"   文件: {json.dumps(data.get('files'), indent=4, ensure_ascii=False)}")
        
        return data.get('status')
    except Exception as e:
        print(f"❌ 查询任务状态失败: {e}")
        return None

def test_list_tasks():
    """测试获取任务列表"""
    print("\n🔍 测试获取任务列表...")
    try:
        response = requests.get(f"{BASE_URL}/tasks", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ 任务列表 (共 {len(data)} 个任务):")
        for task in data[:5]:  # 只显示前5个
            print(f"   - {task.get('task_id')[:8]}... | {task.get('status')} | {task.get('url')}")
        
        return True
    except Exception as e:
        print(f"❌ 获取任务列表失败: {e}")
        return False

def wait_for_completion(task_id, max_wait=300):
    """等待任务完成"""
    print(f"\n⏳ 等待任务完成 (最多等待 {max_wait} 秒)...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        status = test_task_status(task_id)
        
        if status == "completed":
            print("\n✅ 任务已完成！")
            return True
        elif status == "failed":
            print("\n❌ 任务失败！")
            return False
        
        print(f"   等待中... ({int(time.time() - start_time)}秒)")
        time.sleep(5)
    
    print(f"\n⚠️ 等待超时 ({max_wait}秒)")
    return False

def test_download_file(task_id, file_type="video"):
    """测试下载文件"""
    print(f"\n🔍 测试下载文件 (类型: {file_type})...")
    try:
        response = requests.get(
            f"{BASE_URL}/tasks/{task_id}/files/{file_type}",
            timeout=60,
            stream=True
        )
        response.raise_for_status()
        
        # 获取文件名
        content_disp = response.headers.get('content-disposition', '')
        filename = f"test_download_{file_type}.mp4"
        if 'filename=' in content_disp:
            filename = content_disp.split('filename=')[1].strip('"')
        
        # 保存文件
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 文件下载成功: {filename}")
        return True
    except Exception as e:
        print(f"❌ 下载文件失败: {e}")
        return False

def test_delete_task(task_id):
    """测试删除任务"""
    print(f"\n🔍 测试删除任务 (ID: {task_id})...")
    try:
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ 任务删除成功: {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ 删除任务失败: {e}")
        return False

def run_full_test():
    """运行完整测试流程"""
    print("=" * 60)
    print("🚀 YouTube 下载器 API 测试")
    print("=" * 60)
    
    # 1. 健康检查
    if not test_health():
        print("\n❌ 服务未运行或无法访问")
        print("   请确保服务已启动: python app.py")
        sys.exit(1)
    
    # 2. 根路径测试
    test_root()
    
    # 3. 创建任务
    task_id = test_create_task()
    if not task_id:
        print("\n❌ 无法创建任务，测试中止")
        sys.exit(1)
    
    # 4. 查询任务列表
    test_list_tasks()
    
    # 5. 等待任务完成
    if wait_for_completion(task_id, max_wait=180):
        # 6. 下载文件
        test_download_file(task_id, "video")
        test_download_file(task_id, "audio")
    
    # 7. 删除任务
    test_delete_task(task_id)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

def run_quick_test():
    """快速测试（不等待下载完成）"""
    print("=" * 60)
    print("🚀 YouTube 下载器 API 快速测试")
    print("=" * 60)
    
    # 健康检查
    if not test_health():
        print("\n❌ 服务未运行")
        sys.exit(1)
    
    # 根路径
    test_root()
    
    # 创建任务
    task_id = test_create_task()
    if task_id:
        # 查询一次状态
        time.sleep(2)
        test_task_status(task_id)
        
        print(f"\n💡 任务已创建，ID: {task_id}")
        print(f"   可以手动查询状态: curl {BASE_URL}/tasks/{task_id}")
    
    # 列出所有任务
    test_list_tasks()
    
    print("\n" + "=" * 60)
    print("✅ 快速测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="API 测试脚本")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API 基础 URL (默认: http://localhost:8000)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="快速测试模式（不等待下载完成）"
    )
    parser.add_argument(
        "--task-id",
        help="测试特定任务ID的状态"
    )
    
    args = parser.parse_args()
    BASE_URL = args.url.rstrip('/')
    
    print(f"📡 测试 API: {BASE_URL}\n")
    
    try:
        if args.task_id:
            # 测试特定任务
            test_task_status(args.task_id)
        elif args.quick:
            # 快速测试
            run_quick_test()
        else:
            # 完整测试
            run_full_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

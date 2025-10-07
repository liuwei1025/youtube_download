# 快速开始指南

5 分钟上手 YouTube 下载器 API 服务！

## 📝 前置要求

- Python 3.8+
- ffmpeg（用于视频处理）
- yt-dlp（会自动安装）

## 🚀 方式一：本地运行（推荐新手）

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/youtube_download.git
cd youtube_download
```

### 2. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 ffmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows: 从 https://ffmpeg.org/download.html 下载
```

### 3. 启动服务

```bash
# 使用启动脚本（推荐）
./run_server.sh

# 或者直接运行
python app.py
```

服务将在 `http://localhost:8000` 启动

### 4. 测试服务

打开浏览器访问：http://localhost:8000/docs

或使用命令行测试：
```bash
# 快速测试
python test_api.py --quick

# 完整测试
python test_api.py
```

### 5. 创建第一个下载任务

```bash
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "0:10",
    "end_time": "0:20",
    "download_video": true,
    "download_audio": true,
    "download_subtitles": false
  }'
```

你会得到类似这样的响应：
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "任务已创建，正在处理中",
  "created_at": "2025-10-07T12:34:56.789012"
}
```

### 6. 查询任务状态

```bash
# 替换 YOUR_TASK_ID 为上面返回的 task_id
curl "http://localhost:8000/tasks/YOUR_TASK_ID"
```

### 7. 下载完成的文件

```bash
# 下载视频
curl -O "http://localhost:8000/tasks/YOUR_TASK_ID/files/video"

# 下载音频
curl -O "http://localhost:8000/tasks/YOUR_TASK_ID/files/audio"
```

## ☁️ 方式二：部署到 Railway（推荐生产环境）

### 1. Fork 本仓库

访问 GitHub 并 Fork 此仓库到你的账号

### 2. 登录 Railway

访问 [Railway.com](https://railway.com/) 并使用 GitHub 登录

### 3. 创建新项目

1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择你 Fork 的 `youtube_download` 仓库
4. 等待部署完成（约 2-5 分钟）

### 4. 生成域名

1. 进入服务设置
2. 点击 "Generate Domain"
3. 获得你的 API 地址，如：`your-app.up.railway.app`

### 5. 测试部署的服务

```bash
# 访问 API 文档
https://your-app.up.railway.app/docs

# 创建下载任务
curl -X POST "https://your-app.up.railway.app/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": "0:10",
    "end_time": "0:20"
  }'
```

## 🐍 Python 客户端示例

创建一个 `client.py` 文件：

```python
import requests
import time

class YouTubeDownloaderClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def create_task(self, url, start_time, end_time, **kwargs):
        """创建下载任务"""
        payload = {
            "url": url,
            "start_time": start_time,
            "end_time": end_time,
            **kwargs
        }
        response = requests.post(
            f"{self.base_url}/download",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        response = requests.get(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, task_id, timeout=300):
        """等待任务完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(f"任务失败: {status.get('error')}")
            time.sleep(5)
        raise TimeoutError("等待任务完成超时")
    
    def download_file(self, task_id, file_type, output_path):
        """下载文件"""
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}/files/{file_type}",
            stream=True
        )
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path

# 使用示例
if __name__ == "__main__":
    client = YouTubeDownloaderClient()
    
    # 创建任务
    task = client.create_task(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        start_time="0:10",
        end_time="0:20",
        download_video=True,
        download_audio=True
    )
    
    print(f"任务已创建: {task['task_id']}")
    
    # 等待完成
    result = client.wait_for_completion(task['task_id'])
    print(f"任务完成! 文件: {result['files']}")
    
    # 下载文件
    client.download_file(task['task_id'], 'video', 'output_video.mp4')
    client.download_file(task['task_id'], 'audio', 'output_audio.mp3')
    
    print("文件下载完成!")
```

## 🌐 JavaScript/Node.js 示例

```javascript
const axios = require('axios');
const fs = require('fs');

class YouTubeDownloaderClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.client = axios.create({ baseURL });
    }

    async createTask(url, startTime, endTime, options = {}) {
        const response = await this.client.post('/download', {
            url,
            start_time: startTime,
            end_time: endTime,
            ...options
        });
        return response.data;
    }

    async getTaskStatus(taskId) {
        const response = await this.client.get(`/tasks/${taskId}`);
        return response.data;
    }

    async waitForCompletion(taskId, timeout = 300000) {
        const startTime = Date.now();
        while (Date.now() - startTime < timeout) {
            const status = await this.getTaskStatus(taskId);
            
            if (status.status === 'completed') {
                return status;
            } else if (status.status === 'failed') {
                throw new Error(`任务失败: ${status.error}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
        throw new Error('等待任务完成超时');
    }

    async downloadFile(taskId, fileType, outputPath) {
        const response = await this.client.get(
            `/tasks/${taskId}/files/${fileType}`,
            { responseType: 'stream' }
        );
        
        const writer = fs.createWriteStream(outputPath);
        response.data.pipe(writer);
        
        return new Promise((resolve, reject) => {
            writer.on('finish', resolve);
            writer.on('error', reject);
        });
    }
}

// 使用示例
(async () => {
    const client = new YouTubeDownloaderClient();
    
    try {
        // 创建任务
        const task = await client.createTask(
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            '0:10',
            '0:20',
            {
                download_video: true,
                download_audio: true
            }
        );
        
        console.log(`任务已创建: ${task.task_id}`);
        
        // 等待完成
        const result = await client.waitForCompletion(task.task_id);
        console.log(`任务完成! 文件:`, result.files);
        
        // 下载文件
        await client.downloadFile(task.task_id, 'video', 'output_video.mp4');
        await client.downloadFile(task.task_id, 'audio', 'output_audio.mp3');
        
        console.log('文件下载完成!');
    } catch (error) {
        console.error('错误:', error.message);
    }
})();
```

## ❓ 常见问题

### Q: 启动失败，提示 "Address already in use"
A: 端口 8000 已被占用，可以指定其他端口：
```bash
PORT=8001 python app.py
```

### Q: 下载失败，提示 "unable to download"
A: 可能需要配置代理：
```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
python app.py
```

或在请求中指定：
```json
{
  "url": "...",
  "start_time": "1:00",
  "end_time": "2:00",
  "proxy": "http://127.0.0.1:7890"
}
```

### Q: Railway 部署失败
A: 检查以下几点：
1. 确保 `Dockerfile` 和 `railway.json` 存在
2. 查看 Railway 的构建日志
3. 确认 GitHub 仓库权限正确

### Q: 任务一直处于 processing 状态
A: 可能的原因：
1. 视频片段较长，需要更多时间
2. 网络问题导致下载缓慢
3. 查看服务器日志了解详情

## 📚 下一步

- 📖 阅读 [完整 API 文档](docs/API_REFERENCE.md)
- 🚀 查看 [部署指南](docs/DEPLOYMENT.md)
- 🛠️ 了解 [高级配置](docs/README.md)

## 🆘 获取帮助

如果遇到问题：
1. 查看 [API 文档](docs/API_REFERENCE.md)
2. 搜索 GitHub Issues
3. 提交新的 Issue

---

**祝使用愉快！** 🎉

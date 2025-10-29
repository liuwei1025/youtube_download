# Cookies 工具完整使用指南

## 🎯 快速开始

### 测试当前 Cookies 是否有效

```bash
./scripts/test_cookies.sh
```

### 更新 Cookies

```bash
./scripts/update_cookies.sh
```

---

## 📋 工具说明

### 1. `test_cookies.sh` - Cookies 测试工具

**功能**：
- ✅ 检查 cookies 文件是否存在
- ✅ 验证文件格式
- ✅ 显示文件信息（大小、修改时间、cookie 数量）
- ✅ 实际测试下载功能

**使用场景**：
- 遇到下载错误时，先运行此工具确认 cookies 是否有效
- 定期检查 cookies 状态
- 更新 cookies 后验证是否成功

**示例输出**：
```bash
$ ./scripts/test_cookies.sh

🧪 YouTube Cookies 测试工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 检查文件格式...
✅ 文件格式正确

📊 文件信息:
   路径: /Users/liuwei/Github/youtube/cookies/Cookies
   大小: 2736 字节
   修改时间: 2025-10-28 22:28:14
   Cookie 数量: 23

🐳 检查 Docker 服务...

🧪 测试 Cookies 有效性...
   测试视频: https://www.youtube.com/watch?v=jNQXAC9IVRw

✅ Cookies 验证成功！

📺 测试结果:
Learn Italian with Lucrezia

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 测试完成！Cookies 工作正常
```

---

### 2. `update_cookies.sh` - Cookies 更新工具

**功能**：
- ✅ 自动备份旧 cookies
- ✅ 智能检测最近更新的文件
- ✅ 验证文件格式
- ✅ 测试新 cookies 是否有效
- ✅ 自动重启 Docker 服务

**使用场景**：
- 出现 "Sign in to confirm you're not a bot" 错误
- Cookies 过期需要更新
- 定期维护（建议每月一次）

**两种更新方式**：

#### 方式 1：直接覆盖（推荐）

1. 使用浏览器扩展导出 cookies 时，直接保存为：
   ```
   /Users/liuwei/Github/youtube/cookies/Cookies
   ```

2. 运行更新脚本：
   ```bash
   ./scripts/update_cookies.sh
   ```

3. 选择 **选项 1**

#### 方式 2：从其他位置复制

1. 将 cookies 导出到下载文件夹
2. 运行更新脚本
3. 选择 **选项 2**，然后输入文件路径

**示例流程**：
```bash
$ ./scripts/update_cookies.sh

🔧 YouTube Cookies 更新工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 发现现有 cookies 文件
   位置: /Users/liuwei/Github/youtube/cookies/Cookies
✅ 已备份到: /Users/liuwei/Github/youtube/cookies/Cookies.backup.20251028_220000

📋 请按照以下步骤操作：

1️⃣  安装浏览器扩展（选择其中一个）：
   • Chrome/Edge: 'Get cookies.txt LOCALLY'
   • Firefox: 'cookies.txt'

2️⃣  在浏览器中：
   • 访问 https://www.youtube.com
   • 确保已登录您的账户
   • 点击扩展图标
   • 导出 cookies（选择 Netscape 格式）

3️⃣  保存文件：
   • 直接保存到: /Users/liuwei/Github/youtube/cookies/Cookies
   • 或保存到下载文件夹，稍后指定路径

✅ 检测到 cookies 文件刚刚更新（5秒前）
是否使用此文件？(Y/n): y

✅ 使用当前 Cookies 文件

🧪 测试 cookies 是否有效...
✅ Cookies 验证成功！

🔄 是否重启 Docker 服务以应用更改？(Y/n): y
🔄 重启服务中...
✅ 服务已重启

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Cookies 更新完成！
```

---

## 🔧 常见错误处理

### 错误 1: "Sign in to confirm you're not a bot"

**原因**：Cookies 已失效或未配置

**解决**：
```bash
./scripts/update_cookies.sh
```

### 错误 2: "HTTP Error 429: Too Many Requests"

**原因**：请求频率过高

**解决**：
1. 等待 15-30 分钟
2. 然后重试下载

### 错误 3: Cookies 验证失败

**原因**：
- 未在浏览器中登录 YouTube
- Cookies 文件格式错误
- Cookies 已过期

**解决**：
1. 确保浏览器中已登录 YouTube
2. 重新导出 cookies（使用正确的扩展）
3. 再次运行更新脚本

---

## 📂 文件位置

### Cookies 文件
```
/Users/liuwei/Github/youtube/cookies/Cookies
```

### 备份文件
```
/Users/liuwei/Github/youtube/cookies/Cookies.backup.YYYYMMDD_HHMMSS
```

可以定期清理旧的备份文件：
```bash
# 查看所有备份
ls -lh cookies/Cookies.backup.*

# 删除旧备份（保留最近 3 个）
ls -t cookies/Cookies.backup.* | tail -n +4 | xargs rm -f
```

---

## 🔒 安全提示

1. **不要提交到 Git**
   - `cookies/` 目录已在 `.gitignore` 中
   - 包含您的登录信息

2. **不要分享**
   - Cookies 文件相当于您的 YouTube 登录凭证
   - 分享给他人相当于分享账号密码

3. **定期更新**
   - 建议每月更新一次
   - 出现认证错误时立即更新

---

## 📚 相关文档

- 📖 [COOKIES_快速更新.md](./COOKIES_快速更新.md) - 快速上手指南
- 📖 [COOKIES_问题解决.md](./COOKIES_问题解决.md) - 详细问题排查
- 📖 [UPDATE_COOKIES_GUIDE.md](./UPDATE_COOKIES_GUIDE.md) - 英文完整指南
- 📖 [cookies/README.md](./cookies/README.md) - Cookies 目录说明

---

## ⚡ 快速命令参考

```bash
# 测试 cookies
./scripts/test_cookies.sh

# 更新 cookies
./scripts/update_cookies.sh

# 检查文件格式
head -1 cookies/Cookies

# 查看 cookie 数量
grep -v '^#' cookies/Cookies | grep -v '^$' | wc -l

# 查看文件修改时间
ls -lh cookies/Cookies

# 手动测试下载
docker exec youtube-dl-api yt-dlp \
  --cookies /app/cookies/Cookies \
  --proxy http://host.docker.internal:7890 \
  --get-title \
  "https://www.youtube.com/watch?v=VIDEO_ID"

# 重启服务
docker-compose restart youtube-dl-api

# 查看服务日志
docker-compose logs -f youtube-dl-api
```

---

## 💡 最佳实践

1. **定期维护**
   - 每月运行一次 `test_cookies.sh`
   - 必要时运行 `update_cookies.sh`

2. **出现错误时**
   - 先运行 `test_cookies.sh` 诊断
   - 如果 cookies 失效，运行 `update_cookies.sh`
   - 如果是 429 错误，等待 15-30 分钟

3. **备份管理**
   - 保留最近 3-5 个备份即可
   - 定期清理旧备份节省空间

4. **浏览器登录**
   - 保持浏览器中 YouTube 登录状态
   - 定期访问 YouTube 确保账户活跃


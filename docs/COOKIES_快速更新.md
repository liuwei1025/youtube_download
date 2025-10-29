# Cookies 快速更新指南

## 🚀 最简单的方法（推荐）

### 第 1 步：安装浏览器扩展

**Chrome/Edge**：
- 安装扩展：[Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

**Firefox**：
- 安装扩展：搜索 "cookies.txt"

### 第 2 步：导出 Cookies

1. 在浏览器中访问：https://www.youtube.com
2. **确保已登录**
3. 点击扩展图标
4. 点击 "Export" / "导出"
5. **保存为**：`/Users/liuwei/Github/youtube/cookies/Cookies`

   > 💡 直接覆盖原文件即可！

### 第 3 步：运行更新脚本

```bash
cd /Users/liuwei/Github/youtube
./scripts/update_cookies.sh
```

然后选择 **选项 1**（使用默认路径）即可。

---

## 📝 详细流程示例

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

💡 提示：
   • Cookies 通常有效期为几周到几个月
   • 如果再次出现认证错误，请重新运行此脚本
   • 不要分享 cookies 文件，它包含您的登录信息
```

---

## 🎯 默认文件路径

```
/Users/liuwei/Github/youtube/cookies/Cookies
```

浏览器扩展导出时，直接选择这个路径，无需再手动复制文件！

---

## ⚡ 其他选项

### 如果保存到了下载文件夹

脚本会提示选择：

```
请选择更新方式：
  1) 我已经导出到 /Users/liuwei/Github/youtube/cookies/Cookies
  2) 我保存在其他位置，需要指定路径

请选择 (1/2): 2
📥 请输入 cookies 文件路径: ~/Downloads/youtube.com_cookies.txt
```

支持 `~` 符号，会自动展开为用户主目录。

---

## 🔍 手动验证

如果想手动验证 cookies 是否有效：

```bash
# 检查文件格式
head -1 cookies/Cookies
# 应该显示: # Netscape HTTP Cookie File

# 测试下载
docker exec youtube-dl-api yt-dlp \
  --cookies /app/cookies/Cookies \
  --proxy http://host.docker.internal:7890 \
  --get-title \
  "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

如果能显示视频标题，说明 cookies 有效！

---

## ❓ 常见问题

**Q: 必须要登录 YouTube 账户吗？**
A: 是的，必须在浏览器中登录后再导出 cookies。

**Q: Cookies 文件可以分享吗？**
A: 不可以！它包含您的登录信息，分享出去相当于把账号给别人。

**Q: 更新后还是失败怎么办？**
A: 
1. 等待 15-30 分钟（可能是 429 限流）
2. 检查浏览器中是否真的已登录
3. 尝试在浏览器中播放一个视频，确认账户正常
4. 重新导出 cookies

**Q: 可以自动化更新 cookies 吗？**
A: 理论上可以，但需要浏览器支持。目前推荐手动更新（几周一次）。


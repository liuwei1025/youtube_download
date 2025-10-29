# Cookies 完整文档索引

## 🎯 快速导航

根据您的需求，选择对应的文档：

---

## 📖 按使用场景

### 🚀 我想快速开始
👉 [COOKIES_快速更新.md](./COOKIES_快速更新.md)
- 最简单的更新流程
- 图文并茂的操作指南
- 适合新手

### ❓ 我遇到了问题
👉 [COOKIES_FAQ.md](./COOKIES_FAQ.md)
- 常见问题快速解答
- 故障排查步骤
- 适合遇到错误时查阅

### 🔧 我想了解工具
👉 [COOKIES_工具使用指南.md](./COOKIES_工具使用指南.md)
- 详细的工具说明
- 完整的命令参考
- 适合系统管理员

### 🔍 我想深入理解原理
👉 [COOKIES_工作原理.md](./COOKIES_工作原理.md)
- 技术实现细节
- 代码流程分析
- 适合开发人员

### 🆘 下载一直失败
👉 [COOKIES_问题解决.md](./COOKIES_问题解决.md)
- 详细的问题诊断
- 多种解决方案
- 应急处理方法

---

## 📋 按文档类型

### 快速指南 ⚡

| 文档 | 内容 | 推荐人群 |
|------|------|---------|
| [COOKIES_快速更新.md](./COOKIES_快速更新.md) | 3 步更新流程 | 所有用户 |
| [COOKIES_FAQ.md](./COOKIES_FAQ.md) | 10 个常见问题 | 所有用户 |
| [cookies/README.md](./cookies/README.md) | 目录说明 | 所有用户 |

### 详细文档 📚

| 文档 | 内容 | 推荐人群 |
|------|------|---------|
| [COOKIES_工具使用指南.md](./COOKIES_工具使用指南.md) | 工具完整说明 | 高级用户 |
| [COOKIES_工作原理.md](./COOKIES_工作原理.md) | 技术实现原理 | 开发人员 |
| [COOKIES_问题解决.md](./COOKIES_问题解决.md) | 问题排查指南 | 运维人员 |
| [UPDATE_COOKIES_GUIDE.md](./UPDATE_COOKIES_GUIDE.md) | 英文完整指南 | 国际用户 |

### 工具脚本 🛠️

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `scripts/test_cookies.sh` | 测试 cookies 有效性 | 定期检查 |
| `scripts/update_cookies.sh` | 更新 cookies（交互式） | 需要更新时 |
| `scripts/verify_cookies_reload.sh` | 验证热更新机制 | 技术验证 |

---

## 🎓 学习路径

### 新手路径

```
1. COOKIES_快速更新.md        ← 开始这里
   ↓
2. 实际操作：更新一次 cookies
   ↓
3. COOKIES_FAQ.md              ← 了解常见问题
   ↓
4. scripts/test_cookies.sh     ← 学会测试
```

### 进阶路径

```
1. COOKIES_工具使用指南.md     ← 系统学习
   ↓
2. COOKIES_工作原理.md         ← 理解原理
   ↓
3. COOKIES_问题解决.md         ← 掌握排查
   ↓
4. 自定义优化
```

---

## 🔑 核心知识点

### 必须了解

- ✅ Cookies 文件路径：`cookies/Cookies`
- ✅ 更新后**无需重启容器**
- ✅ 使用浏览器扩展导出最简单
- ✅ 定期更新（建议每月一次）

### 应该了解

- 📌 Cookies 格式：Netscape HTTP Cookie File
- 📌 测试命令：`./scripts/test_cookies.sh`
- 📌 更新命令：`./scripts/update_cookies.sh`
- 📌 有效期：几周到几个月

### 可以了解

- 🔍 yt-dlp 每次都读取文件内容
- 🔍 文件通过 Docker 卷挂载
- 🔍 使用 `--no-cache-dir` 避免写入
- 🔍 支持热更新的技术原理

---

## 📊 文档关系图

```
COOKIES_文档索引.md (你在这里)
    │
    ├── 快速开始 ────────→ COOKIES_快速更新.md
    │                      └── scripts/update_cookies.sh
    │
    ├── 常见问题 ────────→ COOKIES_FAQ.md
    │                      └── scripts/test_cookies.sh
    │
    ├── 工具使用 ────────→ COOKIES_工具使用指南.md
    │                      ├── scripts/test_cookies.sh
    │                      ├── scripts/update_cookies.sh
    │                      └── scripts/verify_cookies_reload.sh
    │
    ├── 技术原理 ────────→ COOKIES_工作原理.md
    │                      └── src/downloader/
    │
    └── 问题解决 ────────→ COOKIES_问题解决.md
                           └── 各种排查步骤
```

---

## 🎯 应用场景速查

### 场景 1: 首次配置

```
1. 阅读：COOKIES_快速更新.md
2. 执行：./scripts/update_cookies.sh
3. 测试：./scripts/test_cookies.sh
```

### 场景 2: 出现 "Sign in to confirm" 错误

```
1. 阅读：COOKIES_FAQ.md → Q10
2. 执行：./scripts/test_cookies.sh（确认失效）
3. 执行：./scripts/update_cookies.sh（更新）
4. 参考：COOKIES_问题解决.md（如果仍失败）
```

### 场景 3: 定期维护

```
1. 每月执行：./scripts/test_cookies.sh
2. 如果失败：./scripts/update_cookies.sh
3. 记录：cookies 更新时间
```

### 场景 4: 技术研究

```
1. 阅读：COOKIES_工作原理.md
2. 验证：./scripts/verify_cookies_reload.sh
3. 查看：src/downloader/video.py（代码实现）
```

---

## 📝 更新记录

| 日期 | 内容 | 文档 |
|------|------|------|
| 2025-10-28 | 创建完整文档体系 | 所有文档 |
| 2025-10-28 | 优化更新脚本，说明无需重启 | update_cookies.sh |
| 2025-10-28 | 添加验证脚本 | verify_cookies_reload.sh |
| 2025-10-28 | 创建文档索引 | 本文档 |

---

## 💬 获取帮助

### 文档没有解决问题？

1. 查看日志：`docker-compose logs -f youtube-dl-api`
2. 运行诊断：`./scripts/test_cookies.sh`
3. 检查环境：Docker、代理、网络

### 贡献文档

发现错误或有改进建议？欢迎提交 PR！

---

## 🌟 最佳实践总结

1. **定期检查**：每月运行 `test_cookies.sh`
2. **及时更新**：出错时立即更新
3. **保持登录**：浏览器中保持 YouTube 登录
4. **安全保管**：不分享、不提交到 Git
5. **备份文件**：更新前自动备份（脚本已实现）

---

## 🎁 快捷命令

复制粘贴即用：

```bash
# 测试
./scripts/test_cookies.sh

# 更新
./scripts/update_cookies.sh

# 验证热更新
./scripts/verify_cookies_reload.sh

# 查看文件
cat cookies/Cookies | head -5

# 检查修改时间
ls -lh cookies/Cookies

# 查看日志
docker-compose logs --tail 50 youtube-dl-api
```

---

**Happy Downloading! 🎉**


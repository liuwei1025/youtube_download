# Cookies 常见问题 FAQ

## ❓ 常见问题快速解答

### Q1: 每次下载时都会读取 cookies 文件吗？

**A: 是的 ✅**

- Python 代码传递 cookies 文件路径给 yt-dlp
- yt-dlp **每次执行时**都会重新读取文件内容
- 不会缓存 cookies 内容

---

### Q2: 更新 cookies 后需要重启容器吗？

**A: 不需要 ❌**

- Cookies 文件是**动态读取**的
- 更新文件后，下次下载**立即生效**
- 完全**热更新**，零停机时间

---

### Q3: 如何验证 cookies 是否有效？

**A: 运行测试脚本**

```bash
./scripts/test_cookies.sh
```

---

### Q4: 如何更新 cookies？

**A: 三步搞定**

```bash
# 1. 使用浏览器扩展导出到
/Users/liuwei/Github/youtube/cookies/Cookies

# 2. 运行更新脚本
./scripts/update_cookies.sh

# 3. 完成！无需重启
```

---

### Q5: 更新 cookies 后多久生效？

**A: 立即生效**

- 文件更新后，下一次下载就会使用新 cookies
- 正在进行的下载任务使用旧 cookies
- 新任务使用新 cookies

---

### Q6: Cookies 多久过期？

**A: 通常几周到几个月**

- YouTube cookies 有效期不固定
- 出现认证错误时说明已过期
- 建议每月主动更新一次

---

### Q7: 可以不用 cookies 下载吗？

**A: 可以，但限制较多**

- 某些视频需要登录才能访问
- 无 cookies 可能触发"机器人验证"
- 建议配置 cookies 以获得最佳体验

---

### Q8: Cookies 文件在哪里？

**A: 默认路径**

```
/Users/liuwei/Github/youtube/cookies/Cookies
```

在 Docker 容器内：
```
/app/cookies/Cookies
```

---

### Q9: 如何检查文件是否正确？

**A: 查看第一行**

```bash
head -1 cookies/Cookies
```

应该显示：
```
# Netscape HTTP Cookie File
```

---

### Q10: 更新 cookies 但还是失败？

**A: 可能的原因**

1. **429 错误**：等待 15-30 分钟
2. **Cookies 未更新**：确认文件修改时间
3. **未登录 YouTube**：在浏览器中确认已登录
4. **代理问题**：检查代理是否正常

**排查步骤**：
```bash
# 1. 测试 cookies
./scripts/test_cookies.sh

# 2. 检查代理
docker exec youtube-dl-api curl -x http://host.docker.internal:7890 https://www.google.com

# 3. 查看详细日志
docker-compose logs -f youtube-dl-api
```

---

## 🛠️ 工具速查

| 命令 | 用途 |
|------|------|
| `./scripts/test_cookies.sh` | 测试 cookies 是否有效 |
| `./scripts/update_cookies.sh` | 更新 cookies（交互式） |
| `./scripts/verify_cookies_reload.sh` | 验证无需重启即可生效 |

---

## 📚 详细文档

需要更多信息？查看：

- 📖 [COOKIES_工作原理.md](./COOKIES_工作原理.md) - 技术原理详解
- 📖 [COOKIES_工具使用指南.md](./COOKIES_工具使用指南.md) - 完整使用说明
- 📖 [COOKIES_快速更新.md](./COOKIES_快速更新.md) - 快速上手
- 📖 [COOKIES_问题解决.md](./COOKIES_问题解决.md) - 问题排查

---

## 🎯 最重要的三点

1. ✅ **每次下载都会读取最新的 cookies 文件**
2. ✅ **更新 cookies 后无需重启容器**
3. ✅ **使用 `./scripts/update_cookies.sh` 更新最简单**

---

## 💡 快速记忆

```
更新流程：
浏览器导出 → 覆盖文件 → 立即生效 ✨
不需要：重启 ❌ | 刷新 ❌ | 等待 ❌
```


# YouTube 下载器 API 测试套件

## 概述

本测试套件为 YouTube 下载器 API 提供全面的测试覆盖，包括单元测试、集成测试和模块测试。

## 测试结构

```
tests/
├── __init__.py                  # 测试包初始化
├── conftest.py                  # pytest 配置和共享 fixtures
├── test_unit_api.py            # API 单元测试（使用 mock）
├── test_integration_api.py     # API 集成测试（真实下载）
├── test_youtube_downloader.py  # 下载器模块测试
└── README.md                    # 本文件
```

## 快速开始

### 1. 安装测试依赖

```bash
pip install -r requirements.txt
```

或仅安装测试依赖：

```bash
pip install pytest pytest-asyncio pytest-cov httpx pytest-xdist
```

### 2. 运行所有测试

```bash
# 运行所有测试（不包括集成测试）
pytest tests/ -v

# 运行所有测试（包括集成测试）
SKIP_INTEGRATION_TESTS=false pytest tests/ -v
```

## 测试类型

### 单元测试 (test_unit_api.py)

**特点：**
- 使用 mock 模拟外部依赖
- 执行速度快（约2秒）
- 不需要网络连接
- 不需要真实下载

**运行：**
```bash
pytest tests/test_unit_api.py -v
```

**覆盖范围：**
- ✅ 根端点（/ 和 /health）
- ✅ 任务创建（POST /download）
- ✅ 任务管理（GET /tasks, GET /tasks/{id}, DELETE /tasks/{id}）
- ✅ 文件下载（GET /tasks/{id}/files/{type}）
- ✅ 清理功能（POST /cleanup）
- ✅ 错误处理（404, 400, 422）
- ✅ 并发任务

**测试统计：** 22个测试用例

### 集成测试 (test_integration_api.py)

**特点：**
- 使用真实 YouTube URL
- 执行实际下载操作
- 需要网络连接
- 执行时间较长（5-10分钟）

**运行：**
```bash
# 运行集成测试
SKIP_INTEGRATION_TESTS=false pytest tests/test_integration_api.py -v

# 跳过集成测试（默认）
pytest tests/test_integration_api.py -v
```

**测试 URL：** https://www.youtube.com/watch?v=7opHwsmusvE

**覆盖范围：**
- ✅ 完整下载工作流程
- ✅ 仅下载视频
- ✅ 仅下载音频
- ✅ 不同时间范围
- ✅ 无效 URL 处理
- ✅ 并发下载
- ✅ 任务持久性

**测试统计：** 8个测试用例

### 模块测试 (test_youtube_downloader.py)

**特点：**
- 测试核心下载器模块
- 不依赖 API 层
- 执行速度快（< 1秒）

**运行：**
```bash
pytest tests/test_youtube_downloader.py -v
```

**覆盖范围：**
- ✅ 视频 ID 提取（多种 URL 格式）
- ✅ 时间解析（HH:MM:SS, MM:SS, 秒数）
- ✅ 下载配置（DownloadConfig）
- ✅ 目录管理
- ✅ 磁盘空间检查
- ✅ 代理设置
- ✅ 命令执行
- ✅ 文件命名
- ✅ 边缘情况

**测试统计：** 37个测试用例

## 测试命令大全

### 基础命令

```bash
# 运行所有测试
pytest tests/ -v

# 仅运行单元测试
pytest tests/test_unit_api.py -v

# 仅运行模块测试
pytest tests/test_youtube_downloader.py -v

# 运行特定测试类
pytest tests/test_unit_api.py::TestTaskCreation -v

# 运行特定测试方法
pytest tests/test_unit_api.py::TestTaskCreation::test_create_download_task -v
```

### 高级选项

```bash
# 显示详细输出
pytest tests/ -vv

# 简洁输出
pytest tests/ -q

# 显示打印语句
pytest tests/ -s

# 失败时立即停止
pytest tests/ -x

# 显示最慢的10个测试
pytest tests/ --durations=10

# 并行运行测试（需要 pytest-xdist）
pytest tests/ -n auto
```

### 覆盖率报告

```bash
# 生成覆盖率报告
pytest tests/ --cov=app --cov=src --cov-report=html

# 查看报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 过滤和标记

```bash
# 只运行 mock 测试
pytest tests/test_unit_api.py -v

# 只运行真实下载测试
SKIP_INTEGRATION_TESTS=false pytest tests/test_integration_api.py -v

# 运行匹配模式的测试
pytest tests/ -k "download" -v
pytest tests/ -k "not integration" -v
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SKIP_INTEGRATION_TESTS` | 跳过集成测试 | `true` |
| `HTTP_PROXY` | HTTP 代理设置 | - |
| `HTTPS_PROXY` | HTTPS 代理设置 | - |

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run unit tests
        run: |
          pytest tests/test_unit_api.py tests/test_youtube_downloader.py -v --cov=app --cov=src
      - name: Run integration tests (optional)
        if: github.event_name == 'push'
        run: |
          SKIP_INTEGRATION_TESTS=false pytest tests/test_integration_api.py -v
```

## 测试最佳实践

### 1. 运行测试前

```bash
# 确保依赖已安装
pip install -r requirements.txt

# 确保代码没有 lint 错误
# （如果有 linter 工具）
```

### 2. 开发时

```bash
# 使用监视模式（需要 pytest-watch）
ptw tests/ -- -v

# 或使用 nodemon
nodemon --exec "pytest tests/ -v" --ext py
```

### 3. 提交前

```bash
# 运行所有单元测试和模块测试
pytest tests/test_unit_api.py tests/test_youtube_downloader.py -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov=src --cov-report=term-missing
```

### 4. 发布前

```bash
# 运行所有测试（包括集成测试）
SKIP_INTEGRATION_TESTS=false pytest tests/ -v --cov=app --cov=src
```

## 常见问题

### Q: 集成测试失败怎么办？

A: 集成测试依赖网络和真实的 YouTube 服务，可能因为以下原因失败：
- 网络连接问题
- YouTube 服务不可用
- 代理设置不正确
- 测试视频被删除

解决方法：
1. 检查网络连接
2. 设置正确的代理（如需要）
3. 尝试使用其他 YouTube URL

### Q: 如何加快测试速度？

A: 
1. 只运行单元测试：`pytest tests/test_unit_api.py tests/test_youtube_downloader.py`
2. 使用并行测试：`pytest tests/ -n auto`
3. 跳过慢速测试
4. 跳过集成测试

### Q: 测试覆盖率在哪里？

A: 运行以下命令生成覆盖率报告：
```bash
pytest tests/ --cov=app --cov=src --cov-report=html
open htmlcov/index.html
```

### Q: 如何调试失败的测试？

A:
```bash
# 显示完整错误信息
pytest tests/ -vv --tb=long

# 失败时进入 pdb 调试器
pytest tests/ --pdb

# 只运行失败的测试
pytest tests/ --lf
```

## 测试统计摘要

| 测试类型 | 测试用例数 | 执行时间 | 需要网络 |
|---------|-----------|---------|---------|
| 单元测试 | 22 | ~2秒 | ❌ |
| 集成测试 | 8 | ~5-10分钟 | ✅ |
| 模块测试 | 37 | <1秒 | ❌ |
| **总计** | **67** | **~2-10分钟** | **部分需要** |

## 贡献指南

添加新测试时：

1. 根据测试类型选择正确的文件
2. 遵循现有的测试结构和命名约定
3. 使用描述性的测试名称和文档字符串
4. 确保测试独立且可重复
5. 使用合适的 fixtures 和 mock
6. 运行测试确保通过
7. 更新本 README（如有必要）

## 相关文档

- [API 参考文档](../docs/API_REFERENCE.md)
- [项目结构](../docs/PROJECT_STRUCTURE.md)
- [部署指南](../docs/DEPLOYMENT.md)

## 联系方式

如有问题或建议，请提交 issue 或 pull request。


# ============================================
# 阶段 1: 前端构建
# ============================================
FROM node:20-alpine as frontend-builder

WORKDIR /frontend

# 安装 pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# 复制前端项目文件
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
COPY frontend/pnpm-workspace.yaml* ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制前端源代码
COPY frontend/ ./

# 构建前端
RUN pnpm build

# ============================================
# 阶段 2: Python 依赖构建
# ============================================
FROM python:3.11-slim as python-builder

# 设置时区
ENV TZ=Asia/Shanghai

# 安装构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# 阶段 3: 最终镜像
# ============================================
FROM python:3.11-slim

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制 Python 依赖
COPY --from=python-builder /install /usr/local

# 复制应用代码
COPY . .

# 复制前端构建产物
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV COOKIES_FILE=/app/cookies/Cookies

# 创建必要的目录并设置权限
RUN mkdir -p /app/downloads /app/cookies && \
    chmod 777 /app/downloads && \
    chmod +x /app/entrypoint.sh

# 使用非 root 用户运行
RUN useradd -m -u 1000 youtube && \
    chown -R youtube:youtube /app
USER youtube

# 暴露端口
EXPOSE 8000

# 启动应用
ENTRYPOINT ["/app/entrypoint.sh"]

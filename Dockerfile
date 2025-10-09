# 使用多阶段构建减小镜像大小
FROM python:3.9-slim as builder

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

# 最终镜像
FROM python:3.9-slim

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制安装的包
COPY --from=builder /install /usr/local

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 创建下载目录并设置权限
RUN mkdir -p /app/downloads && \
    chmod 777 /app/downloads

# 使用非 root 用户运行
RUN useradd -m -u 1000 youtube && \
    chown -R youtube:youtube /app
USER youtube

# 启动应用
CMD ["python", "app.py"]
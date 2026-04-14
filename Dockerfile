FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends procps curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码（排除 .env 等敏感文件）
COPY . .

# 复制启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 创建数据目录
RUN mkdir -p /data/chroma_db /data/logs

# 设置环境变量
ENV DATA_DIR=/data
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8080

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]

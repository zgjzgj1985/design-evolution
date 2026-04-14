FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码（排除 .env 等敏感文件）
COPY . .

# 创建数据目录（用于 SQLite 和 ChromaDB）
# Sealos 部署时会挂载持久化卷到 /data
RUN mkdir -p /data/chroma_db /data/logs

# 设置数据目录环境变量
ENV DATA_DIR=/data
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8080

# Sealos 需要监听 0.0.0.0
EXPOSE 8080

# 启动命令
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8080"]

#!/bin/bash
set -e

echo "=== 开始安装依赖 ==="
pip install --no-cache-dir -r /app/requirements.txt

echo "=== 创建数据目录 ==="
mkdir -p /data/chroma_db /data/logs

echo "=== 启动 Streamlit ==="
cd /app
exec streamlit run app.py \
    --server.address=0.0.0.0 \
    --server.port=8080 \
    --server.headless=true \
    --browser.serverAddress=localhost \
    --server.enableCORS=false \
    --server.enableXsrfProtection=true
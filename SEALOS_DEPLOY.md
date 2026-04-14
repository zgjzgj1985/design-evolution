# Sealos 部署配置
# 使用方法: sealos run ghcr.io/labring/dockerfile:python-3.11 -e ENV="" -p 8080:8080

# ============================================
# 部署前准备
# ============================================
# 1. 确保代码已推送到 GitHub
# 2. 在 Sealos 创建一个应用
# 3. 配置环境变量（LLM API Key）
# 4. 挂载持久化存储（保存 SQLite 和 ChromaDB 数据）

# ============================================
# Sealos 控制台操作步骤
# ============================================
# 1. 登录 https://cloud.sealos.top
# 2. 点击「应用管理」→「创建应用」
# 3. 填写配置：
#    - 应用名称：design-evolution-archive
#    - 镜像：python:3.11-slim
#    - 容器端口：8080
#    - 启动命令：见下方 "启动命令"
#    - 环境变量：见下方 "环境变量"
#    - 存储：挂载 /data 目录
# 4. 点击部署

# ============================================
# 启动命令（复制到 Sealos 的「启动命令」输入框）
# ============================================
"""
bash -c "pip install --no-cache-dir -r requirements.txt && mkdir -p /data/chroma_db /data/logs && streamlit run app.py --server.address=0.0.0.0 --server.port=8080 --server.headless=true --browser.serverAddress=localhost"
"""

# ============================================
# 必需的环境变量
# ============================================
# OPENAI_API_KEY=你的API密钥
# LLM_PROVIDER=openai  (或 anthropic, openrouter)
# LLM_MODEL=gpt-4o-mini
# PYTHONUNBUFFERED=1

# ============================================
# 持久化存储说明
# ============================================
# Sealos 需要挂载持久化卷来保存数据：
# - /data/game_design.db  (SQLite 数据库)
# - /data/chroma_db/      (ChromaDB 向量数据)
#
# 在 Sealos 控制台：
# 1. 「存储管理」→「创建存储」
# 2. 选择存储类型（建议用 NFS 或 local-path）
# 3. 挂载到应用的 /data 路径

# ============================================
# GitHub 自动部署（可选）
# ============================================
# 如果你想实现 git push 自动部署，需要：
# 1. 在 Sealos 开启「GitHub Actions」集成
# 2. 或使用 CI/CD 流水线构建 Docker 镜像
# 3. 推送到 GitHub Packages / Docker Hub
# 4. Sealos 监听镜像更新自动部署

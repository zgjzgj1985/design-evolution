# Sealos 部署指南

## 前提条件

1. 代码已推送到 GitHub
2. Sealos 账号（https://cloud.sealos.top）

---

## 方式一：Sealos Web 控制台部署（推荐）

### Step 1: 创建存储卷

Sealos 需要持久化存储来保存 SQLite 和 ChromaDB 数据：

1. 登录 Sealos 控制台
2. 进入「存储管理」
3. 点击「创建存储卷」
   - 名称：`design-archive-data`
   - 类型：选择 `nfs` 或默认类型
   - 大小：建议 1-5GB

### Step 2: 创建应用

1. 进入「应用管理」
2. 点击「创建应用」

### Step 3: 填写配置

```
应用名称：design-evolution-archive
镜像：python:3.11-slim
容器端口：8080
实例数：1
```

### Step 4: 配置启动命令

在「启动命令」输入框中填入：

```bash
bash -c "pip install --no-cache-dir -r requirements.txt && mkdir -p /data/chroma_db /data/logs && streamlit run app.py --server.address=0.0.0.0 --server.port=8080 --server.headless=true --browser.serverAddress=localhost"
```

### Step 5: 配置环境变量

点击「添加环境变量」：

| 变量名 | 值 |
|--------|-----|
| `OPENAI_API_KEY` | 你的 API Key |
| `LLM_PROVIDER` | openai（或其他 provider） |
| `PYTHONUNBUFFERED` | 1 |

### Step 6: 挂载存储

在「存储卷」配置中：

```
挂载路径：/data
选择存储卷：design-archive-data
```

### Step 7: 部署

点击「部署」，等待容器启动（约 2-3 分钟）。

---

## 方式二：GitHub Actions 自动部署

如果想实现代码推送自动更新，需要额外配置。

### 1. 创建 GitHub Actions 工作流

在项目中创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Sealos

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and Push Docker Image
        run: |
          docker build -t your-dockerhub-username/design-archive:${{ github.sha }} .
          docker push your-dockerhub-username/design-archive:${{ github.sha }}

      - name: Deploy to Sealos
        run: |
          # 安装 sealos CLI
          curl -sfL https://download.fastgit.xyz/labring/sealos/releases/download/v4.3.7/sealos_4.3.7_linux_amd64.tar.gz | tar xz
          ./sealos run docker.io/your-dockerhub-username/design-archive:${{ github.sha }}
```

### 2. 配置 Sealos 监听镜像更新

在 Sealos 控制台开启「镜像更新自动部署」。

---

## 常见问题

### Q: 部署后访问显示空白？

检查日志：
1. 在 Sealos 控制台点击应用 → 「日志」
2. 查找 `ModuleNotFoundError` 或端口错误

### Q: 数据没有保存？

确认存储卷已挂载到 `/data`：
1. 检查 Sealos 控制台的存储配置
2. 验证 `/data` 目录存在

### Q: 如何查看 SQLite 数据库？

```bash
# 进入容器
kubectl exec -it <pod-name> -- bash

# 查看数据库文件
ls -la /data/

# 连接 SQLite
sqlite3 /data/game_design.db
```

---

## 部署后访问

应用启动后，通过 Sealos 分配的域名访问，例如：
`https://design-evolution-archive.xxx.sealos.top`

---

## 费用说明

- **7 天免费试用**：新用户有 7 天免费额度
- **付费使用**：约 50 元/月起（根据配置）
- **存储卷**：按实际使用量计费

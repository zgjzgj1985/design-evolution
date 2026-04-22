# Zeabur 部署指南

## 快速部署（推荐）

### 第一步：推送代码到 GitHub

将项目推送到 GitHub 仓库（如果是新仓库）：

```bash
git init
git add .
git commit -m "feat: 准备 Zeabur 部署"
git branch -M main
git remote add origin https://github.com/你的用户名/设计演化档案.git
git push -u origin main
```

### 第二步：在 Zeabur 创建项目

1. 访问 [zeabur.com](https://zeabur.com)，使用 GitHub 账号登录
2. 点击 **New Project** → **Deploy from GitHub**
3. 授权 GitHub 访问权限
4. 选择 `设计演化档案` 仓库
5. Zeabur 会自动检测到 `requirements.txt` 和 `app.py`，识别为 Streamlit 应用

### 第三步：配置环境变量

在 Zeabur 控制台找到你的服务，点击 **Variables** 标签，添加以下环境变量：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API Key（备用） | `sk-...` |
| `LLM_MODEL` | 模型名称 | `anthropic/claude-3.5-sonnet` |
| `OPENROUTER_BASE_URL` | OpenRouter 地址（推荐） | `https://us.novaiapi.com/v1` |

**配置方式**：
- 点击 **Edit as Raw**
- 每行一个 `KEY=value` 格式
- 例如：
  ```
  OPENAI_API_KEY=sk-your-key-here
  LLM_MODEL=anthropic/claude-3.5-sonnet
  OPENROUTER_BASE_URL=https://us.novaiapi.com/v1
  ```

### 第四步：部署

1. 点击 **Deploy**
2. 等待约 1-2 分钟（Zeabur 会安装依赖并启动）
3. 部署完成后，在 **Domains** 标签查看分配的 `.zeabur.app` 子域名
4. 访问该域名即可使用

---

## 使用 Zeabur CLI 部署（可选）

### 安装 CLI

```bash
npm install -g zeabur
```

### 部署命令

```bash
npx zeabur@latest deploy
```

---

## 配置文件说明

项目根目录的 `zbpack.json` 已经为 Zeabur 优化配置：

```json
{
    "python": {
        "version": "3.11",
        "package_manager": "pip"
    },
    "streamlit": {
        "entry": "app.py"
    },
    "build_command": "",
    "start_command": "mkdir -p /data/chroma_db /data/logs && _startup"
}
```

- **Python 3.11**：使用较新的 Python 版本
- **Streamlit 入口**：`app.py`
- **启动命令**：创建数据目录后启动应用

---

## 注意事项

### 环境变量安全

`.env` 文件**不会**被推送到 GitHub（已在 `.gitignore` 中），因此：
- 本地开发使用 `.env` 文件
- Zeabur 部署通过控制台的 **Variables** 配置

### ChromaDB 持久化

ChromaDB 向量数据库存储在 `data/chroma_db/` 目录。该目录不会被提交到 GitHub，每次部署会重新初始化。

### 端口配置

Streamlit 在 Zeabur 中默认监听端口由 `zbpack` 自动处理，不需要手动设置 `PORT` 环境变量。

---

## 常见问题

### Q: 部署失败怎么办？

1. 检查 **Logs** 标签的错误日志
2. 确认环境变量是否正确配置
3. 确认 `requirements.txt` 中的依赖都能正常安装

### Q: 如何更新代码？

只需 `git push` 到 GitHub，Zeabur 会自动检测并重新部署。

### Q: 可以绑定自己的域名吗？

可以。在 **Domains** 标签点击 **Add Domain**，按照提示添加自定义域名并配置 DNS。Zeabur 会自动处理 HTTPS 证书。

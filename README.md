# 设计演化档案 (Design Evolution Archive)

一个专注于分析宝可梦Like游戏多人对战（PvP/PvE）设计演进的 AI 研究工具。

## 功能特性

- **版本编年史** — 收录所有游戏更新日志，支持搜索与分类筛选
- **机制时间轴** — Plotly 交互图表，可视化历代机制演进
- **设计意图分析** — 调用 LLM 深度分析每次改动的设计动机
- **演进报告** — AI 自动发现主题，生成专题研究报告
- **版本对比** — 对比任意两个版本/游戏的更新内容
- **语义检索** — 支持按问题搜索历史改动，如"2v2 集火问题是如何解决的"

## 支持的游戏

| 游戏 | 平台 | 数据来源 |
|------|------|----------|
| Pokemon 剑/盾 | 非 Steam | Wiki + 内置数据 |
| Pokemon 朱/紫 | 非 Steam | Wiki + 内置数据 |
| Temtem | Steam | Steam News API |
| Cassette Beasts | Steam | Steam News API |
| Palworld | Steam | Steam News API |

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 LLM

编辑项目根目录下的 `.llm_settings.json`：

```json
{
  "provider": "openrouter",
  "model": "gemini-3-pro-preview-thinking",
  "base_url": "https://us.novaiapi.com/v1",
  "api_key": "your-api-key"
}
```

支持的 Provider：OpenAI (GPT-4o-mini)、Anthropic (Claude)、OpenRouter

### 启动应用

```bash
streamlit run app.py
```

## 项目结构

```
设计演化档案/
├── app.py                    # Streamlit Web 主入口
├── requirements.txt          # Python 依赖清单
├── .env                      # 环境变量配置
├── .llm_settings.json        # LLM 配置
│
├── scrapers/                 # 数据采集层
│   ├── steam_scraper.py      # Steam News API 爬虫
│   ├── pokemon_wiki.py       # 宝可梦 Wiki + 内置数据
│   ├── bulbapedia.py         # Bulbapedia + PokeAPI
│   ├── smogon.py             # Smogon/Pikalytics
│   └── patch_notes.py        # 更新日志基类
│
├── analyzer/                 # AI 分析层
│   ├── intent_extractor.py   # 设计意图提取
│   ├── ai_topic_discoverer.py # 主题发现
│   ├── report_generator.py   # 演进报告生成
│   ├── research_topics.py    # 研究主题配置
│   └── prompts.py            # Prompt 模板
│
├── db/                       # 数据持久化层
│   ├── sqlite_store.py       # 结构化存储
│   └── vector_store.py       # 向量存储 (ChromaDB)
│
└── utils/
    └── config.py              # 全局配置
```

## 内置研究主题

- **集火与保排机制演进** — 2v2 中如何平衡「两人集火秒杀一人」
- **PvE 团体战体验演进** — 发呆等待、状态失控、贡献度不均
- **爆发资源机制演进** — Mega进化→Z招式→极巨化→太晶化
- **速度线与行动顺序博弈** — 先手优势在双打中的调节
- **VGC 规则赛季迭代** — 通过 Ban/Pick 维持环境多样性

## 数据存储

- **SQLite** — 结构化存储：游戏信息、版本、更新日志、分析结果
- **ChromaDB** — 向量存储：设计意图向量，支持语义搜索

## 扩展新游戏

1. 在 `scrapers/` 中创建专用爬虫类，继承 `PatchNotesScraper` 基类
2. 实现 `get_multiplayer_patches()` 方法
3. 在 `app.py` 中注册新游戏

## 设计理念

1. **结构化数据优先** — 内置完整更新日志，支持增量爬虫扩展
2. **数据驱动研究** — 从真实更新日志出发，而非凭空设计
3. **AI 辅助分析** — 利用 LLM 提取设计意图，而非人工标注
4. **语义搜索能力** — 向量数据库支持"按问题搜索历史改动"
5. **可扩展架构** — 新游戏只需添加 APP_ID 和专用爬虫

## 数据来源

Gen 8/Gen 9 宝可梦更新日志来自 [Serebii.net](https://serebii.net/)

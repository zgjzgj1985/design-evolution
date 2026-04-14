# 设计演化档案 (Design Evolution Archive)

## 项目简介

**设计演化档案**是一个游戏设计研究工具，专注于分析宝可梦Like游戏（Monster Taming Genre）在多人对战（PvP/PvE）设计上的历代迭代演进。

### 核心价值

- **研究视角**：从真实更新日志出发，挖掘 Game Freak 的设计意图与迭代逻辑
- **知识沉淀**：结构化存储宝可梦历代多人机制的演进数据
- **AI 辅助**：利用大语言模型自动提取设计意图，降低人工分析成本
- **语义检索**：支持"按问题搜索历史改动"，如"2v2 集火问题是如何解决的"

---

## 技术架构

### 目录结构

```
设计演化档案/
├── app.py                    # Streamlit Web 主入口
├── requirements.txt          # Python 依赖清单
├── .env.example              # 环境变量模板
├── .llm_settings.json        # LLM 配置（用户级配置）
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
    └── config.py             # 全局配置
```

### 数据流

```
外部数据源 (Steam API, Wiki, PokeAPI)
    ↓
数据采集层 (scrapers/)
    ↓
数据存储层 (SQLite + ChromaDB)
    ↓
AI 分析层 (LLM)
    ↓
Web UI 展示 (Streamlit)
```

---

## 核心功能

### Web UI 五大标签页

| Tab | 名称 | 功能描述 |
|-----|------|----------|
| 1 | 版本编年史 | 展示所有更新日志，支持搜索和分类筛选 |
| 2 | 机制时间轴 | Plotly 交互图表，可视化历代机制演进 |
| 3 | 设计意图分析 | 调用 LLM 分析单条更新的设计意图 |
| 4 | 演进报告 | AI 主题发现 → 用户选择 → 生成报告 |
| 5 | 版本对比 | 对比两个游戏/版本的更新内容 |

### 内置研究主题

- **集火与保排机制演进** - 2v2 中如何平衡「两人集火秒杀一人」
- **PvE 团体战体验演进** - 发呆等待、状态失控、贡献度不均
- **爆发资源机制演进** - Mega进化→Z招式→极巨化→太晶化
- **速度线与行动顺序博弈** - 先手优势在双打中的调节
- **VGC 规则赛季迭代** - 通过 Ban/Pick 维持环境多样性

---

## 支持的游戏

| 游戏 | 平台 | 数据来源 |
|------|------|----------|
| Pokemon 剑/盾 | 非 Steam | Wiki 爬虫 + 内置数据 |
| Pokemon 朱/紫 | 非 Steam | Wiki 爬虫 + 内置数据 |
| Temtem | Steam (ID: 1179580) | Steam News API |
| Cassette Beasts | Steam (ID: 1322240) | Steam News API |
| Palworld | Steam (ID: 1623730) | Steam News API |

---

## LLM 集成

### 支持的 Provider

- **OpenAI** (GPT-4o-mini)
- **Anthropic** (Claude)
- **OpenRouter** (聚合 API，支持 Gemini 等模型)

### 配置方式

用户可通过 `.llm_settings.json` 配置自己的 LLM：

```json
{
  "provider": "openrouter",
  "model": "gemini-3-pro-preview-thinking",
  "base_url": "https://us.novaiapi.com/v1",
  "api_key": "your-api-key"
}
```

---

## 数据存储

### SQLite 结构化存储

存储游戏信息、版本、更新日志、分析结果。

### ChromaDB 向量存储

存储设计意图向量，支持语义搜索：
- 集合名：`design_intents`
- 持久化目录：`data/chroma_db/`

---

## 开发指南

### 环境配置

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 LLM（编辑 .llm_settings.json）
# 或复制 .env.example 并配置环境变量

# 3. 运行应用
streamlit run app.py
```

### 扩展新游戏

1. 在 `scrapers/` 中创建专用爬虫类
2. 继承 `PatchNotesScraper` 基类
3. 实现 `get_multiplayer_patches()` 方法
4. 在 `app.py` 中注册新游戏

---

## 项目状态

- **版本**：正式版 (v1.0+)
- **数据完整性**：Gen 8/Gen 9 宝可梦更新日志已完成
- **数据来源**：Serebii.net 官方更新日志页面

### 数据来源说明

宝可梦朱紫/剑盾的更新日志数据来源于 [Serebii.net](https://serebii.net/)，这是最权威的宝可梦资讯站点之一：

- **Gen 9 (朱/紫)**：包含 v1.0.1 ~ v4.0.0 所有版本
- **Gen 8 (剑/盾)**：包含 1.0.0 ~ 1.3.2 所有版本
- **DLC 内容**：碧之假面、蓝之圆盘详细数据

---

## 设计理念

1. **结构化数据优先**：内置完整的更新日志，支持增量爬虫扩展
2. **数据驱动研究**：从真实更新日志出发，而非凭空设计
3. **AI 辅助分析**：利用 LLM 提取设计意图，而非人工标注
4. **语义搜索能力**：向量数据库支持"按问题搜索历史改动"
5. **可扩展架构**：新游戏只需添加 APP_ID 和专用爬虫

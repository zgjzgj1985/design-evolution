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
├── data_manager.py           # 本地数据管理（核心）
├── fetch_all_data.py         # 数据采集脚本（一次性执行）
├── fetch_vgc_history.py      # VGC 历史数据采集脚本
├── requirements.txt          # Python 依赖清单
├── .env                      # 环境变量配置
├── .llm_settings.json        # LLM 配置（用户级配置）
│
├── data/                     # 预采集静态数据
│   ├── temtem/patches.json   # Temtem 更新日志（100条）
│   ├── palworld/            # 幻兽帕鲁数据
│   │   ├── patches.json     # Steam News 更新日志（100条）
│   │   └── patches_early.json # Wiki 补全早期版本（v0.1-v0.6）
│   ├── pokemon/
│   │   └── vgc_history.json # Pokemon VGC 历史赛季数据
│   └── cassette_beasts/
│       └── patches.json      # 占位（Steam 无公告）
│
├── docs/                     # 研究报告与文档
│   ├── index.html            # 交互式报告（Web 入口）
│   ├── report_data.json      # 报告结构化数据
│   └── CODE_REVIEW.md        # 代码审查报告
│
├── scrapers/                 # 数据采集层
│   ├── steam_scraper.py      # Steam 爬虫（本地优先，API降级）
│   ├── pokemon_wiki.py       # 宝可梦 Wiki + 内置数据
│   ├── bulbapedia.py         # Bulbapedia + PokeAPI
│   ├── smogon.py             # Smogon/Pikalytics
│   ├── palworld_wiki.py      # Palworld Wiki 早期版本补全
│   └── patch_notes.py        # 更新日志基类
│
├── analyzer/                 # AI 分析层
│   ├── intent_extractor.py   # 设计意图提取
│   ├── ai_topic_discoverer.py # AI 动态主题发现
│   ├── report_generator.py   # 演进报告生成
│   ├── research_topics.py    # 研究主题配置（已降级为兼容模块）
│   └── prompts.py            # Prompt 模板库
│
├── db/                       # 数据持久化层
│   ├── sqlite_store.py       # 结构化存储
│   └── vector_store.py       # 向量存储 (ChromaDB)
│
├── scripts/                   # 数据优化与审核脚本
│   ├── p1_data_optimization.py
│   ├── p2_data_optimization.py
│   ├── p3_data_optimization.py
│   ├── audit_fixes_v3.py
│   └── generate_report_data.py
│
└── utils/
    └── config.py              # 全局配置
```

### 数据流

```
本地 data/ 目录（预采集 JSON，不访问网络）
    ↓
数据管理层 (data_manager.py)
    ↓
AI 分析层 (LLM)
    ↓
Web UI 展示 (Streamlit)

Steam API（仅当本地数据不存在时降级访问）
    ↓
fetch_all_data.py（一次性采集，更新 data/ 目录）
```

---

## 核心功能

### Web UI 四大标签页

| Tab | 名称 | 功能描述 |
|-----|------|----------|
| 1 | 版本编年史 | 展示所有更新日志，支持搜索和分类筛选（研究价值/时间顺序） |
| 2 | 机制时间轴 | Plotly 交互图表，可视化历代机制演进（类型/游戏筛选） |
| 3 | 设计意图分析 | 调用 LLM 分析单条更新的设计意图，支持语义搜索 |
| 4 | 演进报告 | **AI 动态发现主题** → 用户选择 → 生成定制化报告 |

### 动态主题发现

本工具已升级为**完全动态化主题发现**，不再依赖预置主题：

- **AI 自动扫描**：分析当前游戏所有更新日志，从数据本身涌现设计主题
- **无先入为主**：不预设"正确答案"，从数据中自然发现问题
- **跨游戏通用**：任何新游戏接入后，工具能自动发现该游戏的设计主题
- **早期版本研究示例方向**（仅供参考）：
  - 集火与保排机制演进
  - PvE 团体战体验演进
  - 爆发资源机制演进
  - 速度线与行动顺序博弈
  - VGC 规则赛季迭代

---

## 支持的游戏

| 游戏 | 平台 | 数据来源 | 数据量 |
|------|------|----------|--------|
| Pokemon 剑/盾 | Nintendo | Wiki 爬虫 + 内置数据 | Gen 8 完整 |
| Pokemon 朱/紫 | Nintendo | Wiki 爬虫 + 内置数据 | Gen 9 完整 |
| Temtem | Steam (ID: 745920) | Steam News API | 100条预采集 |
| Cassette Beasts | Steam (ID: 1322240) | Steam（无公开公告） | 暂缺 |
| Palworld | Steam (ID: 1623730) | Steam News API + Wiki | 100条+早期版本 |

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

- **版本**：正式版 (v3.6.0+)
- **交互式报告版本**：v3.0
- **数据完整性**：
  - Gen 1-9 宝可梦更新日志已完成
  - Gen 10（Pokemon Champions）展望数据
  - VGC 历史数据覆盖 2009-2026 赛季（18个赛季）
  - Palworld 数据含早期版本（v0.1-v0.6）Wiki 补全
- **数据来源**：[Serebii.net](https://serebii.net/) 官方更新日志页面

---

## 设计理念

1. **结构化数据优先**：内置完整的更新日志，支持增量爬虫扩展
2. **数据驱动研究**：从真实更新日志出发，而非凭空设计
3. **AI 辅助分析**：利用 LLM 提取设计意图，而非人工标注
4. **语义搜索能力**：向量数据库支持"按问题搜索历史改动"
5. **可扩展架构**：新游戏只需添加 APP_ID 和专用爬虫

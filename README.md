# 设计演化档案 (Design Evolution Archive)

一个专注于**游戏设计演进研究**的 AI 辅助分析工具。通过收集真实更新日志，结合大语言模型，追踪和理解多人对战游戏的设计迭代逻辑。

## 核心定位

**面向谁**：有经验的游戏设计师、设计研究者（目的是在设计类宝可梦like新游时，在设计多人PVE玩法和PVP玩法上，从历代更新，迭代中找到参考和经验）
**解决什么问题**：将散布在多个平台（Wiki、Steam News、Bulbapedia 等）的更新日志系统化整理，不仅告诉你"改了什么"，还分析"为什么这样改"以及"历代有哪些不同的解法"
**与 Wiki 的区别**：不是数据查询工具，而是**分析工具**——提供设计意图推断、历史演进脉络、跨游戏对比等 Wiki 无法提供的研究型输出

## 功能特性

- **版本编年史** — 收录所有游戏更新日志，支持搜索与分类筛选
- **机制时间轴** — Plotly 交互图表，可视化历代机制演进
- **设计意图分析** — 调用 LLM 深度分析每次改动的设计动机
- **演进报告** — AI 自动发现主题，生成专题研究报告
- **语义检索** — 支持按问题搜索历史改动，如"2v2 集火问题是如何解决的"
- **交互式报告** — [综合研究报告：宝可梦 VGC 多人对战设计演进](docs/index.html) — 可交互的 10 条设计原则速查、时间轴、检查清单

## 支持的游戏

- **Pokemon 剑/盾** — Wiki + 内置数据
- **Pokemon 朱/紫** — Wiki + 内置数据
- **Temtem** — Steam News API
- **Cassette Beasts** — Steam News API
- **Palworld** — Steam News API + [paldb.cc Wiki](https://paldb.cc/version)（早期版本 v0.1-v0.4 由 Wiki 补全）

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

### 配置文件优先级

项目使用两套配置文件，优先级如下：

| 优先级 | 文件 | 用途 | 示例 |
|--------|------|------|------|
| **高** | `.llm_settings.json` | 运行时 LLM 配置（UI 侧边栏修改） | base_url、model、api_key |
| **低** | `.env` | 全局环境变量（手动编辑） | OPENAI_API_KEY、OPENROUTER_BASE_URL |

**说明**：
- LLM 连接时，程序优先读取 `.llm_settings.json`。如果文件不存在或字段缺失，才回退到 `.env` 中的默认值。
- 侧边栏「LLM 设置」保存后，内容写入 `.llm_settings.json`，不会修改 `.env`。
- `.env` 和 `.llm_settings.json` 都会被 `.gitignore` 忽略，不会提交到 Git。

### 启动应用

```bash
streamlit run app.py
```

## 项目结构

```
设计演化档案/
├── app.py                    # Streamlit Web 主入口
├── data_manager.py           # 本地数据管理（核心）
├── fetch_all_data.py         # 数据采集脚本（一次性执行）
├── fetch_vgc_history.py      # VGC 历史数据采集脚本
├── requirements.txt          # Python 依赖清单
├── .env                      # 环境变量配置
├── .llm_settings.json        # LLM 配置
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
│   ├── CODE_REVIEW.md        # 代码审查报告
│   └── VERSION_CHRONICLES_PAGE.md # 版本编年史页面
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
├── scripts/                   # 数据优化脚本
│   ├── p1_data_optimization.py
│   ├── p2_data_optimization.py
│   ├── p3_data_optimization.py
│   ├── audit_fixes_v3.py
│   └── generate_report_data.py
│
└── utils/
    └── config.py              # 全局配置
```

## 内置研究主题

**注意**：本工具已升级为**完全动态化主题发现**，不再依赖预置主题。AI 会自动扫描当前游戏的所有更新日志，归纳出值得研究的设计主题。以下为早期版本示例方向：

- **集火与保排机制演进** — 2v2 中如何平衡「两人集火秒杀一人」
- **PvE 团体战体验演进** — 发呆等待、状态失控、贡献度不均
- **爆发资源机制演进** — Mega进化→Z招式→极巨化→太晶化
- **速度线与行动顺序博弈** — 先手优势在双打中的调节
- **VGC 规则赛季迭代** — 通过 Ban/Pick 维持环境多样性

## 数据存储

- **本地 data/ 目录** — Steam 游戏预采集更新日志（JSON，不访问网络）
- **SQLite** — 结构化存储：游戏信息、版本、分析结果
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

# 设计演化档案 (Design Evolution Archive)

一个专注于**游戏设计演进研究**的 AI 辅助分析工具。通过收集真实更新日志，结合大语言模型，追踪和理解回合制MMO游戏的设计迭代逻辑。

## 核心定位

**面向谁**：有经验的游戏设计师、设计研究者（目的是在设计类梦幻西游Like回合制MMO新游时，在设计多人PVE/PVP玩法上，从历代更新迭代中找到参考和经验）

**解决什么问题**：将散布在多个平台的更新日志系统化整理，不仅告诉你"改了什么"，还分析"为什么这样改"以及"历代有哪些不同的解法"

**与 Wiki 的区别**：不是数据查询工具，而是**分析工具**——提供设计意图推断、历史演进脉络、跨游戏对比等 Wiki 无法提供的研究型输出

## 功能特性

- **版本编年史** — 收录所有游戏更新日志，支持搜索与分类筛选（按研究价值/时间顺序排序）
- **机制时间轴** — Plotly 交互图表，可视化历代机制演进，支持按类型/游戏筛选
- **设计意图分析** — 调用 LLM 深度分析每次改动的设计动机，支持语义搜索
- **演进报告** — AI 自动发现主题，生成专题研究报告（支持分层主题树）
- **语义检索** — 支持按问题搜索历史改动，如"封印系统是如何演进的"
- **交互式报告** — [综合研究报告：梦幻西游Like回合制MMO设计演进](docs/index.html) — 可交互的 10 条设计原则速查、时间轴、检查清单、决策树

### 交互式报告特色功能

- **10条设计原则**（三层架构：战斗设计/经济设计/运营设计）
- **47条检查清单**（7个维度，含详细决策逻辑指南）
- **历代时间轴**（含世代综述卡、演进链纵向索引）
- **决策树诊断**（快速定位设计问题 → 场景详情弹窗）
- **宝可梦vs梦幻西游对照表**（帮助理解两种游戏类型的设计对应关系）

## 支持的游戏

### 梦幻西游Like游戏（核心）

| 游戏 | 开发商 | 数据来源 | 数据量 |
|------|--------|----------|--------|
| **梦幻西游** | 网易 | 内置历史数据 + 社区整理 | 完整 |
| **神武** | 多益网络 | 内置历史数据 | 完整 |
| **大话西游** | 网易 | 内置历史数据 | 完整 |

### 宝可梦Like游戏（保留）

| 游戏 | 平台 | 数据来源 | 数据量 |
|------|------|----------|--------|
| **Pokemon** | Nintendo | Wiki 爬虫 + 内置数据（Gen 1-10） | 完整 |
| **Temtem** | Steam (ID: 745920) | Steam News API（预采集） | 100条 |
| **Palworld** | Steam (ID: 1623730) | Steam News API + Wiki 补全 | 100条+早期版本 |

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

### 采集数据

```bash
# 采集梦幻西游Like游戏数据（内置数据）
python fetch_mhxy_data.py --timeline

# 采集 Steam 游戏数据（如需要）
python fetch_all_data.py
```

### 启动应用

```bash
streamlit run app.py
```

## 项目结构

```
设计演化档案/
├── app.py                    # Streamlit Web 主入口
├── data_manager.py           # 本地数据管理（核心）
├── fetch_all_data.py         # Steam游戏数据采集脚本
├── fetch_mhxy_data.py        # 梦幻西游Like数据采集脚本
├── requirements.txt          # Python 依赖清单
├── .env                      # 环境变量配置
├── .llm_settings.json        # LLM 配置
│
├── data/                     # 预采集静态数据
│   ├── mhxy/                 # 梦幻西游数据
│   │   └── patches.json     # 更新日志（40条）
│   ├── shenwu/              # 神武数据
│   │   └── patches.json     # 更新日志
│   ├── dhxy/                # 大话西游数据
│   │   └── patches.json     # 更新日志
│   ├── temtem/patches.json   # Temtem 更新日志
│   ├── palworld/            # 幻兽帕鲁数据
│   │   ├── patches.json     # Steam News 更新日志
│   │   └── patches_early.json # Wiki 补全早期版本
│   ├── pokemon/
│   │   └── vgc_history.json # Pokemon VGC 历史赛季数据
│   └── cassette_beasts/
│       └── patches.json      # 占位（Steam 无公告）
│
├── docs/                     # 研究报告与文档
│   ├── index.html            # 交互式报告（Web 入口）
│   ├── report_data.json      # 报告结构化数据
│   └── timeline_data.json     # 时间轴数据结构
│
├── scrapers/                 # 数据采集层
│   ├── steam_scraper.py      # Steam 爬虫（本地优先，API降级）
│   ├── pokemon_wiki.py       # 宝可梦 Wiki + 内置数据
│   ├── mhxy_data.py          # 梦幻西游Like内置数据
│   ├── bulbapedia.py         # Bulbapedia + PokeAPI
│   ├── smogon.py             # Smogon/Pikalytics
│   ├── palworld_wiki.py      # Palworld Wiki 早期版本补全
│   └── patch_notes.py        # 更新日志基类
│
├── analyzer/                 # AI 分析层
│   ├── intent_extractor.py   # 设计意图提取
│   ├── ai_topic_discoverer.py # AI 动态主题发现
│   ├── report_generator.py   # 演进报告生成
│   ├── research_topics.py    # 研究主题配置（兼容模块）
│   └── prompts.py            # Prompt 模板库
│
├── db/                       # 数据持久化层
│   ├── sqlite_store.py       # 结构化存储
│   └── vector_store.py        # 向量存储 (ChromaDB)
│
├── scripts/                   # 数据优化脚本
│   ├── p1_data_optimization.py
│   ├── p2_data_optimization.py
│   └── generate_report_data.py
│
└── utils/
    └── config.py              # 全局配置
```

## 内置研究主题（梦幻西游Like方向）

**注意**：本工具已升级为**完全动态化主题发现**，不再依赖预置主题。AI 会自动扫描当前游戏的所有更新日志，归纳出值得研究的设计主题。以下为研究方向示例：

- **封印与解封设计演进** — 如何平衡封印命中率和反制手段
- **门派平衡设计演进** — 历代门派强弱调整的逻辑
- **阵法战术设计演进** — 阵法克制与站位策略
- **召唤兽生态设计演进** — 从个性宠到全红多技能的演变
- **数值经济设计演进** — 免费vs付费差距的平衡
- **5v5配合设计演进** — 团队分工与指挥反馈

## 数据存储

- **本地 data/ 目录** — 预采集更新日志（JSON，不访问网络）
- **SQLite** — 结构化存储：游戏信息、版本、分析结果
- **ChromaDB** — 向量存储：设计意图向量，支持语义搜索

## 扩展新游戏

### 扩展梦幻西游Like游戏

1. 在 `scrapers/mhxy_data.py` 中添加新游戏的数据
2. 在 `MHXYDataProvider.GAME_DATA_MAP` 中注册
3. 运行 `python fetch_mhxy_data.py` 更新数据

### 扩展宝可梦Like游戏

1. 在 `scrapers/` 中创建专用爬虫类，继承 `PatchNotesScraper` 基类
2. 实现 `get_multiplayer_patches()` 方法
3. 在 `app.py` 中注册新游戏
4. 运行 `python fetch_all_data.py` 采集数据

## 设计理念

1. **结构化数据优先** — 内置完整更新日志，支持增量爬虫扩展
2. **数据驱动研究** — 从真实更新日志出发，而非凭空设计
3. **AI 辅助分析** — 利用 LLM 提取设计意图，而非人工标注
4. **语义搜索能力** — 向量数据库支持"按问题搜索历史改动"
5. **可扩展架构** — 新游戏只需添加数据源和专用模块

## 数据来源

### 梦幻西游Like游戏

| 数据类型 | 来源 | 说明 |
|----------|------|------|
| 版本历史 | 内置历史数据 | 来自社区整理和官方公告 |
| 门派调整 | 内置历史数据 | 历代门派平衡调整记录 |
| 召唤兽演进 | 内置历史数据 | 召唤兽系统迭代记录 |

### 宝可梦Like游戏

| 数据类型 | 来源 | 说明 |
|----------|------|------|
| Pokemon 版本日志 | [Serebii.net](https://serebii.net/) | Gen 1-10 完整版本历史 |
| VGC 赛季数据 | Serebii.net | 2009-2026 完整赛季记录 |
| Palworld 更新 | Steam News API + [paldb.cc Wiki](https://paldb.cc/version) | 预采集数据 + Wiki 补全早期版本 |
| Temtem 更新 | Steam News API | 预采集数据 |

## 宝可梦 vs 梦幻西游Like对照表

| 宝可梦概念 | 梦幻西游Like对应 | 说明 |
|------------|-----------------|------|
| 宝可梦（对战单位） | 召唤兽（宝宝）/ 角色 | 宝可梦是独立的战斗单位，类似召唤兽 |
| Mega进化/Z招式/极巨化 | 经脉/奇经八脉/进阶系统 | 都是给已有单位增加强化机制的设计 |
| VGC双打规则 | 5v5比武 / 武神坛 | 最高级别的竞技规则 |
| 属性克制（火克草） | 阵法克制（蛇蟠克龙飞） | 都是增加策略深度的克制系统 |
| 特性（隐特性/普通特性） | 召唤兽特性（潮汐/洪荒等） | 都是附加在单位上的特殊能力 |
| 道具（树果/携带物品） | 装备特效（神佑/永不磨损） | 都是附加在单位上的装备效果 |
| 单打 / 双打 | 3v3 / 5v5 | 不同人数的对战规则 |
| Smogon禁止组合 | 武神坛规则限制 | 都是通过规则限制来解决平衡问题 |

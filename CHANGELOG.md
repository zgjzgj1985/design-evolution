# Changelog

所有版本变更记录遵循 [Keep a Changelog](https://keepachangelog.com/) 规范。

## [1.5.1] - 2026-04-16

### Changed

- **重构版本编年史分析渲染逻辑为独立辅助函数**
  - 新增 `get_content_hash()` 函数：使用 MD5 哈希生成内容唯一标识
  - 新增 `_render_analysis_result()` 函数：将 AI 分析结果卡片的渲染逻辑独立出来，支持 PvP 相关标记和来源标签
  - 新增 `_render_patch_detail()` 函数：将补丁详情区域（分析结果/分析按钮）的渲染逻辑封装，支持 session_state 管理和重分析触发
  - 新增 `_render_patch_card()` 函数：将补丁卡片（列表项+详情展开）的渲染逻辑封装，整合 PvP 相关检测、类型标签和背景信息折叠区
  - 大量内联代码（约 120 行）提取为独立函数，提升代码可维护性

### Fixed

- **版本编年史世代切换 Bug 修复**
  - 修复切换世代时第 11-20 条更新残留显示的问题
  - 为搜索框和类别筛选器添加带世代信息的 key，切换世代时自动重置
  - 修复统计信息区域 col4 缩进错误
  - 修复 `patch.get('url')` 字段引用错误，改为 `source_url`
  - 切换世代时同步清除 patch 分析相关的 session_state

## [1.5.0] - 2026-04-15

### Added

- **完全动态化主题发现流程**
  - 新增 AI 自动扫描更新日志，从数据本身涌现研究主题
  - 不再依赖任何预置主题，完全基于数据驱动
  - 新增游戏接入时自动发现该游戏的设计主题，无需手动配置
  - `analyzer/ai_topic_discoverer.py` 新增 `_detect_game_context()` 方法，从数据中检测游戏上下文（是否多人对战/PvP/PvE/关键词）
  - 主题发现器 Prompt 完全通用化，适用于任何游戏类型

- **演进报告生成器重构**
  - 移除硬编码的宝可梦特定知识（如 Mega 进化、Z 招式、极巨化、太晶化等）
  - 改为通用 Prompt 模板，基于实际数据生成分析
  - 新增 `match_patches_by_keywords()` 方法，支持从所有更新中按关键词匹配相关数据
  - 支持任意宝可梦 Like 游戏的演进分析

- **研究主题配置简化**
  - `analyzer/research_topics.py` 中的预置主题列表已清空
  - 保留文件仅用于向后兼容
  - 新流程中不再使用预置关键词和 game_context

### Changed

- **AI 主题发现器增强**
  - 改进 Prompt 模板，完全从数据出发，不预设任何游戏特定主题
  - 主题发现更加灵活，能适应不同游戏的设计演进模式

- **演进报告生成器通用化**
  - 报告结构从"预设六大方向"改为"基于发现的主题"生成定制化分析
  - 输出格式改为 Markdown 深度报告，包含六大部分：研究问题本质、历代解决方案、设计师决策逻辑、跨游戏对比、问题本质与未来方向、关键设计洞察

- **LLM 配置与错误处理优化**
  - `analyzer/intent_extractor.py` 优化 LLM 初始化逻辑和错误分类
  - 新增针对 OpenRouter 频率限制、连接失败、API Key 无效等场景的专门处理
  - 为 OpenRouter 添加 `api-version` 请求头以确保兼容性

- **Steam 爬虫架构调整**
  - `scrapers/steam_scraper.py` 保持代理设置启用（trust_env=True），确保能通过代理访问 Steam API
  - 请求超时从 30 秒增加到 60 秒，提升大数据量获取稳定性
  - 重试策略：最多重试 3 次，指数退避（0.5s/1s/2s）

- **Pokemon Wiki 数据扩展**
  - `scrapers/pokemon_wiki.py` 大幅扩展内置版本数据
  - 新增朱紫 4.0.0（Switch 2 兼容更新）等最新版本
  - 完善细节注释和 VGC 相关性说明

- **UI 交互优化**
  - Tab 4「演进报告」的流程优化：主题发现 → 选择 → 生成报告，三步状态指示更清晰
  - 报告生成时即时反馈，避免用户等待焦虑

### Fixed

- 修复了报告生成器在处理数据量较少时的提示不明确问题
- 优化了 LLM 调用超时和错误处理，提供更友好的用户提示
- 清理了 `db/sqlite_store.py` 中遗留的空白注释区域

## [1.4.7] - 2026-04-15

### Removed

- **移除玩家社区反应模块**
  - 删除 `scrapers/community_scraper.py` 和 `scrapers/community_scraper_v2.py`
  - 删除 `analyzer/community_analyzer.py`
  - 删除 `scripts/prefetch_community_data.py`
  - 删除 `_check_community_data.py`
  - 从 `db/sqlite_store.py` 移除 `community_reactions` 和 `reaction_summaries` 表及相关方法
  - 从 `analyzer/prompts.py` 移除 `COMMUNITY_FEEDBACK_PROMPT`、`COMMUNITY_EVIDENCE_INTEGRATION_PROMPT`、`DEMAND_DESIGN_ALIGNMENT_PROMPT`
  - 从 `app.py` 移除玩家社区反应 UI 区块及所有相关代码
  - 原因：当前采集器无法准确关联评论与版本，关键词搜索获得的评论与版本日期无真实关联，模块功能存在但效果不可控

## [1.4.6] - 2026-04-15

### Changed

- **重新设计玩家社区反应模块（V4）**
  - 删除旧版 300+ 行臃肿代码（情感分布条、评论网格、分页筛选、需求类型提取等）
  - 改为简洁三列布局：情感分布条 / 统计摘要（样本数+置信度）/ 高赞代表声音（各情感前2条）
  - 删除了无数据时仍占位的 expander，改为完全隐藏保持界面整洁
  - 保留核心数据源：反应摘要（情感分布、平台来源、置信度）+ 代表性评论原文
  - AI 分析段完整保留（深度分析按钮、分析结果卡片、重新分析按钮）

## [1.4.5] - 2026-04-15

### Changed

- **重构数据采集架构为「本地静态数据优先」**
  - 新增 `data_manager.py`：统一管理本地预采集数据，负责加载、过滤、分类
  - 新增 `fetch_all_data.py`：一次性数据采集脚本，从 Steam API 拉取所有更新日志保存为 JSON
  - 新增 `data/` 目录：包含 `temtem/patches.json`（100条）和 `palworld/patches.json`（100条）
  - Steam 游戏（Temtem、Cassette Beasts、Palworld）的更新日志优先从本地读取，不再在用户访问时实时抓取
  - `steam_scraper.py` 改为降级方案：仅在本地数据不存在时才访问 Steam API
  - Cassette Beasts 在 Steam News API 无数据，已添加空占位文件
  - UI 文案全部更新，从「实时数据源」改为「本地静态数据」
  - 版本号从 v0.2 更新至 v0.3
- **优化玩家社区反应面板**：评论列表默认折叠展示，每页仅显示 10 条，带分页导航；移除无信息量的「核心摘要」AI 废话，改为展示点赞最高的正面/负面代表性评论原文

### Added

- `data/temtem/patches.json`：Temtem 100条更新日志（预采集）
- `data/palworld/patches.json`：幻兽帕鲁 100条更新日志（预采集）
- `data/cassette_beasts/patches.json`：占位文件（Cassette Beasts Steam 无公告）

## [1.4.4] - 2026-04-15

### Changed

- **彻底重新设计玩家社区反应展示模块（用户反应模块 V3）**
  - **交互重构**：将隐藏式 expander 改为平面化卡片网格，评论内容一览无余
  - **信息层次重构**：
    - 第一行：情感分布条形图 + 平台来源图标列表 + 置信度 + 核心摘要
    - 第二行：评论网格（2列布局，每张卡片展示情感标签 + 内容预览 + 点赞数 + 来源平台）
  - **评论筛选**：新增情感类型筛选器（全部/正面/负面/混合/中性），一键切换
  - **视觉增强**：情感标签彩色边框、热度标记（🔥热评/👍高赞）、平台 Emoji 图标
  - **零数据处理**：无数据时完全隐藏区块，不显示任何占位，保持界面整洁

## [1.4.3] - 2026-04-15

### Changed

- **重构玩家反应模块：从"展示信息"到"提取设计问题线索"**
  - 完全重新设计模块目的：从展示情感数据 → 通过玩家评论识别设计问题
  - 核心问题框架：
    1. **玩家指出了什么设计问题** — 修复期望 / 增强诉求 / 削弱诉求 / 新增请求（按类型和占比呈现）
    2. **设计矛盾** — 玩家分化说明存在设计师无法同时满足的内在矛盾
    3. **情感方向** — 整体不满还是认可（服务于判断这次改动是否被接受）
  - 评论选择逻辑改为**代表性优先**：有具体诉求内容 > 情感强烈 > 点赞高
  - 每个评论的 expander 标签改为**诉求类型标签**（认为太弱/认为太强/希望新增/认为有问题）
  - 移除所有 Plotly 图表、`html`/`go` 导入、`_demand_type_insight` 死函数

## [1.4.2] - 2026-04-15

### Fixed
- 修复 Temtem 版本编年史数据抓取失败问题：更正 Steam App ID 从 `1179580`（KAKU: Ancient Seal）到 `745920`（Temtem）
  - `scrapers/steam_scraper.py` - 主爬虫
  - `scrapers/community_scraper.py` - 评测采集器
  - `scrapers/patch_notes.py` - 更新日志采集器
  - `PROJECT.md` - 文档更新

### Changed
- 移除爬虫中的 `trust_env = False` 禁用代理设置，恢复系统代理以确保 Steam API 可访问

## [1.4.1] - 2026-04-15

### Fixed
- 修复 `StreamlitDuplicateElementKey` 错误：循环内的图表 key 添加 patch 索引后缀 `idx_patch`，避免同一批次更新渲染时 key 重复

## [1.4.0] - 2026-04-15

### Changed

- **重新设计玩家社区反应展示模块**
  - 移除原有的简单 expander 折叠结构，改为内联可视化展示
  - 新增 Plotly 情感分布饼图，直观展示好评/差评/混合/中性比例
  - 新增 Plotly 玩家群体满意度横向柱状图，竞技 vs 休闲对比一目了然
  - 新增诉求类型横向柱状图，替代原有纯文字 metric
  - 新增热点目标进度条，附语义标注（BUG修复/数值调整/新内容请求）
  - 新增"社区洞察"区块，自动提炼诉求类型的深层含义
  - 两极分化展示新增仪表盘 Gauge 图，直观呈现分化程度
  - 新增分化原因逐条说明及设计内在矛盾分析
  - 高价值评论按情感分组（好评代表/差评代表/中性混合），每组展示价值评分与诉求标签

### Added

- 新增 `_demand_type_insight()` 辅助函数，将诉求类型转换为语义化洞察描述

## [1.3.0] - 2026-04-15

### Added

- **完全动态化主题发现流程**
  - 新增 AI 自动扫描更新日志，从数据本身涌现研究主题
  - 不再依赖预置主题，完全基于数据驱动
  - 新游戏接入时自动发现该游戏的设计主题，无需手动配置

### Changed

- **按钮交互反馈优化**
  - 点击 AI 按钮后立即显示"正在调用 AI..."提示，不再等待 1 秒
  - 数据获取结果缓存到 session_state，避免每次按钮点击都重新发起网络请求
  - Tab 3 "设计意图分析" 和 Tab 4 "演进报告" 的按钮交互优化

- **演进报告生成器重构**
  - 移除硬编码的 Pokemon 特定知识（如 Mega进化、Z招式、极巨化、太晶化）
  - 改为通用 Prompt 模板，基于实际数据生成分析
  - 支持任意宝可梦Like游戏的演进分析

- **AI 主题发现器增强**
  - 新增 `_detect_game_context()` 方法，从数据中检测游戏上下文
  - 改进 Prompt 模板，完全从数据出发，不预设任何游戏特定主题
  - 主题发现更加灵活，适用于任何游戏类型

- **研究主题配置简化**
  - `research_topics.py` 中的预置主题列表已清空
  - 保留文件仅用于向后兼容
  - 新流程中不再使用预置关键词和 game_context

### Benefits

- **跨游戏通用性**：任何新的宝可梦Like游戏接入后，工具能自动发现该游戏的设计主题
- **无先入为主**：不预设"正确答案"，从数据中自然涌现研究问题
- **数据驱动**：真正做到从真实更新日志出发，而非用预设理论套数据

## [1.2.0] - 2026-04-15

### Added

- **玩家社区反应深度分析模块 V2**
  - 新增 `PlayerDemandExtractor` 玩家诉求提取器
    - 自动识别增强、削弱、新增、修复、反对等诉求类型
    - 提取玩家关注的具体目标（宝可梦、机制、技能等）
    - 计算诉求提取置信度
  - 新增 `PolarizationAnalyzer` 两极分化原因分析器
    - 分析玩家群体差异（竞技 vs 休闲）
    - 检测情感强度两极化
    - 识别好评与抱怨并存的维度差异
    - 探索设计内在矛盾
  - 新增 `HighValueCommentSelector` 高价值评论识别器
    - 多维度价值评分（upvotes、内容质量、具体性、诉求）
    - 优先筛选具有代表性的高质量评论
    - 格式化用于展示
  - 新增 `TrendAnalyzer` 跨版本趋势分析器
    - 计算玩家满意度变化趋势
    - 追踪情感演变
    - 分析分化趋势和诉求演变

- **增强版反应聚合器**
  - 集成所有分析器，提供完整社区反应报告
  - 新增 `demands` 字段：玩家诉求摘要
  - 新增 `polarization` 字段：两极分化分析
  - 新增 `top_comments` 字段：高价值评论精选
  - 新增 `_generate_enhanced_summary` 方法：整合多维度信息的摘要

- **增强版 Prompt 模板**
  - `COMMUNITY_EVIDENCE_INTEGRATION_PROMPT`：深度整合社区证据的完整 Prompt
    - 包含基础统计、玩家群体分析、诉求摘要、分化分析、高价值评论
    - 要求 LLM 提供诉求-设计对照分析
    - 要求分析设计师从改动中学到了什么
  - `DEMAND_DESIGN_ALIGNMENT_PROMPT`：诉求-设计对齐度分析 Prompt
    - 分析玩家诉求被采纳的程度
    - 预测设计师决策风格

- **数据库扩展**
  - 新增 `get_reaction_trends` 方法：获取跨版本反应趋势
  - 新增 `get_raw_reactions_for_trend` 方法：获取原始反应数据用于深度分析
  - 新增 `get_all_patches_with_reactions` 方法：获取所有有反应数据的补丁
  - 新增 `get_player_demand_history` 方法：获取玩家诉求历史

### Changed

- **社区数据价值提升**
  - 从简单的"样本量 + 可信度"摘要 → 多维度的深度分析报告
  - 从单一的总体情感 → 玩家群体差异 + 诉求提取 + 分化原因
  - 从随机展示评论 → 高价值评论优先 + 代表性引语

### Fixed

- 修复了玩家评论信息被过度压缩的问题
- 修复了缺乏玩家诉求深度分析的问题
- 修复了无法分析两极分化深层原因的问题
- **修复了社区反应展示未使用增强分析的 bug**
  - app.py 现在会获取原始反应数据进行增强分析
  - 展示新增的诉求分析、两极分化分析等维度
  - 高价值评论现在按综合得分排序展示

## [1.1.0] - 2026-04-15

### Changed

- **玩家社区反应数据展示流程重构**
  - 移除了低质量的内置逻辑推导数据展示（`elif pf:` 分支）
  - 移除了手动采集按钮（用户无需手动触发）
  - 现在只展示从数据库读取的真实采集数据
  - 无真实数据时显示"暂无玩家社区反应数据（历史数据需预先采集）"

- **移除不再使用的导入**
  - `CommunityScraper`、`analyze_community_reactions` 从主应用中移除

### Added

- **新的免费社区数据采集方案 V2**
  - `scrapers/community_scraper_v2.py` - 统一采集器
  - **Metacritic 用户评论采集器**：通过后端 API 获取 Pokemon 系列用户评论
    - 支持 Pokemon 剑/盾、朱/紫、阿尔宙斯等游戏
    - API 端点：`https://backend.metacritic.com/reviews/metacritic/user/games/{slug}/platform/{platform}/web`
  - **Steam 评测采集器**：使用 steamreviews 库（无需 API Key）
    - 支持 Temtem、Cassette Beasts、Palworld

- **智能关键词提取**
  - 自动将中文关键词映射为英文搜索词
  - 支持 Pokemon/Temtem 特定关键词扩展
  - 确保始终有足够的搜索关键词

- **预采集脚本**
  - `scripts/prefetch_community_data.py`
  - 测试模式：`--test`（1-2个更新）
  - 批量模式：`--batch`（所有更新）
  - 支持指定游戏和世代：`--game Pokemon --generation 9`

- **数据库扩展**
  - `reaction_summaries` 表新增 `metacritic_count` 字段
  - 支持统计来自 Metacritic 的反应数据

### Dependencies

- 新增 `steamreviews>=0.9.6` 依赖（Steam 评测免费采集）

## [1.0.0] - 2026-04-15

### Added
- 项目初始化，完成基础架构搭建
- 实现 Web UI 五大标签页（版本编年史、机制时间轴、设计意图分析、演进报告、版本对比）
- 内置 Gen 8/Gen 9 宝可梦更新日志数据
- 支持 Steam News API 爬虫（Temtem、Cassette Beasts、Palworld）
- 实现 LLM 设计意图提取功能
- 实现 ChromaDB 向量存储与语义搜索
- 支持多 Provider（OpenAI、Anthropic、OpenRouter）

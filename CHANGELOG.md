# Changelog

所有版本变更记录遵循 [Keep a Changelog](https://keepachangelog.com/) 规范。

## [3.0.0] - 2026-04-19

### Added
- 全新交互式报告 v4.0：完全重新设计的用户界面，从"信息展示型报告"转变为"问题诊断型工具"
- **`scripts/generate_report_data.py`**：报告数据提取脚本，从 Python 常量直接生成 `docs/report_data.json`（替代原有的 Markdown 解析流程）
- **`scripts/generate_interactive_report.py`**：HTML 生成脚本，通过括号计数算法精确定位并替换 `INLINE_REPORT_DATA` 区段
- **`scripts/check_html.py`**：HTML 验证脚本，包含 42 项功能检查（数据结构/函数/版本号等）
- **`docs/report_data.json`**：报告结构化数据文件，供交互式报告前端使用
- **`scrapers/palworld_wiki.py`**：Palworld Wiki 爬虫，从 paldb.cc/version 补全 Steam News API 未覆盖的早期版本（v0.1-v0.4）
- Palworld 数据从 100 条扩展至 118 条，时间范围从 2025-01-15 扩展到 2024-01-25（v0.1.3）
- `data/palworld/patches_early.json`：早期版本独立存档（v0.1-v0.4 系列）

### Changed
- 首页重新设计：删除7个场景卡片按钮，改为 PvP/PvE 两大核心入口，让设计师快速定位问题类型
- 侧边栏重构：按"快速入口 → 场景导航 → 设计工具 → 参考资料"重新组织信息层级
- 新增场景详情页：每个入口（PvP/PvE）包含三段式布局——历史教训(Why) → 设计原则(What) → 检查清单(How)
- PvP 场景页新增"历史教训"模块：从 Pokemon 演进中找到的设计规律，按年份排列
- PvE 场景页新增"历史教训"模块：Pokemon 团体战演进 + Palworld Raid 设计实践
- 视觉设计升级：从浅色极简风格改为深色主题（#0d1117 底色），增加橙色(#f97316) PvP 和青色(#06b6d4) PvE 色彩体系
- 视觉引导增强：首页入口卡片 hover 动画、箭头引导、进度条始终显示
- 清单筛选标签优化：维度筛选改为优先级（全部/未完成/核心/重要/一般）
- **`app.py` Design Language v6 升级**：完整重构 CSS 设计系统，从 Streamlit 默认彩色风格改为极简克制高级风格——去掉所有 linear-gradient、统一字体/间距/圆角层级
- **`docs/report_data.json` 数据结构重建**：
  - 10 条原则新增 `confidence`（置信度）、`confidence_note`、`counter_example`（反例）、`boundary_condition`（边界条件）、`producer_note`（制作人提示）、`scenario_tags`（场景标签）字段
  - 47 条清单条目新增 `decision_logic`（决策逻辑说明）和 `related_principles`（关联原则 ID 数组）字段
  - Pokemon 时间轴从 7 个节点扩展为 9 个（补全 Gen 3「双打正式确立+天气系统革命」和 Gen 5「VGC 赛季制度建立+顺风」）
  - Palworld 时间轴基于 `data/palworld/patches.json` 真实 Steam 数据重建，修正了 v0.5/v0.6/v0.7 的错误日期，新增 `data_verified` 标注
  - 对照表从 5 维度扩展，新增"商业模型对竞技的影响"和"新人门槛设计"两个维度，每行增加 `takeaway` 设计规律总结
  - 版本号升级至 2.3
- **README.md 更新**：新增交互式报告星标入口，更新 Palworld 数据来源说明，更新项目结构说明

### Fixed
- 决策树导航逻辑：点击选项后跳转到清单页并自动滚动到对应维度
- 清单决策逻辑：改为默认折叠、点击展开，避免信息过载
- Palworld 数据缺失：修正 `data/palworld/patches.json` 缺失 v0.1-v0.4 系列早期版本的长期问题
- Palworld 特殊版本日期：为无 HTML 日期段落的版本（v0.6.8、v0.6.4、v0.3.10、v0.4.12）添加 KNOWN_DATES 查表修正
- `generate_interactive_report.py` 括号计数算法增强：加入 skip string literals 逻辑（`"` 内的嵌套括号不参与计数），修复复杂 JSON 中括号匹配失败问题

## [2.2.1] - 2026-04-19

### Fixed
- 修正"三层防御体系"用词不清晰问题：原"守住（单体）→ 看我嘛（嘲讽）→ 威吓（削弱）"缺乏游戏设计知识的人无法理解，改为带编号和功能解释的格式
- 修正 `generate_interactive_report.py` 的正则表达式 bug：原 `...\\n\};` 要求换行符导致匹配失败，改为纯括号计数算法更健壮

### Changed
- `docs/index.html` 中的硬编码 insight-box 文本同步更新为解释性格式

## [2.3.0] - 2026-04-19

### Added
- 新增 7 个"场景分组"（pvp_combat / enhancement / pvp_speed / pvp_environment / pve_group / meta_governance / meta_progression），按用户决策场景聚合原则和清单
- 新增首页场景引导界面：用户先选问题类型，再看到对应的原则和清单
- 清单页维度汇总头：显示"集火与保护 · 8 项（3 核心 / 4 重要 / 1 一般）"
- 清单决策逻辑默认展开（不再需要点击）
- 原则卡片中的关联原则标签改为可点击，直接打开对应原则模态框

### Changed
- 完整重写 CSS 设计系统：从彩色张扬风格改为极简克制型——去掉所有 linear-gradient、减少视觉噪音、统一字体/间距/圆角层级
- 优先级标签从彩色徽章改为灰阶文字（核心/重要/一般）
- 模态框最大宽度从 720px 缩小到 640px
- localStorage 键版本升级为 v3（不继承旧版本状态）
- 版本号升级到 v2.3

### Fixed
- 决策树节点点击后自动筛选清单到对应维度，并滚动定位
- 时间轴动画从固定的 nth-child 延迟改为 CSS 变量 `--i` 自动递增，解决超过 9 项后时序错乱问题
- 清单元数据展示新增维度定位锚点
- 清单筛选支持场景 ID（通过 `checklist_ids` 匹配）

### Deprecated
- 旧版本 localStorage 状态（vgc-report-state-v2）不再兼容

## [2.2.0] - 2026-04-19

### Added

- **`docs/index.html` 首次访问弹窗**：新增"数据来源与置信度说明"弹窗（首次访问显示，`localStorage` 记忆），将数据来源分为高/中/低三档置信度，让读者明确哪些是官方记录、哪些是社区推断、哪些是 AI 归纳
- **制作人速查决策树**：侧边栏新增"制作人决策树"入口，提供交互式问题引导（PvP / PvE / Meta 三大类），点击后跳转到对应原则卡片和清单条目
- **全局搜索**：顶部搜索栏 + `Ctrl+K` 快捷键，支持全文搜索（原则 / 清单 / 时间轴），搜索结果按类型分组，支持键盘导航
- **原则 Modal 补全**：Modal 从 4 个区块扩展为 8 个，新增置信度标签（含置信度说明）、反例对照、边界条件、制作人提示、同类别原则导航
- **清单关联原则标签**：每条清单条目关联对应的设计原则编号，点击可跳转
- **清单导出/清空功能**：检查清单新增"导出已勾选"（复制到剪贴板）和"清空所有勾选"按钮

### Changed

- **`docs/report_data.json` 数据层重建**：
  - 10 条原则新增 `confidence`（置信度）、`confidence_note`、`counter_example`（反例）、`boundary_condition`（边界条件）、`producer_note`（制作人提示）字段，内容从 Markdown 第九章提取
  - 47 条清单条目新增 `decision_logic`（决策逻辑说明）和 `related_principles`（关联原则 ID 数组）字段
  - Pokemon 时间轴从 7 个节点扩展为 9 个（补全 Gen 3「双打正式确立+天气系统革命」和 Gen 5「VGC 赛季制度建立+顺风」）
  - Palworld 时间轴基于 `data/palworld/patches.json` 真实 Steam 数据重建，修正了 v0.5/v0.6/v0.7 的错误日期（v0.7.0 实为 2026-01-31 而非 2025-12），新增 `data_verified` 标注
  - 对照表从 5 维度扩展，新增"商业模型对竞技的影响"和"新人门槛设计"两个维度，每行增加 `takeaway` 设计规律总结
- **CSS 设计 Token 体系重建**：建立完整 CSS 变量系统（颜色/间距/圆角/阴影/字体/过渡），全部使用语义化变量名替代硬编码值
- **UI 视觉升级**：
  - 侧边栏从 248px 收窄到 220px
  - 原则卡片左上角彩色竖条改为左侧 4px 色条（按类别区分）
  - 置信度徽章直接显示在卡片上（高=绿 / 中=黄 / 低=红）
  - Modal 动画从无过渡升级为 `scale(0.96) + translateY(8px)` 入场动画
  - 进度条宽度增加到 5px，更平滑
  - 面包屑导航显示当前章节路径
  - Insight Box 渐变色按类别区分（蓝色/橙色/青色/紫色）
- **时间轴增强**：新增按类型筛选（奠基/PvP/强化/PvE），双轨对照视图显示 Pokemon/Palworld 标签区分来源
- **清单增强**：
  - 新增"未完成"筛选
  - 清单条目左侧优先级颜色条（核心=红 / 重要=橙 / 一般=灰）
  - 展开 decision_logic 改为点击主体区域触发，箭头图标旋转动画
  - 清单工具栏布局优化（筛选在左，操作按钮在右）

### Deprecated

- **`scripts/generate_report_data.py` 的旧数据结构**：v1.x 版本的 Python 常量格式已废弃，v2.0 版本使用完整的结构化字段

## [2.1.0] - 2026-04-19

### Changed

- **交互式报告 `docs/index.html`**：全面重构 UI 设计语言，与 app.py Streamlit 风格统一：
  - 配色方案：主色 `#1f77b4`（Streamlit 蓝）、Danger/PvP `#ff6b6b`、PvE `#4ecdc4`、Mechanic `#45b7d1`、Balance `#96ceb4`
  - 背景层次：`#f0f4f8` → `#e8f4fd` → `#ffffff` 三层递进
  - 卡片设计：左侧色条（4px）+ 渐变背景 + 8px 圆角，hover 时加阴影和上浮
  - Insight Box：采用 app.py 风格 `linear-gradient(135deg, #e8f4fd 0%, #f0f7ff 100%)` + 左侧蓝色边框
  - 标签系统：统一为 `#tag` 圆角样式
  - 整体风格从"暗色工具感"转为"白底轻量信息感"
- **`docs/report_data.json`**：重新生成匹配新报告内容的数据结构，新增 `decision_logic` 字段（每条原则的决策逻辑）和 `takeaway` 字段（对照表每行的核心结论），新增设计维度 `icon` 字段
- **综合研究报告 Markdown**：重写检查清单附录，从简单表格升级为 47 条详细条目（3000+ 字），每条包含：检查问题 + 为什么重要 + Pokemon 实际案例 + 检查维度的四段式结构；为 14 条核心红线条目增加深度说明（500+ 字/条）

### Fixed

- **CORS 问题**（`docs/index.html`）：将 `report_data.json` 嵌入为 `INLINE_REPORT_DATA` 常量，移除 `fetch()` 调用，解决直接打开 `file://` 路径时的跨域限制

## [2.0.0] - 2026-04-19

### Added

- **Palworld 早期历史数据补全**（`scrapers/palworld_wiki.py`）：新增爬虫从 `paldb.cc/version` 补全了 Steam News API 未覆盖的早期版本，新增 18 条历史记录（v0.1.3 ~ v0.6.4），数据来源标注为 `source: "wiki_compilation"`
- **Pokemon vs Palworld 对照文档**（`docs/Pokemon_vs_Palworld_多人对战设计对照.md`）：新增跨游戏对照文档，涵盖 PvP 模式、团体战、平衡管理、强化机制、合作系统等 7 个维度
- **综合研究报告审核报告**（`docs/综合研究报告_审核报告.md`）：对综合研究报告进行系统性审核，提出 3 个严重问题、改进建议和优先级汇总
- **交互式 Web 报告**（`docs/index.html`）：新增纯 HTML 单文件交互式报告，包含 10 条设计原则卡片（可展开详情）、Pokemon/Palworld 双轨演进时间轴、Pokemon vs Palworld 对照表、设计检查清单（可勾选 + 优先级筛选 + 进度条 + localStorage 持久化）
- **报告数据提取脚本**（`scripts/generate_report_data.py`）：从 Markdown 提取结构化 JSON（`docs/report_data.json`）供前端使用

### Changed

- **Palworld patches.json**：合并 Wiki 爬取的早期版本后，总条目从 100 条增加到 118 条，覆盖时间范围从 2025-01-15 扩展到 2024-01-25（v0.1.3）
- **交互式报告技术方案**（`docs/交互式Web报告技术方案.md`）：设计并与用户确认采用纯 HTML 单文件方案（方案 A）
- **README.md**：新增「交互式报告」功能特性入口，星标标注；更新 Palworld 数据来源说明（Steam API + paldb.cc Wiki 补全）；更新项目结构说明（新增 docs/ 和 scrapers/palworld_wiki.py）

### Fixed

- **Palworld 数据缺失**：修正 `data/palworld/patches.json` 缺失 v0.1-v0.4 系列早期版本的长期问题
- **Palworld 特殊版本日期**：为无 HTML 日期段落的版本（v0.6.8、v0.6.4、v0.3.10、v0.4.12）添加 KNOWN_DATES 查表修正

## [1.9.0] - 2026-04-18

### Changed

- **综合研究报告：宝可梦 VGC 多人对战设计经验**：制作人评审修订版，主要改进如下：

  - **事实修正**：修正三处历史事实错误——第一代双打实际从第二代（金银版）开始；第八代极巨团体战实为第九代（朱/紫）内容；梦世界是网页平台而非游戏内装备系统
  - **结构重构**：为每章增加前置核心结论摘要框；新增十项设计原则速查表；对检查清单增加优先级标注（⚠️核心/重要/一般）和快速索引
  - **内容补全**：新增第四章付费模式与对战生态（买断制 vs DLC 模式分析）；新增制作人评审说明（工具局限性、使用边界）
  - **章节重组**：报告从七章扩展为九章，模块重新划分为 PvP 机制 / PvE 机制 / Meta管理与养成 / 商业运营 / 综合原则

### Added

- **核心结论摘要**：每个分析章节开头增加一行核心结论摘要，提炼该章节最关键的设计洞察
- **适用条件说明**：每章可操作建议末尾增加适用条件说明，明确建议在什么前提下成立、在什么前提下不成立
- **制作人评审附录**：新增"本报告的使用边界"章节，提醒策划团队报告作为"后验研究"的局限性、数据偏差、交叉验证必要性等

### Deprecated

- **版本号 1.0**：综合研究报告 v1.0 版本标记为已废弃，请使用 v1.1 版本

## [1.8.3] - 2026-04-17

### Fixed

- **Pokemon 第8/9世代数据缺失**：修复 `patches_db` 字典只有1-7世代数据的问题，新增第8世代（剑/盾，6条更新记录）和第9世代（朱/紫，11条更新记录），切换到第9世代时现在可以正常显示版本编年史

### Added

- **第8世代数据**：收录剑/盾首发补丁、极巨团体战、铠之孤岛DLC、冠之雪原DLC等关键版本
- **第9世代数据**：收录朱/紫首发补丁、VGC开放、大型bug修复、零之秘宝DLC（碧之假面、蓝之圆盘）、Switch 2兼容更新等完整版本历史

## [1.8.2] - 2026-04-17

### Changed

- **侧边栏数据概览增强**：Steam 游戏（Temtem/Palworld）显示本地记录总数、多人对战相关条数及占比、最新记录日期；Pokemon 显示数据来源说明
- **侧边栏 LLM 状态指示**：在 LLM 设置折叠区外部显示 AI 分析就绪状态（已就绪/连接异常/未配置），无需展开即可确认
- **侧边栏免责声明加强**：从 caption 改为 warning 样式，提高可见度

### Added

- **Tab1 版本编年史排序切换**：新增「研究价值」「时间顺序」单选切换，默认按研究价值排序（PvP/平衡/机制/Bug四档优先级）
- **Tab1 官方日志原文样式调整**：从黑色代码块改为浅灰背景+正常字体，提升阅读体验
- **Tab2 机制时间轴补充区块**：图表下方新增「已分析条目」展示区，从本地数据库读取多人对战相关分析结果，支持关键词筛选
- **Tab3/4 分析结果置信度标注**：平衡评估用色块标签（力度适中/调整不足/矫枉过正），分析置信度显示高/中/低，历史案例引用增加警告提示（建议交叉验证）
- **演进报告置信度标注**：报告头部显示基于多少条相关更新及置信度等级
- **report_generator 数据置信度字段**：返回字典增加 `_confidence` 字段，基于相关更新数量自动计算

### Removed

- **Tab5「版本对比」功能移除**：该 Tab 仅展示两条更新原文并排（无语义对齐），无法提供有意义的 AI 驱动设计对比，与工具"分析演进"的核心定位不符；README 功能列表同步移除此条目
- 界面中所有非功能性 emoji 图标（演进枝标签、分页按钮、主题缓存提示等处），保持简洁专业风格
- Prompt 模板中的功能性 emoji（数据较少/丰富提示），替换为纯文本标记

## [1.8.1] - 2026-04-17

### Fixed

- **Gen 1-7 官方更新日志原文（official_notes）未实际更新的 Bug**
  - `scrapers/pokemon_wiki.py` Gen 1-7 共 20 个条目的 `official_notes` 字段原为一句话简介（如 `"Pokemon Red and Green released in Japan."`），虽然 CHANGELOG 记录了数据重构，但 UI 渲染的"官方更新日志原文"区块实际上未显示有价值内容
  - 现已为 Gen 1-7 所有 20 个条目补全 `official_notes` 为详细的对战设计演进内容，涵盖：
    - Gen 1 (3条)：Game Boy Link Cable 双打框架、属性克制系统、PP/速度线等核心机制建立
    - Gen 2 (3条)：特性系统（威吓/道具/同步）、昼夜系统、Wi-Fi 对战雏形
    - Gen 3 (3条)：VGC 双打标准确立、天气系统完整实现、战斗边疆设计
    - Gen 4 (4条)：Wi-Fi 全球对战、物理/特殊分类改革、Stealth Rock 控场体系、Garchomp/Soul Dew 禁用先例
    - Gen 5 (2条)：组队预览信息透明化、天气能力民主化实验、Drizzle+Swift Swim 联合禁用
    - Gen 6 (3条)：Mega 进化设计约束、三打对战、赛季禁用列表制度化
    - Gen 7 (4条)：Z 招式民主化实验、阿罗拉形态、究极异兽新设计语言
  - 修复后：打开任意 Gen 1-7 补丁卡片的"查看详情"，点击"官方更新日志原文"区块，将显示有深度的对战设计演进内容（而非一句话简介）

## [1.8.0] - 2026-04-17

### Changed

- **Gen 1-7 版本数据全面重构：从无价值发布日志替换为真正的对战设计演进数据**
  - `scrapers/pokemon_wiki.py` `get_patch_notes_sample()` Gen 1-7 数据完全重写
  - **替换前**：仅有"游戏发布公告"和"Bug修复"等无价值内容（如"Pokemon Red and Green released"）
  - **替换后**：完整的对战设计演进记录，包含以下维度：
    - **Gen 1**：Game Boy Link Cable 双打对战框架、集火/保护博弈基础、全国图鉴收集体系建立
    - **Gen 2**：特性系统（威吓/压迫感/同步）上线、道具系统、昼夜系统、电话对战异步PVP雏形
    - **Gen 3**：双打正式确立为VGC标准（4v4选2）、天气系统全面上线（晴/雨/沙/冰雹+启动特性）、VGC 2005规则确立、战斗边疆Battle Frontier上线
    - **Gen 4**：Wi-Fi对战正式上线（全球化时代开启）、物理/特殊招式分类改革、秘密基地(Stealth Rock)引入、Garchomp因沙隐+沙暴被禁（首个非传说禁用案例）、Soul Dew被禁（道具禁用制度化）
    - **Gen 5**：组队预览(Team Preview)消除信息不对称、天气战争爆发、Drizzle Politoed统治环境、Drizzle+Swift Swim联合禁用（首个机制组合禁用）、PWT世界锦标赛专属规则
    - **Gen 6**：Mega进化上线（48种，仅8种有竞技价值）、超级特别团体战、三打对战(3v3)上线、战斗计时器正式引入、Mega妙蛙花/Mega耿鬼被Ban（首个赛季禁用特定Mega）
    - **Gen 7**：Z招式上线（全员可用vsMega限定专属）、阿罗拉形态、究极异兽(UB)系列引入、UB-Adhesive弱策战术、赛季禁用规则体系

- **Gen 1-7 `get_detailed_patch_notes()` 详细背景信息扩展**
  - 为每个世代的关键版本添加完整的 `full_context`（设计背景）、`balance_changes`（具体数值/机制变化）、`impact`（对环境的影响）、`vgc_relevance`（VGC相关度）、`key_insight`（核心洞察）
  - 关键洞察包括：
    - "竞技公平性的核心是减少运气成分——Garchomp沙隐被禁确立了'不可靠机制 > 强力数值'原则"
    - "技术平台升级(Wi-Fi)与机制改革(物理/特殊)并行——没有全球化用户基础就没有电竞生态"
    - "回合制观赏性是电竞化的前提——黄版动画统一为VGC转播奠定视觉基础"
    - "'单独平衡 ≠ 组合平衡'——Drizzle+Swift Swim联合禁用揭示了机制组合监管的盲区"
    - "爆发资源设计关键不是强度，而是使用成本(道具槽)+使用限制(单次/限时)+使用时机(何时进化)三者权衡"

- **`_enrich_changes_with_feedback` 玩家反馈数据库扩展**
  - 为 Gen 1-7 所有关键机制演进添加预置玩家反馈数据
  - 包含情感分析(sentiment)、社区总结(summary)、具体反馈要点(key_points)
  - 覆盖特性系统、Wi-Fi对战、物理/特殊改革、双打VGC标准确立、天气系统、Garchomp禁用、组队预览、天气战争、Mega进化、Z招式等所有核心演进节点
  - 反馈内容基于 VGC/Smogon 社区真实历史反应数据

## [1.7.2] - 2026-04-17

### Fixed

- **P1-1 LLM 幻觉防护**：`intent_extractor.py` 中 `analyze_intent()` 增加 `_disclaimer` 标注（建议交叉验证）和 `_estimate_confidence()` 置信度评估（高/中/低，基于历史案例引用质量、design_rationale 实质内容、原始信息量三个信号综合判断）
- **P1-2 技术债务清理**：删除 `analyzer/topic_discovery.py`（死代码，无其他模块引用）；重构 `analyzer/research_topics.py` 为废弃占位模块，明确标注各函数已废弃并指向新流程（`AITopicDiscoverer`）
- **P1-3 演进报告信息密度优化**：报告展示区域增加当前位置导航（"维度 → 演进枝 · 共 N 个演进阶段"），降低多层嵌套的认知负荷
- **P1-4 报告导出功能**：演进报告展示区域新增复制（剪贴板）和下载（Markdown 文件）两个导出按钮，用户可方便保存分析结果
- **P1-5 版本对比功能加免责声明**：Tab 5 顶部 `st.info()` 明确说明"无语义对齐，不自动比较设计差异"，并引导用户使用演进报告 Tab 做真正有意义的跨游戏设计比较
- **P1-6 数据质量面板**：侧边栏新增数据概览区，展示当前游戏的数据来源、存储类型、本地记录数、最早/最新记录日期
- **P1-7 README 定位明确化**：README 开头新增"核心定位"段落，明确工具面向谁、解决什么问题、与 Wiki 的本质区别，替代原有模糊的"AI 研究工具"描述

### Changed

- **P2-1 向量存储单例化**：`db/vector_store.py` 改造为单例模式（`get_instance()` 类方法），全局复用同一 ChromaDB 连接；`intent_extractor.py` 和 `app.py` 中的调用点均已同步更新
- **P2-2 主题树 SQLite 持久化缓存**：`db/sqlite_store.py` 新增 `save_topic_tree()` / `get_topic_tree_cache()` / `delete_topic_tree_cache()` 方法；`app.py` 主题发现流程改造为：优先读取 SQLite 缓存 → 命中则直接展示并标注缓存时间 → 未命中则调用 AI 并写入缓存 → 用户可随时「重新发现」清除缓存
- **P2-3 Tab 3 分析结果卡片布局**：`_render_analysis_result()` 中 `balance_assessment` 字段增加直观彩色标签映射（🟢恰到好处/🟡力度不足/🔴过犹不及/🟠治标不治本）；新增置信度标签（高/中/低）和免责声明展示
- **P2-4 游戏选择器数据量展示**：侧边栏游戏选择器旁新增本地数据条数提示（如"📊 本地数据 100 条"），帮助用户切换游戏前感知数据规模
- **P2-5 关键词分类互斥逻辑**：`data_manager.py` 新增 `PVP_EXCLUDE`（排除 battle pass 等商业词汇）和 `PVE_EXCLUDE` 互斥关键词表；`_categorize()` 改造为分类型判断，PvP/PvE 分类时自动排除互斥词，解决"battle pass 被误判为 PvP"问题
- **P2-7 品牌感知统一**：清理 `app.py` 中 3 处工具描述（文件头部/页面副标题/页脚）的"宝可梦Like"痕迹，替换为"多人对战游戏"通用表述；保留内部机制数据内容（极巨化/Mega进化等游戏研究数据）
- **P2-8 批量分析并发化**：`intent_extractor.py` 的 `batch_analyze()` 改造为 `ThreadPoolExecutor` 并发执行（默认 5 线程），小批量（≤3条）自动降级为串行避免线程开销；100 条更新等待时间从约 1000 秒降至 200 秒级别

## [1.7.1] - 2026-04-17

### Fixed

- **P0-1 Prompts 残留字段清理**：`analyzer/prompts.py` 中 `SIMPLE_EXTRACT_PROMPT` 移除了 `"pokemon_mentioned"` 字段，输出 schema 现已完全通用化，不包含任何特定游戏系列术语
- **P0-2 报告生成进度反馈**：演进报告生成流程中增加了 `st.progress()` 进度条（准备→AI 调用→完成），替代原有不确定的 spinner 等待，新旧版兼容分支均已同步更新
- **P0-3 报告生成错误信息优化**：新增 `_show_report_error()` 辅助函数，针对超时/频率限制/API 配置/连接失败/生成中断等不同错误类型给出差异化友好提示，替代通用"报告生成失败"信息
- **设计上下文知识库去游戏特化**：`analyzer/prompts.py` 中 `GAME_DESIGN_CONTEXT` 和所有 Prompt 模板的宝可梦特定术语替换为通用游戏设计表述，适用于任何有多人对战元素的游戏

## [1.7.0] - 2026-04-17

### Changed

- **演进报告主题发现流程重构：从扁平列表改为分层主题树**
  - `analyzer/ai_topic_discoverer.py` 完全重新设计主题发现 Prompt
  - 新流程：AI 先识别 2~3 个**设计维度**（顶层），每个维度下展开 2~3 条**演进枝**（具体设计问题的历代演变路径）
  - 每条演进枝包含：问题定义、历代解法（按时间排序）、核心洞察、相关补丁引用
  - 关键改进：演进枝必须体现"变化"，主题之间要求区分度，优先挖掘独特设计尝试
  - `_parse_json_response` 支持树形 JSON 结构，同时保持旧数组格式兼容
  - 新增 `_flatten_topic_tree()` 方法：将分层结构扁平化，用于向后兼容

- **演进报告生成器适配分层主题**
  - `analyzer/report_generator.py` 新增 `TREE_TOPIC_REPORT_TEMPLATE`：利用预结构化的演进枝数据生成报告，减少 LLM 推理负担
  - 新增 `_build_evolution_data_text()` 和 `_extract_patch_titles_from_branch()` 辅助方法
  - `generate_report()` 自动检测主题格式（树形 vs 扁平），走不同 Prompt 路径
  - 新增 `_is_tree_topic` 字段到返回结果，供 UI 层判断展示方式

- **演进报告 UI 重构：维度选择 + 演进枝两步选择**
  - `app.py` Tab 4 重新设计，新增 `topic_discovery_v3` 缓存 key
  - 维度层：可折叠卡片展示，展开后显示所有演进枝
  - 演进枝：显示时间线（Gen6 → Gen7 → Gen8 → ...）、核心洞察标签、🔄/📈 演进类型标记
  - 选中演进枝后：展示演进时间线预览，确认后再生成报告
  - 整体方向：Step 1 显示 AI 归纳的"整体方向"一句话概括
  - 旧版扁平主题列表保留为降级路径，确保兼容

### Benefits

- **主题区分度提升**：演进枝之间必须解决明显不同的设计问题，不再出现主题重叠
- **研究深度增强**：每条演进枝直接对应一个具体设计问题历代演变路径，分析报告更有针对性
- **数据利用率提高**：补丁引用从"关键词匹配"升级为"演进枝结构化引用"，减少无关补丁混入
- **用户体验改善**：两步选择（维度 → 演进枝）比直接看扁平列表更有层次感，用户对研究范围更清晰

### Fixed

- **设计上下文知识库去游戏特化**：将 `analyzer/prompts.py` 中的所有宝可梦特定术语替换为通用游戏设计表述
  - "看我嘛(Follow Me)" → "嘲讽/吸引机制"
  - "守住/广域防守/击掌奇袭" → "单体保护/范围保护/先手压制"
  - "急速折返/抛下狠话/蜻蜓回转" → "攻击后换人/降能力后换人/强制换人"
  - "空间类技能/顺风/黏黏网" → "空间类效果/全员加速/全员减速"
  - "宝可梦多人对战" → "多人对战游戏"
  - "宝可梦-like游戏多人对战" → "多人对战游戏"
  - "宝可梦名称和种族值" → "单位名称和具体数值"
  - 文件描述更新为"多人对战设计上下文知识（通用）"
  - 适用于任何有多人对战元素的游戏系列

## [1.6.2] - 2026-04-17

### Fixed

- **修复 Docker 构建失败：`steamreviews` 版本要求过高**
  - `requirements.txt` 中 `steamreviews>=0.9.6` 改为 `>=0.9.5`
  - PyPI 上 `0.9.6` 及以上版本要求 Python >= 3.12，与部分 Docker 镜像环境不兼容
  - 当前 PyPI 可用最高版本为 `0.9.5`，适用于所有 Python 3 环境

## [1.6.1] - 2026-04-16

### Added

- **世代1-7补丁数据代码实现**
  - `scrapers/pokemon_wiki.py` 新增 Gen 1-7 版本补丁数据，覆盖1996-2019年重要版本记录
  - 包含：特性系统、天气系统、Wi-Fi对战、Mega进化、Z招式等关键机制演进数据
- **Steam游戏数据采集**
  - 采集 Temtem、Cassette Beasts、Palworld 的 Steam 更新日志到 `data/` 目录
  - `data/temtem/patches.json`、`data/palworld/patches.json` 等数据文件

### Changed

- **`.gitignore` 更新**
  - 移除 `data/` 整体忽略规则，改为保留 `.gitkeep` 的同时允许数据文件版本控制
  - 新增 `data/` 的强制跟踪 (`!data/.gitkeep`)

## [1.6.0] - 2026-04-16

### Added

- **VGC 历史数据采集脚本**
  - 新增 `scrapers/bulbapedia.py` 中 `SerebiiScraper.get_vgc_season_rules()` 方法：从 Serebii.net 采集 VGC 赛季规则
  - 新增 `fetch_vgc_history.py` 脚本：批量采集 2009-2021 年共 13 个 VGC 赛季数据
  - 新增 `data/pokemon/vgc_history.json` 数据文件：包含完整的 VGC 历史规则（禁用宝可梦列表、特殊条款、世界冠军等）
  - 覆盖 Gen 4-7 的 VGC 赛季历史：2009(Gen4)、2010-2013(Gen5)、2014-2016(Gen6)、2017-2019(Gen7)

- **宝可梦第1-7世代全面支持**
  - 新增第1世代（1996-1999）数据：红/绿/蓝/黄基础双打对战、招式学习系统、能力值系统
  - 新增第2世代（1999-2001）数据：特性系统引入、道具有效化、电话对战系统
  - 新增第3世代（2002-2006）数据：双打正式确立为VGC基础、天气系统引入
  - 新增第4-7世代 VGC 赛季数据：Wi-Fi对战、赛季制、世界锦标赛、规则迭代等
  - 新增第6世代数据：Mega进化系统、Prankster特性
  - 新增第7世代数据：Z招式系统、究极异兽系列
  - 各世代多人对战机制演进数据（20+条时间轴节点）

### Changed

- **世代选择器扩展**
  - 侧边栏世代选择器从 [8, 9] 扩展为 [1, 2, 3, 4, 5, 6, 7, 8, 9]，覆盖全部9个世代
  - 时间轴图表高度从500px扩展至600px，y轴标签清晰标注 Gen 1-9
  - 机制演进时间轴新增第1-7世代关键节点

- **数据加载架构优化**
  - `pokemon_wiki.py` 新增 VGC 历史数据懒加载机制，运行时按需加载
  - `pokemon_wiki.py` 新增 `_get_vgc_history_for_generation()` 方法，自动整合 VGC 赛季数据到各世代

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

- **世代切换性能优化**
  - `scrapers/pokemon_wiki.py` 新增模块级缓存：`_PATCH_NOTES_CACHE`、`_DETAILED_PATCH_NOTES_CACHE`、`_MULTIPLAYER_FEATURES_CACHE`
  - `get_patch_notes_sample()` 添加缓存，世代切换时避免重复数据处理
  - `get_detailed_patch_notes()` 添加缓存，避免重复加载大字典
  - `get_multiplayer_features()` 添加缓存，避免每次调用都遍历整个 features 数据库
  - `app.py` Tab 2 PokeAPI 请求添加 `session_state` 缓存
  - 移除 `fetch_game_data()` 中未使用的 `get_multiplayer_features()` 调用
  - 世代切换时间从秒级降至毫秒级

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

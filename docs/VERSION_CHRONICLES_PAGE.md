# 版本编年史页面文档

> 生成时间：2026-04-16
> 所属模块：Tab 1 — 版本编年史（Version Chronicles）
> 对应代码位置：`app.py` 第 586-809 行

---

## 一、页面定位

版本编年史是应用的主 Tab 页面，负责展示从各数据源（Steam News API / Wiki）预采集的游戏更新日志记录。核心功能包括：

- **列表展示**：以卡片形式展示更新条目摘要
- **全文搜索 + 类别筛选**：多条件过滤
- **详情展开**：点击「查看详情」展开完整信息
- **AI 深度分析**：针对单条更新调用 LLM 提取设计意图
- **相关性标记**：自动判断条目是否与「多人对战机制演进研究」相关，高亮显示

---

## 二、显示内容详解

### 2.1 页面头部

```
st.header("版本编年史")
st.markdown("从 Steam News API 预采集的更新日志记录" if 非Pokemon else "基于 Wiki 结构化整理的版本更新记录")
```

- 非 Pokemon 游戏（Temtem/Palworld/Cassette Beasts）：显示 Steam 数据源说明
- Pokemon 游戏：显示 Wiki 结构化数据说明

---

### 2.2 筛选控件区（第 605-618 行）

**布局**：两列，左 3/4 + 右 1/4

| 控件 | 类型 | 说明 |
|------|------|------|
| 搜索框 | `text_input` | 全文搜索 title + content |
| 类别筛选 | `multiselect` | 从所有 patches 的 categories 字段动态生成，默认选中前 3 个 |

**筛选逻辑**（第 621-634 行）：

1. **世代过滤**：`patches` 列表从 session 缓存获取后再按 `generation == 当前世代` 过滤
2. **关键词搜索**：匹配 title 或 content 中是否包含搜索词（不区分大小写）
3. **类别过滤**：patch 的 categories 与选中类别至少有一个交集

> ⚠️ **Bug 隐患**：patches 列表在第 621 行做了世代过滤（`[p for p in patches if p.get("generation") == generation]`），但搜索和类别过滤在此基础上进行，若 generation=None（如非 Pokemon 游戏）则 `== None` 永远为 False，导致列表为空。

---

### 2.3 卡片列表展示（第 724-784 行）

每条更新以**内嵌卡片**形式展示，**非 expander**，直接渲染在页面中（最多 20 条）。

#### 卡片结构

```
┌──────────────────────────────────────────────────────────┐
│ [研究相关/更新] 2024-01-15 — Pokemon Scarlet v1.2.0 更新  │
│ 版本: 1.2.0  类别: 平衡调整 / 技能改动                     │
│ 削弱了某个宝可梦的种族值...                                 │
└──────────────────────────────────────────────────────────┘
```

#### 卡片字段说明

| 字段 | 来源 | 说明 |
|------|------|------|
| badge | 实时判断 | `[研究相关]` 或 `[更新]`（基于关键词匹配） |
| date | `patch["date"]` | 版本发布日期 |
| title | `patch["title"]` | 版本标题，截取前 60 字符 |
| version | `patch["version"]` | 版本号 |
| categories | `patch["categories"]` | 取前 3 个类别，斜杠分隔 |
| content 预览 | `patch["content"]` | 前 100 字符 + "..." |
| PvP/PvE 类型标签 | 实时推断 | 从内容关键词推断，显示彩色小标签 |
| 多人对战相关标签 | 实时判断 | 研究关键词命中时显示红色标签 |

#### 相关性判断逻辑（第 731-748 行）

实时关键词匹配，使用 `raw = (title + content).lower()` 全文小写后匹配：

**集火/保护机制**：`集火`, `保排`, `保护`, `守住`, `看我嘛`, `愤怒粉`, `双击`, `2v2`, `双打`, `单打`

**团体战**：`raid`, `团体战`, `极巨团体`, `太晶团体`, `集体`, `多人`

**爆发资源机制**：`mega`, `极巨化`, `太晶化`, `z招式`, `z招`

**速度博弈**：`先制`, `速度`, `顺风`, `高速`, `优先度`

**VGC/规则**：`vgc`, `规则`, `ban`, `禁止`, `分级`, `赛季`, `规则表`, `pvp`, `pve`, `对战`

**平衡性**：`削弱`, `增强`, `buff`, `nerf`

命中任意关键词 → 高亮边框变红，添加"多人对战相关"标签。

---

### 2.4 详情展开区（`with st.expander("查看详情")`）

每张卡片下方有一个「查看详情」展开区域，包含以下内容：

#### 2.4.1 元信息行（三列布局）

```
col_m1: 日期
col_m2: 版本号
col_m3: 类别标签（HTML badge）
```

#### 2.4.2 内容展示

| 字段 | 显示方式 | 样式 |
|------|---------|------|
| 更新摘要 `content` | 绿色边框卡片 | `.patch-full-content` |
| 详细改动 `detail` | 黄色边框卡片 | 内联样式 |
| 详细背景 `full_context` | 灰底卡片（需二次展开） | 内联样式 |
| 数值改动 `balance_changes` | 无序列表 | 内联样式 |
| 影响分析 `impact` | 蓝底卡片 | 内联样式 |
| VGC相关 `vgc_relevance` | 浅蓝底卡片 | 内联样式 |
| 官方更新日志原文 `official_notes` | 深色等宽字体框 | `font-family:monospace`, max-height:400px 可滚动 |

#### 2.4.3 设计意图

- 字段：`patch["intent"]`
- 显示：`st.info()` 提示框

---

### 2.5 AI 分析区域（第 858-1016 行）

#### 分析结果来源优先级

```
session_state[patch_key]（新分析结果）
    ↓ 无
DB缓存 global_db.get_classification()（旧缓存）
    ↓ 无
显示「深度分析」按钮
```

#### 已分析结果展示

当存在分析结果时，以蓝色渐变背景卡片展示以下字段：

| 字段 | 来源 key |
|------|---------|
| 具体改动 | `exact_change` |
| 竞技影响 | `competitive_impact` / `intent_summary` |
| 设计理由 | `design_rationale` / `problem_solved` |
| 研究方向 | `research_direction` |
| 涉及机制 | `mechanic_tags`（渲染为彩色标签） |
| 受影响玩家 | `player_impact` / `affected_players` |
| 平衡评估 | `balance_assessment` / `design_pattern` |
| 历史参照 | `similar_historical_cases`（最多 3 条） |

卡片左上角显示来源标签：`新分析`（绿色）或 `旧缓存`（灰色）。

提供**重新分析**按钮，触发后重新调用 LLM。

#### 未分析时

- 若 LLM 可用：显示「深度分析」**主按钮**
- 若 LLM 不可用：显示警告提示

分析完成后：
1. 结果存入 `session_state[patch_key]`
2. 结果存入 SQLite 数据库（`global_db.add_classification()`）
3. 触发 `st.rerun()` 刷新显示

---

## 三、交互方式总结

| 交互 | 触发 | 结果 |
|------|------|------|
| 输入搜索词 | `text_input` change | 实时过滤（rerun） |
| 勾选类别 | `multiselect` change | 实时过滤（rerun） |
| 点击「查看详情」 | `st.expander` toggle | 展开/折叠详情内容 |
| 点击「深度分析」 | `st.button` click | 调用 LLM → 存 DB → 刷新页面 |
| 点击「重新分析」 | `st.button` click | 清除缓存 → 重新调用 LLM → 刷新页面 |
| 点击官方原文链接 | Markdown link | 新窗口打开 `patch["url"]` |

---

## 四、现有 Bug 分析

### Bug 1：世代过滤导致的空列表（严重）

**位置**：第 621 行

```python
filtered_patches = [p for p in patches if p.get("generation") == generation]
```

**问题**：
- 非 Pokemon 游戏（Temtem/Palworld/Cassette Beasts）的 patches 数据中 `generation` 字段为 `None`
- 当 `generation = None` 时，`== None` 在 Python 中只有显式比较才为 True（`x == None`），但如果存储时字段根本不存在，`.get()` 返回 `None`，此时 `== None` 为 True，能正常工作
- **真正的问题**：当传入 `generation = None` 且 patches 列表为空时，什么都不显示

**根本问题**：这个过滤是多余的，因为 `fetch_game_data()` 已经在返回时根据游戏类型正确设置了 generation 字段。

### Bug 2：session_state 缓存键设计混乱

- 使用 `f"patch_analysis_{content_hash}"` 作为每条更新的分析结果 key
- 使用 `f"reanalysis_triggered_{patch_key}"` 作为重新分析触发器
- 使用 `f"show_reanalysis_result_{patch_key}"` 作为结果显示标记
- 三个 key 的命名规则不统一，且 hash 计算存在边缘情况

### Bug 3：expander 内部 rerun 逻辑复杂

重新分析触发时（第 882-913 行）使用 `st.rerun()`，这在 expander 展开状态下会重置 UI 状态。

### Bug 4：重复代码

分析逻辑在两个地方完全重复：
- 首次分析：第 984-1013 行
- 重新分析：第 882-913 行

### Bug 5：卡片无分页

最多显示 20 条（`filtered_patches[:20]`），没有分页控件。

---

## 五、重写目标

1. **修复世代过滤 bug**：移除冗余的 `generation == generation` 过滤
2. **简化 session_state 管理**：统一 key 命名，使用数据类/字典集中管理状态
3. **提取可复用组件**：将分析逻辑提取为独立函数
4. **添加分页支持**：处理大量更新条目
5. **优化性能**：避免每次 rerun 都重新计算关键词匹配
6. **改善代码可读性**：减少嵌套层级，使用早期返回

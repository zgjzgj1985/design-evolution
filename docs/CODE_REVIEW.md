# 代码审查报告：设计演化档案

> 审查日期：2026-04-15
> 审查范围：整体任务流程逻辑、代码质量、潜在 bug

---

## 一、任务流程梳理

```
用户选择游戏
    ↓
Tab 1: 版本编年史
    → scrapers/ 从数据源获取更新列表
    → db/sqlite_store.py 存储
    ↓
Tab 3: 设计意图分析（单条更新）
    → intent_extractor.py 调用 LLM
    → 存入 DB，缓存到 session_state
    ↓
Tab 4: 演进报告（主题研究）
    → report_generator.py 加载 research_topics.py 的主题配置
    → 按关键词过滤所有更新
    → 一次性发给 LLM 生成报告
    ↓
社区数据采集（可选项）
    → community_scraper.py 采集 Reddit/Smogon/Steam
    → community_analyzer.py 聚合分析
```

---

## 三、问题清单（按优先级排序）

### P0 - 必须修复（会导致运行时错误）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| P0-1 | `app.py:56-62` | ~~`save_llm_settings` 函数体缺少闭合括号~~ 经验证语法正确（误判） | ✅ 已排除 |
| P0-2 | `scrapers/community_scraper.py` | 关键词提取失败时直接返回空列表，导致所有平台都跳过采集 | ✅ 已修复 |

### P1 - 高优先级（影响核心功能）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| P1-1 | `scrapers/community_scraper.py` | HTML 降级方案脆弱，Reddit 更新 DOM 结构后静默失败 | ✅ 已修复 |
| P1-2 | `scrapers/*.py` | 所有 Session 未禁用 `trust_env`，可能受系统代理影响 | ✅ 已修复 |
| P1-3 | `analyzer/intent_extractor.py` | `_setup_proxy()` 从 Windows 注册表读取代理设置 | ✅ 已修复 |

### P2 - 中优先级（潜在风险）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| P2-1 | `utils/config.py:30` | `LLM_DEFAULT_MODELS` 声明为 `dict` 实际是 `set` | ✅ 已修复 |
| P2-2 | `analyzer/prompts.py:164` | `TIMELINE_PROMPT` 中变量名 `mECHANISM_NAME` 大小写不规范 | ✅ 已修复 |
| P2-3 | `analyzer/report_generator.py` | Prompt 长度未做截断控制，可能超出 LLM 上下文窗口 | ✅ 已修复 |
| P2-4 | `analyzer/research_topics.py` | `ResearchTopic \| None` 类型语法要求 Python 3.10+ | ✅ 已验证兼容性 |

### P3 - 低优先级（代码质量改进）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| P3-1 | `README.md` | 未说明 `.env` 和 `.llm_settings.json` 的优先级关系 | ⏳ 待处理 |
| P3-2 | `analyzer/prompts.py` | 双层大括号 `{{}}` 容易误认为 bug | ✅ 已排除（是正确语法） |

---

## 四、已修复问题详情

### ✅ P0-2: 关键词提取兜底逻辑
- **文件**：`scrapers/community_scraper.py`
- **问题**：关键词提取依赖预定义列表，无匹配时返回空列表
- **修复**：添加中文/英文词汇自动提取兜底，无关键词时使用游戏名作为默认值

### ✅ P1-1: 社区采集详细日志
- **文件**：`scrapers/community_scraper.py`
- **问题**：Reddit HTML 解析失败时静默返回空列表，用户不知道是哪个平台失败
- **修复**：在采集过程中打印每个平台的采集结果，包含成功/失败/跳过/异常

### ✅ P1-2: 禁用系统代理
- **文件**：`scrapers/*.py`（8个文件）
- **问题**：`requests.Session` 可能继承系统代理设置
- **修复**：所有 Session 添加 `trust_env = False`

### ✅ P1-3: 移除代理自动检测
- **文件**：`analyzer/intent_extractor.py`
- **问题**：`_setup_proxy()` 从 Windows 注册表读取代理，导致认证失败
- **修复**：删除该方法，改为清空代理环境变量

### ✅ P2-1: 修复类型声明
- **文件**：`utils/config.py`
- **问题**：`LLM_DEFAULT_MODELS` 声明为 `dict` 实际是 `set`
- **修复**：改为 `list` 类型

### ✅ P2-2: 修复变量命名
- **文件**：`analyzer/prompts.py`
- **问题**：`mECHANISM_NAME` 大小写不规范
- **修复**：改为 `mechanism_name`

### ✅ P2-3: 控制 Prompt 长度
- **文件**：`analyzer/report_generator.py`
- **问题**：Prompt 长度未做截断控制
- **修复**：添加 `MAX_PATCH_CONTENT_LENGTH = 800` 限制

---

## 五、架构亮点

1. **分层清晰**：采集层 → 存储层 → 分析层 → UI 层，职责明确
2. **降级方案**：LLM 不可用时有 fallback 逻辑
3. **主题配置化**：`research_topics.py` 将研究主题与代码解耦
4. **多数据源**：支持 Steam API、Wiki、论坛、社区多渠道采集

---

## 六、总结

项目整体架构设计合理，核心功能完整。主要风险在于：
1. **运行时稳定性**：`save_llm_settings` 语法错误必须修复
2. **数据采集可靠性**：需要改进错误处理和日志
3. **LLM 调用稳定性**：需要控制 Prompt 长度

建议优先修复 P0 问题后进行测试验证。

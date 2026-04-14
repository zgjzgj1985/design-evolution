"""
研究主题配置
定义工具要研究的核心设计问题，以及对应的过滤逻辑和 Prompt 模板
"""

from typing import TypedDict


class ResearchTopic(TypedDict):
    """研究主题定义"""
    id: str
    name: str  # 显示名称
    description: str  # 简短描述
    keywords: list[str]  # 匹配更新内容的关键词（OR 逻辑）
    exclude_keywords: list[str]  # 排除关键词
    game_context: str  # 该主题专属的设计上下文
    analysis_prompt: str  # 一次性分析整条演化线的 Prompt


RESEARCH_TOPICS: list[ResearchTopic] = [

    # ========== 主题 1：集火与保排 ==========
    {
        "id": "focus_protect",
        "name": "集火与保排机制演进",
        "description": "2v2 中如何平衡「两人集火秒杀一人」的问题，历代保护/嘲讽机制的迭代",
        "keywords": [
            # 保护系
            "保护", "守住", "Protect", "守住", "广域防守", "Wide Guard",
            "看我嘛", "Follow Me", "愤怒粉", "Follow Me",
            "击掌奇袭", "Fake Out", "挑衅", "Taunt",
            # 仇恨转移
            "怨恨", "Rage Powder", "黏黏网", "Sticky Web",
            # 通用
            "嘲讽", "保护", "集火", "分散",
        ],
        "exclude_keywords": [],
        "game_context": """
当前已知的历代解决方案：
- Gen1: 守住(Protect)登场，完全抵挡单次攻击，无法连续使用
- Gen2: 广域防守(Wide Guard)出现，保护全队免AOE
- Gen3: 看我嘛(Follow Me)登场，吸引单体攻击1回合
- Gen4: 击掌奇袭(Fake Out)先制使对方退缩
- Gen6: Mega进化提供新的站场爆发选项
- Gen8: 极巨化提供新的保护形态（极巨防壁）
- Gen9: 太晶化1回合限制，强制玩家在爆发和保护间抉择

请分析这些机制在历代版本中如何相互配合与制约。
""",
        "analysis_prompt": """你是一位游戏设计师，正在研究一个核心设计问题：多人对战中「集火秒杀 vs 保护」如何平衡。

## 研究问题
这条演化线上的历代更新，体现了设计者如何应对「两人集火秒杀一人」的体验问题。

## 输入：历代相关更新
{updates_text}

## 游戏设计背景知识
{game_context}

## 输出要求
请按以下结构输出分析报告（直接输出JSON）：

```json
{{
    "research_question": "这条演化线要研究的设计问题",
    "evolution_summary": "一句话概括历代解决思路的演进趋势",
    "generation_analysis": [
        {{
            "period": "世代/版本区间（如 Gen6-7）",
            "core_solution": "当时的核心解决方案是什么",
            "mechanism_used": "使用了哪些具体机制",
            "effect": "效果如何（玩家反馈/数据表现/是否达到目的）",
            "side_effect": "带来了什么新问题"
        }}
    ],
    "key_insight": "最重要的设计洞察（1-2句话）",
    "unresolved_problems": "至今仍未解决或仍在迭代的问题",
    "design_principle": "从中提炼的可指导未来设计的原则"
}}
```

请直接输出JSON，不要有其他内容。""",
    },

    # ========== 主题 2：PvE 团体战体验迭代 ==========
    {
        "id": "pve_raid",
        "name": "PvE 团体战体验演进",
        "description": "多人打 Boss 时，如何解决「发呆等待」「状态失控」「贡献度不均」",
        "keywords": [
            # 团体战核心
            "团体战", "raid", "Raid", "团体战", "极巨团体战", "太晶团体战",
            # Boss 设计
            "护盾", "shield", "Shield", "血量", "Boss",
            # 状态相关
            "状态异常", "异常状态", "睡眠", "混乱", "麻痹", "中毒", "烧伤",
            # 等待时间
            "等待", "指令", "时间", "即时", "同步",
            # 奖励/参与度
            "奖励", "贡献", "参与", "PVPVE",
            # Gen8 极巨
            "极巨化", "mega raid", "极巨团体战",
            # Gen9 太晶
            "太晶化", "太晶团体战", "tera raid",
        ],
        "exclude_keywords": ["单打", "单打", "1v1"],
        "game_context": """
已知的多人 PvE 设计问题及其历代解法：

问题1：发呆等待（Wait Time）
- 4人轮流指令，等待时间过长
- Gen8 极巨团体战：回合制，玩家等待时间长
- Gen9 太晶团体战：引入半即时制时间轴，玩家可边移动边等待

问题2：状态失控（Status Stacking）
- 4人无限叠 debuff，Boss 成木桩
- Gen8 极巨团体战：Boss 护盾机制（满血时清除负面状态）
- Gen9 太晶团体战：强化版护盾，更智能的状态清除

问题3：贡献度不均（Freeloading）
- 部分玩家挂机蹭奖励
- Gen9 太晶团体战：战斗参与度影响奖励品质

请分析这些机制在历代补丁中的具体迭代。
""",
        "analysis_prompt": """你是一位游戏设计师，正在研究一个核心设计问题：多人 PvE 团体战中，如何解决「发呆等待」「状态失控」「贡献度不均」三大体验痛点。

## 研究问题
这条演化线上的历代更新，体现了设计者如何应对多人 PvE 的体验问题。

## 输入：历代相关更新
{updates_text}

## 游戏设计背景知识
{game_context}

## 输出要求
请按以下结构输出分析报告（直接输出JSON）：

```json
{{
    "research_question": "这条演化线要研究的设计问题",
    "problem_tree": {{
        "wait_time": {{
            "description": "问题描述",
            "generations": [历代解决方案],
            "trend": "演进趋势"
        }},
        "status_stacking": {{
            "description": "问题描述",
            "generations": [历代解决方案],
            "trend": "演进趋势"
        }},
        "freeloading": {{
            "description": "问题描述",
            "generations": [历代解决方案],
            "trend": "演进趋势"
        }}
    }},
    "key_insight": "最重要的设计洞察（1-2句话）",
    "still_unsolved": "至今仍未解决的问题",
    "design_principle": "提炼的设计原则（可指导未来多人 PvE 设计）"
}}
```

请直接输出JSON，不要有其他内容。""",
    },

    # ========== 主题 3：爆发资源的演进 ==========
    {
        "id": "burst_mechanism",
        "name": "爆发资源机制演进",
        "description": "Mega进化→Z招式→极巨化→太晶化，每次演进解决了什么、带来了什么新问题",
        "keywords": [
            "Mega", "极巨化", "Z招式", "太晶化", "Z-Move", "Dynamax",
            "Tera", "超级进化", "超级进化", "mega evolution",
            "登场", "出场", "mega", "dynamax", "tera",
            "规则", "禁止", "ban", "限制",
        ],
        "exclude_keywords": [],
        "game_context": """
历代爆发机制的演进：

Gen6 Mega进化：
- 需要特定宝可梦才能使用
- 持续3回合
- 提供巨大属性加成和新特性
- 问题：Mega宝可梦过于强大，部分Mega成为环境主宰

Gen7 Z招式：
- 任何宝可梦都能用1次Z招式
- 一次消耗型资源
- 强力但不可持续
- 问题：Z招式过于同质化，缺乏Mega的个性化感

Gen8 极巨化：
- 任何宝可梦都能极巨化
- 持续3回合，同时改变招式
- 有反制手段（弱点突袭）
- 问题：极巨化回合过长，环境节奏变慢

Gen9 太晶化：
- 任何宝可梦都能太晶化
- 仅1回合
- 可改变属性获得抗性/打击面
- 问题：博弈窗口极短，决策压力极大

演进趋势总结：
- 门槛：特定→任意（降低）
- 持续：3回合→1回合（压缩）
- 博弈：属性压制→属性克制+招式选择（深化）
""",
        "analysis_prompt": """你是一位游戏设计师，正在研究一个核心设计问题：历代爆发机制（Mega进化→Z招式→极巨化→太晶化）如何演进，每次解决了什么问题、带来了什么新问题。

## 研究问题
这条演化线上的历代更新，体现了设计者如何迭代「玩家爆发资源」这一核心机制。

## 输入：历代相关更新
{updates_text}

## 游戏设计背景知识
{game_context}

## 输出要求
请按以下结构输出分析报告（直接输出JSON）：

```json
{{
    "research_question": "这条演化线要研究的设计问题",
    "evolution_stages": [
        {{
            "generation": "世代",
            "mechanism": "机制名称",
            "core_ability": "核心能力（改变了什么）",
            "problem_solved": "解决了什么问题",
            "new_problem": "带来了什么新问题",
            "player_reaction": "玩家/社区反应如何"
        }}
    ],
    "design_trend": "跨世代演进的设计趋势总结",
    "key_insight": "最重要的设计洞察",
    "design_principle": "提炼的设计原则"
}}
```

请直接输出JSON，不要有其他内容。""",
    },

    # ========== 主题 4：速度线与行动顺序 ==========
    {
        "id": "speed_order",
        "name": "速度线与行动顺序博弈",
        "description": "先手优势在2v2中被放大，如何通过空间/顺风/威吓等机制调节速度线",
        "keywords": [
            "速度", "Speed", "顺风", "Tailwind", "威吓", "Intimidate",
            " Trick Room", "trick room", "空间", "戏法空间",
            "黏黏网", "Sticky Web", "电网", "Electric Terrain",
            "优先度", "先制度", "priority", "先制",
            "慢启动", "slow start", "加速", "speed boost",
            "急速折返", "U-turn", "抛下狠话", "Parting Shot",
            "蜻蜓回转", "Dragon Tail",
        ],
        "exclude_keywords": [],
        "game_context": """
速度线是多人对战的核心博弈维度：

先手优势在双打中被放大：
- 2v2中，先手可以配合队友集火秒杀
- 速度线顶端往往决定了环境 Meta

历代速度调节机制：
- Gen3: 威吓(Intimidate)特性，降低对方物攻
- Gen4: 戏法空间(Trick Room)，反转速度顺序
- Gen5: 顺风(Tailwind)，全体速度翻倍
- Gen6: 黏黏网(Sticky Web)，降低对方全体速度
- Gen8: 电网(Electric Terrain)，提高电系速度
- Gen9: 慢启动限制（如请假王），控制速度线顶端

速度线设计的核心矛盾：
- 速度太快→无法反制→策略单一
- 速度太慢→毫无存在感→无意义
""",
        "analysis_prompt": """你是一位游戏设计师，正在研究一个核心设计问题：多人对战中「速度线与行动顺序」如何设计，如何防止先手优势在2v2中被过度放大。

## 研究问题
这条演化线上的历代更新，体现了设计者如何调节速度线博弈。

## 输入：历代相关更新
{updates_text}

## 游戏设计背景知识
{game_context}

## 输出要求
请按以下结构输出分析报告（直接输出JSON）：

```json
{{
    "research_question": "这条演化线要研究的设计问题",
    "speed_control_mechanisms": [
        {{
            "mechanism": "机制名称",
            "type": "强化己方/削弱对方/反转顺序",
            "generation": "引入世代",
            "purpose": "设计目的",
            "effectiveness": "实际效果（是否达到目的）"
        }}
    ],
    "meta_impact": "速度线设计对环境 Meta 的影响",
    "key_insight": "最重要的设计洞察",
    "design_principle": "提炼的设计原则"
}}
```

请直接输出JSON，不要有其他内容。""",
    },

    # ========== 主题 5：规则赛季迭代 ==========
    {
        "id": "vgc_rules",
        "name": "VGC 规则赛季迭代",
        "description": "官方赛事如何通过 Ban/Pick 规则维持环境多样性，防止 Meta 固化",
        "keywords": [
            "规则", "Rule", "规则表", "规则E", "规则D", "规则G",
            "禁止", "ban", "Ban", "限制", "限制", "禁用",
            "传说", "一级神", "二级神", "限定",
            "VGC", "Worlds", "官方", "赛季",
            "票选", "投票", "禁止",
        ],
        "exclude_keywords": [],
        "game_context": """
VGC 规则赛季的核心目的：
- 防止少数几只宝可梦统治环境
- 保持环境新鲜感
- 给予非主流宝可梦出场机会

历代规则迭代逻辑：
- Gen5: 引入分级规则（规则D/E等）
- Gen6: 引入"超级模式"(Sun/Moon Series)
- Gen8: 引入"等级100"和"等级50"切换
- Gen9: 引入"票选禁用"机制，玩家投票决定ban什么

规则设计的核心矛盾：
- 规则太宽松→少数强力宝可梦统治环境
- 规则太严格→玩家配队成本过高
- 规则变化太频繁→竞技玩家疲惫
- 规则变化太慢→Meta 固化
""",
        "analysis_prompt": """你是一位游戏设计师，正在研究一个核心设计问题：官方赛事（VGC）如何通过赛季规则迭代维持环境多样性，防止 Meta 固化。

## 研究问题
这条演化线上的历代更新，体现了规则制定者如何平衡「限制强力宝可梦」和「保持环境活力」。

## 输入：历代相关更新
{updates_text}

## 游戏设计背景知识
{game_context}

## 输出要求
请按以下结构输出分析报告（直接输出JSON）：

```json
{{
    "research_question": "这条演化线要研究的设计问题",
    "rule_iteration_phases": [
        {{
            "period": "版本/赛季区间",
            "key_rules": "核心规则",
            "banned_pokemon": "被禁止的宝可梦类型",
            "design_goal": "规则设计目标",
            "outcome": "实际效果"
        }}
    ],
    "meta_patterns": "通过规则迭代观察到的 Meta 规律",
    "key_insight": "最重要的设计洞察",
    "design_principle": "提炼的设计原则"
}}
```

请直接输出JSON，不要有其他内容。""",
    },

    # ========== 主题 6：全量分析（通用） ==========
    {
        "id": "general",
        "name": "全量设计意图分析",
        "description": "通用模式，不限定主题，对所有多人对战相关内容进行综合分析",
        "keywords": [
            "对战", "双打", "单打", "VGC", "多人",
            "极巨化", "太晶化", "Mega", "Z招式",
            "特性", "技能", "宝可梦",
            "团体战", "raid", "PVPVE",
            "规则", "ban", "限制",
            "削弱", "增强", "调整", "修改",
            "PvP", "PvE", "PVE", "PVP",
        ],
        "exclude_keywords": [],
        "game_context": """
宝可梦多人对战设计的核心维度：

PvP 双打（VGC）：
- 集火与保排的平衡
- 速度线与行动顺序
- 站场收益与联防轮转
- AOE 与单体伤害的权衡

PvE 团体战：
- 等待时间问题
- 状态失控问题
- 贡献度不均问题

爆发资源：
- Mega进化 → Z招式 → 极巨化 → 太晶化
- 门槛降低、持续压缩、博弈深化
""",
        "analysis_prompt": """你是一位游戏设计师，正在对一系列多人对战相关的版本更新进行综合分析，提炼设计意图和演化规律。

## 研究问题
给定一系列版本更新，分析其中反映的多人对战设计意图和历代演进规律。

## 输入：版本更新列表
{updates_text}

## 游戏设计背景知识
{game_context}

## 输出要求
请按以下结构输出分析报告（直接输出JSON）：

```json
{{
    "total_updates_analyzed": "分析的更新总数",
    "key_themes": ["识别出的主要设计主题"],
    "evolution_highlights": [
        {{
            "theme": "主题",
            "description": "历代如何处理这个问题",
            "insight": "设计洞察"
        }}
    ],
    "cross_generation_pattern": "跨世代设计规律总结",
    "key_insights": ["最重要的1-3条洞察"],
    "design_principle": "提炼的设计原则（可指导未来多人游戏设计）"
}}
```

请直接输出JSON，不要有其他内容。""",
    },
]


def get_topic_by_id(topic_id: str) -> ResearchTopic | None:
    """根据 ID 获取研究主题"""
    for topic in RESEARCH_TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None


def filter_patches_for_topic(patches: list, topic: ResearchTopic) -> list:
    """
    根据研究主题的关键词过滤更新

    Args:
        patches: 所有更新列表
        topic: 研究主题配置

    Returns:
        过滤后的相关更新列表
    """
    keywords = [k.lower() for k in topic["keywords"]]
    exclude_keywords = [k.lower() for k in topic["exclude_keywords"]]

    matched = []
    for patch in patches:
        text = (
            patch.get("title", "") + " " + patch.get("content", "")
        ).lower()

        # 排除
        if exclude_keywords and any(k in text for k in exclude_keywords):
            continue

        # 匹配
        if any(k in text for k in keywords):
            matched.append(patch)

    return matched

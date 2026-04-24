"""
梦幻西游Like游戏设计原则和检查清单配置

支持两种游戏类型：
- mhxy: 梦幻西游Like（回合制MMO）
- pokemon: 宝可梦Like

每种游戏类型有独立的设计原则和检查清单配置。
"""

from typing import Dict, List, Any


# ══════════════════════════════════════════════════════════════════════════════
# 梦幻西游Like游戏设计原则（8条）
# 核心：门派技能差异化 + 召唤兽体系 + 阵法克制 + 数值付费
# ══════════════════════════════════════════════════════════════════════════════
MHXY_PRINCIPLES = [
    {
        "id": 1,
        "name": "封印必须有代价",
        "summary": "任何让封印无脑连中的机制，都是危险的",
        "layer": "combat",
        "layer_label": "战斗设计",
        "category": "封印控制",
        "category_label": "封印控制",
        "category_color": "#ff6b6b",
        "decision_tree": {
            "核心检查": "封印命中后是否有足够的反制手段？",
            "判断标准": {
                "无反制手段": "该机制必须重做——这是对游戏乐趣的根本性破坏",
                "有解封手段但代价高": "继续检查：解封是否影响节奏？",
                "有解封手段且代价合理": "设计通过——对手有选择"
            },
            "配套检查": "封印命中率是否与双方属性/修炼相关联？"
        },
        "decision_logic": "设计封印机制时，必须同时回答三个问题：(1) 封印命中率是否合理？(2) 解封手段是否存在？(3) 解封代价是否可接受？这三个环节缺一不可。",
        "case_study": {
            "evolution": "方寸山封印命中率调整 → 封印命中/抵抗修炼 → 水清/玉清等解封技能",
            "core_insight": "纯粹的封印流如果没有解封手段，会让对手失去游戏体验；但完全可解的封印又会让封印失去意义。关键是找到封印时间与解封代价的平衡点。",
            "positive_case": "水清诀（解除封印+少量回复）是成功的解封设计。它给了对手明确的选择窗口。"
        },
        "confidence": "高",
        "confidence_note": "封印系统的设计与调整在梦幻西游历史上有大量记录",
        "counter_example": "某些PVE副本中的强制封印机制并非设计失误——因为这是Boss机制的一部分。",
        "boundary_condition": "本原则适用于PVP场景。对于PVE/Boss战，强制封印可能作为机制设计的一部分。核心条件：PVP对战中，被封印方应始终有机会在合理的时间窗口内做出有意义的选择。"
    },
    {
        "id": 2,
        "name": "输出必须有代价",
        "summary": "强力输出必须伴随高风险或高消耗",
        "layer": "combat",
        "layer_label": "战斗设计",
        "category": "门派平衡",
        "category_label": "门派平衡",
        "category_color": "#ff6b6b",
        "decision_tree": {
            "核心检查": "输出门派的核心输出技能是否有足够的限制？",
            "判断标准": {
                "无代价": "迟早被滥用——设计失败",
                "有代价（愤怒/血量/限制）": "继续检查：代价是否合理？",
                "代价过高": "门派沦为下水道——需要调整",
                "代价合理": "设计通过"
            },
            "配套检查": "输出门派是否有足够的生存能力作为补偿？"
        },
        "decision_logic": "设计输出机制时，必须回答：(1) 核心输出的代价是什么？(2) 这个代价是否与输出强度成正比？(3) 无代价的高输出是否会破坏游戏生态？",
        "case_study": {
            "evolution": "大唐官府点杀能力调整 → 横扫千军从无代价到有血量限制 → 配合宝宝保护机制",
            "core_insight": "大唐官府的核心是点杀，但无代价的点杀会让对手失去参与感。通过血量限制，确保大唐在点杀时自身也处于风险之中。",
            "positive_case": "横扫千军（消耗气血）的设计让大唐的点杀有了代价。使用横扫意味着自身血量下降，对手有机会反制或等待大唐进入虚弱状态。"
        },
        "confidence": "高",
        "confidence_note": "门派调整历史有大量公开记录",
        "scenario_tags": ["pvp_combat"]
    },
    {
        "id": 3,
        "name": "辅助必须有定位",
        "summary": "辅助门派的价值必须被清晰感知",
        "layer": "combat",
        "layer_label": "战斗设计",
        "category": "门派平衡",
        "category_label": "门派平衡",
        "category_color": "#ff6b6b",
        "decision_tree": {
            "核心检查": "辅助门派在团队中的核心价值是什么？",
            "判断标准": {
                "定位模糊": "该门派需要重新定位——玩家不知道什么时候选",
                "定位清晰但价值低": "需要增强或重做",
                "定位清晰且有价值": "设计通过"
            },
            "配套检查": "辅助门派的替代性有多高？"
        },
        "decision_logic": "辅助门派的设计必须回答：(1) 这个门派的不可替代性是什么？(2) 没有这个门派，团队会缺什么？(3) 辅助的价值如何量化/感知？",
        "case_study": {
            "evolution": "化生寺从纯治疗 → 化生寺+一苇渡江（攻击辅助）→ 多辅并存",
            "core_insight": "纯治疗门派容易陷入'有他没他一个样'的困境。通过增加攻击辅助能力，让辅助门派的贡献更可见。",
            "positive_case": "一苇渡江（提升全队伤害）的引入让化生寺从'奶妈'变成了'辅助核心'。"
        },
        "confidence": "高",
        "confidence_note": "门派定位调整是回合制MMO的核心议题"
    },
    {
        "id": 4,
        "name": "宝宝必须有差异",
        "summary": "召唤兽之间必须有明确的使用场景差异",
        "layer": "combat",
        "layer_label": "战斗设计",
        "category": "召唤兽生态",
        "category_label": "召唤兽生态",
        "category_color": "#f0ad4e",
        "decision_tree": {
            "核心检查": "不同召唤兽的使用场景是否有足够的区分度？",
            "判断标准": {
                "无差异（同质化）": "召唤兽体系需要重做",
                "有一定差异": "继续检查：差异是否与养成成本匹配？",
                "差异合理": "设计通过"
            },
            "配套检查": "是否有足够的召唤兽种类支撑差异化？"
        },
        "decision_logic": "设计召唤兽体系时，必须确保：(1) 不同类型的宝宝有不同的最优使用场景；(2) 高价值宝宝的使用场景与获取难度匹配；(3) 存在多种可行的宝宝配置方案。",
        "case_study": {
            "evolution": "个性宠 → 全红多技能 → 特性系统",
            "core_insight": "从'资质决定一切'到'技能决定一切'再到'特性决定一切'，召唤兽差异化经历了多轮演进。核心是确保每只宝宝都有其独特价值。",
            "positive_case": "特殊特性（如潮汐、洪荒）的引入为召唤兽提供了新的差异化维度。"
        },
        "confidence": "高",
        "confidence_note": "召唤兽系统迭代历史清晰"
    },
    {
        "id": 5,
        "name": "阵法必须有克制",
        "summary": "阵法之间必须有清晰的克制关系",
        "layer": "combat",
        "layer_label": "战斗设计",
        "category": "阵法战术",
        "category_label": "阵法战术",
        "category_color": "#06b6d4",
        "decision_tree": {
            "核心检查": "阵法之间的克制关系是否清晰可感知？",
            "判断标准": {
                "无克制（等价）": "阵法系统沦为装饰——玩家随便选",
                "克制过于极端": "最优解唯一——没有选择空间",
                "克制合理": "设计通过"
            },
            "配套检查": "阵法转换是否有过高的操作成本？"
        },
        "decision_logic": "阵法设计必须满足：(1) 存在至少一种阵法克制关系；(2) 克制关系不是一边倒（每种阵法都有被克制和克制的对象）；(3) 阵法选择本身是有意义的决策。",
        "case_study": {
            "evolution": "龙飞阵一家独大 → 蛇蟠克龙飞、虎翼克鸟翔 → 阵法平衡调整",
            "core_insight": "早期阵法设计的教训是'最强阵法压制其他一切选择'。通过引入克制关系，让不同阵法都有上场机会。",
            "positive_case": "蛇蟠阵克龙飞阵的设计让游戏从'无脑龙飞'变成了'阵法博弈'。"
        },
        "confidence": "高",
        "confidence_note": "阵法克制调整是历史主题"
    },
    {
        "id": 6,
        "name": "付费必须有限度",
        "summary": "免费与付费玩家的差距必须有上限",
        "layer": "meta",
        "layer_label": "数值经济",
        "category": "数值经济",
        "category_label": "数值经济",
        "category_color": "#8b5cf6",
        "decision_tree": {
            "核心检查": "付费带来的数值优势是否有明确上限？",
            "判断标准": {
                "无上限": "数值膨胀不可避免——迟早流失免费玩家",
                "有上限但过高": "付费体验仍然碾压——需要调整",
                "有合理上限": "设计通过"
            },
            "配套检查": "免费玩家是否有追赶路径？"
        },
        "decision_logic": "付费设计必须考虑：(1) 免费玩家与付费玩家的数值差距是否有上限？(2) 这个上限是否在可接受范围内？(3) 免费玩家是否有不付费也能体验核心内容的路径？",
        "case_study": {
            "evolution": "无级别装备 → 简易特效 → 装备等级限制",
            "core_insight": "无级别装备曾是'氪金碾压一切'的象征。通过简易特效和等级限制，逐步缩小差距。",
            "positive_case": "简易特效（降低等级要求）让低等级装备有了价值，减少了无级别对游戏的过度影响。"
        },
        "confidence": "高",
        "confidence_note": "数值付费是中国回合制MMO的核心议题"
    },
    {
        "id": 7,
        "name": "养成必须有目标",
        "summary": "玩家的养成投入必须有可见的成长路径",
        "layer": "meta",
        "layer_label": "养成进度",
        "category": "养成进度",
        "category_label": "养成进度",
        "category_color": "#10b981",
        "decision_tree": {
            "核心检查": "玩家是否能清晰看到养成目标？",
            "判断标准": {
                "目标模糊": "玩家不知道该往哪努力——流失风险",
                "目标清晰但太远": "需要增加中期目标",
                "目标清晰有节奏": "设计通过"
            },
            "配套检查": "每个养成阶段是否有明确的里程碑？"
        },
        "decision_logic": "养成系统设计必须确保：(1) 玩家知道自己的下一个目标是什么；(2) 目标之间的距离合理（不太近也不太远）；(3) 达成目标有满足感。",
        "case_study": {
            "evolution": "等级压制 → 修炼系统 → 多维度养成",
            "core_insight": "早期'等级压制一切'让新手门槛极高。通过引入修炼、宝石等多维度养成，降低单一维度的重要性。",
            "positive_case": "多维度养成让玩家可以根据自己的投入程度找到合适的目标。"
        },
        "confidence": "高",
        "confidence_note": "养成系统演进有完整记录"
    },
    {
        "id": 8,
        "name": "版本必须有节奏",
        "summary": "更新节奏必须与玩家进度匹配",
        "layer": "meta",
        "layer_label": "版本运营",
        "category": "版本节奏",
        "category_label": "版本节奏",
        "category_color": "#f59e0b",
        "decision_tree": {
            "核心检查": "版本更新节奏是否考虑了玩家养成周期？",
            "判断标准": {
                "更新太快": "玩家永远追不上——疲劳累积",
                "更新太慢": "玩家没有目标——内容空窗",
                "节奏合适": "设计通过"
            },
            "配套检查": "每次大更新是否提供足够的新内容让玩家消化？"
        },
        "decision_logic": "版本节奏设计必须考虑：(1) 玩家完成当前版本内容需要多长时间？(2) 新版本推出的间隔是否足够玩家消化？(3) 是否存在'长草期'过长的问题？",
        "case_study": {
            "evolution": "一年一个大资料片 → 半年一次大更新 → 持续内容迭代",
            "core_insight": "从'一年一资料片'到'持续内容迭代'，版本节奏的演变反映了运营思路的变化。核心是保持玩家始终有事可做。",
            "positive_case": "日常+周常+赛季的多层内容结构让玩家在任何时间点都有目标。"
        },
        "confidence": "中",
        "confidence_note": "版本节奏更多依赖运营经验"
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# 梦幻西游Like游戏检查清单（7个维度，27条）
# ══════════════════════════════════════════════════════════════════════════════
MHXY_CHECKLISTS = [
    {
        "id": "封印设计",
        "title": "封印设计",
        "description": "封印与解封机制的平衡设计",
        "icon": "🔒",
        "principles": [1],
        "items": [
            {
                "id": "M.1.1",
                "text": "封印命中率是否与双方属性差/修炼等级相关联？",
                "priority": "core",
                "decision_logic": "封印机制必须避免'无脑连中'或'永远不中'两个极端。通过属性差/修炼等级让封印命中率成为可量化的、有策略空间的变量。",
                "related_principles": [1]
            },
            {
                "id": "M.1.2",
                "text": "解封手段（水清、玉清等）是否存在且代价合理？",
                "priority": "core",
                "decision_logic": "纯粹的封印流如果没有解封手段，会让对手失去游戏体验。解封手段必须有明确代价（愤怒消耗、回合限制等），不能是无成本的。",
                "related_principles": [1]
            },
            {
                "id": "M.1.3",
                "text": "封印持续回合数是否有上限？",
                "priority": "core",
                "decision_logic": "无限封印会让对手失去所有参与感。通过回合限制或解封机制确保封印不会永远持续。",
                "related_principles": [1]
            },
            {
                "id": "M.1.4",
                "text": "封印门派是否在无封印时有其他战斗手段？",
                "priority": "important",
                "decision_logic": "封印门派如果只能封印，在封印失效后会成为'废人'。需要确保封印门派在非封印回合也有贡献能力。",
                "related_principles": [1, 3]
            },
        ]
    },
    {
        "id": "门派平衡",
        "title": "门派平衡",
        "description": "门派之间的强度平衡与差异化",
        "icon": "⚔️",
        "principles": [2, 3],
        "items": [
            {
                "id": "M.2.1",
                "text": "输出门派的核心技能是否有明确的代价（愤怒/血量/回合限制）？",
                "priority": "core",
                "decision_logic": "无代价的高输出是游戏平衡的最大敌人。每个输出技能必须有明确的限制条件，确保强力输出伴随着高风险。",
                "related_principles": [2]
            },
            {
                "id": "M.2.2",
                "text": "辅助门派的核心价值是否不可替代？",
                "priority": "core",
                "decision_logic": "辅助门派如果可以被其他门派完全替代，说明辅助设计失败。必须找到辅助门派的独特价值点。",
                "related_principles": [3]
            },
            {
                "id": "M.2.3",
                "text": "门派之间是否存在清晰的克制关系？",
                "priority": "important",
                "decision_logic": "纯数值平衡永远做不到完美。通过机制克制（封印克输出、治疗克消耗等）让门派间形成策略博弈。",
                "related_principles": [2, 3]
            },
            {
                "id": "M.2.4",
                "text": "新门派推出时是否有足够的测试期？",
                "priority": "important",
                "decision_logic": "新门派的推出往往带来环境剧变。必须给予足够的测试期和观察期，避免'数值碾压一切'的局面。",
                "related_principles": [2]
            },
            {
                "id": "M.2.5",
                "text": "经脉/奇经八脉是否提供了足够的差异化选择？",
                "priority": "general",
                "decision_logic": "分支强化系统（如经脉）应该让同一门派有不同的玩法方向，而不是只有一个最优解。",
                "related_principles": [3]
            },
        ]
    },
    {
        "id": "阵法战术",
        "title": "阵法战术",
        "description": "阵法系统的克制关系与策略深度",
        "icon": "📐",
        "principles": [5],
        "items": [
            {
                "id": "M.3.1",
                "text": "阵法之间是否存在清晰的双向克制关系？",
                "priority": "core",
                "decision_logic": "阵法克制必须满足：(1) 每种阵法都有克星；(2) 每种阵法都能克制另一种；(3) 克制关系不是一边倒。",
                "related_principles": [5]
            },
            {
                "id": "M.3.2",
                "text": "阵法选择是否是有意义的战术决策？",
                "priority": "core",
                "decision_logic": "如果存在'最强阵法'，说明阵法设计失败。必须确保阵法选择是基于对手阵容的策略决策，而非无脑选最强。",
                "related_principles": [5]
            },
            {
                "id": "M.3.3",
                "text": "阵法站位是否有足够的策略空间？",
                "priority": "important",
                "decision_logic": "阵法站位应该提供保护核心输出位、针对对手站位等策略选择，而不是固定最优站位。",
                "related_principles": [5]
            },
        ]
    },
    {
        "id": "召唤兽生态",
        "title": "召唤兽生态",
        "description": "召唤兽的差异化与价值体系",
        "icon": "🐾",
        "principles": [4],
        "items": [
            {
                "id": "M.4.1",
                "text": "不同类型的召唤兽是否有明确的使用场景差异？",
                "priority": "core",
                "decision_logic": "血攻/耐攻/敏攻/法宠/龟速等类型必须有各自的最优使用场景，不能出现某种类型全面碾压其他的情况。",
                "related_principles": [4]
            },
            {
                "id": "M.4.2",
                "text": "召唤兽的价值（技能数/资质/成长）是否与获取难度匹配？",
                "priority": "core",
                "decision_logic": "多技能宠物的价值应该呈指数增长，但获取难度也应该相应提高。确保高价值宝宝不是人人都有。",
                "related_principles": [4]
            },
            {
                "id": "M.4.3",
                "text": "特殊技能/特性是否有足够的使用场景？",
                "priority": "important",
                "decision_logic": "稀有技能（如潮汐、洪荒）必须有实际价值，不能只是'好看'的装饰。",
                "related_principles": [4]
            },
            {
                "id": "M.4.4",
                "text": "召唤兽打书是否存在有意义的权衡？",
                "priority": "important",
                "decision_logic": "打书应该是'这个技能vs那个技能'的有意义选择，而不是'只有唯一正确答案'。",
                "related_principles": [4]
            },
        ]
    },
    {
        "id": "数值经济",
        "title": "数值经济",
        "description": "付费差距控制与经济系统平衡",
        "icon": "💰",
        "principles": [6],
        "items": [
            {
                "id": "M.5.1",
                "text": "付费带来的数值优势是否有明确上限？",
                "priority": "core",
                "decision_logic": "无级别装备等'无上限强化'机制会破坏游戏生态。必须引入等级/属性上限来控制数值膨胀。",
                "related_principles": [6]
            },
            {
                "id": "M.5.2",
                "text": "免费玩家是否有追赶付费玩家的路径？",
                "priority": "core",
                "decision_logic": "纯付费碾压会导致免费玩家流失。必须设计追赶路径（如日常活动、赛季奖励）让免费玩家也能提升。",
                "related_principles": [6]
            },
            {
                "id": "M.5.3",
                "text": "游戏经济系统是否有防止通货膨胀的机制？",
                "priority": "important",
                "decision_logic": "金币产出必须有消耗途径（强化、交易税、打造等），否则通货膨胀会摧毁经济系统。",
                "related_principles": [6]
            },
            {
                "id": "M.5.4",
                "text": "外观付费与数值付费是否有效分离？",
                "priority": "important",
                "decision_logic": "锦衣祥瑞等外观付费不应该影响数值。必须确保付费差距来自玩法投入，而非单纯氪金。",
                "related_principles": [6]
            },
        ]
    },
    {
        "id": "PvP配合",
        "title": "PvP配合",
        "description": "5v5团队战术配合的设计",
        "icon": "🤝",
        "principles": [3, 5],
        "items": [
            {
                "id": "M.6.1",
                "text": "团队中是否需要明确的职责分工？",
                "priority": "core",
                "decision_logic": "5v5对战中，封系、辅助、输出、宝宝应该有各自的不可替代职责，让团队配合有意义。",
                "related_principles": [3]
            },
            {
                "id": "M.6.2",
                "text": "指挥指令是否清晰可执行？",
                "priority": "important",
                "decision_logic": "回合制MMO的沟通成本高。必须提供清晰的快捷指令系统，降低配合门槛。",
                "related_principles": [3]
            },
            {
                "id": "M.6.3",
                "text": "集火决策是否有足够的策略空间？",
                "priority": "important",
                "decision_logic": "点杀目标的选择应该基于策略考量（对方核心、当前局势等），而非无脑集火。",
                "related_principles": [2]
            },
            {
                "id": "M.6.4",
                "text": "愤怒/特技系统是否增加了策略深度？",
                "priority": "general",
                "decision_logic": "罗汉、晶清等特技应该有明确的使用时机，让愤怒管理成为战术的一部分。",
                "related_principles": [3]
            },
        ]
    },
    {
        "id": "养成进度",
        "title": "养成进度",
        "description": "角色与召唤兽的养成节奏",
        "icon": "📈",
        "principles": [7],
        "items": [
            {
                "id": "M.7.1",
                "text": "玩家是否能清晰看到下一个养成目标？",
                "priority": "core",
                "decision_logic": "从10级到满级，从普通宝宝到多技能宝宝，每个阶段应该有清晰的目标指引。",
                "related_principles": [7]
            },
            {
                "id": "M.7.2",
                "text": "养成阶段之间的时间间隔是否合理？",
                "priority": "important",
                "decision_logic": "目标太近会太快失去动力，目标太远会感到绝望。每个阶段应该有1-2周的稳定投入期。",
                "related_principles": [7]
            },
            {
                "id": "M.7.3",
                "text": "达成养成目标是否有足够的满足感？",
                "priority": "important",
                "decision_logic": "升级/突破应该有视觉反馈、属性提升、技能解锁等明确的满足感来源。",
                "related_principles": [7]
            },
        ]
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# 游戏类型元数据配置
# ══════════════════════════════════════════════════════════════════════════════
GAME_TYPE_METADATA = {
    "mhxy": {
        "name": "梦幻西游Like",
        "description": "回合制MMO（门派技能+召唤兽+阵法克制）",
        "game_type": "回合制MMO",
        "core_features": ["门派技能", "召唤兽体系", "阵法克制", "数值付费", "5v5比武"],
        "periods": [
            {"id": "起步期", "name": "起步期", "years": "2001-2002", "description": "游戏公测，建立核心玩法框架"},
            {"id": "资料片迭代期", "name": "资料片迭代期", "years": "2003-2005", "description": "通过资料片逐步完善游戏内容"},
            {"id": "资料片爆发期", "name": "资料片爆发期", "years": "2006-2010", "description": "大量资料片涌现，系统不断完善"},
            {"id": "成熟稳定期", "name": "成熟稳定期", "years": "2011-2015", "description": "游戏进入成熟期，更新趋于稳定"},
            {"id": "持续运营期", "name": "持续运营期", "years": "2016-2020", "description": "通过定期更新维持游戏活力"},
            {"id": "现代化更新期", "name": "现代化更新期", "years": "2021-2024", "description": "对老系统进行现代化改造"},
            {"id": "持续演进期", "name": "持续演进期", "years": "2025-未来", "description": "游戏持续演进，探索新方向"},
        ],
        "scenarios": [
            {"id": "封印设计", "title": "封印设计", "description": "封印与解封机制的平衡设计", "related_principles": [1]},
            {"id": "门派平衡", "title": "门派平衡", "description": "门派之间的强度平衡与差异化", "related_principles": [2, 3]},
            {"id": "阵法战术", "title": "阵法战术", "description": "阵法系统的克制关系与策略深度", "related_principles": [5]},
            {"id": "召唤兽生态", "title": "召唤兽生态", "description": "召唤兽的差异化与价值体系", "related_principles": [4]},
            {"id": "数值经济", "title": "数值经济", "description": "付费差距控制与经济系统平衡", "related_principles": [6]},
            {"id": "PvP配合", "title": "PvP配合", "description": "5v5团队战术配合的设计", "related_principles": [3]},
            {"id": "养成进度", "title": "养成进度", "description": "角色与召唤兽的养成节奏", "related_principles": [7]},
        ],
        "design_premises": [
            {"id": "P1", "title": "门派技能差异化", "description": "不同门派有独特的技能体系，玩家通过选择门派确定核心玩法定位。"},
            {"id": "P2", "title": "回合制决策", "description": "对战是回合制的，决策显性且可回溯。没有操作速度/手速/微操的变量。"},
            {"id": "P3", "title": "组合为核心乐趣", "description": "核心乐趣来自门派配合、阵法搭配、召唤兽组合的策略组合。"},
            {"id": "P4", "title": "高培育成本", "description": "角色和召唤兽需要投入大量时间/资源培育，培育成果影响对战胜负。"},
            {"id": "P5", "title": "数值付费生态", "description": "游戏存在免费玩家与付费玩家的差距，通过外观/便利性付费与数值付费并存。"},
        ],
        "meta_insight": {
            "title": "元洞察：回合制MMO的平衡难题",
            "content": "回合制MMO（如梦幻西游）近20年的演进揭示了一个深层事实：在门派技能差异化与整体平衡之间存在永恒的张力。原因是：(1) 差异化=特色=玩家选择=商业价值；(2) 差异化=强度差异=付费倾向=经济驱动；(3) 差异化=永远做不完的平衡工作。因此，与其追求「完美的门派平衡」，不如追求「可接受的差异化 + 清晰的竞技规则 + 合理的赛事分级」。"
        },
        "comparison_table": {
            "title": "回合制MMO vs 宝可梦Like对照表",
            "rows": [
                {"dimension": "对战单位", "mhxy": "角色 + 召唤兽（独立养成）", "pokemon": "宝可梦（可替换）"},
                {"dimension": "强化机制", "mhxy": "经脉/奇经八脉", "pokemon": "Mega进化/Z招式/极巨化/太晶化"},
                {"dimension": "控制机制", "mhxy": "封印命中 + 解封技能", "pokemon": "异常状态（麻痹/睡眠等）"},
                {"dimension": "速度博弈", "mhxy": "敏捷属性 + 阵法站位", "pokemon": "速度属性 + 空间类效果"},
                {"dimension": "团队配合", "mhxy": "5v5门派分工 + 特技配合", "pokemon": "4v4队伍配置"},
                {"dimension": "培育系统", "mhxy": "等级+修炼+宝石+装备+宝宝", "pokemon": "EV/IV/个体值培育"},
                {"dimension": "赛事体系", "mhxy": "武神坛/华山论剑", "pokemon": "VGC世界锦标赛"},
            ]
        }
    },
    "pokemon": {
        "name": "宝可梦Like",
        "description": "宝可梦系列多人对战设计经验",
        "game_type": "宝可梦Like",
        "core_features": ["宝可梦收集", "属性克制", "队伍构建", "VGC竞技"],
        # Pokemon的配置从scripts/generate_report_data.py的PRINCIPLES_DATA和CHECKLIST_DATA读取
        # 这里只定义元数据
        "scenarios": [
            {"id": "集火与保护", "title": "集火与保护", "description": "2v2中「击杀」与「保命」的设计平衡", "related_principles": [1, 2]},
            {"id": "强化机制", "title": "强化机制", "description": "变身/爆发/强化机制的设计陷阱", "related_principles": [4, 5, 6]},
            {"id": "速度博弈", "title": "速度博弈", "description": "如何让「先手」不是唯一的胜负手", "related_principles": [7]},
            {"id": "环境控制", "title": "环境控制", "description": "天气/地形/环境的战略价值", "related_principles": [3]},
            {"id": "4人合作", "title": "4人合作团体战", "description": "多人PvE三重困境", "related_principles": [7, 8]},
            {"id": "Meta管理", "title": "Meta管理", "description": "禁用表设计与版本平衡", "related_principles": [3]},
            {"id": "养成系统", "title": "养成系统", "description": "培育门槛与路径设计", "related_principles": [10]},
        ],
        "design_premises": [
            {"id": "P1", "title": "单位可替代性", "description": "对战单位之间可以互换（Boss战除外）。"},
            {"id": "P2", "title": "回合制决策", "description": "对战是回合制的，决策显性且可回溯。"},
            {"id": "P3", "title": "组合为核心乐趣", "description": "核心乐趣来自队伍构建的组合策略。"},
            {"id": "P4", "title": "高培育成本", "description": "单位需要投入时间/资源培育。"},
        ],
        "meta_insight": {
            "title": "元洞察：30年试错没有完美解",
            "content": "Pokemon近30年的演进揭示了一个深层事实：强化机制（Mega进化→Z招式→极巨化→太晶化）在宝可梦Like中可能不存在完美的解决方案。"
        },
    }
}


def get_report_data_for_game(game_type: str, pokemon_principles_data: List[Dict] = None, 
                              pokemon_checklist_data: List[Dict] = None,
                              pokemon_meta: Dict = None) -> Dict[str, Any]:
    """
    根据游戏类型生成对应的报告数据结构
    
    Args:
        game_type: 游戏类型 ('mhxy' 或 'pokemon')
        pokemon_principles_data: 宝可梦的设计原则数据（从generate_report_data.py获取）
        pokemon_checklist_data: 宝可梦的检查清单数据
        pokemon_meta: 宝可梦的报告元数据
    
    Returns:
        完整的报告数据结构
    """
    if game_type == "mhxy":
        return _generate_mhxy_report_data()
    elif game_type == "pokemon":
        return _generate_pokemon_report_data(pokemon_principles_data, pokemon_checklist_data, pokemon_meta)
    else:
        raise ValueError(f"不支持的游戏类型: {game_type}")


def _generate_mhxy_report_data() -> Dict[str, Any]:
    """生成梦幻西游Like游戏的报告数据"""
    metadata = GAME_TYPE_METADATA["mhxy"]
    
    # 计算检查清单总数
    total_checklist_items = sum(len(cat["items"]) for cat in MHXY_CHECKLISTS)
    
    return {
        "meta": {
            "title": "综合研究报告：梦幻西游Like回合制MMO设计演进",
            "subtitle": "MHXY-Like Turn-Based MMO Design Evolution",
            "version": "4.0-mhxy",
            "generated_at": None,  # 运行时填充
            "source": "梦幻西游Like回合制MMO多人对战设计演进研究",
            "description": f"回合制MMO多人对战设计演进研究，含{len(MHXY_PRINCIPLES)}条设计原则与{total_checklist_items}条详细检查清单",
            "data_sources": [
                {"name": "梦幻西游官方公告", "type": "official", "description": "网易官方更新公告"},
                {"name": "NGA梦幻西游", "type": "community", "description": "玩家社区讨论、攻略、反馈"},
                {"name": "叶子猪梦幻西游", "type": "database", "description": "游戏数据库、资料站"},
                {"name": "AI 分析归纳", "type": "inferred", "description": "从补丁历史中推断的设计意图"},
            ],
            "design_premises": {
                "title": "设计前提",
                "description": "本报告的原则基于以下回合制MMO核心特征。",
                "premises": metadata["design_premises"]
            },
            "meta_insight": metadata["meta_insight"],
            "game_type": "mhxy"
        },
        "principles": MHXY_PRINCIPLES,
        "checklist": MHXY_CHECKLISTS,
        "scenarios": metadata["scenarios"],
        "timeline": [],  # 时间轴数据从各游戏数据源动态加载
        "generation_metadata": metadata["periods"],
        "comparison_table": metadata["comparison_table"],
    }


def _generate_pokemon_report_data(principles_data: List[Dict] = None, 
                                   checklist_data: List[Dict] = None,
                                   meta_data: Dict = None) -> Dict[str, Any]:
    """
    生成宝可梦Like游戏的报告数据
    原则和检查清单从 generate_report_data.py 动态获取
    """
    if meta_data is None:
        meta_data = {
            "title": "综合研究报告：宝可梦 VGC 多人对战设计演进",
            "subtitle": "Pokemon VGC Multiplayer Design Evolution",
            "version": "3.0",
            "description": "Pokemon 30年（1996-2026）多人对战设计演进研究，含10条设计原则与47条详细检查清单",
        }
    
    return {
        "meta": {
            **meta_data,
            "game_type": "pokemon"
        },
        "principles": principles_data or [],
        "checklist": checklist_data or [],
        "scenarios": GAME_TYPE_METADATA["pokemon"]["scenarios"],
        "timeline": [],
        "generation_metadata": [],
    }


def get_principles_count(game_type: str) -> int:
    """获取指定游戏类型的设计原则数量"""
    if game_type == "mhxy":
        return len(MHXY_PRINCIPLES)
    elif game_type == "pokemon":
        # Pokemon的10条原则是固定的
        return 10
    return 0


def get_checklist_count(game_type: str) -> int:
    """获取指定游戏类型的检查清单数量"""
    if game_type == "mhxy":
        return sum(len(cat["items"]) for cat in MHXY_CHECKLISTS)
    elif game_type == "pokemon":
        # Pokemon的47条检查清单是固定的
        return 47
    return 0


def get_scenarios_count(game_type: str) -> int:
    """获取指定游戏类型的场景数量"""
    if game_type == "mhxy":
        return len(MHXY_CHECKLISTS)
    elif game_type == "pokemon":
        return len(GAME_TYPE_METADATA["pokemon"]["scenarios"])
    return 0

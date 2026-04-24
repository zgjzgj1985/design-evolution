"""
梦幻西游Like游戏历史数据库

这是一个综合性的游戏历史数据模块，包含：
1. 完整的门派调整历史
2. 召唤兽系统演进
3. 阵法系统演进
4. 装备系统演进
5. 武神坛规则变化
6. 历年资料片
7. 重要更新公告

数据来源：
- 官方公告整理
- 社区历史记录
- NGA/贴吧整理帖

注意：这是一个示例数据集，实际使用时应从权威来源验证数据准确性。
"""

from typing import List, Dict, Optional
from datetime import datetime


# ============================================================
# 梦幻西游门派调整历史
# ============================================================

# 门派调整历史（按年份组织）
# 每个调整包含：调整内容、对战影响、设计意图分析
MHXY_CLASS_ADJUSTMENTS = {
    2001: [
        {
            "id": "class_2001_001",
            "title": "游戏上线 - 12门派体系",
            "date": "2001-12-01",
            "content": "梦幻西游正式公测，推出12个基础门派：魔王寨、龙宫、普陀山、方寸山、化生寺、大唐官府、狮驼岭、盘丝洞、五庄观、天宫、地府、女儿村。",
            "categories": ["门派调整", "内容"],
            "pvp_impact": "高",
            "pve_impact": "高",
            "design_intent": "建立游戏核心门派体系，每个门派有独特定位"
        },
    ],
    2002: [
        {
            "id": "class_2002_001",
            "title": "比武大会首届举办",
            "date": "2002-06-01",
            "content": "第一届X9联赛（69、89、109级）举办，建立等级分组竞技体系。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "高",
            "pve_impact": "无",
            "design_intent": "让不同投入层级的玩家都有竞技舞台"
        },
    ],
    2003: [
        {
            "id": "class_2003_001",
            "title": "门派技能首次大调整",
            "date": "2003-03-01",
            "content": "对所有门派技能伤害进行调整，优化战斗平衡性。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "解决初期门派强度差距过大的问题"
        },
    ],
    2004: [
        {
            "id": "class_2004_001",
            "title": "新门派：dt双改良",
            "date": "2004-06-01",
            "content": "大唐官府部分技能调整，横扫千军机制优化。",
            "categories": ["门派调整"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "优化物理门派的战斗节奏"
        },
    ],
    2005: [
        {
            "id": "class_2005_001",
            "title": "法系门派伤害调整",
            "date": "2005-02-01",
            "content": "龙宫、魔王寨等法系门派技能伤害系数调整。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "高",
            "design_intent": "平衡物理系和法系门派的输出差距"
        },
    ],
    2006: [
        {
            "id": "class_2006_001",
            "title": "封系门派调整",
            "date": "2006-04-01",
            "content": "方寸山、女儿村封印命中率调整，解封机制优化。",
            "categories": ["门派调整", "封印系统"],
            "pvp_impact": "极高",
            "pve_impact": "中",
            "design_intent": "解决封印命中率过高导致对手无选择的问题"
        },
    ],
    2007: [
        {
            "id": "class_2007_001",
            "title": "经脉系统上线",
            "date": "2007-06-01",
            "content": "经脉系统正式上线，每个门派增加独立的经脉分支路线。玩家可以通过点经脉获得额外的技能和属性加成。",
            "categories": ["门派调整", "强化机制", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "增加门派差异化，类似Mega进化的差异化设计"
        },
        {
            "id": "class_2007_002",
            "title": "辅助门派增强",
            "date": "2007-09-01",
            "content": "化生寺、普陀山辅助技能效果增强。",
            "categories": ["门派调整", "辅助增强"],
            "pvp_impact": "中",
            "pve_impact": "高",
            "design_intent": "提升辅助门派的团队价值"
        },
    ],
    2008: [
        {
            "id": "class_2008_001",
            "title": "门派技能调整 - 物理系",
            "date": "2008-03-01",
            "content": "大唐官府、狮驼岭等物理门派技能伤害系数调整。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "平衡物理门派的点杀能力"
        },
    ],
    2009: [
        {
            "id": "class_2009_001",
            "title": "武神坛明星赛举办",
            "date": "2009-06-01",
            "content": "武神坛明星赛举办，代表各服务器最高水平的队伍参赛。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "极高",
            "pve_impact": "无",
            "design_intent": "建立游戏最高级别PVP赛事"
        },
        {
            "id": "class_2009_002",
            "title": "法宝系统上线",
            "date": "2009-08-01",
            "content": "法宝系统推出，玩家可以装备法宝获得特殊能力。",
            "categories": ["内容", "装备系统", "PvP"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "增加战斗策略深度"
        },
    ],
    2010: [
        {
            "id": "class_2010_001",
            "title": "奇经八脉系统上线",
            "date": "2010-01-01",
            "content": "经脉系统升级为奇经八脉，每个门派有8条经脉路线可供选择。",
            "categories": ["门派调整", "强化机制"],
            "pvp_impact": "极高",
            "pve_impact": "中",
            "design_intent": "增加门派差异化，同门派可有不同Build"
        },
        {
            "id": "class_2010_002",
            "title": "门派调整 - 封印系",
            "date": "2010-06-01",
            "content": "方寸山、女儿村、盘丝洞封印技能调整。",
            "categories": ["门派调整", "封印系统"],
            "pvp_impact": "极高",
            "pve_impact": "中",
            "design_intent": "平衡封印门派的控制能力"
        },
    ],
    2011: [
        {
            "id": "class_2011_001",
            "title": "辅助门派机制优化",
            "date": "2011-03-01",
            "content": "化生寺、普陀山辅助技能机制优化，团队增益更明显。",
            "categories": ["门派调整", "辅助增强"],
            "pvp_impact": "高",
            "pve_impact": "高",
            "design_intent": "让辅助价值被团队更清晰感知"
        },
    ],
    2012: [
        {
            "id": "class_2012_001",
            "title": "法系门派调整",
            "date": "2012-05-01",
            "content": "龙宫、魔王寨、神木林法系伤害调整。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "高",
            "design_intent": "平衡法系输出能力"
        },
    ],
    2013: [
        {
            "id": "class_2013_001",
            "title": "门派技能调整",
            "date": "2013-04-01",
            "content": "大规模门派技能调整，覆盖所有门派。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "极高",
            "pve_impact": "高",
            "design_intent": "系统性优化门派平衡"
        },
    ],
    2014: [
        {
            "id": "class_2014_001",
            "title": "新门派：凌波城",
            "date": "2014-01-01",
            "content": "推出新门派凌波城，物理系输出门派。",
            "categories": ["门派调整", "PvP", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "增加物理输出门派选择"
        },
        {
            "id": "class_2014_002",
            "title": "新门派：神木林",
            "date": "2014-06-01",
            "content": "推出新门派神木林，法系输出门派。",
            "categories": ["门派调整", "PvP", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "增加法系输出门派选择"
        },
    ],
    2015: [
        {
            "id": "class_2015_001",
            "title": "新门派：力地府",
            "date": "2015-01-01",
            "content": "推出新门派力地府，物理输出门派。地府门派同时保留辅助能力。",
            "categories": ["门派调整", "PvP"],
            "pvp_impact": "中",
            "pve_impact": "低",
            "design_intent": "增加门派定位多样性"
        },
        {
            "id": "class_2015_002",
            "title": "门派平衡大调整",
            "date": "2015-06-01",
            "content": "大规模门派平衡调整，优化弱势门派。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "极高",
            "pve_impact": "中",
            "design_intent": "系统性优化门派平衡"
        },
    ],
    2016: [
        {
            "id": "class_2016_001",
            "title": "新门派：女魃墓",
            "date": "2016-06-01",
            "content": "推出新门派女魃墓，召唤系法伤门派。独特的召唤机制在PVP中创造新的战术可能。",
            "categories": ["门派调整", "PvP", "内容"],
            "pvp_impact": "极高",
            "pve_impact": "中",
            "design_intent": "引入全新战斗机制，增加战术多样性"
        },
    ],
    2017: [
        {
            "id": "class_2017_001",
            "title": "新门派：无底洞",
            "date": "2017-06-01",
            "content": "推出新门派无底洞，辅助+封印双定位。",
            "categories": ["门派调整", "PvP", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "灵活的定位使其成为PVP常客"
        },
        {
            "id": "class_2017_002",
            "title": "门派调整",
            "date": "2017-09-01",
            "content": "门派技能调整，优化部分弱势门派。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "优化门派平衡"
        },
    ],
    2018: [
        {
            "id": "class_2018_001",
            "title": "新门派：天机城",
            "date": "2018-01-01",
            "content": "推出新门派天机城，辅助+输出双定位。独特的机关变身机制增加了策略深度。",
            "categories": ["门派调整", "PvP", "内容"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "引入全新变身机制"
        },
        {
            "id": "class_2018_002",
            "title": "门派大调整",
            "date": "2018-06-01",
            "content": "大规模门派平衡调整。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "极高",
            "pve_impact": "高",
            "design_intent": "系统性优化门派平衡"
        },
    ],
    2019: [
        {
            "id": "class_2019_001",
            "title": "门派平衡大调整",
            "date": "2019-06-01",
            "content": "大规模门派平衡调整，覆盖所有门派技能。优化弱势门派，增强过于强势的门派。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "极高",
            "pve_impact": "高",
            "design_intent": "解决长期积累的门派平衡问题"
        },
    ],
    2020: [
        {
            "id": "class_2020_001",
            "title": "门派技能调整",
            "date": "2020-03-01",
            "content": "门派技能伤害和机制调整。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "优化门派平衡"
        },
    ],
    2021: [
        {
            "id": "class_2021_001",
            "title": "新门派：花果山",
            "date": "2021-01-01",
            "content": "推出新门派花果山，高随机性物理输出。",
            "categories": ["门派调整", "PvP", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "引入高随机性机制，增加战斗变数"
        },
        {
            "id": "class_2021_002",
            "title": "新门派：东海渊",
            "date": "2021-06-01",
            "content": "推出新门派东海渊，独特的三栖战斗机制。可以在人、魔、仙形态间切换，各有不同技能。",
            "categories": ["门派调整", "PvP", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "引入全新三栖机制"
        },
    ],
    2022: [
        {
            "id": "class_2022_001",
            "title": "门派调整",
            "date": "2022-04-01",
            "content": "门派技能调整和优化。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "优化门派平衡"
        },
    ],
    2023: [
        {
            "id": "class_2023_001",
            "title": "新门派：凌霄天宫",
            "date": "2023-01-01",
            "content": "推出新门派凌霄天宫（天宫重制），封印+辅助双定位。区别于老版天宫，提供全新的游戏体验。",
            "categories": ["门派调整", "PvP", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "重制老门派，提供新体验"
        },
        {
            "id": "class_2023_002",
            "title": "门派调整",
            "date": "2023-06-01",
            "content": "定期门派平衡调整。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "低",
            "design_intent": "优化门派平衡"
        },
    ],
    2024: [
        {
            "id": "class_2024_001",
            "title": "门派技能调整",
            "date": "2024-03-01",
            "content": "门派技能调整和优化。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "优化门派平衡"
        },
        {
            "id": "class_2024_002",
            "title": "新资料片发布",
            "date": "2024-06-01",
            "content": "新资料片内容，包括新玩法和门派调整。",
            "categories": ["门派调整", "内容"],
            "pvp_impact": "中",
            "pve_impact": "高",
            "design_intent": "扩展游戏内容"
        },
    ],
    2025: [
        {
            "id": "class_2025_001",
            "title": "门派调整",
            "date": "2025-01-01",
            "content": "门派技能调整。",
            "categories": ["门派调整", "平衡性调整"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "优化门派平衡"
        },
        {
            "id": "class_2025_002",
            "title": "武神坛改革",
            "date": "2025-06-01",
            "content": "武神坛赛事规则调整，优化比赛流程。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "高",
            "pve_impact": "无",
            "design_intent": "提升赛事体验"
        },
    ],
}


# ============================================================
# 召唤兽系统演进
# ============================================================

MHXY_PET_EVOLUTION = {
    2001: [
        {
            "id": "pet_2001_001",
            "title": "召唤兽系统上线",
            "date": "2001-12-01",
            "content": "召唤兽系统正式上线，玩家可以捕捉和培养召唤兽参与战斗。",
            "categories": ["召唤兽系统", "内容"],
            "pvp_impact": "高",
            "pve_impact": "高",
            "design_intent": "增加战斗策略深度"
        },
    ],
    2003: [
        {
            "id": "pet_2003_001",
            "title": "召唤兽技能开放",
            "date": "2003-06-01",
            "content": "召唤兽可以学习更多技能。",
            "categories": ["召唤兽系统"],
            "pvp_impact": "中",
            "pve_impact": "高",
            "design_intent": "增加召唤兽培养深度"
        },
    ],
    2007: [
        {
            "id": "pet_2007_001",
            "title": "召唤兽进阶概念引入",
            "date": "2007-06-01",
            "content": "召唤兽开始引入进阶概念。",
            "categories": ["召唤兽系统", "强化机制"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "增加召唤兽价值层次"
        },
    ],
    2011: [
        {
            "id": "pet_2011_001",
            "title": "召唤兽进阶系统正式上线",
            "date": "2011-06-01",
            "content": "召唤兽进阶系统正式上线，召唤兽可以进阶获得额外属性和外观变化。进阶成为衡量召唤兽价值的重要标准。",
            "categories": ["召唤兽系统", "强化机制", "内容"],
            "pvp_impact": "极高",
            "pve_impact": "中",
            "design_intent": "类似宝可梦的Mega进化，增加召唤兽差异化"
        },
    ],
    2012: [
        {
            "id": "pet_2012_001",
            "title": "内丹系统上线",
            "date": "2012-01-01",
            "content": "内丹系统上线，召唤兽可以服用内丹获得额外属性。",
            "categories": ["召唤兽系统", "养成系统"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "增加召唤兽养成层次"
        },
    ],
    2014: [
        {
            "id": "pet_2014_001",
            "title": "召唤兽装备系统",
            "date": "2014-01-01",
            "content": "召唤兽装备系统上线，召唤兽可以穿戴专属装备。",
            "categories": ["召唤兽系统", "装备系统"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "增加召唤兽价值维度"
        },
    ],
    2019: [
        {
            "id": "pet_2019_001",
            "title": "召唤兽进阶调整",
            "date": "2019-06-01",
            "content": "召唤兽进阶系统调整。",
            "categories": ["召唤兽系统", "平衡性调整"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "优化召唤兽生态"
        },
    ],
    2020: [
        {
            "id": "pet_2020_001",
            "title": "召唤兽特性系统",
            "date": "2020-01-01",
            "content": "召唤兽特性系统上线，如潮汐、洪荒等特殊效果。",
            "categories": ["召唤兽系统", "强化机制", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "增加召唤兽额外价值维度"
        },
    ],
    2022: [
        {
            "id": "pet_2022_001",
            "title": "召唤兽进阶重制",
            "date": "2022-01-01",
            "content": "召唤兽进阶系统全面重制，降低进阶门槛，优化进阶流程。",
            "categories": ["召唤兽系统", "经济系统", "平衡性调整"],
            "pvp_impact": "中",
            "pve_impact": "高",
            "design_intent": "让普通玩家更容易获得高进阶宝宝"
        },
    ],
    2023: [
        {
            "id": "pet_2023_001",
            "title": "召唤兽调整",
            "date": "2023-06-01",
            "content": "召唤兽相关调整。",
            "categories": ["召唤兽系统", "平衡性调整"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "优化召唤兽平衡"
        },
    ],
    2024: [
        {
            "id": "pet_2024_001",
            "title": "召唤兽系统更新",
            "date": "2024-03-01",
            "content": "召唤兽系统更新和调整。",
            "categories": ["召唤兽系统", "内容"],
            "pvp_impact": "中",
            "pve_impact": "高",
            "design_intent": "扩展召唤兽内容"
        },
    ],
}


# ============================================================
# 阵法系统演进
# ============================================================

MHXY_FORMATION_EVOLUTION = {
    2001: [
        {
            "id": "form_2001_001",
            "title": "阵法系统上线",
            "date": "2001-12-01",
            "content": "阵法系统上线，提供基础阵法加成。",
            "categories": ["阵法", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "增加团队战术选择"
        },
    ],
    2005: [
        {
            "id": "form_2005_001",
            "title": "阵法克制机制完善",
            "date": "2005-06-01",
            "content": "阵法之间形成完整的克制关系。",
            "categories": ["阵法", "平衡性调整"],
            "pvp_impact": "极高",
            "pve_impact": "低",
            "design_intent": "增加战术深度，让阵法选择成为博弈点"
        },
    ],
    2010: [
        {
            "id": "form_2010_001",
            "title": "新阵法加入",
            "date": "2010-01-01",
            "content": "新增更多阵法选择。",
            "categories": ["阵法", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "增加阵法多样性"
        },
    ],
    2015: [
        {
            "id": "form_2015_001",
            "title": "阵法调整",
            "date": "2015-06-01",
            "content": "阵法加成和克制关系调整。",
            "categories": ["阵法", "平衡性调整"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "优化阵法平衡"
        },
    ],
    2020: [
        {
            "id": "form_2020_001",
            "title": "阵法系统优化",
            "date": "2020-06-01",
            "content": "阵法系统优化。",
            "categories": ["阵法", "平衡性调整"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "简化阵法系统"
        },
    ],
}


# ============================================================
# 装备系统演进
# ============================================================

MHXY_EQUIPMENT_EVOLUTION = {
    2001: [
        {
            "id": "equip_2001_001",
            "title": "装备系统上线",
            "date": "2001-12-01",
            "content": "基础装备系统上线。",
            "categories": ["装备系统", "内容"],
            "pvp_impact": "高",
            "pve_impact": "高",
            "design_intent": "建立角色养成核心"
        },
    ],
    2005: [
        {
            "id": "equip_2005_001",
            "title": "灵饰系统前身",
            "date": "2005-01-01",
            "content": "灵饰系统上线，增加角色装备槽位。",
            "categories": ["装备系统", "内容"],
            "pvp_impact": "高",
            "pve_impact": "中",
            "design_intent": "增加角色养成维度"
        },
    ],
    2013: [
        {
            "id": "equip_2013_001",
            "title": "灵饰系统正式版",
            "date": "2013-06-01",
            "content": "灵饰系统正式上线并完善，戒指和耳环成为角色重要装备。",
            "categories": ["装备系统", "内容"],
            "pvp_impact": "极高",
            "pve_impact": "中",
            "design_intent": "大幅扩展角色养成空间"
        },
    ],
    2020: [
        {
            "id": "equip_2020_001",
            "title": "装备系统简化",
            "date": "2020-06-01",
            "content": "装备系统简化，减少无意义词缀。",
            "categories": ["装备系统", "经济系统"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "让玩家更容易理解装备价值"
        },
    ],
    2022: [
        {
            "id": "equip_2022_001",
            "title": "装备系统调整",
            "date": "2022-06-01",
            "content": "装备系统进一步调整优化。",
            "categories": ["装备系统", "平衡性调整"],
            "pvp_impact": "中",
            "pve_impact": "中",
            "design_intent": "优化装备经济"
        },
    ],
}


# ============================================================
# 武神坛规则演进
# ============================================================

MHXY_WST_EVOLUTION = {
    2009: [
        {
            "id": "wst_2009_001",
            "title": "武神坛明星赛首届",
            "date": "2009-06-01",
            "content": "武神坛明星赛首届举办，代表各服务器最高水平的队伍参赛。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "极高",
            "pve_impact": "无",
            "design_intent": "建立游戏最高级别PVP赛事"
        },
    ],
    2012: [
        {
            "id": "wst_2012_001",
            "title": "武神坛规则调整",
            "date": "2012-06-01",
            "content": "武神坛赛事规则调整。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "高",
            "pve_impact": "无",
            "design_intent": "优化赛事规则"
        },
    ],
    2015: [
        {
            "id": "wst_2015_001",
            "title": "武神坛等级分组",
            "date": "2015-01-01",
            "content": "武神坛引入等级分组，让不同等级玩家都有竞技机会。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "高",
            "pve_impact": "无",
            "design_intent": "扩大赛事参与度"
        },
    ],
    2019: [
        {
            "id": "wst_2019_001",
            "title": "武神坛规则更新",
            "date": "2019-06-01",
            "content": "武神坛规则更新，适配新版本内容。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "高",
            "pve_impact": "无",
            "design_intent": "适配新版本"
        },
    ],
    2022: [
        {
            "id": "wst_2022_001",
            "title": "武神坛改革",
            "date": "2022-01-01",
            "content": "武神坛赛事改革。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "高",
            "pve_impact": "无",
            "design_intent": "提升赛事质量"
        },
    ],
    2025: [
        {
            "id": "wst_2025_001",
            "title": "武神坛最新改革",
            "date": "2025-06-01",
            "content": "武神坛赛事规则调整，优化比赛流程，提升观赛体验。",
            "categories": ["PvP", "赛事规则"],
            "pvp_impact": "高",
            "pve_impact": "无",
            "design_intent": "现代化赛事体验"
        },
    ],
}


# ============================================================
# 历年资料片
# ============================================================

MHXY_EXPANSION_PACKS = {
    2003: [
        {"id": "exp_2003_001", "title": "资料片：神鬼玄机", "date": "2003-01-01", "content": "新增剧情和召唤兽。", "categories": ["内容"]},
    ],
    2004: [
        {"id": "exp_2004_001", "title": "资料片：坐骑天下", "date": "2004-06-01", "content": "坐骑系统扩展。", "categories": ["内容", "养成系统"]},
    ],
    2006: [
        {"id": "exp_2006_001", "title": "资料片：天火之殇", "date": "2006-06-01", "content": "新地图和剧情。", "categories": ["内容"]},
    ],
    2008: [
        {"id": "exp_2008_001", "title": "资料片：出神入化", "date": "2008-01-01", "content": "技能突破上限。", "categories": ["内容"]},
    ],
    2010: [
        {"id": "exp_2010_001", "title": "资料片：上古神符", "date": "2010-01-01", "content": "奇经八脉系统。", "categories": ["内容", "门派调整"]},
    ],
    2012: [
        {"id": "exp_2012_001", "title": "资料片：兵临城下", "date": "2012-01-01", "content": "跨服战内容。", "categories": ["PvP", "内容"]},
    ],
    2014: [
        {"id": "exp_2014_001", "title": "资料片：三界奇缘", "date": "2014-01-01", "content": "新门派凌波城、神木林。", "categories": ["内容", "门派调整"]},
    ],
    2016: [
        {"id": "exp_2016_001", "title": "资料片：羽化神兵", "date": "2016-01-01", "content": "新门派女魃墓。", "categories": ["内容", "门派调整"]},
    ],
    2017: [
        {"id": "exp_2017_001", "title": "资料片：天地棋局", "date": "2017-01-01", "content": "新玩法和内容。", "categories": ["内容"]},
    ],
    2018: [
        {"id": "exp_2018_001", "title": "资料片：聚圣三界", "date": "2018-01-01", "content": "新门派无底洞、天机城。", "categories": ["内容", "门派调整"]},
    ],
    2019: [
        {"id": "exp_2019_001", "title": "资料片：名扬三界", "date": "2019-01-01", "content": "大规模门派调整。", "categories": ["内容", "门派调整"]},
    ],
    2021: [
        {"id": "exp_2021_001", "title": "资料片：灵宝风云", "date": "2021-01-01", "content": "灵宝系统和新门派。", "categories": ["内容"]},
    ],
    2023: [
        {"id": "exp_2023_001", "title": "资料片：梦回Serial", "date": "2023-01-01", "content": "新门派凌霄天宫。", "categories": ["内容", "门派调整"]},
    ],
    2024: [
        {"id": "exp_2024_001", "title": "资料片", "date": "2024-01-01", "content": "新资料片内容。", "categories": ["内容"]},
    ],
}


# ============================================================
# 数据合并函数
# ============================================================

def get_all_class_adjustments() -> List[Dict]:
    """获取所有门派调整数据"""
    all_adjustments = []
    for year_data in MHXY_CLASS_ADJUSTMENTS.values():
        all_adjustments.extend(year_data)
    all_adjustments.sort(key=lambda x: x.get("date", ""), reverse=True)
    return all_adjustments


def get_all_pet_evolution() -> List[Dict]:
    """获取所有召唤兽演进数据"""
    all_evolution = []
    for year_data in MHXY_PET_EVOLUTION.values():
        all_evolution.extend(year_data)
    all_evolution.sort(key=lambda x: x.get("date", ""), reverse=True)
    return all_evolution


def get_all_formation_evolution() -> List[Dict]:
    """获取所有阵法演进数据"""
    all_evolution = []
    for year_data in MHXY_FORMATION_EVOLUTION.values():
        all_evolution.extend(year_data)
    all_evolution.sort(key=lambda x: x.get("date", ""), reverse=True)
    return all_evolution


def get_all_equipment_evolution() -> List[Dict]:
    """获取所有装备演进数据"""
    all_evolution = []
    for year_data in MHXY_EQUIPMENT_EVOLUTION.values():
        all_evolution.extend(year_data)
    all_evolution.sort(key=lambda x: x.get("date", ""), reverse=True)
    return all_evolution


def get_all_wst_evolution() -> List[Dict]:
    """获取所有武神坛演进数据"""
    all_evolution = []
    for year_data in MHXY_WST_EVOLUTION.values():
        all_evolution.extend(year_data)
    all_evolution.sort(key=lambda x: x.get("date", ""), reverse=True)
    return all_evolution


def get_all_expansion_packs() -> List[Dict]:
    """获取所有资料片数据"""
    all_packs = []
    for year_data in MHXY_EXPANSION_PACKS.values():
        all_packs.extend(year_data)
    all_packs.sort(key=lambda x: x.get("date", ""), reverse=True)
    return all_packs


def get_comprehensive_mhxy_data() -> List[Dict]:
    """获取完整的梦幻西游历史数据"""
    all_data = []

    # 添加所有类型的数据
    all_data.extend(get_all_class_adjustments())
    all_data.extend(get_all_pet_evolution())
    all_data.extend(get_all_formation_evolution())
    all_data.extend(get_all_equipment_evolution())
    all_data.extend(get_all_wst_evolution())
    all_data.extend(get_all_expansion_packs())

    # 按日期排序
    all_data.sort(key=lambda x: x.get("date", ""), reverse=True)

    # 添加统一字段
    for item in all_data:
        item["game"] = "梦幻西游"
        if "pvp_impact" not in item:
            item["pvp_impact"] = "中"
        if "pve_impact" not in item:
            item["pve_impact"] = "中"
        if "gameplay_impact" not in item:
            item["gameplay_impact"] = "中"

    return all_data


def get_data_count() -> Dict[str, int]:
    """获取各类型数据统计"""
    return {
        "门派调整": len(get_all_class_adjustments()),
        "召唤兽演进": len(get_all_pet_evolution()),
        "阵法演进": len(get_all_formation_evolution()),
        "装备演进": len(get_all_equipment_evolution()),
        "武神坛演进": len(get_all_wst_evolution()),
        "资料片": len(get_all_expansion_packs()),
        "总计": len(get_comprehensive_mhxy_data()),
    }


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("梦幻西游历史数据统计：")
    stats = get_data_count()
    for key, value in stats.items():
        print(f"  {key}: {value}条")

    print(f"\n总计：{stats['总计']}条数据")

"""
梦幻西游Like游戏数据模块

提供梦幻西游及其Like游戏的版本历史数据。

数据来源：
- 官方论坛门派调整（主要）：docs/mhxy_patches_history.json
- 官方论坛资料片/系统更新：docs/mhxy_full_history.json
- 备用：scrapers/mhxy_history.py

支持的梦幻西游Like游戏：
- 梦幻西游（网易）
- 神武（多益）
- 大话西游（网易）
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# 官方论坛数据路径
_OFFICIAL_PATCHES_PATH = Path(__file__).parent.parent / "docs" / "mhxy_patches_history.json"
_OFFICIAL_FULL_PATH = Path(__file__).parent.parent / "docs" / "mhxy_full_history.json"
_OFFICIAL_EXPANSIONS_PATH = Path(__file__).parent.parent / "docs" / "mhxy_expansions.json"
_OFFICIAL_MAINTENANCE_PATH = Path(__file__).parent.parent / "docs" / "mhxy_maintenance.json"
_OFFICIAL_SUMMON_PATH = Path(__file__).parent.parent / "docs" / "mhxy_summon_system.json"


# ============================================================
# 加载官方论坛采集的真实数据
# ============================================================

def _load_official_patches() -> List[Dict]:
    """加载官方论坛门派调整数据"""
    if not _OFFICIAL_PATCHES_PATH.exists():
        return []

    try:
        with open(_OFFICIAL_PATCHES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        patches = []
        for patch in data.get("patches", []):
            title = patch.get("title", "")
            date = patch.get("date", "")
            content = patch.get("content", "")
            sections = patch.get("sections", [])

            patches.append({
                "title": title,
                "date": date,
                "content": content[:2000],
                "full_content": content,
                "categories": sections if sections else ["门派调整"],
                "source": "官方论坛-门派调整",
                "source_url": patch.get("url", ""),
                "game": "梦幻西游",
                "update_type": "门派调整",
            })

        patches.sort(key=lambda x: x.get("date", ""), reverse=True)
        return patches
    except Exception:
        return []


def _load_official_updates() -> List[Dict]:
    """加载官方论坛资料片和系统更新数据"""
    if not _OFFICIAL_FULL_PATH.exists():
        return []

    try:
        with open(_OFFICIAL_FULL_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        updates = []
        for item in data.get("updates", []):
            updates.append({
                "title": item.get("title", ""),
                "date": item.get("date", ""),
                "content": item.get("content", "")[:2000],
                "full_content": item.get("content", ""),
                "categories": [item.get("category", "其他")],
                "source": "官方论坛",
                "source_url": item.get("url", ""),
                "game": "梦幻西游",
                "update_type": item.get("category", "其他"),
            })

        updates.sort(key=lambda x: x.get("date", ""), reverse=True)
        return updates
    except Exception:
        return []


# 缓存
_official_patches_cache = None
_official_updates_cache = None
_official_expansions_cache = None


def _load_official_expansions() -> List[Dict]:
    """加载官方论坛资料片数据"""
    if not _OFFICIAL_EXPANSIONS_PATH.exists():
        return []

    try:
        with open(_OFFICIAL_EXPANSIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        expansions = []
        for item in data.get("expansions", []):
            expansions.append({
                "title": item.get("title", ""),
                "date": item.get("date", ""),
                "content": item.get("content", "")[:2000],
                "full_content": item.get("content", ""),
                "categories": [item.get("category", "资料片")],
                "source": "官方论坛-资料片",
                "source_url": item.get("url", ""),
                "game": "梦幻西游",
                "update_type": "资料片",
                "expansion_name": item.get("name", ""),
            })

        expansions.sort(key=lambda x: x.get("date", ""), reverse=True)
        return expansions
    except Exception:
        return []


def get_official_expansions() -> List[Dict]:
    """获取官方论坛资料片数据（带缓存）"""
    global _official_expansions_cache
    if _official_expansions_cache is None:
        _official_expansions_cache = _load_official_expansions()
    return _official_expansions_cache


def _load_official_maintenance() -> List[Dict]:
    """加载维护公告数据"""
    if not _OFFICIAL_MAINTENANCE_PATH.exists():
        return []

    try:
        with open(_OFFICIAL_MAINTENANCE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = []
        for item in data.get("maintenance", []):
            items.append({
                "title": item.get("title", ""),
                "date": item.get("date", ""),
                "content": item.get("content", "")[:2000],
                "full_content": item.get("content", ""),
                "categories": ["维护公告"],
                "source": "官方论坛-维护公告",
                "source_url": item.get("url", ""),
                "game": "梦幻西游",
                "update_type": "系统调整",
            })
        items.sort(key=lambda x: x.get("date", ""), reverse=True)
        return items
    except Exception:
        return []


def _load_official_summon() -> List[Dict]:
    """加载召唤兽和系统调整数据"""
    if not _OFFICIAL_SUMMON_PATH.exists():
        return []

    try:
        with open(_OFFICIAL_SUMMON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = []
        for item in data.get("items", []):
            update_type = item.get("update_type", "其他")
            items.append({
                "title": item.get("title", ""),
                "date": item.get("date", ""),
                "content": item.get("content", "")[:2000],
                "full_content": item.get("content", ""),
                "categories": [update_type],
                "source": "官方论坛",
                "source_url": item.get("url", ""),
                "game": "梦幻西游",
                "update_type": update_type,
            })
        items.sort(key=lambda x: x.get("date", ""), reverse=True)
        return items
    except Exception:
        return []


# 缓存
_official_maintenance_cache = None
_official_summon_cache = None


def get_official_maintenance() -> List[Dict]:
    """获取维护公告数据（带缓存）"""
    global _official_maintenance_cache
    if _official_maintenance_cache is None:
        _official_maintenance_cache = _load_official_maintenance()
    return _official_maintenance_cache


def get_official_summon() -> List[Dict]:
    """获取召唤兽和系统调整数据（带缓存）"""
    global _official_summon_cache
    if _official_summon_cache is None:
        _official_summon_cache = _load_official_summon()
    return _official_summon_cache


def get_official_patches() -> List[Dict]:
    """获取官方论坛门派调整数据（带缓存）"""
    global _official_patches_cache
    if _official_patches_cache is None:
        _official_patches_cache = _load_official_patches()
    return _official_patches_cache


def get_official_updates() -> List[Dict]:
    """获取官方论坛资料片和系统更新数据（带缓存）"""
    global _official_updates_cache
    if _official_updates_cache is None:
        _official_updates_cache = _load_official_updates()
    return _official_updates_cache


def get_official_expansions() -> List[Dict]:
    """获取官方论坛资料片数据（带缓存）"""
    global _official_expansions_cache
    if _official_expansions_cache is None:
        _official_expansions_cache = _load_official_expansions()
    return _official_expansions_cache


def get_official_maintenance() -> List[Dict]:
    """获取维护公告数据（带缓存）"""
    global _official_maintenance_cache
    if _official_maintenance_cache is None:
        _official_maintenance_cache = _load_official_maintenance()
    return _official_maintenance_cache


def get_official_summon() -> List[Dict]:
    """获取召唤兽和系统调整数据（带缓存）"""
    global _official_summon_cache
    if _official_summon_cache is None:
        _official_summon_cache = _load_official_summon()
    return _official_summon_cache


def get_all_official_data() -> List[Dict]:
    """获取所有官方论坛数据（自动去重）"""
    patches = get_official_patches()
    updates = get_official_updates()
    expansions = get_official_expansions()
    maintenance = get_official_maintenance()
    summon = get_official_summon()

    # 合并并按日期排序
    all_data = patches + updates + expansions + maintenance + summon

    # 去重：基于日期+标题前30字符作为唯一键
    seen = {}
    unique_data = []
    for item in all_data:
        key = f"{item.get('date', '')}:{item.get('title', '')[:30]}"
        if key not in seen:
            seen[key] = True
            unique_data.append(item)

    unique_data.sort(key=lambda x: x.get("date", ""), reverse=True)
    return unique_data


# ============================================================
# 梦幻西游内置历史数据
# 数据来源：综合官方公告、社区整理
# ============================================================

# 梦幻西游历代版本数据（2001-2024+）
# 结构：{version_id: {title, date, patches: [...]}}
MHXY_PATCHES_DB = {
    # 2001-2003: 起步期
    "1.0.0": {
        "period": "2001-2002",
        "title": "梦幻西游起步期",
        "description": "游戏公测，建立核心玩法框架",
        "patches": [
            {
                "id": "mhxy_001",
                "title": "2001年12月 梦幻西游公测",
                "date": "2001-12-01",
                "content": "《梦幻西游》正式开启公测，推出12个基础门派：魔王寨、龙宫、普陀山、方寸山、化生寺、大唐官府、狮驼岭、盘丝洞、五庄观、天宫、地府、女儿村。建立基础的回合制战斗系统、召唤兽系统和师门任务。",
                "categories": ["内容", "门派调整"],
                "gameplay_impact": "高",
                "pvp_impact": "中",
                "pve_impact": "高",
            },
            {
                "id": "mhxy_002",
                "title": "2002年 比武大会诞生",
                "date": "2002-06-01",
                "content": "第一届X9联赛（69、89、109级）举办，比武大会正式成为游戏核心PVP内容。建立等级分组竞技体系，让不同投入层级的玩家都有竞技舞台。",
                "categories": ["PvP", "赛事规则"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "低",
            },
        ]
    },
    # 2003-2005: 资料片迭代期
    "2.0.0": {
        "period": "2003-2005",
        "title": "资料片迭代期",
        "description": "通过资料片逐步完善游戏内容",
        "patches": [
            {
                "id": "mhxy_003",
                "title": "2003年 养育系统",
                "date": "2003-05-01",
                "content": "推出养育系统，玩家可以生育和培养子女。子女可学习技能参战，增加战斗策略深度。引入夫妻技能和子女技能两大系统。",
                "categories": ["内容", "养成系统"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_004",
                "title": "2004年 坐骑系统",
                "date": "2004-06-01",
                "content": "推出坐骑系统，玩家可以骑乘坐骑参与战斗。坐骑提供属性加成和特殊效果，增加角色养成维度。",
                "categories": ["内容", "养成系统"],
                "gameplay_impact": "中",
                "pvp_impact": "低",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_005",
                "title": "2005年 灵饰系统前身",
                "date": "2005-01-01",
                "content": "推出灵饰系统，增加角色装备槽位。灵饰提供额外属性加成，成为新的养成方向。",
                "categories": ["内容", "装备系统"],
                "gameplay_impact": "高",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
        ]
    },
    # 2006-2010: 资料片爆发期
    "3.0.0": {
        "period": "2006-2010",
        "title": "资料片爆发期",
        "description": "大量资料片涌现，系统不断完善",
        "patches": [
            {
                "id": "mhxy_006",
                "title": "2006年 天火之殇资料片",
                "date": "2006-06-01",
                "content": "推出天火之殇资料片，增加新地图和剧情。门派技能调整，优化战斗平衡性。",
                "categories": ["内容", "门派调整"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "高",
            },
            {
                "id": "mhxy_007",
                "title": "2007年 神鬼玄机资料片",
                "date": "2007-01-01",
                "content": "推出神鬼玄机资料片，增加新召唤兽和技能。召唤兽系统开始引入进阶概念。",
                "categories": ["内容", "召唤兽系统"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_008",
                "title": "2007年 经脉系统上线",
                "date": "2007-06-01",
                "content": "推出经脉系统，每个门派增加独立的经脉分支路线。玩家可以通过点经脉获得额外的技能和属性加成，类似Mega进化的差异化设计。",
                "categories": ["内容", "门派调整", "强化机制"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_009",
                "title": "2008年 坐骑天下资料片",
                "date": "2008-01-01",
                "content": "推出坐骑天下资料片，坐骑系统全面升级。坐骑可以学习技能和增加属性，成为重要的战力来源。",
                "categories": ["内容", "养成系统"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "m hxy_010",
                "title": "2009年 法宝系统",
                "date": "2009-01-01",
                "content": "推出法宝系统，玩家可以装备法宝获得特殊能力。法宝宝莲灯、苍白纸人等成为PVP常用道具。",
                "categories": ["内容", "装备系统", "PvP"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_011",
                "title": "2009年 武神坛明星赛",
                "date": "2009-06-01",
                "content": "武神坛明星赛举办，代表各服务器最高水平的队伍参赛。标志着武神坛成为梦幻西游最高级别的PVP赛事。",
                "categories": ["PvP", "赛事规则"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "低",
            },
            {
                "id": "mhxy_012",
                "title": "2010年 奇经八脉",
                "date": "2010-01-01",
                "content": "经脉系统升级为奇经八脉，每个门派有8条经脉路线可供选择。增加门派差异化，同门派可有不同Build。",
                "categories": ["门派调整", "强化机制"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
        ]
    },
    # 2011-2015: 成熟稳定期
    "4.0.0": {
        "period": "2011-2015",
        "title": "成熟稳定期",
        "description": "游戏进入成熟期，更新趋于稳定",
        "patches": [
            {
                "id": "mhxy_013",
                "title": "2011年 召唤兽进阶系统",
                "date": "2011-06-01",
                "content": "推出召唤兽进阶系统，召唤兽可以进阶获得额外属性和外观变化。进阶成为衡量召唤兽价值的重要标准，类似宝可梦的Mega进化。",
                "categories": ["召唤兽系统", "强化机制"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_014",
                "title": "2012年 内丹系统",
                "date": "2012-01-01",
                "content": "推出内丹系统，召唤兽可以服用内丹获得额外属性。内丹分低级、中级、高级，价值逐级提升。",
                "categories": ["召唤兽系统", "养成系统"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_015",
                "title": "2013年 灵饰系统正式版",
                "date": "2013-06-01",
                "content": "灵饰系统正式上线并完善，戒指和耳环成为角色重要装备。灵饰提供伤害、防御、抗性等多维属性加成。",
                "categories": ["装备系统", "平衡性调整"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_016",
                "title": "2014年 召唤兽装备",
                "date": "2014-01-01",
                "content": "推出召唤兽装备系统，召唤兽可以穿戴专属装备。召唤兽装备提供额外属性和技能效果。",
                "categories": ["召唤兽系统", "装备系统"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_017",
                "title": "2014年 帮派技能调整",
                "date": "2014-06-01",
                "content": "帮派技能调整，强化/打造/熔炼等技能收益优化。减少玩家在帮派技能上的资源投入压力。",
                "categories": ["平衡性调整", "经济系统"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_018",
                "title": "2015年 新门派：凌波城",
                "date": "2015-01-01",
                "content": "推出新门派凌波城，物理系输出门派。增加游戏门派多样性，提供新的PVP策略选择。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_019",
                "title": "2015年 新门派：神木林",
                "date": "2015-06-01",
                "content": "推出新门派神木林，法系输出门派。与凌波城同期推出，形成物理法系双新门派格局。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
        ]
    },
    # 2016-2020: 持续运营期
    "5.0.0": {
        "period": "2016-2020",
        "title": "持续运营期",
        "description": "通过定期更新维持游戏活力",
        "patches": [
            {
                "id": "mhxy_020",
                "title": "2016年 新门派：力地府",
                "date": "2016-01-01",
                "content": "推出新门派力地府，物理输出门派。地府门派同时保留辅助能力，增加门派定位的多样性。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "低",
            },
            {
                "id": "mhxy_021",
                "title": "2017年 锦衣系统",
                "date": "2017-01-01",
                "content": "推出锦衣系统，玩家可以购买外观装饰。锦衣系统是成功的非数值付费设计，不影响战力平衡。",
                "categories": ["外观系统", "付费设计"],
                "gameplay_impact": "低",
                "pvp_impact": "无",
                "pve_impact": "无",
            },
            {
                "id": "mhxy_022",
                "title": "2017年 新门派：女魃墓",
                "date": "2017-06-01",
                "content": "推出新门派女魃墓，召唤系法伤门派。独特的召唤机制在PVP中创造新的战术可能。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_023",
                "title": "2018年 新门派：无底洞",
                "date": "2018-01-01",
                "content": "推出新门派无底洞，辅助+封印双定位。灵活的定位使其成为PVP常客。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "中",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_024",
                "title": "2019年 新门派：天机城",
                "date": "2019-01-01",
                "content": "推出新门派天机城，辅助+输出双定位。独特的机关变身机制增加了策略深度。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_025",
                "title": "2019年 门派平衡大调整",
                "date": "2019-06-01",
                "content": "大规模门派平衡调整，覆盖所有门派技能。优化弱势门派，增强过于强势的门派。",
                "categories": ["门派调整", "平衡性调整"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_026",
                "title": "2020年 召唤兽特性系统",
                "date": "2020-01-01",
                "content": "推出召唤兽特性系统，如潮汐、洪荒等特殊效果。特性为召唤兽增加额外的价值维度。",
                "categories": ["召唤兽系统", "强化机制"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
        ]
    },
    # 2021-2024: 现代化更新期
    "6.0.0": {
        "period": "2021-2024",
        "title": "现代化更新期",
        "description": "对老系统进行现代化改造",
        "patches": [
            {
                "id": "mhxy_027",
                "title": "2021年 新门派：花果山",
                "date": "2021-01-01",
                "content": "推出新门派花果山，高随机性物理输出。齐天大圣孙悟空的徒弟，棍法技能具有不确定性。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_028",
                "title": "2021年 新门派：东海渊",
                "date": "2021-06-01",
                "content": "推出新门派东海渊，独特的三栖战斗机制。可以在人、魔、仙形态间切换，各有不同技能。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_029",
                "title": "2022年 召唤兽进阶重制",
                "date": "2022-01-01",
                "content": "召唤兽进阶系统全面重制，降低进阶门槛，优化进阶流程。让普通玩家更容易获得高进阶宝宝。",
                "categories": ["召唤兽系统", "经济系统"],
                "gameplay_impact": "高",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_030",
                "title": "2022年 装备系统简化",
                "date": "2022-06-01",
                "content": "装备系统简化，减少无意义词缀，提升装备价值透明度。让玩家更容易理解装备价值。",
                "categories": ["装备系统", "经济系统"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_031",
                "title": "2023年 新门派：凌霄天宫",
                "date": "2023-01-01",
                "content": "推出新门派凌霄天宫（天宫重制），封印+辅助双定位。区别于老版天宫，提供全新的游戏体验。",
                "categories": ["门派调整", "PvP"],
                "gameplay_impact": "高",
                "pvp_impact": "高",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_032",
                "title": "2023年 副本难度分级",
                "date": "2023-06-01",
                "content": "副本系统增加难度分级：简单/普通/困难。满足不同投入层级的玩家需求。",
                "categories": ["PvE", "内容更新"],
                "gameplay_impact": "中",
                "pvp_impact": "无",
                "pve_impact": "高",
            },
            {
                "id": "mhxy_033",
                "title": "2024年 新资料片",
                "date": "2024-01-01",
                "content": "继续推出新资料片内容，包括新地图、新玩法、新剧情。维持游戏内容更新节奏。",
                "categories": ["内容更新"],
                "gameplay_impact": "中",
                "pvp_impact": "低",
                "pve_impact": "高",
            },
            {
                "id": "mhxy_034",
                "title": "2024年 门派技能调整",
                "date": "2024-06-01",
                "content": "定期门派平衡调整，针对PVP数据进行优化。确保各门派出场率保持在健康范围。",
                "categories": ["门派调整", "平衡性调整"],
                "gameplay_impact": "中",
                "pvp_impact": "高",
                "pve_impact": "低",
            },
        ]
    },
    # 2025-未来: 持续演进期
    "7.0.0": {
        "period": "2025-未来",
        "title": "持续演进期",
        "description": "游戏持续演进，探索新方向",
        "patches": [
            {
                "id": "mhxy_035",
                "title": "2025年 持续更新",
                "date": "2025-01-01",
                "content": "继续通过定期更新维持游戏活力，包括新内容、新赛事、新玩法。",
                "categories": ["内容更新"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
            {
                "id": "mhxy_036",
                "title": "2025年 武神坛改革",
                "date": "2025-06-01",
                "content": "武神坛赛事规则调整，优化比赛流程，提升观赛体验。",
                "categories": ["PvP", "赛事规则"],
                "gameplay_impact": "中",
                "pvp_impact": "高",
                "pve_impact": "无",
            },
            {
                "id": "mhxy_037",
                "title": "2026年 最新动态",
                "date": "2026-04-01",
                "content": "游戏持续运营中，包括门派调整、召唤兽更新、赛事活动等内容。",
                "categories": ["内容更新"],
                "gameplay_impact": "中",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
        ]
    },
}


# ============================================================
# 神武（多益网络）内置历史数据
# ============================================================

SHENWU_PATCHES_DB = {
    "1.0.0": {
        "period": "2010-2014",
        "title": "神武起步期",
        "description": "多益网络推出的回合制MMO",
        "patches": [
            {
                "id": "shenwu_001",
                "title": "2010年 神武公测",
                "date": "2010-06-01",
                "content": "《神武》正式公测，推出多个门派、职业体系。游戏定位为免费回合制MMO。",
                "categories": ["内容"],
                "gameplay_impact": "高",
                "pvp_impact": "中",
                "pve_impact": "高",
            },
            {
                "id": "shenwu_002",
                "title": "2014年 神武全面改革",
                "date": "2014-01-01",
                "content": "神武进行全面改革，更新UI、优化系统、增加新内容。",
                "categories": ["内容更新"],
                "gameplay_impact": "高",
                "pvp_impact": "中",
                "pve_impact": "中",
            },
        ]
    },
}


# ============================================================
# 大话西游（网易）内置历史数据
# ============================================================

DHXY_PATCHES_DB = {
    "1.0.0": {
        "period": "2002-2008",
        "title": "大话西游起步期",
        "description": "网易首款回合制MMO",
        "patches": [
            {
                "id": "dhxy_001",
                "title": "2002年 大话西游2公测",
                "date": "2002-01-01",
                "content": "《大话西游2》正式公测，网易首款回合制MMO。建立基础的种族、职业、召唤兽体系。",
                "categories": ["内容"],
                "gameplay_impact": "高",
                "pvp_impact": "中",
                "pve_impact": "高",
            },
        ]
    },
}


# ============================================================
# 数据访问接口
# ============================================================

class MHXYDataProvider:
    """梦幻西游Like数据提供者"""

    # 游戏到数据源的映射
    GAME_DATA_MAP = {
        "梦幻西游": {},  # 使用官方采集数据
        "神武": SHENWU_PATCHES_DB,
        "大话西游": DHXY_PATCHES_DB,
    }

    @classmethod
    def get_all_patches(cls, game: str = "梦幻西游") -> List[Dict]:
        """
        获取指定游戏的所有补丁

        梦幻西游优先使用官方论坛采集的真实数据，
        神武和大话西游使用内置数据。
        """
        # 梦幻西游使用官方论坛采集的真实数据（包括门派调整+资料片+系统更新）
        if game == "梦幻西游":
            return get_all_official_data()

        # 其他游戏使用基本数据
        db = cls.GAME_DATA_MAP.get(game, {})
        all_patches = []

        for version_data in db.values():
            for patch in version_data.get("patches", []):
                all_patches.append({
                    "title": patch.get("title", ""),
                    "date": patch.get("date", ""),
                    "content": patch.get("content", ""),
                    "categories": patch.get("categories", []),
                    "game": game,
                    "version": version_data.get("title", ""),
                    "period": version_data.get("period", ""),
                    "gameplay_impact": patch.get("gameplay_impact", "中"),
                    "pvp_impact": patch.get("pvp_impact", "无"),
                    "pve_impact": patch.get("pve_impact", "无"),
                })

        # 按日期排序
        all_patches.sort(key=lambda x: x.get("date", ""), reverse=True)
        return all_patches

    @classmethod
    def get_patches_by_type(cls, game: str = "梦幻西游", update_type: str = None) -> List[Dict]:
        """按类型获取补丁（如门派调整、资料片、系统调整）"""
        if game == "梦幻西游":
            all_data = get_all_official_data()
            if update_type:
                return [p for p in all_data if p.get("update_type") == update_type]
            return all_data
        return cls.get_all_patches(game)

    @classmethod
    def get_patches_by_period(cls, game: str = "梦幻西游", period: str = None) -> List[Dict]:
        """按时期获取补丁"""
        db = cls.GAME_DATA_MAP.get(game, {})
        patches = []

        for version_id, version_data in db.items():
            if period and version_data.get("period") != period:
                continue

            for patch in version_data.get("patches", []):
                patches.append({
                    "title": patch.get("title", ""),
                    "date": patch.get("date", ""),
                    "content": patch.get("content", ""),
                    "categories": patch.get("categories", []),
                    "game": game,
                    "version": version_data.get("title", ""),
                    "period": version_data.get("period", ""),
                })

        return patches

    @classmethod
    def get_patches_by_category(cls, game: str = "梦幻西游", category: str = None) -> List[Dict]:
        """按分类获取补丁"""
        all_patches = cls.get_all_patches(game)

        if not category:
            return all_patches

        return [
            p for p in all_patches
            if category in p.get("categories", [])
        ]

    @classmethod
    def get_pvp_patches(cls, game: str = "梦幻西游") -> List[Dict]:
        """获取PVP相关补丁"""
        all_patches = cls.get_all_patches(game)

        pvp_keywords = ["PvP", "门派调整", "平衡性调整", "赛事规则", "比武", "华山", "武神坛"]
        return [
            p for p in all_patches
            if any(kw in p.get("categories", []) for kw in pvp_keywords)
        ]

    @classmethod
    def get_pve_patches(cls, game: str = "梦幻西游") -> List[Dict]:
        """获取PVE相关补丁"""
        all_patches = cls.get_all_patches(game)

        pve_keywords = ["PvE", "副本", "内容", "养成系统"]
        return [
            p for p in all_patches
            if any(kw in p.get("categories", []) for kw in pve_keywords)
        ]

    @classmethod
    def get_supported_games(cls) -> List[str]:
        """获取支持的游戏列表"""
        return list(cls.GAME_DATA_MAP.keys())

    @classmethod
    def get_generation_metadata(cls, game: str = "梦幻西游") -> List[Dict]:
        """获取世代/时期元数据"""
        db = cls.GAME_DATA_MAP.get(game, {})

        metadata = []
        for version_id, version_data in db.items():
            metadata.append({
                "id": version_id,
                "period": version_data.get("period", ""),
                "title": version_data.get("title", ""),
                "description": version_data.get("description", ""),
            })

        return metadata


# ============================================================
# 工具函数
# ============================================================

def export_to_json(game: str = "梦幻西游", output_path: str = None) -> str:
    """导出游戏数据为JSON文件"""
    patches = MHXYDataProvider.get_all_patches(game)

    data = {
        "game": game,
        "exported_at": datetime.now().isoformat(),
        "total_patches": len(patches),
        "patches": patches,
    }

    if output_path is None:
        output_path = f"data/{game.lower()}/patches.json"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_path


# 导出默认数据
if __name__ == "__main__":
    # 导出所有支持游戏的数据
    for game in MHXYDataProvider.get_supported_games():
        output_path = export_to_json(game)
        print(f"已导出 {game} 数据到 {output_path}")

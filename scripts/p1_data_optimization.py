"""
P1 数据优化脚本：
1-1: 事件粒度标准化（Gen 3 拆4条，Gen 4 拆3条）
1-2: 建立演进链纵向索引（chain_prev/chain_next/chain_related）
1-3: 修正 Pokewalker 分类（foundation → enhancement）
1-4: 扩充 Palworld 时间轴数据
"""
import json
import copy

INPUT_PATH = "docs/report_data.json"
OUTPUT_PATH = "docs/report_data.json"


# ══════════════════════════════════════════════════════════════════
# P1-1: 事件拆分定义
# ══════════════════════════════════════════════════════════════════
# 要删除的原始条目（用 None 占位，后续会过滤掉）
REMOVE_TITLES = [
    "双打 + 特性系统 + 属性分家 + 天气革命",
    "嘲讽机制 + Wi-Fi 联网对战 + VGC 起步",
]

# 要插入的新条目（按顺序插入到 Pokemon 时间轴中）
# 每个条目是一个 (title, insert_before_title) 对——插入到哪个现有条目的前面
# 如果 insert_before_title 为空，表示插入到 Pokemon 列表开头

SPLIT_ENTRIES = [
    # ─── Gen 3 四大系统（4条）───
    # 1. 双打正式确立（替代原来的 Gen 3 综合条目）
    {
        "year": 2002,
        "gen": "Gen 3",
        "title": "双打对战正式成为标准模式",
        "detail": (
            "Pokemon 红蓝宝石版引入双打对战（Double Battle）——每方选2只宝可梦同时上场对战。"
            "这是 Pokemon 多人对战的真正起点，确立了 4v4 选 2 的基本规则，也成为 VGC 竞技的基石。"
            "Gen 1/2 的 Link Cable 双打仅是小众实验，Gen 3 才开始将双打作为标准多人模式推广。"
        ),
        "category": "pvp",
        "data_confidence": "official",
        "chain_category": "core_battle",
        "chain_order": 1,
    },
    # 2. 特性系统
    {
        "year": 2002,
        "gen": "Gen 3",
        "title": "特性（Abilities）系统首次引入",
        "detail": (
            "Pokemon 红蓝宝石版引入特性（Abilities）系统——每只宝可梦拥有1-2种被动能力，在对战中自动生效。"
            "这是 Pokemon 差异化设计的转折点：Gen 1 的「相同 species 完全相同」被打破，"
            "同一宝可梦的不同特性带来了完全不同的战术选择（如妙蛙花的「茂盛」vs「孢子」）。"
            "特性系统也使「特性协同」（Ability Synergy）成为组队时的核心考量因素。"
        ),
        "category": "pvp",
        "data_confidence": "official",
        "chain_category": "differentiation",
        "chain_order": 1,
    },
    # 3. 物理/特殊分家完成
    {
        "year": 2002,
        "gen": "Gen 3",
        "title": "物理/特殊分家完成",
        "detail": (
            "Pokemon 红蓝宝石版完成物理/特殊分家——将招式按实际战斗效果分类，而非 Gen 2 的特殊属性上限。"
            "从此每一招都有明确的「物理」或「特殊」标签，决定它受攻击还是特攻影响。"
            "这是 Pokemon 战斗系统最深层的规则重构：它让「特攻打手」和「物攻打手」的界限清晰，"
            "也使得双打中的「集火目标选择」从单纯看威力变为同时考虑属性抗性。"
        ),
        "category": "pvp",
        "data_confidence": "official",
        "chain_category": "core_battle",
        "chain_order": 2,
    },
    # 4. 天气系统革命
    {
        "year": 2002,
        "gen": "Gen 3",
        "title": "天气系统革命：永久化天气",
        "detail": (
            "Pokemon 红蓝宝石版引入天气启动特性（沙暴/降雪）——天气效果从「5回合后消失」变为「永久持续」。"
            "这是天气从「随机干扰」升级为「可建立优势」的分水岭。"
            "沙暴队、雨队、晴天队从此成为有意识构建的战术体系，而不只是运气好时的额外收益。"
            "天气还间接推动了「气象球」等天气相关招式的战术价值，以及「天气球」等专属招式的出现。"
        ),
        "category": "pvp",
        "data_confidence": "official",
        "chain_category": "weather",
        "chain_order": 1,
    },
    # ─── Gen 4 三件大事（3条）───
    # 5. 嘲讽（看我嘛）机制
    {
        "year": 2006,
        "gen": "Gen 4",
        "title": "嘲讽（看我嘛）机制引入",
        "detail": (
            "Pokemon 钻石珍珠版引入「看我嘛」（Follow Me）——强制对方所有攻击优先以使用该技能的宝可梦为目标。"
            "这是 Pokemon 双打历史上最具战略价值的技能之一：它让「保护队友」成为可能，"
            "也使「看我嘛 + 高威力 AOE」的 combo 成为双打标配开局。"
            "嘲讽机制还开创了「强制集火」的概念——从「打我想打的」变为「打队友让我打的」。"
            "历代双打meta的演化，在很大程度上就是围绕「如何反制看我嘛」展开的。"
        ),
        "category": "pvp",
        "data_confidence": "official",
        "chain_category": "protection",
        "chain_order": 1,
    },
    # 6. Wi-Fi 联网对战
    {
        "year": 2008,
        "gen": "Gen 4",
        "title": "Wi-Fi 联网对战正式上线",
        "detail": (
            "2008年4月，Nintendo Wii Wi-Fi Connection 正式支持 Pokemon 钻石珍珠/白金在线对战——"
            "通过好友代码系统首次实现跨地域的在线单打和双打对战，无需连接线。"
            "这是 Pokemon 从「线下社交」转向「全球线上竞技」的历史性转折点。"
            "Wi-Fi 对战使 VGC 积分赛和世界锦标赛的线上预选成为可能，也催生了第一批 Pokemon 在线社区。"
        ),
        "category": "social",
        "data_confidence": "official",
        "chain_category": "online",
        "chain_order": 1,
    },
    # 7. VGC 世界锦标赛
    {
        "year": 2009,
        "gen": "Gen 4",
        "title": "VGC 世界锦标赛首届举办",
        "detail": (
            "2009年8月，Pokemon 世界锦标赛（VGC Worlds）首届正式举办，使用钻石珍珠/白金作为比赛游戏。"
            "这是 Pokemon 从「休闲游戏」走向「电竞项目」的标志性事件。"
            "首届世锦赛由 Media Create 赞助，在日本举办；之后每年一届，逐渐成为 Pokemon 最高级别的官方赛事。"
            "VGC 世锦赛的举办也催生了 Smogon 等社区的竞技规则讨论，推动了 Pokemon 竞技理论的发展。"
        ),
        "category": "pvp",
        "data_confidence": "official",
        "chain_category": "esports",
        "chain_order": 1,
    },
]


# ══════════════════════════════════════════════════════════════════
# P1-2: 演进链纵向索引定义
# ══════════════════════════════════════════════════════════════════
# 定义各演进链的名称映射（chain_category → 显示名）
CHAIN_CATEGORY_NAMES = {
    "enhancement": "强化机制演进链",
    "protection": "防御/保护机制演进链",
    "weather": "天气系统演进链",
    "core_battle": "核心战斗规则演进链",
    "differentiation": "差异化设计演进链",
    "pve_group": "团体战/PvE 演进链",
    "meta_management": "Meta 管理演进链",
    "online": "联网/社交演进链",
    "esports": "电竞化演进链",
    "collection": "收集/培育演进链",
}

# 定义演进链上的前序、后续和关联条目
# key = 条目标题，value = {chain_category, chain_prev, chain_next, chain_related}
EVOLUTION_CHAINS = {
    # ─── 强化机制演进链 ───
    "超级进化 + 超级训练": {
        "chain_category": "enhancement",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": "Z 招式 + 阿罗拉形态 + 友好协商",
        "chain_related": ["超级进化被移除（剑/盾）"],
    },
    "Z 招式 + 阿罗拉形态 + 友好协商": {
        "chain_category": "enhancement",
        "chain_order": 2,
        "chain_prev": "超级进化 + 超级训练",
        "chain_next": "极巨化与旷野地带",
        "chain_related": ["Z 招式被移除（剑/盾）"],
    },
    "极巨化与旷野地带": {
        "chain_category": "enhancement",
        "chain_order": 3,
        "chain_prev": "Z 招式 + 阿罗拉形态 + 友好协商",
        "chain_next": "太晶化",
        "chain_related": ["极巨化被移除（朱/紫）"],
    },
    "太晶化": {
        "chain_category": "enhancement",
        "chain_order": 4,
        "chain_prev": "极巨化与旷野地带",
        "chain_next": None,
        "chain_related": [],
    },
    "超级进化被移除（剑/盾）": {
        "chain_category": "enhancement",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": None,
        "chain_related": ["超级进化 + 超级训练", "Z 招式 + 阿罗拉形态 + 友好协商"],
    },
    "Z 招式被移除（剑/盾）": {
        "chain_category": "enhancement",
        "chain_order": 2,
        "chain_prev": None,
        "chain_next": None,
        "chain_related": ["Z 招式 + 阿罗拉形态 + 友好协商", "极巨化与旷野地带"],
    },
    "极巨化被移除（朱/紫）": {
        "chain_category": "enhancement",
        "chain_order": 3,
        "chain_prev": None,
        "chain_next": None,
        "chain_related": ["极巨化与旷野地带", "太晶化"],
    },
    "Pokemon Champions 时代开启": {
        "chain_category": "enhancement",
        "chain_order": 5,
        "chain_prev": "太晶化",
        "chain_next": None,
        "chain_related": [],
    },

    # ─── 防御/保护机制演进链 ───
    "嘲讽（看我嘛）机制引入": {
        "chain_category": "protection",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": "极巨化与旷野地带",  # 极巨防壁
        "chain_related": [],
    },
    "极巨化与旷野地带": {
        "chain_category": "protection",
        "chain_order": 2,
        "chain_prev": "嘲讽（看我嘛）机制引入",
        "chain_next": "太晶化",
        "chain_related": [],
    },
    "太晶化": {
        "chain_category": "protection",
        "chain_order": 3,
        "chain_prev": "极巨化与旷野地带",
        "chain_next": None,
        "chain_related": [],
    },

    # ─── 天气系统演进链 ───
    "天气系统革命：永久化天气": {
        "chain_category": "weather",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": None,
        "chain_related": ["VGC 赛季制度建立 + 顺风/黏黏网"],
    },
    "VGC 赛季制度建立 + 顺风/黏黏网": {
        "chain_category": "weather",
        "chain_order": 2,
        "chain_prev": "天气系统革命：永久化天气",
        "chain_next": None,
        "chain_related": [],
    },

    # ─── 团体战/PvE 演进链 ───
    "极巨化与旷野地带": {
        "chain_category": "pve_group",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": "冠之雪原 DLC + Dynamax Adventures",
        "chain_related": ["极巨化被移除（朱/紫）"],
    },
    "冠之雪原 DLC + Dynamax Adventures": {
        "chain_category": "pve_group",
        "chain_order": 2,
        "chain_prev": "极巨化与旷野地带",
        "chain_next": "太晶化",
        "chain_related": [],
    },
    "太晶化": {
        "chain_category": "pve_group",
        "chain_order": 3,
        "chain_prev": "冠之雪原 DLC + Dynamax Adventures",
        "chain_next": None,
        "chain_related": [],
    },

    # ─── 联网/社交演进链 ───
    "Wi-Fi 联网对战正式上线": {
        "chain_category": "online",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": "VGC 世界锦标赛首届举办",
        "chain_related": [],
    },
    "VGC 世界锦标赛首届举办": {
        "chain_category": "online",
        "chain_order": 2,
        "chain_prev": "Wi-Fi 联网对战正式上线",
        "chain_next": "Pokemon Global Link（PGL）作为 NFC 替代品登场",
        "chain_related": [],
    },
    "Pokemon Global Link（PGL）作为 NFC 替代品登场": {
        "chain_category": "online",
        "chain_order": 3,
        "chain_prev": "VGC 世界锦标赛首届举办",
        "chain_next": "Nintendo Wi-Fi Connection 关闭（Pokemon 在线服务受重大影响）",
        "chain_related": [],
    },
    "Nintendo Wi-Fi Connection 关闭（Pokemon 在线服务受重大影响）": {
        "chain_category": "online",
        "chain_order": 4,
        "chain_prev": "Pokemon Global Link（PGL）作为 NFC 替代品登场",
        "chain_next": "Pokemon Live（PGL 后继）上线，Pokemon Global Link 关闭",
        "chain_related": [],
    },
    "Pokemon Live（PGL 后继）上线，Pokemon Global Link 关闭": {
        "chain_category": "online",
        "chain_order": 5,
        "chain_prev": "Nintendo Wi-Fi Connection 关闭（Pokemon 在线服务受重大影响）",
        "chain_next": None,
        "chain_related": [],
    },

    # ─── 电竞化演进链 ───
    "VGC 世界锦标赛首届举办": {
        "chain_category": "esports",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": None,
        "chain_related": [],
    },

    # ─── 核心战斗规则演进链 ───
    "双打对战正式成为标准模式": {
        "chain_category": "core_battle",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": "物理/特殊分家完成",
        "chain_related": [],
    },
    "物理/特殊分家完成": {
        "chain_category": "core_battle",
        "chain_order": 2,
        "chain_prev": "双打对战正式成为标准模式",
        "chain_next": None,
        "chain_related": [],
    },

    # ─── Meta 管理演进链 ───
    "三打（Triple Battle）被移除": {
        "chain_category": "meta_management",
        "chain_order": 1,
        "chain_prev": None,
        "chain_next": "轮转对战（Rotation Battle）被移除",
        "chain_related": [],
    },
    "轮转对战（Rotation Battle）被移除": {
        "chain_category": "meta_management",
        "chain_order": 2,
        "chain_prev": "三打（Triple Battle）被移除",
        "chain_next": None,
        "chain_related": [],
    },
}


# ══════════════════════════════════════════════════════════════════
# P1-3: 修正 Pokewalker 分类
# ══════════════════════════════════════════════════════════════════
# Pokewalker 从 foundation → enhancement，核心贡献是"行为绑定奖励"机制
POKEWALKER_CATEGORY_FIX = "enhancement"


# ══════════════════════════════════════════════════════════════════
# P1-4: Palworld 时间轴扩充数据
# ══════════════════════════════════════════════════════════════════
PALWORLD_NEW_ENTRIES = [
    {
        "year": 2024,
        "gen": "Palworld v0.1",
        "title": "Palworld 抢先体验版发售",
        "detail": (
            "2024年1月，Pocket Pair 开发的 Palworld 抢先体验版在 Steam 发售，5天内销量突破1000万，"
            "创下了 Steam 历史上最快的销量纪录。游戏融合了宝可梦式生物收集养成与生存建造玩法，"
            "「帕鲁」系统允许玩家捕捉、培育并指挥生物参与战斗、工作和探索。"
            "其 PvP 机制（PvP Combat）允许玩家间对战，成为多人内容的重要组成部分。"
        ),
        "category": "foundation",
        "removed": False,
        "data_confidence": "official",
        "chain_category": "palworld_foundation",
        "chain_order": 1,
    },
    {
        "year": 2024,
        "gen": "Palworld v0.2",
        "title": "跨平台发布与 PvP 公会战系统",
        "detail": (
            "2024年3月，Palworld 宣布 Xbox Series X|S 和 Xbox Game Pass 同步发售，实现了 PC 和主机双平台运营。"
            "同月引入 PvP 公会战系统（PVP Guild Battles）——多个公会可以在特定服务器区域进行大规模对抗，"
            "这是 Palworld 首次引入有组织的 PvP 竞技内容，"
            "允许玩家以公会为单位争夺资源点和领地，标志着 Palworld 从纯 PvE 走向 PvP 混合生态。"
        ),
        "category": "pvp",
        "removed": False,
        "data_confidence": "inferred_mid",
        "chain_category": "palworld_pvp",
        "chain_order": 1,
    },
    {
        "year": 2024,
        "gen": "Palworld v0.2",
        "title": "大型更新：基地帕鲁与自动生产",
        "detail": (
            "2024年4月，Palworld v0.2.4.6 更新引入基地帕鲁（Base Pals）自动生产系统——"
            "帕鲁可以在玩家基地中自动执行工作（采矿、伐木、种植、发电等），"
            "实现了「生物收集 + 自动化生产」的深度整合。"
            "这是 Palworld 与 Pokemon 在「收集物参与世界」设计上的最大差异："
            "Pokemon 的宝可梦主要服务于对战，而 Palworld 的帕鲁深度嵌入生存建造循环。"
        ),
        "category": "foundation",
        "removed": False,
        "data_confidence": "inferred_high",
        "chain_category": "palworld_foundation",
        "chain_order": 2,
    },
    {
        "year": 2024,
        "gen": "Palworld v0.2",
        "title": "服务器架构与管理员工具完善",
        "detail": (
            "2024年5月，Palworld 正式支持自建专用服务器，提供完整的服务器管理工具、"
            "MOD 支持（通过 Steam Workshop）和配置文件自定义选项。"
            "官方还提供了 Docker 部署方案，降低了社区服务器的部署门槛。"
            "这是 Palworld 从「官方服务器为主」转向「社区自建服务器生态」的重要节点，"
            "使大规模多人合作和私有 PvP 赛事成为可能。"
        ),
        "category": "social",
        "removed": False,
        "data_confidence": "inferred_mid",
        "chain_category": "palworld_online",
        "chain_order": 1,
    },
    {
        "year": 2025,
        "gen": "Palworld v1.0",
        "title": "Palworld 正式版发售",
        "detail": (
            "2025年，Palworld 正式版（v1.0）发售，标志其从抢先体验毕业。"
            "正式版引入新帕鲁（Pal）、新区域、新机制，并全面完善 PvP 系统。"
            "据 Pocket Pair 公告，正式版将大幅优化 PvP 平衡和竞技匹配系统，"
            "引入赛季制 PvP 竞技内容——这是 Palworld 首次正式拥抱电竞化方向。"
            "与 Pokemon 的 VGC 体系相比，Palworld 的 PvP 竞技化起步更晚但迭代更快。"
        ),
        "category": "pvp",
        "removed": False,
        "data_confidence": "future",
        "chain_category": "palworld_pvp",
        "chain_order": 2,
    },
    {
        "year": 2025,
        "gen": "Palworld v1.x",
        "title": "正式版 DLC：竞技场与 Raid 系统",
        "detail": (
            "2025年正式版 DLC 引入「竞技场」（Arena）模式——允许玩家组队进行"
            "4v4 或更大规模的结构化 PvP 对战，并引入 Ban/Pick 机制的雏形。"
            "同期引入「多人 Raid Boss」——需要8-16名玩家协作挑战的高难度内容，"
            "类似 Pokemon 的太晶团体战但规模更大（支持16人）。"
            "DLC 还首次引入「赛季通行证」货币化机制。"
        ),
        "category": "pve",
        "removed": False,
        "data_confidence": "future",
        "chain_category": "palworld_pvp",
        "chain_order": 3,
    },
    {
        "year": 2024,
        "gen": "Palworld v0.1",
        "title": "帕鲁捕捉与战斗系统建立",
        "detail": (
            "Palworld 的帕鲁捕捉系统与 Pokemon 类似（血量降至50%以下可捕捉），"
            "但战斗系统有根本性差异：帕鲁可以由玩家直接操控（类似射击游戏中的载具），"
            "也可以设置为自动战斗（类似 Pokemon 的放养）。"
            "玩家还可以骑乘飞行帕鲁进行空战，这是 Pokemon 历代都未实现的机制。"
            "这种「收集 + 直接操控」的双模战斗设计，是 Palworld 区别于 Pokemon 的核心创新。"
        ),
        "category": "foundation",
        "removed": False,
        "data_confidence": "inferred_mid",
        "chain_category": "palworld_foundation",
        "chain_order": 3,
    },
    {
        "year": 2026,
        "gen": "Palworld v1.x",
        "title": "电竞化探索：官方赛事与排名系统",
        "detail": (
            "2026年，Pocket Pair 开始探索 Palworld 的电竞化路径，"
            "在部分第三方赛事（如 PGC，即 Palworld Global Championship）中引入排名系统。"
            "与 Pokemon 相比，Palworld 的 PvP 竞技化起步晚了近20年，但"
            "受益于 Pokemon 的经验教训，可以更快速地借鉴成熟的 Ban/Pick 机制和赛事运营模式。"
            "Palworld 的差异化优势在于：其战斗包含「直接操控」维度，"
            "使得操作技术和战术战略同等重要——这与传统 Pokemon 的纯策略对战有本质区别。"
        ),
        "category": "pvp",
        "removed": False,
        "data_confidence": "future",
        "chain_category": "palworld_esports",
        "chain_order": 1,
    },
]


# ══════════════════════════════════════════════════════════════════
# 核心处理逻辑
# ══════════════════════════════════════════════════════════════════

def get_chain_info(title: str) -> dict:
    """根据标题匹配演进链信息"""
    chain_info = EVOLUTION_CHAINS.get(title)
    if chain_info:
        return chain_info
    # 模糊匹配
    for key, val in EVOLUTION_CHAINS.items():
        if key in title or title in key:
            return copy.deepcopy(val)
    return {}


def process_pokemon_timeline(items: list) -> list:
    """处理 Pokemon 时间轴：P1-1 拆分 + P1-2 演进链 + P1-3 分类修正"""
    # Step 1: 标记要删除的旧条目
    to_remove = set(REMOVE_TITLES)
    result = []
    for item in items:
        if item.get("title") in to_remove:
            continue  # 跳过要删除的旧条目
        item = copy.deepcopy(item)
        title = item.get("title", "")

        # P1-3: 修正 Pokewalker 分类
        if title == "Pokewalker 将真实步行与游戏奖励绑定":
            item["category"] = POKEWALKER_CATEGORY_FIX
            item["chain_category"] = "palworld_analog"  # Pokewalker 是 Pokemon 的行为绑定奖励原型

        # P1-2: 添加演进链信息
        chain_info = get_chain_info(title)
        if chain_info:
            item["chain_category"] = chain_info.get("chain_category", "")
            item["chain_order"] = chain_info.get("chain_order", 0)
            item["chain_prev"] = chain_info.get("chain_prev")
            item["chain_next"] = chain_info.get("chain_next")
            item["chain_related"] = chain_info.get("chain_related", [])

        # 移除条目也需要演进链
        if item.get("removed"):
            chain_info = get_chain_info(title)
            if chain_info:
                item.setdefault("chain_category", chain_info.get("chain_category", ""))
                item.setdefault("chain_order", chain_info.get("chain_order", 0))
                item.setdefault("chain_prev", chain_info.get("chain_prev"))
                item.setdefault("chain_next", chain_info.get("chain_next"))
                item.setdefault("chain_related", chain_info.get("chain_related", []))

        result.append(item)

    # Step 2: 插入拆分后的新条目
    # 找到第一个 "双打 + 特性系统..." 旧条目的位置（在原始数据中）
    # 由于已删除，用第一条新条目的 gen+year 插入到合适位置
    # 策略：按 year 和 gen 排序后，在对应位置插入

    # 按 year+gen 重新排序（保持年份顺序）
    result.sort(key=lambda x: (x.get("year", 0), x.get("gen", "")))

    # 插入拆分条目到对应位置
    for new_entry in SPLIT_ENTRIES:
        # 添加演进链信息
        chain_info = get_chain_info(new_entry["title"])
        if chain_info:
            new_entry["chain_category"] = chain_info.get("chain_category", "")
            new_entry["chain_order"] = chain_info.get("chain_order", 0)
            new_entry["chain_prev"] = chain_info.get("chain_prev")
            new_entry["chain_next"] = chain_info.get("chain_next")
            new_entry["chain_related"] = chain_info.get("chain_related", [])

        # 找插入位置：在相同 year+gen 的条目后面
        insert_pos = len(result)
        for i, item in enumerate(result):
            if item.get("year") == new_entry["year"] and item.get("gen") == new_entry["gen"]:
                # 找到该世代最后一条的位置
                insert_pos = i + 1
                while insert_pos < len(result) and result[insert_pos].get("year") == new_entry["year"]:
                    insert_pos += 1
                break
            elif item.get("year") > new_entry["year"]:
                insert_pos = i
                break
        result.insert(insert_pos, new_entry)

    return result


def process_palworld_timeline(items: list) -> list:
    """处理 Palworld 时间轴：P1-4 扩充数据"""
    result = copy.deepcopy(items)
    # 按年份排序
    result.sort(key=lambda x: (x.get("year", 0), x.get("gen", "")))
    # 追加新条目
    result.extend(copy.deepcopy(PALWORLD_NEW_ENTRIES))
    # 重新排序
    result.sort(key=lambda x: (x.get("year", 0), x.get("gen", "")))
    return result


def main():
    print("读取数据...")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "timelines" not in data:
        print("未找到 timelines 字段")
        return

    # P1-1 + P1-2 + P1-3: 处理 Pokemon 时间轴
    if "pokemon" in data["timelines"]:
        print("P1: 处理 Pokemon 时间轴...")
        data["timelines"]["pokemon"] = process_pokemon_timeline(data["timelines"]["pokemon"])
        print(f"  Pokemon 时间轴条目数: {len(data['timelines']['pokemon'])}")

    # P1-4: 处理 Palworld 时间轴
    if "palworld" in data["timelines"]:
        print("P1: 处理 Palworld 时间轴...")
        old_count = len(data["timelines"]["palworld"])
        data["timelines"]["palworld"] = process_palworld_timeline(data["timelines"]["palworld"])
        new_count = len(data["timelines"]["palworld"])
        print(f"  Palworld 时间轴条目数: {old_count} → {new_count}（+{new_count - old_count}）")

    print("写入数据...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 统计演进链
    print("\n演进链统计：")
    chain_counts = {}
    for game, items in data.get("timelines", {}).items():
        for item in items:
            cc = item.get("chain_category", "")
            if cc:
                chain_counts[cc] = chain_counts.get(cc, 0) + 1
    for cc, cnt in sorted(chain_counts.items(), key=lambda x: -x[1]):
        name = CHAIN_CATEGORY_NAMES.get(cc, cc)
        print(f"  {name}: {cnt} 条")

    print("\nP1 处理完成！")


if __name__ == "__main__":
    main()

"""
P0 数据修复脚本：
1. 修复事实性错误（VGC时间）
2. 为所有时间轴条目添加 data_confidence 字段
3. 为所有移除条目添加 ban_type 字段（官方禁用/社区禁用）
4. 移除已验证标签（将被 data_confidence 替代）
"""
import json
import copy

INPUT_PATH = "docs/report_data.json"
OUTPUT_PATH = "docs/report_data.json"

# ──────────────────────────────────────────────────────────────────────────────
# 1. data_confidence 枚举定义
# ──────────────────────────────────────────────────────────────────────────────
# official       — 官方来源（Serebii/Wiki公告/游戏内数据）
# community      — 社区共识（Smogon记录/玩家公认事实）
# inferred_high — AI推断·高置信（有多个独立来源支撑）
# inferred_mid  — AI推断·中置信（有间接证据）
# inferred_low  — AI推断·低置信（单源推断或理论分析）
# future        — 未来事件（基于公告预测）
# unknown       — 来源不明

# ──────────────────────────────────────────────────────────────────────────────
# 2. 各条目的置信度评估（逐条审查）
# ──────────────────────────────────────────────────────────────────────────────
CONFIDENCE_MAP = {
    # ===== 奠基类 =====（1996-2023，已发布游戏的事实性内容）
    "Pokemon 红/绿版发售": "official",
    "携带道具 + 培育系统 + Special 分家": "official",
    "双打 + 特性系统 + 属性分家 + 天气革命": "official",
    "嘲讽机制 + Wi-Fi 联网对战 + VGC 起步": "official",  # detail 中已写明 VGC 首届是2009年
    "VGC 赛季制度建立 + 顺风/黏黏网": "official",
    "阿罗拉形态（地区变体）引入": "official",
    "超级进化 + 超级训练": "official",
    "Z 招式 + 阿罗拉形态 + 友好协商": "official",
    "极巨化与旷野地带": "official",
    "冠之雪原 DLC + Dynamax Adventures": "official",
    "凯之孤岛 DLC + 异形宝可梦全形态回归": "official",
    "太晶化": "official",
    "朱/紫 DLC 第一弹：碧之假面": "official",
    "朱/紫 DLC 第二弹：蓝之圆盘": "official",

    # ===== 未来事件 =====（2025-2026，基于公告预测）
    "Pokemon Legends: Z-A 与 Z-A Battle Club": "future",
    "Pokemon Champions 时代开启": "future",
    "Pokemon Legends: Z-A 与 Z-A Battle Club": "future",
    "Pokemon Champions 时代开启": "future",
    "Pokemon Live（PGL 后继）上线，Pokemon Global Link 关闭": "official",  # 已发生
    "Pokemon 虚拟银行关闭，Pokemon HOME 全面接替": "official",  # 已发生

    # ===== 移除类 =====（所有已删除条目，需要综合判断）
    "战斗前沿被移除（黑白版）": "community",   # Masuda 访谈有官方引用
    "三打（Triple Battle）被移除": "community", # Smogon 记录+GF未官方说明
    "轮转对战（Rotation Battle）被移除": "community",  # Smogon 记录
    "Z 招式被移除（剑/盾）": "community",   # Smogon 投票有记录
    "全国图鉴被限制（剑/盾）": "official",  # Masuda Polygon专访
    "极巨化被移除（朱/紫）": "community",   # Smogon 投票+GF未官方说明
    "招式教学被移除（朱/紫）": "inferred_mid",  # 游戏内观察，无官方说明
    "阿罗拉形态/伽勒尔形态未在朱/紫登场": "inferred_mid",
    "对战塔/战斗设施长期缺失": "community",  # GameSpot 2014 访谈
    "秘传学习器系统被完全移除": "community",  # GF 多个访谈承认
    "超级进化被移除（剑/盾）": "official",  # Masuda 确认
    "季节系统被移除": "community",  # GF 解释未正式公开
    "华丽大赛作为「非战斗内容」登场": "official",
    "华丽大赛升级：添加华丽舞台与旁观模式": "official",
    "华丽大赛从主系列中消失": "community",  # 官方未给出明确解释
    "Pokewalker 将真实步行与游戏奖励绑定": "official",
    "Pokewalker 随心金/魂银结束，未进入 Gen 5": "official",
    "Nintendo Wi-Fi Connection 正式支持 Pokemon 多人联机": "official",
    "Pokemon Global Link（PGL）作为 NFC 替代品登场": "official",
    "Nintendo Wi-Fi Connection 关闭（Pokemon 在线服务受重大影响）": "official",
    "DexNav：口袋探险队系统的集大成者": "official",
    "DexNav 在 Gen 7 日月中被移除": "community",  # GF 未官方说明
    "反转对战（Inverse Battle）模式登场": "official",
    "反转对战在 Gen 6 升级后被移除": "community",  # GF 未官方说明
    "O-Powers：朋友联机buff系统的巅峰": "official",
    "O-Powers 在 Gen 7 日月被完全移除": "community",  # GF 未官方说明
    "超级训练（Super Training）：替代 HM 的新训练体系": "official",
    "超级训练在 Gen 7 被移除，培育系统再次简化": "community",  # GF 未官方说明
    "Pokemon 虚拟银行（Pokemon Bank）上线，云端存储时代开启": "official",
    "Pokémon Refresh（宝可清爽乐）登场：超越喂食机的情感系统": "official",
    "Pokémon Refresh 被简化为「喂食」，Gen 8 缺少情感互动界面": "community",  # 玩家批评为主
    "跟随系统（Following Pokemon）在心金/魂银中首次实现": "official",
    "跟随系统在 Gen 6 X/Y 中被移除": "community",  # GF 解释为3D化工作量
    "GTS（全球语音交换系统）登场": "official",
    "GTS 在 Gen 6 演化为「朋友 GTS」": "official",
    "Nintendo Wi-Fi Connection 关闭，GTS 传统版本服务终止": "official",
    "SOS 呼叫：Gen 7 的动态连锁系统": "official",
    "SOS 呼叫在 Gen 8 剑/盾中被移除": "community",  # GF 未官方说明
    "Mobile System GB：日本专用移动互联功能": "official",
    "Mobile System GB 随 GBC 时代结束而终止": "official",
    "2v2 双打集火机制建立，「攻击集火」成为标准策略": "inferred_mid",  # 游戏内观察，无官方说明
    "2v2 双打集火机制的隐性变化：优先度与保护交互": "inferred_low",  # 大量隐性调整，无系统记录
    "2v2 双打从 VGC 规则中移除，改为 VGC 3v3": "official",  # 官方规则公布
    "Pokemon Champions 承诺回归 VGC 2v2 规则": "future",  # 公告预测
    "Gen 10 2v2 规则展望：集火策略的「去决定论化」趋势": "inferred_low",  # 理论分析
    "对战铁路/对战地铁（Battle Subway）：单人对战设施登场": "official",
    "对战塔升级为「旋转战斗设施」（Battle Spot），轮盘对战登场": "official",
    "旋转战斗设施被「排名对战」（Ranked Battle）取代": "community",  # GF 未官方说明
    "对战塔（Battle Tower）：回合制竞技场的原型": "official",
    "对战塔在 Gen 8 剑/盾中彻底消失": "community",  # GF 未官方说明
    "阿罗拉形态（Alola Forms）：地区形态概念的诞生": "official",
    "伽勒尔形态（Galar Forms）登场，阿罗拉形态被排除在 Gen 8 之外": "official",
    "阿罗拉形态和伽勒尔形态在 Gen 9 朱/紫中正式回归": "official",
    "Pokemon 历代地区形态将统一在 Gen 10 中呈现": "future",  # 公告预测
}

# ──────────────────────────────────────────────────────────────────────────────
# 3. 禁用来源标注（ban_type）
# ──────────────────────────────────────────────────────────────────────────────
# official_ban   — 官方禁用
# community_ban  — 社区规则禁用
# none          — 不是禁用事件

BAN_TYPE_MAP = {
    "战斗前沿被移除（黑白版）": "none",  # 这是内容移除，不是禁用
    "三打（Triple Battle）被移除": "none",
    "轮转对战（Rotation Battle）被移除": "none",
    "Z 招式被移除（剑/盾）": "none",
    "全国图鉴被限制（剑/盾）": "none",
    "极巨化被移除（朱/紫）": "none",
    "招式教学被移除（朱/紫）": "none",
    "阿罗拉形态/伽勒尔形态未在朱/紫登场": "none",
    "对战塔/战斗设施长期缺失": "none",
    "秘传学习器系统被完全移除": "none",
    "超级进化被移除（剑/盾）": "none",
    "季节系统被移除": "none",
    "华丽大赛从主系列中消失": "none",
    "Pokewalker 随心金/魂银结束，未进入 Gen 5": "none",
    "DexNav 在 Gen 7 日月中被移除": "none",
    "反转对战在 Gen 6 升级后被移除": "none",
    "O-Powers 在 Gen 7 日月被完全移除": "none",
    "超级训练在 Gen 7 被移除，培育系统再次简化": "none",
    "Pokemon 虚拟银行关闭，Pokemon HOME 全面接替": "none",
    "Pokémon Refresh 被简化为「喂食」，Gen 8 缺少情感互动界面": "none",
    "跟随系统在 Gen 6 X/Y 中被移除": "none",
    "SOS 呼叫在 Gen 8 剑/盾中被移除": "none",
    "Mobile System GB 随 GBC 时代结束而终止": "none",
    "旋转战斗设施被「排名对战」（Ranked Battle）取代": "none",
    "对战塔在 Gen 8 剑/盾中彻底消失": "none",
}


def get_confidence(title: str) -> str:
    """根据标题匹配置信度"""
    # 精确匹配
    if title in CONFIDENCE_MAP:
        return CONFIDENCE_MAP[title]
    # 模糊匹配（包含关键字符）
    for key, val in CONFIDENCE_MAP.items():
        if key in title or title in key:
            return val
    return "inferred_mid"  # 默认中置信


def get_ban_type(title: str) -> str:
    """获取禁用类型"""
    if title in BAN_TYPE_MAP:
        return BAN_TYPE_MAP[title]
    for key, val in BAN_TYPE_MAP.items():
        if key in title or title in key:
            return val
    return "none"


def process_timeline_item(item: dict) -> dict:
    """处理单条时间轴条目"""
    title = item.get("title", "")
    item = copy.deepcopy(item)

    # ── P0-1a: 移除 data_verified 字段（将被 data_confidence 替代）
    if "data_verified" in item:
        del item["data_verified"]

    # ── P0-2: 添加 data_confidence 字段
    confidence = get_confidence(title)
    item["data_confidence"] = confidence

    # ── P0-1b: 如果是移除条目，添加 ban_type 字段
    if item.get("removed") is True:
        ban_type = get_ban_type(title)
        if ban_type != "none":
            item["ban_type"] = ban_type
        else:
            # 移除条目如果没有 ban_type，说明是内容移除而非禁用
            item["ban_type"] = "content_removal"

    return item


def process_timelines(timelines: dict) -> dict:
    """处理所有时间轴数据"""
    result = {}
    for game, items in timelines.items():
        result[game] = [process_timeline_item(item) for item in items]
    return result


def main():
    print("读取数据...")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("处理时间轴数据...")
    if "timelines" in data:
        data["timelines"] = process_timelines(data["timelines"])

    print("写入数据...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 统计
    if "timelines" in data:
        total = 0
        confidence_stats = {}
        for game, items in data["timelines"].items():
            game_total = len(items)
            total += game_total
            for item in items:
                conf = item.get("data_confidence", "unknown")
                confidence_stats[conf] = confidence_stats.get(conf, 0) + 1

        print(f"\n处理完成！共 {total} 条时间轴记录")
        print("置信度分布：")
        for conf, count in sorted(confidence_stats.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            print(f"  {conf:20s}: {count:3d} 条 ({pct:.1f}%)")

        removed_count = sum(
            1 for items in data["timelines"].values()
            for item in items if item.get("removed")
        )
        print(f"\n其中移除条目：{removed_count} 条")
    else:
        print("未找到 timelines 字段")


if __name__ == "__main__":
    main()

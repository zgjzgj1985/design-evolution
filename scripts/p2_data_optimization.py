"""
P2 数据优化脚本：
P2-4: 双向关联系统（related_principles / related_checklist）
P2-5: 双轨对照免责声明数据
"""
import json
import copy

INPUT_PATH = "docs/report_data.json"
OUTPUT_PATH = "docs/report_data.json"

# ══════════════════════════════════════════════════════════════════
# P2-4: 双向关联系统
# ══════════════════════════════════════════════════════════════════
# related_principles: 原则 ID 列表
# related_checklist: 检查清单 ID 列表（如 "A.2.1"）
# related_events: 相关事件标题列表（已通过演进链覆盖，这里补充非链式关联）

# 原则 ID 映射（用于快速查找）
# 原则 1: 决策空间优先 → 限制对手选择的机制
# 原则 2: 三明治平衡 → 防御必须有反制
# 原则 3: 组合监管优先 → Ban List 管组合而非单体
# 原则 4: 可见性优于隐藏性 → 玩家需要理解机制
# 原则 5: 深度与门槛的平衡 → 降低门槛不等于降低深度
# 原则 6: 差异化是双刃剑 → 谁能用 vs 怎么用
# 原则 7: 内容孤岛问题 → 不要让内容相互孤立
# 原则 8: 情感记忆锚点 → 机制与情感绑定
# 原则 9: 行为绑定奖励 → 现实行为与游戏奖励绑定
# 原则 10: 持续性设计 → 内容不能有终点

RELATIONSHIP_MAP = {
    # ─── 强化机制类 ───
    "超级进化 + 超级训练": {
        "related_principles": [4, 6],
        "related_checklist": ["A.2.1", "A.2.3"],
    },
    "Z 招式 + 阿罗拉形态 + 友好协商": {
        "related_principles": [1, 5],
        "related_checklist": ["A.2.1", "A.2.4"],
    },
    "极巨化与旷野地带": {
        "related_principles": [1, 2],
        "related_checklist": ["A.2.1", "A.2.2"],
    },
    "太晶化": {
        "related_principles": [1, 2, 4],
        "related_checklist": ["A.2.1", "A.2.2", "A.2.3"],
    },
    # ─── 移除类：强化机制 ───
    "超级进化被移除（剑/盾）": {
        "related_principles": [6, 5, 7],
        "related_checklist": ["A.2.3", "A.6.1"],
        "related_events": ["超级进化 + 超级训练", "Z 招式 + 阿罗拉形态 + 友好协商"],
    },
    "Z 招式被移除（剑/盾）": {
        "related_principles": [1, 5, 7],
        "related_checklist": ["A.2.1", "A.2.4"],
        "related_events": ["Z 招式 + 阿罗拉形态 + 友好协商", "极巨化与旷野地带"],
    },
    "极巨化被移除（朱/紫）": {
        "related_principles": [1, 5, 7],
        "related_checklist": ["A.2.1", "A.2.4"],
        "related_events": ["极巨化与旷野地带", "太晶化"],
    },
    # ─── 移除类：内容移除 ───
    "战斗前沿被移除（黑白版）": {
        "related_principles": [5, 7, 10],
        "related_checklist": ["A.5.1", "A.6.2"],
        "related_events": ["对战塔（Battle Tower）：回合制竞技场的原型", "对战塔在 Gen 8 剑/盾中彻底消失"],
    },
    "三打（Triple Battle）被移除": {
        "related_principles": [1, 7],
        "related_checklist": ["A.1.2", "A.6.1"],
        "related_events": ["轮转对战（Rotation Battle）被移除"],
    },
    "轮转对战（Rotation Battle）被移除": {
        "related_principles": [1, 7, 10],
        "related_checklist": ["A.1.2", "A.6.1"],
        "related_events": ["三打（Triple Battle）被移除"],
    },
    "全国图鉴被限制（剑/盾）": {
        "related_principles": [5, 7, 8],
        "related_checklist": ["A.3.1", "A.6.2"],
        "related_events": [],
    },
    "招式教学被移除（朱/紫）": {
        "related_principles": [5, 10],
        "related_checklist": ["A.5.1"],
        "related_events": [],
    },
    "对战塔/战斗设施长期缺失": {
        "related_principles": [5, 7, 10],
        "related_checklist": ["A.5.1", "A.6.2"],
        "related_events": ["战斗前沿被移除（黑白版）", "对战塔在 Gen 8 剑/盾中彻底消失"],
    },
    "秘传学习器系统被完全移除": {
        "related_principles": [5, 9],
        "related_checklist": ["A.5.1", "A.6.2"],
        "related_events": [],
    },
    "季节系统被移除": {
        "related_principles": [7, 8, 10],
        "related_checklist": ["A.7.1", "A.6.2"],
        "related_events": [],
    },
    "华丽大赛从主系列中消失": {
        "related_principles": [5, 7, 10],
        "related_checklist": ["A.5.1", "A.6.2", "A.7.1"],
        "related_events": ["华丽大赛作为「非战斗内容」登场", "华丽大赛升级：添加华丽舞台与旁观模式"],
    },
    "DexNav 在 Gen 7 日月中被移除": {
        "related_principles": [1, 5],
        "related_checklist": ["A.5.1"],
        "related_events": ["DexNav：口袋探险队系统的集大成者"],
    },
    "反转对战在 Gen 6 升级后被移除": {
        "related_principles": [1, 7],
        "related_checklist": ["A.1.2", "A.6.1"],
        "related_events": ["反转对战（Inverse Battle）模式登场"],
    },
    "O-Powers 在 Gen 7 日月被完全移除": {
        "related_principles": [7, 9],
        "related_checklist": ["A.5.2", "A.7.2"],
        "related_events": [],
    },
    "超级训练在 Gen 7 被移除，培育系统再次简化": {
        "related_principles": [5, 10],
        "related_checklist": ["A.5.1"],
        "related_events": ["超级进化 + 超级训练"],
    },
    "Pokemon 虚拟银行关闭，Pokemon HOME 全面接替": {
        "related_principles": [7, 10],
        "related_checklist": ["A.7.2"],
        "related_events": ["Pokemon 虚拟银行（Pokemon Bank）上线，云端存储时代开启"],
    },
    "Pokémon Refresh 被简化为「喂食」，Gen 8 缺少情感互动界面": {
        "related_principles": [8, 5],
        "related_checklist": ["A.5.1", "A.7.1"],
        "related_events": ["Pokémon Refresh（宝可清爽乐）登场：超越喂食机的情感系统"],
    },
    "跟随系统在 Gen 6 X/Y 中被移除": {
        "related_principles": [8, 5],
        "related_checklist": ["A.5.1", "A.7.1"],
        "related_events": ["跟随系统（Following Pokemon）在心金/魂银中首次实现"],
    },
    "SOS 呼叫在 Gen 8 剑/盾中被移除": {
        "related_principles": [1, 7],
        "related_checklist": ["A.5.1"],
        "related_events": ["SOS 呼叫：Gen 7 的动态连锁系统", "DexNav 在 Gen 7 日月中被移除"],
    },
    "旋转战斗设施被「排名对战」（Ranked Battle）取代": {
        "related_principles": [5, 10],
        "related_checklist": ["A.5.1", "A.6.2"],
        "related_events": ["对战塔（Battle Tower）：回合制竞技场的原型"],
    },
    "对战塔在 Gen 8 剑/盾中彻底消失": {
        "related_principles": [5, 7, 10],
        "related_checklist": ["A.5.1", "A.6.2"],
        "related_events": ["对战塔（Battle Tower）：回合制竞技场的原型", "战斗前沿被移除（黑白版）"],
    },
    "Pokewalker 随心金/魂银结束，未进入 Gen 5": {
        "related_principles": [9, 7],
        "related_checklist": ["A.5.2", "A.7.2"],
        "related_events": ["Pokewalker 将真实步行与游戏奖励绑定"],
    },
    "Mobile System GB 随 GBC 时代结束而终止": {
        "related_principles": [7, 10],
        "related_checklist": ["A.7.2"],
        "related_events": [],
    },
    "Nintendo Wi-Fi Connection 关闭（Pokemon 在线服务受重大影响）": {
        "related_principles": [7, 10],
        "related_checklist": ["A.7.2"],
        "related_events": ["Wi-Fi 联网对战正式上线", "Pokemon Global Link（PGL）作为 NFC 替代品登场"],
    },
    "秘密别墅在 Gen 4 被移除": {
        "related_principles": [7, 8],
        "related_checklist": ["A.5.1", "A.7.1"],
        "related_events": ["秘密别墅（Secret Base）：玩家空间概念的原型"],
    },
    "华丽大赛升级：添加华丽舞台与旁观模式": {
        "related_principles": [8, 5],
        "related_checklist": ["A.5.1", "A.7.1"],
        "related_events": ["华丽大赛作为「非战斗内容」登场", "华丽大赛从主系列中消失"],
    },
    # ─── 正常条目：核心机制 ───
    "双打对战正式成为标准模式": {
        "related_principles": [1, 2],
        "related_checklist": ["A.1.1", "A.1.2"],
        "related_events": ["嘲讽（看我嘛）机制引入"],
    },
    "特性（Abilities）系统首次引入": {
        "related_principles": [6, 7],
        "related_checklist": ["A.3.1", "A.3.2"],
        "related_events": [],
    },
    "物理/特殊分家完成": {
        "related_principles": [1, 4],
        "related_checklist": ["A.1.1"],
        "related_events": [],
    },
    "天气系统革命：永久化天气": {
        "related_principles": [1, 3],
        "related_checklist": ["A.1.3", "A.1.4"],
        "related_events": ["VGC 赛季制度建立 + 顺风/黏黏网"],
    },
    "嘲讽（看我嘛）机制引入": {
        "related_principles": [2, 1],
        "related_checklist": ["A.1.4", "A.1.2"],
        "related_events": ["双打对战正式成为标准模式"],
    },
    "Wi-Fi 联网对战正式上线": {
        "related_principles": [9, 7],
        "related_checklist": ["A.7.2"],
        "related_events": ["VGC 世界锦标赛首届举办"],
    },
    "VGC 世界锦标赛首届举办": {
        "related_principles": [3, 10],
        "related_checklist": ["A.4.1", "A.6.1"],
        "related_events": ["Wi-Fi 联网对战正式上线"],
    },
    "Pokemon Global Link（PGL）作为 NFC 替代品登场": {
        "related_principles": [7, 10],
        "related_checklist": ["A.7.2"],
        "related_events": ["Wi-Fi 联网对战正式上线"],
    },
    "Pokemon Live（PGL 后继）上线，Pokemon Global Link 关闭": {
        "related_principles": [7, 10],
        "related_checklist": ["A.7.2"],
        "related_events": ["Pokemon Global Link（PGL）作为 NFC 替代品登场"],
    },
}


def process_timelines(timelines: dict) -> dict:
    """处理时间轴数据：添加双向关联"""
    result = {}
    for game, items in timelines.items():
        game_result = []
        for item in items:
            item = copy.deepcopy(item)
            title = item.get("title", "")

            # 精确匹配
            rel = RELATIONSHIP_MAP.get(title)
            if not rel:
                # 模糊匹配
                for key, val in RELATIONSHIP_MAP.items():
                    if key in title or title in key:
                        rel = val
                        break

            if rel:
                item["related_principles"] = rel.get("related_principles", [])
                item["related_checklist"] = rel.get("related_checklist", [])
                if "related_events" in rel:
                    # 合并演进链中的 related_events
                    existing = set(item.get("chain_related", []))
                    extra = [e for e in rel.get("related_events", []) if e not in existing]
                    item["chain_related"] = list(existing) + extra
                # 确保字段存在
                if "related_principles" not in item:
                    item["related_principles"] = []
                if "related_checklist" not in item:
                    item["related_checklist"] = []
            else:
                item.setdefault("related_principles", [])
                item.setdefault("related_checklist", [])

            game_result.append(item)
        result[game] = game_result
    return result


def main():
    print("读取数据...")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "timelines" not in data:
        print("未找到 timelines 字段")
        return

    # P2-4: 添加双向关联
    print("P2-4: 添加双向关联...")
    data["timelines"] = process_timelines(data["timelines"])

    # P2-5: 添加双轨对照免责声明
    if "comparison" in data:
        # 在 comparison 末尾添加说明
        pass  # 免责声明在前端添加

    # 统计
    total_related = 0
    for game, items in data.get("timelines", {}).items():
        game_related = sum(
            1 for item in items
            if item.get("related_principles") or item.get("related_checklist")
        )
        total_related += game_related
        print(f"  {game}: {game_related} 条有双向关联")

    print(f"\n共有 {total_related} 条时间轴事件建立了双向关联")
    print("写入数据...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("P2 处理完成！")


if __name__ == "__main__":
    main()

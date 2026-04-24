"""
本地静态数据管理模块（梦幻西游Like版）

架构原则：
- Steam 游戏（Temtem, Cassette Beasts, Palworld）的更新日志提前采集为本地 JSON 文件
- Pokemon 由 pokemon_wiki.py 提供内置结构化数据
- 梦幻西游Like游戏由 mhxy_data.py 提供数据
- 应用启动时直接读本地文件，不访问网络（除非本地数据不存在）
- 新增数据：通过 fetch_mhxy_data.py 脚本手动采集，更新到 data/ 目录

设计原则和检查清单：
- 根据游戏类型动态生成：梦幻西游Like使用独立配置，Pokemon使用内置配置
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# 导入报告配置模块
try:
    from report_generator_config import (
        get_report_data_for_game,
        GAME_TYPE_METADATA,
        MHXY_PRINCIPLES,
        MHXY_CHECKLISTS,
    )
    HAS_REPORT_CONFIG = True
except ImportError:
    HAS_REPORT_CONFIG = False
    MHXY_PRINCIPLES = []
    MHXY_CHECKLISTS = []


# 游戏标识到本地数据目录的映射（不含 Pokemon，Pokemon 由 pokemon_wiki.py 单独处理）
GAME_DATA_MAP = {
    # Steam 游戏
    "Temtem": "temtem",
    "Cassette Beasts": "cassette_beasts",
    "Palworld": "palworld",
    # 梦幻西游Like游戏
    "梦幻西游": "mhxy",
    "神武": "shenwu",
    "大话西游": "dhxy",
}

# Pokemon 专用数据文件
POKEMON_DATA_FILES = {
    "vgc_history": "pokemon/vgc_history.json",
}


class DataManager:
    """本地数据管理器"""

    # 梦幻西游Like版本的玩法关键词
    GAMEPLAY_KEYWORDS = [
        # 战斗相关
        "battle", "raid", "pvp", "pve", "竞技", "比武", "华山", "剑会",
        "mechanic", "feature", "system", "ability", "特性", "技能", "招式",
        "封印", "输出", "辅助", "治疗", "物理", "法术",
        "move", "skill", "attack", "type", "属性",
        "balance", "nerf", "buff", "adjust", "调整", "修改", "平衡", "削弱", "增强",
        "fix", "bug", "修复", "错误",
        # 门派相关
        "门派", "大唐", "方寸", "化生", "女儿", "狮驼", "魔王", "龙宫", "地府", "普陀", "天宫", "五庄", "盘丝", "凌波", "神木", "力地府", "女魃", "无底", "天机", "花果", "东海", "凌霄",
        # 召唤兽相关
        "召唤兽", "宝宝", "炼妖", "打书", "进阶", "内丹", "资质", "成长", "特性",
        # 阵法相关
        "阵法", "龙飞", "虎翼", "鸟翔", "云垂", "蛇蟠", "鹰啸", "地载", "天覆",
        # 系统相关
        "patch", "update", "ver", "version", "版本", "更新", "资料片",
        "dlc", "expansion", "content", "new", "新增",
        # 经济相关
        "装备", "宝石", "灵饰", "修炼", "强化", "打造", "熔炼",
        # 养成相关
        "等级", "经验", "金币", "银币", "仙玉", "日常", "周常",
        "组队", "对战", "双打", "单打", "5v5", "多人",
    ]

    EXCLUDE_KEYWORDS = [
        "price", "sale", "discount", "打折", "降价",
        "achievement", "steam award", "成就",
        "localization", "language", "语言",
        "soundtrack", "ost", "音乐",
        # 梦幻西游特有的排除项
        "锦衣", "祥瑞", "外观",  # 纯外观付费，不影响战力
    ]

    # 梦幻西游Like版本的分类规则
    CATEGORY_RULES = {
        # 战斗分类
        "PvP": ["pvp", "竞技", "比武", "华山", "剑会", "双打", "单打", "5v5", "对战"],
        "PvE": ["raid", "dungeon", "boss", "团体战", "合作", "副本", "神器", "归墟", "地煞"],
        # 机制分类
        "门派调整": ["门派", "大唐", "方寸", "化生", "女儿", "狮驼", "魔王", "龙宫", "地府", "普陀", "天宫", "五庄", "盘丝"],
        "召唤兽": ["召唤兽", "宝宝", "炼妖", "打书", "进阶", "内丹", "资质", "成长", "特性"],
        "阵法": ["阵法", "龙飞", "虎翼", "鸟翔", "云垂", "蛇蟠"],
        "装备": ["装备", "灵饰", "宝石", "打造", "熔炼"],
        "平衡性": ["balance", "nerf", "buff", "adjust", "调整", "削弱", "增强", "修改"],
        "内容": ["dlc", "expansion", "新增", "加入", "开放", "资料片"],
        "修复": ["fix", "bug", "issue", "crash", "error", "修复", "错误", "问题"],
    }

    # 互斥关键词：出现这些词时不判定为多人对战
    PVP_EXCLUDE = [
        "battle pass", "battle pass:", "battle pass：",
        "price", "sale", "discount", "打折", "降价",
        "achievement", "steam award", "成就",
        "localization", "language pack", "语言包",
        "soundtrack", "ost", "音乐",
        "锦衣", "祥瑞", "外观",  # 纯外观付费
    ]

    # PvE 互斥词：排除明显的商业/社交词汇
    PVE_EXCLUDE = [
        "battle pass", "season", "赛季", "price", "sale",
        "成就", "achievement", "steam",
        "锦衣", "祥瑞", "外观",
    ]

    # 梦幻西游Like版本的多人对战关键词
    MULTIPLAYER_KEYWORDS = [
        "raid", "battle", "doubles", "co-op", "multiplayer", "multi-player",
        "online", "versus", "vs", "tournament", "vgc", "competitive",
        "team", "group", "friends", "lobby",
        "团体战", "对战", "双打", "单打", "多人", "合作", "联机",
        # 梦幻西游特有
        "比武", "华山", "剑会", "武神坛", "5v5", "组队",
        "封印", "输出", "辅助", "点杀", "保护",
    ]

    def __init__(self, data_dir: Path = None):
        # data_manager.py 位于项目根目录，所以 .parent 就是项目根目录
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self._cache = {}

    # ---- 核心加载方法 ----

    def get_patches(self, game: str, count: int = 100) -> List[dict]:
        """
        获取更新日志（从本地文件）

        与 SteamScraper.get_patch_notes() 输出格式兼容，
        保证 app.py 无需感知数据来源差异。
        """
        data_key = game
        if data_key in self._cache:
            raw_patches = self._cache[data_key]
        else:
            raw_patches = self._load_local(game)

        # 过滤 + 分类
        filtered = []
        for patch in raw_patches[:count]:
            title = patch.get("title", "")
            content = patch.get("content", "")
            if self._is_gameplay_related(title, content):
                categories = self._categorize(title, content)
                filtered.append({
                    "title": title,
                    "date": patch.get("date", ""),
                    "url": patch.get("url", ""),
                    "content": content[:5000],
                    "categories": categories,
                    "game": game,
                })
        return filtered

    def get_multiplayer_patches(self, game: str, count: int = 100) -> List[dict]:
        """只获取与多人对战相关的更新"""
        all_patches = self.get_patches(game, count)
        mp_patches = []
        for patch in all_patches:
            text = f"{patch['title']} {patch['content']}".lower()
            if any(kw.lower() in text for kw in self.MULTIPLAYER_KEYWORDS):
                mp_patches.append(patch)
        return mp_patches

    def get_news(self, game: str, count: int = 50) -> List[dict]:
        """获取原始新闻列表（未过滤）"""
        return self._load_local(game)[:count]

    # ---- 内部方法 ----

    def _load_local(self, game: str) -> List[dict]:
        """从本地文件加载原始补丁数据"""
        data_key = game
        if data_key in self._cache:
            return self._cache[data_key]

        folder = GAME_DATA_MAP.get(game)
        if not folder:
            return []

        filepath = self.data_dir / folder / "patches.json"
        if not filepath.exists():
            return []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            patches = data.get("patches", [])
            self._cache[data_key] = patches
            return patches
        except (json.JSONDecodeError, IOError):
            return []

    def _is_gameplay_related(self, title: str, content: str) -> bool:
        """判断是否与玩法相关"""
        text = f"{title} {content}".lower()
        has_gameplay = any(kw in text for kw in self.GAMEPLAY_KEYWORDS)
        is_excluded = all(kw in text for kw in self.EXCLUDE_KEYWORDS)
        return has_gameplay and not is_excluded

    def _categorize(self, title: str, content: str) -> List[str]:
        """为更新打标签（互斥逻辑防止误分类）"""
        text = (f"{title} {content}").lower()
        categories = []

        # 先检查互斥词
        has_pvp_exclude = any(ex in text for ex in self.PVP_EXCLUDE)
        has_pve_exclude = any(ex in text for ex in self.PVE_EXCLUDE)

        for cat, keywords in self.CATEGORY_RULES.items():
            # PvP/PvE 分类时应用互斥逻辑
            if cat in ("PvP", "PvE") and any(kw.lower() in text for kw in keywords):
                if cat == "PvP" and has_pvp_exclude:
                    continue
                if cat == "PvE" and has_pve_exclude:
                    continue
                categories.append(cat)
            elif cat not in ("PvP", "PvE") and any(kw.lower() in text for kw in keywords):
                categories.append(cat)

        return categories if categories else ["其他"]

    # ---- 设计原则和检查清单 ----

    def get_report_data(self, game: str = None, game_type: str = None) -> Dict[str, Any]:
        """
        获取指定游戏的报告数据（设计原则、检查清单等）

        Args:
            game: 游戏名称（可选，用于判断游戏类型）
            game_type: 游戏类型 ('mhxy' 或 'pokemon')，优先级高于 game

        Returns:
            报告数据字典，包含 principles（设计原则）、checklist（检查清单）等
        """
        # 确定游戏类型
        if game_type is None and game:
            game_type = self._get_game_type(game)

        if not HAS_REPORT_CONFIG:
            return {"principles": [], "checklist": [], "scenarios": [], "meta": {}}

        return get_report_data_for_game(game_type)

    def get_principles(self, game: str = None, game_type: str = None) -> List[Dict]:
        """获取设计原则列表"""
        report_data = self.get_report_data(game, game_type)
        return report_data.get("principles", [])

    def get_checklist(self, game: str = None, game_type: str = None) -> List[Dict]:
        """获取检查清单列表"""
        report_data = self.get_report_data(game, game_type)
        return report_data.get("checklist", [])

    def get_principles_count(self, game: str = None, game_type: str = None) -> int:
        """获取设计原则数量"""
        report_data = self.get_report_data(game, game_type)
        return len(report_data.get("principles", []))

    def get_checklist_count(self, game: str = None, game_type: str = None) -> int:
        """获取检查清单条目总数"""
        report_data = self.get_report_data(game, game_type)
        checklist = report_data.get("checklist", [])
        return sum(len(cat.get("items", [])) for cat in checklist)

    def _get_game_type(self, game: str) -> str:
        """根据游戏名称判断游戏类型"""
        mhxy_games = ["梦幻西游", "神武", "大话西游"]
        pokemon_games = ["Pokemon", "Temtem", "Cassette Beasts", "Palworld"]

        if game in mhxy_games:
            return "mhxy"
        elif game in pokemon_games:
            return "pokemon"
        else:
            return "pokemon"  # 默认

    # ---- 数据统计 ----

    def get_stats(self, game: str) -> dict:
        """获取本地数据统计"""
        raw = self._load_local(game)
        gameplay = self._is_gameplay_related
        patches = [p for p in raw if self._is_gameplay_related(p.get("title", ""), p.get("content", ""))]
        return {
            "total": len(raw),
            "gameplay": len(patches),
            "game": game,
            "source": "local",
        }


# 全局实例
data_manager = DataManager()

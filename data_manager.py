"""
本地静态数据管理模块

架构原则：
- Steam 游戏（Temtem, Cassette Beasts, Palworld）的更新日志提前采集为本地 JSON 文件
- Pokemon 由 pokemon_wiki.py 提供内置结构化数据
- 应用启动时直接读本地文件，不访问网络（除非本地数据不存在）
- 新增数据：通过 fetch_all_data.py 脚本手动采集，更新到 data/ 目录

数据来源：
- Steam 游戏：运行 fetch_all_data.py 采集 Steam News API
- Pokemon：内置于 scrapers/pokemon_wiki.py（已包含 Gen 8/9 完整数据）
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime


# 游戏标识到本地数据目录的映射（不含 Pokemon，Pokemon 由 pokemon_wiki.py 单独处理）
GAME_DATA_MAP = {
    "Temtem": "temtem",
    "Cassette Beasts": "cassette_beasts",
    "Palworld": "palworld",
}

# Pokemon 专用数据文件
POKEMON_DATA_FILES = {
    "vgc_history": "pokemon/vgc_history.json",
}


class DataManager:
    """本地数据管理器"""

    GAMEPLAY_KEYWORDS = [
        "battle", "raid", "vgc", "doubles", "singles", "tournament", "championship",
        "mechanic", "feature", "system", "ability", "特性", "技能", "招式",
        "move", "skill", "attack", "type", "属性",
        "balance", "nerf", "buff", "adjust", "调整", "修改", "平衡",
        "fix", "bug", "修复", "错误",
        "dynamax", "gigantamax", "tera", "mega", "z-move", "极巨化", "太晶化",
        "patch", "update", "ver", "version", "版本", "更新",
        "dlc", "expansion", "content", "new", "新增",
        "co-op", "multiplayer", "2v2", "组队", "对战", "双打", "单打",
    ]

    EXCLUDE_KEYWORDS = [
        "price", "sale", "discount", "打折", "降价",
        "achievement", "steam award", "成就",
        "localization", "language", "语言",
        "soundtrack", "ost", "音乐",
    ]

    CATEGORY_RULES = {
        "PvP": ["vgc", "tournament", "championship", "doubles", "singles", "ranked", "对战", "竞技", "双打", "单打"],
        "PvE": ["raid", "dungeon", "boss", "团体战", "合作"],
        "机制": ["mechanic", "system", "feature", "ability", "特性", "move", "skill", "type", "技能", "招式", "极巨化", "太晶化", "mega", "dynamax", "tera"],
        "平衡性": ["balance", "nerf", "buff", "adjust", "modify", "调整", "削弱", "增强", "修改"],
        "内容": ["dlc", "expansion", "新增", "加入", "开放"],
        "修复": ["fix", "bug", "issue", "crash", "error", "修复", "错误", "问题"],
    }

    # 互斥关键词：出现这些词时不判定为多人对战
    # 解决 "battle pass" 被误判为 PvP 的问题
    PVP_EXCLUDE = [
        "battle pass", "battle pass:", "battle pass：",
        "price", "sale", "discount", "打折", "降价",
        "achievement", "steam award", "成就",
        "localization", "language pack", "语言包",
        "soundtrack", "ost", "音乐",
    ]

    # PvE 互斥词：排除明显的商业/社交词汇
    PVE_EXCLUDE = [
        "battle pass", "season", "赛季", "price", "sale",
        "成就", "achievement", "steam",
    ]

    MULTIPLAYER_KEYWORDS = [
        "raid", "battle", "doubles", "co-op", "multiplayer", "multi-player",
        "online", "versus", "vs", "tournament", "vgc", "competitive",
        "team", "group", "friends", "lobby",
        "团体战", "对战", "双打", "单打", "多人", "合作", "联机",
        "dynamax", "tera", "gigantamax", "极巨化", "太晶化",
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

"""
Steam 官方 API 和页面爬虫

架构说明：
- Steam 游戏（Temtem, Cassette Beasts, Palworld）的更新日志优先从本地 data/ 目录读取
- 本地数据通过 fetch_all_data.py 脚本提前采集
- 仅当本地数据不存在时，才访问 Steam API（降级方案）
"""

import re
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from utils.config import config

# 本地数据管理器（优先）
try:
    from data_manager import DataManager
    _data_manager = DataManager()
except ImportError:
    _data_manager = None


class SteamScraper:
    """Steam 平台爬虫基类"""

    STEAM_NEWS_API = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
    STEAM_STORE_API = "https://store.steampowered.com"
    COMMUNITY_API = "https://steamcommunity.com"

    APP_IDS = {
        "Pokemon": {
            "name": "Pokemon Sword/Shield",
            "id": "1181700",
            "name_localized": "宝可梦 剑·盾",
        },
        "Temtem": {
            "name": "Temtem",
            "id": "745920",
            "name_localized": "Temtem",
        },
        "Cassette Beasts": {
            "name": "Cassette Beasts",
            "id": "1322240",
            "name_localized": "磁带妖怪",
        },
        "Palworld": {
            "name": "Palworld",
            "id": "1623730",
            "name_localized": "幻兽帕鲁",
        },
    }

    def __init__(self, game: str = "Pokemon"):
        if game not in self.APP_IDS:
            raise ValueError(f"不支持的游戏: {game}，支持的: {list(self.APP_IDS.keys())}")

        self.game = game
        self.app_id = self.APP_IDS[game]["id"]
        self.game_name = self.APP_IDS[game]["name"]
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})
        self.session.trust_env = False

        # 配置重试策略和超时
        retry_strategy = Retry(
            total=3,  # 最多重试3次
            backoff_factor=0.5,  # 重试间隔：0.5秒、1秒、2秒
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _fetch_steam_api(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """调用 Steam API"""
        try:
            response = self.session.get(
                endpoint,
                params=params,
                timeout=60,  # 增加到60秒超时
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Steam API 请求失败: {e}")
            return None

    def _fetch_html(self, url: str) -> Optional[BeautifulSoup]:
        """获取 HTML 页面"""
        try:
            response = self.session.get(url, timeout=60)  # 增加到60秒超时
            response.raise_for_status()
            return BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"HTML 请求失败: {url}, {e}")
            return None

    # ==================== 核心功能 ====================

    def get_news(self, count: int = 50) -> List[dict]:
        """
        获取 Steam 新闻（更新日志）
        优先从本地 data/ 目录读取，本地不存在时访问 Steam API
        """
        # 优先使用本地数据
        if _data_manager is not None:
            local_news = _data_manager.get_news(self.game, count)
            if local_news:
                return local_news

        # 降级：访问 Steam API
        data = self._fetch_steam_api(
            self.STEAM_NEWS_API,
            params={
                "appid": self.app_id,
                "count": count,
                "format": "json",
            }
        )

        if not data or "appnews" not in data:
            return []

        news_items = []
        for item in data["appnews"]["newsitems"]:
            news_items.append({
                "gid": item.get("gid"),
                "title": item.get("title"),
                "url": item.get("url"),
                "date": datetime.fromtimestamp(item.get("date", 0)).strftime("%Y-%m-%d"),
                "timestamp": item.get("date"),
                "author": item.get("author"),
                "contents": self._clean_html(item.get("contents", "")),
                "feed_label": item.get("feedlabel"),
            })

        return news_items

    def get_patch_notes(self, count: int = 100) -> List[dict]:
        """
        获取版本更新日志
        自动过滤只保留与玩法相关的更新
        优先从本地读取，API 仅降级
        """
        # 优先使用本地数据（DataManager 已完成过滤+分类）
        if _data_manager is not None:
            local_patches = _data_manager.get_patches(self.game, count)
            if local_patches:
                return local_patches

        # 降级：自己从 API 数据中过滤+分类
        news = self.get_news(count)
        patches = []

        for item in news:
            content = item["contents"]
            title = item["title"]

            if self._is_gameplay_related(title, content):
                categories = self._categorize(title, content)

                patches.append({
                    "title": title,
                    "date": item["date"],
                    "url": item["url"],
                    "content": content[:5000],
                    "categories": categories,
                    "game": self.game,
                })

        return patches

    def get_store_announcements(self) -> List[dict]:
        """从商店页面获取公告"""
        announcements = []

        url = f"{self.STEAM_STORE_API}/app/{self.app_id}/"
        soup = self._fetch_html(url)

        if not soup:
            return announcements

        # Steam 商店页面的公告区域
        news_section = soup.find("div", {"id": "game_highlights"})
        if news_section:
            links = news_section.find_all("a")
            for link in links:
                href = link.get("href", "")
                if "steamcommunity.com" in href or "/announcements" in href:
                    announcements.append({
                        "title": link.get_text(strip=True),
                        "url": href,
                    })

        return announcements

    # ==================== 辅助方法 ====================

    def _clean_html(self, html_content: str) -> str:
        """清理 HTML 为纯文本"""
        soup = BeautifulSoup(html_content, "lxml")

        # 移除脚本和样式
        for tag in soup(["script", "style"]):
            tag.decompose()

        # 提取文本
        text = soup.get_text(separator="\n", strip=True)
        # 清理空行
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def _is_gameplay_related(self, title: str, content: str) -> bool:
        """判断是否与玩法相关"""
        text = f"{title} {content}".lower()

        # 玩法相关关键词
        gameplay_keywords = [
            # 多人/对战
            "battle", "对战", "vgc", "raid", "团体战", "multiplayer", "co-op",
            "2v2", "doubles", "singles", "tournament", "championship",
            # 机制
            "mechanic", "feature", "system", "ability", "特性", "技能", "招式",
            "move", "skill", "attack", "type", "属性",
            # 平衡
            "balance", "nerf", "buff", "adjust", "调整", "修改", "平衡",
            "fix", "bug", "修复", "错误",
            # 强化系统
            "dynamax", "gigantamax", "tera", "mega", "z-move", "极巨化", "太晶化",
            # 版本
            "patch", "update", "ver", "version", "版本", "更新",
            "dlc", "expansion", "content", "new", "新增",
        ]

        # 排除关键词
        exclude_keywords = [
            "price", "sale", "discount", "打折", "降价",
            "achievement", "steam award", "成就",
            "localization", "language", "语言",
            "soundtrack", "ost", "音乐",
        ]

        # 必须包含玩法关键词
        has_gameplay = any(kw in text for kw in gameplay_keywords)

        # 不能只包含排除关键词
        is_excluded = all(kw in text for kw in exclude_keywords)

        return has_gameplay and not is_excluded

    def _categorize(self, title: str, content: str) -> List[str]:
        """为更新打标签"""
        text = f"{title} {content}"
        categories = []

        category_rules = {
            "PvP": [
                "battle", "vgc", "tournament", "championship", "doubles",
                "singles", "ranked", "对战", "竞技",
            ],
            "PvE": [
                "raid", "dungeon", "boss", "adventure", "story",
                "团体战", "团体战", "合作", "多人",
            ],
            "机制": [
                "mechanic", "system", "feature", "ability", "特性",
                "move", "skill", "type", "技能", "招式",
            ],
            "平衡性": [
                "balance", "nerf", "buff", "adjust", "modify",
                "调整", "削弱", "增强", "修改",
            ],
            "内容": [
                "new", "add", "introduce", "dlc", "expansion",
                "新增", "加入", "开放", "content",
            ],
            "修复": [
                "fix", "bug", "issue", "crash", "error",
                "修复", "错误", "问题",
            ],
        }

        for category, keywords in category_rules.items():
            if any(kw.lower() in text.lower() for kw in keywords):
                categories.append(category)

        return categories if categories else ["其他"]

    # ==================== 多人相关筛选 ====================

    def get_multiplayer_patches(self, count: int = 100) -> List[dict]:
        """
        只获取与多人对战相关的更新
        优先从本地数据读取
        """
        # 优先使用本地数据
        if _data_manager is not None:
            local_mp = _data_manager.get_multiplayer_patches(self.game, count)
            if local_mp:
                return local_mp

        # 降级：自己过滤
        all_patches = self.get_patch_notes(count)
        multiplayer_patches = []

        multiplayer_keywords = [
            # 英文
            "raid", "battle", "doubles", "co-op", "multiplayer", "multi-player",
            "online", "versus", "vs", "tournament", "vgc", "competitive",
            "team", "group", "friends", "lobby",
            # 中文
            "团体战", "对战", "双打", "单打", "多人", "合作", "联机",
            "raid", "工会", "组队", "匹配",
            # 机制
            "dynamax", "tera", "gigantamax", "极巨化", "太晶化",
        ]

        for patch in all_patches:
            text = f"{patch['title']} {patch['content']}".lower()
            if any(kw.lower() in text for kw in multiplayer_keywords):
                multiplayer_patches.append(patch)

        return multiplayer_patches

    def get_mechanic_changes(self, mechanic: str, count: int = 100) -> List[dict]:
        """
        获取特定机制相关的更新
        例如: mechanic="dynamax", mechanic="tera"
        """
        all_patches = self.get_patch_notes(count)
        mechanic_patches = []

        for patch in all_patches:
            text = f"{patch['title']} {patch['content']}"
            if mechanic.lower() in text.lower():
                mechanic_patches.append(patch)

        return mechanic_patches

    def rate_limit(self):
        """遵守速率限制"""
        time.sleep(1)


# ==================== 各游戏专用爬虫 ====================


class PokemonSteamScraper(SteamScraper):
    """宝可梦剑/盾 Steam 爬虫"""

    def __init__(self):
        super().__init__("Pokemon")

    def get_dynamax_changes(self) -> List[dict]:
        """获取极巨化相关变更"""
        return self.get_mechanic_changes("dynamax")

    def get_tera_changes(self) -> List[dict]:
        """获取太晶化相关变更（朱紫）"""
        return self.get_mechanic_changes("tera")

    def get_raid_changes(self) -> List[dict]:
        """获取团体战相关变更"""
        return self.get_mechanic_changes("raid")


class TemtemSteamScraper(SteamScraper):
    """Temtem Steam 爬虫"""

    def __init__(self):
        super().__init__("Temtem")

    def get_ban_pick_changes(self) -> List[dict]:
        """获取 Ban/Pick 机制变更"""
        return self.get_mechanic_changes("ban")

    def get_luma_changes(self) -> List[dict]:
        """获取异色/闪光系统变更"""
        return self.get_mechanic_changes("luma")


class PalworldSteamScraper(SteamScraper):
    """幻兽帕鲁 Steam 爬虫"""

    def __init__(self):
        super().__init__("Palworld")

    def get_raid_changes(self) -> List[dict]:
        """获取 Raid Boss 相关变更"""
        return self.get_mechanic_changes("raid")

    def get_pal_changes(self) -> List[dict]:
        """获取帕鲁（宠物）平衡调整"""
        return self.get_mechanic_changes("work")


class CassetteBeastsScraper(SteamScraper):
    """磁带妖怪 Steam 爬虫"""

    def __init__(self):
        super().__init__("Cassette Beasts")

    def get_fusion_changes(self) -> List[dict]:
        """获取融合机制变更"""
        return self.get_mechanic_changes("fusion")

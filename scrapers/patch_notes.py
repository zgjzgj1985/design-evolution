"""
官方更新日志爬虫模块
从 Steam 社区等渠道抓取游戏更新日志
"""

from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.config import config


class PatchNotesScraper:
    """游戏更新日志爬虫基类"""

    STEAM_APP_IDS = {
        "Pokemon": {
            "name": "宝可梦 剑/盾",
            "id": "1181700",
            "url": "https://store.steampowered.com/news/app/1181700",
        },
        "Temtem": {
            "name": "Temtem",
            "id": "745920",
            "url": "https://store.steampowered.com/news/app/745920",
        },
        "Cassette Beasts": {
            "name": "Cassette Beasts",
            "id": "1322240",
            "url": "https://store.steampowered.com/news/app/1322240",
        },
        "Palworld": {
            "name": "幻兽帕鲁",
            "id": "1623730",
            "url": "https://store.steampowered.com/news/app/1623730",
        },
    }

    def __init__(self, game: str = "Pokemon"):
        self.game = game
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})
        # 保持代理设置启用，确保能通过代理访问 Steam API

        if game in self.STEAM_APP_IDS:
            self.steam_info = self.STEAM_APP_IDS[game]
        else:
            raise ValueError(f"不支持的游戏: {game}，支持的: {list(self.STEAM_APP_IDS.keys())}")

    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """通用页面获取方法"""
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None

    def get_patch_notes(self, limit: int = 20) -> list:
        """
        从 Steam 社区获取更新日志
        返回: [{"title": "更新标题", "date": "2024-01-01", "url": "...", "content": "..."}, ...]
        """
        steam_news_url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={self.steam_info['id']}&count={limit}&format=json"

        try:
            response = self.session.get(steam_news_url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            news_items = []
            for item in data.get("appnews", {}).get("newsitems", []):
                # 转换时间戳
                timestamp = int(item.get("date", 0))
                date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d") if timestamp else ""

                news_items.append({
                    "title": item.get("title", ""),
                    "date": date_str,
                    "url": item.get("url", ""),
                    "gid": item.get("gid", ""),
                    "content": self._clean_html(item.get("contents", "")),
                })
            return news_items
        except requests.RequestException as e:
            print(f"获取 Steam 新闻失败: {e}")
            return []

    def get_patch_notes_from_community(self, limit: int = 20) -> list:
        """
        从 Steam 社区页面直接抓取更新日志（备选方案）
        """
        soup = self._fetch_page(self.steam_info["url"])
        if not soup:
            return []

        patches = []
        # Steam 社区新闻页面结构
        news_items = soup.select(".newsPost")

        for item in news_items[:limit]:
            title_elem = item.select_one(".newsPostTitle")
            date_elem = item.select_one(".date")
            link_elem = item.select_one("a")

            if title_elem:
                patches.append({
                    "title": title_elem.get_text(strip=True),
                    "date": date_elem.get_text(strip=True) if date_elem else "",
                    "url": link_elem.get("href", "") if link_elem else "",
                })

        return patches

    def _clean_html(self, html_content: str) -> str:
        """清理 HTML 标签，保留纯文本"""
        soup = BeautifulSoup(html_content, "lxml")
        return soup.get_text(separator="\n", strip=True)

    def filter_multiplayer_changes(self, patch_content: str) -> bool:
        """
        判断更新日志是否包含多人对战相关内容
        关键词匹配
        """
        multiplayer_keywords = [
            # PvP 相关
            "对战", "VGC", "双打", "单打", "单打", "规则", "限制",
            "ban", "Ban", "禁止", "规则E", "规则D", "规则B",
            # PvE 多人相关
            "团体战", "raid", "Raid", "合作", "多人",
            # 机制相关
            "极巨化", "太晶化", "特性", "技能", "平衡",
        ]

        content_lower = patch_content.lower()
        return any(kw.lower() in content_lower for kw in multiplayer_keywords)

    def categorize_patch(self, title: str, content: str) -> list:
        """
        为更新日志打标签
        返回: ["PvP", "机制调整"] 等标签列表
        """
        categories = []
        text = f"{title} {content}"

        category_rules = {
            "PvP": ["VGC", "对战", "双打", "单打", "规则", "限制", "ban", "Ban"],
            "PvE": ["团体战", "raid", "Raid", "合作", "冒险", "故事"],
            "机制": ["极巨化", "太晶化", "特性", "技能", "招式", "变化"],
            "平衡性": ["调整", "修改", "变更", "nerf", "buff", "削弱", "增强"],
            "内容": ["新增", "加入", "开放", "追加", "新加入"],
        }

        for category, keywords in category_rules.items():
            if any(kw in text for kw in keywords):
                categories.append(category)

        return categories if categories else ["其他"]

    def get_temtem_patch_notes(self) -> list:
        """
        Temtem 更新日志（MVP阶段使用结构化数据）
        Temtem 每两周发布一次更新
        """
        # TODO: 爬取 https://crema.gg/temtem/temtem-roadmap/
        # 或 https://store.steampowered.com/news/app/745920
        patches = [
            {
                "version": "1.0",
                "date": "2023-08-15",
                "title": "Temtem 正式版发布",
                "changes": [
                    {
                        "category": "PvP",
                        "content": "2v2 Ban/Pick 竞技场正式上线",
                        "intent": "正式引入电竞化的 Ban/Pick 机制，增强竞技深度",
                    },
                ],
            },
        ]
        return patches

    def get_palworld_patch_notes(self) -> list:
        """
        幻兽帕鲁更新日志（MVP阶段使用结构化数据）
        """
        # TODO: 爬取 https://store.steampowered.com/news/app/1623730
        patches = [
            {
                "version": "0.1.0",
                "date": "2024-01-19",
                "title": "EA 早期测试开始",
                "changes": [
                    {
                        "category": "PvE",
                        "content": "多人Raid Boss 机制上线",
                        "intent": "引入多人合作挑战内容，填补生存建造+战斗的空白",
                    },
                ],
            },
        ]
        return patches

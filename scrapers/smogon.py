"""
Smogon / Pikalytics 数据爬虫
数据源:
- Smogon: https://www.smogon.com - 宝可梦竞技规则和分析
- Pikalytics: https://pikalytics.com - 宝可梦使用率数据
"""

import re
import time
import requests
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from utils.config import config


class SmogonScraper:
    """Smogon 竞技数据爬虫"""

    BASE_URL = "https://www.smogon.com"
    STATS_BASE = "https://www.smogon.com/stats"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        })

    def _fetch(self, path: str) -> Optional[BeautifulSoup]:
        """获取页面"""
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Smogon 请求失败: {url}, {e}")
            return None

    def get_format_list(self) -> List[dict]:
        """获取所有竞技规则格式"""
        formats = []

        soup = self._fetch("forums/categories/pokemon-showdown.13/")
        if not soup:
            # 尝试 stats 页面
            soup = self._fetch("stats/")

        if soup:
            links = soup.find_all("a")
            for link in links:
                href = link.get("href", "")
                if "/stats/" in href or "format" in href.lower():
                    text = link.get_text(strip=True)
                    if text and text not in ["", "/"]:
                        formats.append({
                            "name": text,
                            "url": href if href.startswith("http") else f"{self.BASE_URL}{href}",
                        })

        return formats

    def get_metagame_overview(self, format_name: str) -> dict:
        """
        获取特定规则的 Meta 游戏概览
        例如: format_name = "gen9vgc2024"
        """
        overview = {}

        soup = self._fetch(f"forums/posts/{format_name}/")
        if not soup:
            return overview

        # 解析页面内容
        # Smogon 页面结构复杂，这里简化处理
        main_content = soup.find("div", class_="main-content")
        if main_content:
            overview["content"] = main_content.get_text(separator="\n", strip=True)

        return overview


class SmogonStatsScraper:
    """Smogon 统计数据爬虫"""

    STATS_URL = "https://www.smogon.com/stats"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT + " (Research Bot)",
        })

    def _fetch_text(self, url: str) -> Optional[str]:
        """获取纯文本数据（Smogon stats 用文本格式）"""
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Stats 请求失败: {url}, {e}")
            return None

    def get_monthly_stats(self, year: int, month: int) -> List[dict]:
        """
        获取月度统计数据
        例如: year=2024, month=1 -> 2024-01
        """
        month_str = f"{year}-{month:02d}"
        url = f"{self.STATS_URL}/?month={month_str}"

        text = self._fetch_text(url)
        if not text:
            return []

        stats = []
        lines = text.strip().split("\n")

        for line in lines[:50]:  # 限制解析行数
            parts = line.split("|")
            if len(parts) >= 4:
                rank = parts[1].strip()
                pokemon = parts[2].strip()
                usage = parts[3].strip()

                if rank.isdigit() and pokemon:
                    stats.append({
                        "rank": int(rank),
                        "pokemon": pokemon,
                        "usage_percent": usage,
                        "month": month_str,
                    })

        return stats

    def get_pokemon_usage_details(self, pokemon_name: str, format_name: str = "gen9") -> dict:
        """
        获取特定宝可梦的使用详情
        """
        details = {}

        # 构造 URL
        url = f"{self.STATS_URL}/moveset/{format_name}/{pokemon_name.lower().replace(' ', '-')}.txt"

        text = self._fetch_text(url)
        if not text:
            return details

        # 解析数据
        lines = text.strip().split("\n")
        current_section = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Moveset:"):
                current_section = "moveset"
                details["moveset"] = line.replace("Moveset:", "").strip()
            elif line.startswith("Ability:"):
                current_section = "ability"
                details["ability"] = line.replace("Ability:", "").strip()
            elif line.startswith("Items:"):
                current_section = "items"
                details["items"] = line.replace("Items:", "").strip()
            elif line.startswith("Spreads:"):
                current_section = "spreads"
                details["spreads"] = line.replace("Spreads:", "").strip()
            elif line.startswith("Teammates:"):
                current_section = "teammates"
                details["teammates"] = []
            elif current_section == "teammates" and not line.startswith("=="):
                details["teammates"].append(line)

        return details


class PikalyticsScraper:
    """Pikalytics 数据爬虫 - 宝可梦使用率数据"""

    BASE_URL = "https://pikalytics.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT,
        })

    def _fetch(self, path: str) -> Optional[BeautifulSoup]:
        """获取页面"""
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Pikalytics 请求失败: {url}, {e}")
            return None

    def get_pokemon_data(self, pokemon_name: str, format_name: str = "vgc") -> dict:
        """
        获取宝可梦的详细使用数据
        包括: 使用率、技能配置、特性、道具等
        """
        data = {}

        # Pikalytics URL 格式: /pokedex/{format}/{pokemon}/
        url = f"pokedex/{format_name}/{pokemon_name.lower().replace(' ', '-')}/"
        soup = self._fetch(url)

        if not soup:
            return data

        # 解析页面
        # 使用率
        usage_elem = soup.find("span", class_="usage-percent")
        if usage_elem:
            data["usage_percent"] = usage_elem.get_text(strip=True)

        # 技能配置
        moves_section = soup.find("div", {"id": "moves"})
        if moves_section:
            moves = moves_section.find_all("li")
            data["moves"] = [m.get_text(strip=True) for m in moves[:4]]

        # 特性
        abilities_section = soup.find("div", {"id": "abilities"})
        if abilities_section:
            abilities = abilities_section.find_all("li")
            data["abilities"] = [a.get_text(strip=True) for a in abilities]

        # 道具
        items_section = soup.find("div", {"id": "items"})
        if items_section:
            items = items_section.find_all("li")
            data["items"] = [i.get_text(strip=True) for i in items[:4]]

        # 努力值分布
        spreads_section = soup.find("div", {"id": "spreads"})
        if spreads_section:
            spreads = spreads_section.find_all("li")
            data["spreads"] = [s.get_text(strip=True) for s in spreads[:5]]

        return data

    def get_format_data(self, format_name: str = "vgc") -> dict:
        """
        获取整体 Meta 数据
        """
        data = {}

        url = f"pokedex/{format_name}/"
        soup = self._fetch(url)

        if not soup:
            return data

        # 解析整体统计
        # 这个页面的结构可能变化，需要根据实际情况调整

        return data


# ==================== 开发者博客爬虫 ====================


class DevBlogScraper:
    """游戏开发者博客爬虫"""

    DEV_BLOGS = {
        "Pokemon": [
            "https://Pokemon.com",
            "https://Pokemon.co.jp",
        ],
        "Temtem": [
            "https://crema.gg/temtem/",
            "https://crema.gg/blog/",
        ],
        "Cassette Beasts": [
            "https://www.bytten Studio.com/blog/",
        ],
        "Palworld": [
            "https://Pocketpair.jp/",
        ],
    }

    def __init__(self, game: str = "Temtem"):
        self.game = game
        self.blogs = self.DEV_BLOGS.get(game, [])

    def get_dev_posts(self) -> List[dict]:
        """获取开发者博客文章"""
        posts = []

        for blog_url in self.blogs:
            posts.extend(self._fetch_blog_posts(blog_url))

        return posts

    def _fetch_blog_posts(self, url: str) -> List[dict]:
        """获取单个博客的文章列表"""
        posts = []
        import requests

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")

            # 查找文章链接
            articles = soup.find_all("article")
            for article in articles[:20]:
                link = article.find("a") or article.find_parent("a")
                title = article.find("h2") or article.find("h3")
                date = article.find("time") or article.find("span", class_="date")

                if link:
                    posts.append({
                        "title": title.get_text(strip=True) if title else "",
                        "url": link.get("href", ""),
                        "date": date.get_text(strip=True) if date else "",
                    })

        except Exception as e:
            print(f"博客获取失败 {url}: {e}")

        return posts

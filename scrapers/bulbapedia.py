"""
Bulbapedia Wiki 爬虫
数据源: https://bulbapedia.bulbagarden.net
Bulbapedia 是宝可梦最全面的英文 Wiki，包含历代版本信息、历史改动等
"""

import re
import time
import requests
from typing import Optional, List
from bs4 import BeautifulSoup
from utils.config import config


class BulbapediaScraper:
    """Bulbapedia Wiki 爬虫"""

    BASE_URL = "https://bulbapedia.bulbagarden.net"
    API_URL = "https://bulbapedia.bulbagarden.net/api.php"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT,
            "Accept": "application/json",
        })

    def _api_request(self, params: dict) -> Optional[dict]:
        """调用 Bulbapedia API"""
        default_params = {
            "format": "json",
            "maxlag": "5",
        }
        default_params.update(params)

        try:
            response = self.session.get(
                self.API_URL,
                params=default_params,
                timeout=config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API 请求失败: {e}")
            return None

    def search_pages(self, query: str, limit: int = 10) -> List[dict]:
        """搜索 Wiki 页面"""
        result = self._api_request({
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
        })

        if not result or "query" not in result:
            return []

        return [
            {
                "pageid": page["pageid"],
                "title": page["title"],
                "snippet": page.get("snippet", ""),
            }
            for page in result["query"]["search"]
        ]

    def get_page_content(self, title: str) -> Optional[str]:
        """获取页面内容（解析后的 wikitext）"""
        result = self._api_request({
            "action": "parse",
            "page": title,
            "prop": "wikitext",
            "formatversion": "2",
        })

        if result and "parse" in result:
            return result["parse"]["wikitext"]
        return None

    def get_page_html(self, title: str) -> Optional[BeautifulSoup]:
        """获取页面 HTML 内容"""
        result = self._api_request({
            "action": "parse",
            "page": title,
            "prop": "text",
        })

        if result and "parse" in result:
            html = result["parse"]["text"]["*"]
            return BeautifulSoup(html, "lxml")
        return None

    def get_version_history(self, game_name: str) -> List[dict]:
        """
        获取宝可梦游戏版本历史页面
        目标页面如: "Pokemon_Video_Game_Release_Dates" 或各版本专属页面
        """
        versions = []

        # 搜索相关页面
        search_results = self.search_pages(f"{game_name} release history", limit=5)

        for result in search_results:
            if "release" in result["title"].lower() or "history" in result["title"].lower():
                content = self.get_page_html(result["title"])
                if content:
                    versions.extend(self._parse_version_table(content))

        return versions

    def _parse_version_table(self, soup: BeautifulSoup) -> List[dict]:
        """解析版本信息表格"""
        versions = []

        tables = soup.find_all("table", class_="wikitable")
        for table in tables:
            rows = table.find_all("tr")
            headers = []

            # 解析表头
            header_row = rows[0] if rows else None
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]

            # 解析数据行
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    version_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            version_data[headers[i].lower()] = cell.get_text(strip=True)
                        else:
                            version_data[f"col_{i}"] = cell.get_text(strip=True)

                    if version_data:
                        versions.append(version_data)

        return versions

    def get_pokemon_mechanics_by_generation(self, generation: int) -> List[dict]:
        """
        获取指定世代的宝可梦对战机制信息
        """
        mechanics = []

        # 搜索该世代的相关页面
        search_term = f"Generation_{generation}_video_game_features"
        content = self.get_page_html(search_term)

        if not content:
            # 尝试通用页面
            content = self.get_page_html(f"Pokemon_Video_Game_Release_Dates")

        if content:
            # 解析主要内容和表格
            mechanics.extend(self._parse_mechanics_section(content))

        return mechanics

    def _parse_mechanics_section(self, soup: BeautifulSoup) -> List[dict]:
        """解析机制相关内容"""
        mechanics = []

        # 查找包含机制信息的章节
        headings = soup.find_all(["h2", "h3", "h4"])
        current_section = ""

        for heading in headings:
            heading_text = heading.get_text(strip=True)
            if any(kw in heading_text.lower() for kw in ["battle", "combat", "mechanic", "feature"]):
                current_section = heading_text

                # 查找该章节后的内容
                next_elem = heading.find_next_sibling()
                while next_elem:
                    if next_elem.name in ["h2", "h3"]:
                        break

                    if next_elem.name == "p":
                        text = next_elem.get_text(strip=True)
                        if text:
                            mechanics.append({
                                "section": current_section,
                                "content": text,
                            })

                    next_elem = next_elem.find_next_sibling()

        return mechanics

    def get_vgc_changes(self, year: int = None) -> List[dict]:
        """
        获取 VGC (Video Game Championships) 规则变更历史
        """
        changes = []

        # 获取 VGC 规则页面
        content = self.get_page_html("Pokemon_Video_Game_Championships")

        if content:
            # 解析表格获取历年规则
            tables = content.find_all("table", class_="wikitable")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows[1:]:  # 跳过表头
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 3:
                        year_text = cells[0].get_text(strip=True)
                        format_text = cells[1].get_text(strip=True)
                        notes_text = cells[2].get_text(strip=True)

                        if year is None or str(year) in year_text:
                            changes.append({
                                "year": year_text,
                                "format": format_text,
                                "notes": notes_text,
                            })

        return changes

    def rate_limit(self):
        """遵守 API 速率限制"""
        time.sleep(1)


# ==================== Serebii.net 爬虫 ====================


class SerebiiScraper:
    """Serebii.net 爬虫 - 宝可梦数据网站"""

    BASE_URL = "https://www.serebii.net"

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
            print(f"请求失败: {url}, {e}")
            return None

    def get_game_index(self) -> List[dict]:
        """获取所有宝可梦游戏索引页面"""
        games = []

        soup = self._fetch("games.shtml")
        if not soup:
            return games

        # 查找游戏列表
        main_content = soup.find("div", class_="content")
        if main_content:
            links = main_content.find_all("a")
            for link in links:
                href = link.get("href", "")
                if "game" in href.lower() or ".shtml" in href:
                    games.append({
                        "name": link.get_text(strip=True),
                        "url": href,
                    })

        return games

    def get_game_details(self, game_path: str) -> dict:
        """获取游戏详细信息"""
        details = {}

        soup = self._fetch(game_path)
        if not soup:
            return details

        # 解析游戏详情
        main_content = soup.find("div", class_="content")
        if main_content:
            details["content"] = main_content.get_text(separator="\n", strip=True)

        return details

    def get_pokemon_movesets(self, pokemon_name: str) -> List[dict]:
        """获取宝可梦的招式配置"""
        movesets = []

        # 转换名称格式
        name_lower = pokemon_name.lower().replace(" ", "").replace("'", "").replace(".", "")

        soup = self._fetch(f"pokemon/{name_lower}.shtml")
        if not soup:
            return movesets

        # 查找 Movesets 部分
        moveset_section = soup.find("a", {"name": re.compile("moveset", re.I)})
        if moveset_section:
            current = moveset_section.find_next_sibling()
            while current:
                if current.name == "a" and current.get("name"):
                    break

                if current.name == "td":
                    text = current.get_text(strip=True)
                    if text and text not in ["TM", "TR", "Egg", "Move Tutor"]:
                        movesets.append({"move": text})

                current = current.find_next_sibling()

        return movesets


# ==================== PokeAPI 爬虫 ====================


class PokeAPIScraper:
    """PokeAPI.co 爬虫 - 官方宝可梦数据 API"""

    BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT,
        })

    def get_generation(self, generation_id: int) -> Optional[dict]:
        """获取世代信息"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/generation/{generation_id}",
                timeout=config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取世代 {generation_id} 失败: {e}")
            return None

    def get_version_group(self, group_id: str) -> Optional[dict]:
        """获取版本组信息"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/version-group/{group_id}",
                timeout=config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取版本组失败: {e}")
            return None

    def get_version_changelog(self, generation: int) -> List[dict]:
        """
        获取版本变更历史
        PokeAPI 本身不存储变更日志，但可以获取版本对应的宝可梦列表
        """
        changelog = []

        # 获取世代信息
        gen_data = self.get_generation(generation)
        if not gen_data:
            return changelog

        # 获取版本组
        version_groups = gen_data.get("version_groups", [])
        for vg in version_groups:
            vg_name = vg["name"]
            vg_data = self.get_version_group(vg_name)
            if vg_data:
                versions = vg_data.get("versions", [])
                for version in versions:
                    changelog.append({
                        "generation": generation,
                        "version_group": vg_name,
                        "version": version["name"],
                        "version_url": version["url"],
                    })

        return changelog

    def get_pokemon_by_version(self, pokemon_id: int, version_group: str) -> Optional[dict]:
        """获取特定版本中宝可梦的详细信息"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/pokemon-species/{pokemon_id}",
                timeout=config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            # 筛选该版本的变种
            varieties = data.get("varieties", [])
            available_in = [
                v["version"]["name"]
                for v in varieties
                if version_group in v["version"]["url"]
            ]

            return {
                "id": data["id"],
                "name": data["name"],
                "available_versions": available_in,
            }
        except requests.RequestException as e:
            print(f"获取宝可梦 {pokemon_id} 失败: {e}")
            return None

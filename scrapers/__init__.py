"""
爬虫模块 - 从可靠数据源获取真实的游戏更新和版本信息

数据源:
- Steam News API: 游戏官方更新公告
- Bulbapedia/Serebii: Wiki 百科资料
- PokeAPI: 宝可梦数据 API
- Smogon/Pikalytics: 竞技数据和 Meta 分析
"""

from .steam_scraper import (
    SteamScraper,
    PokemonSteamScraper,
    TemtemSteamScraper,
    PalworldSteamScraper,
    CassetteBeastsScraper,
)
from .bulbapedia import BulbapediaScraper, SerebiiScraper, PokeAPIScraper
from .smogon import SmogonScraper, SmogonStatsScraper, PikalyticsScraper, DevBlogScraper
from .patch_notes import PatchNotesScraper
from .pokemon_wiki import PokemonWikiScraper

__all__ = [
    "SteamScraper",
    "PokemonSteamScraper",
    "TemtemSteamScraper",
    "PalworldSteamScraper",
    "CassetteBeastsScraper",
    "BulbapediaScraper",
    "SerebiiScraper",
    "PokeAPIScraper",
    "SmogonScraper",
    "SmogonStatsScraper",
    "PikalyticsScraper",
    "DevBlogScraper",
    "PatchNotesScraper",
    "PokemonWikiScraper",
]

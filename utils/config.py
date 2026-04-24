"""
配置管理模块
管理 API Key 和全局配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"警告: {env_path} 不存在，请复制 .env.example 为 .env 并配置 API Key")


class Config:
    """全局配置类"""

    # OpenRouter 配置（固定使用）
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://us.novaiapi.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # LLM API Key（支持从环境变量读取）
    LLM_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # 默认模型
    LLM_DEFAULT_MODELS: list = [
        "anthropic/claude-3.5-sonnet",
    ]

    # 数据库配置
    # 部署时可通过 DATA_DIR 环境变量指定路径
    _base_dir = Path(os.getenv("DATA_DIR", str(Path(__file__).parent.parent / "data")))
    DATA_DIR: Path = _base_dir
    CHROMA_PERSIST_DIR: Path = _base_dir / "chroma_db"
    SQLITE_DB_PATH: Path = _base_dir / "game_design.db"

    # 确保数据目录存在
    DATA_DIR.mkdir(exist_ok=True)

    # 请求配置
    REQUEST_TIMEOUT: int = 30
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # 目标游戏列表（键: 英文标识符, 值: 显示名称）
    # 宝可梦Like游戏
    POKEMON_LIKE_GAMES: dict = {
        "Pokemon": "宝可梦 (Pokemon)",
        "Temtem": "Temtem",
        "Cassette Beasts": "磁带妖怪 (Cassette Beasts)",
        "Palworld": "幻兽帕鲁 (Palworld)",
    }

    # 梦幻西游Like游戏
    MHXY_LIKE_GAMES: dict = {
        "梦幻西游": "梦幻西游",
        "神武": "神武",
        "大话西游": "大话西游",
    }

    # 合并所有支持的游戏
    SUPPORTED_GAMES: dict = {**POKEMON_LIKE_GAMES, **MHXY_LIKE_GAMES}

    # 宝可梦各世代信息
    POKEMON_GENERATIONS: dict = {
        1: {"name": "第一世代", "games": ["红/绿/蓝/黄"], "years": "1996-1999", "region": "关都", "pvp_intro": " Stadium 提供首个官方双打对战平台"},
        2: {"name": "第二世代", "games": ["金/银/水晶"], "years": "1999-2001", "region": "城都", "pvp_intro": "水晶版开放电话对战功能"},
        3: {"name": "第三世代", "games": ["红宝石/蓝宝石/绿宝石"], "years": "2002-2006", "region": "丰缘", "pvp_intro": "RS为VGC双打确立了标准规则"},
        4: {"name": "第四世代", "games": ["钻石/珍珠/白金"], "years": "2006-2010", "region": "神奥", "pvp_intro": "Wi-Fi对战正式上线，开启线上竞技时代"},
        5: {"name": "第五世代", "games": ["黑/白/黑2/白2"], "years": "2011-2016", "region": "合众", "pvp_intro": "Seasonal Tournament将VGC带入赛季制时代"},
        6: {"name": "第六世代", "games": ["X/Y/欧米伽红宝石/阿尔法蓝宝石"], "years": "2013-2016", "region": "卡洛斯", "pvp_intro": "Mega进化成为首个跨世代双打强化机制"},
        7: {"name": "第七世代", "games": ["太阳/月亮/究极之日/究极之月"], "years": "2016-2019", "region": "阿罗拉", "pvp_intro": "首次实现跨平台跨世代宝可梦传递"},
        8: {"name": "第八世代", "games": ["剑/盾", "盾/剑"], "years": "2019-2022", "region": "伽勒尔", "pvp_intro": "极巨化成为VGC核心机制"},
        9: {"name": "第九世代", "games": ["朱/紫"], "years": "2022-2024", "region": "帕底亚", "pvp_intro": "太晶化替代极巨化，全宠可强化"},
    }

    # 梦幻西游各时期信息
    MHXY_PERIODS: dict = {
        "起步期": {"name": "起步期", "years": "2001-2002", "description": "游戏公测，建立核心玩法框架"},
        "资料片迭代期": {"name": "资料片迭代期", "years": "2003-2005", "description": "通过资料片逐步完善游戏内容"},
        "资料片爆发期": {"name": "资料片爆发期", "years": "2006-2010", "description": "大量资料片涌现，系统不断完善"},
        "成熟稳定期": {"name": "成熟稳定期", "years": "2011-2015", "description": "游戏进入成熟期，更新趋于稳定"},
        "持续运营期": {"name": "持续运营期", "years": "2016-2020", "description": "通过定期更新维持游戏活力"},
        "现代化更新期": {"name": "现代化更新期", "years": "2021-2024", "description": "对老系统进行现代化改造"},
        "持续演进期": {"name": "持续演进期", "years": "2025-未来", "description": "游戏持续演进，探索新方向"},
    }

    # Reddit API 配置（用于社区反应采集）
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")


config = Config()

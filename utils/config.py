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
    SUPPORTED_GAMES: dict = {
        "Pokemon": "宝可梦 (Pokemon)",
        "Temtem": "Temtem",
        "Cassette Beasts": "磁带妖怪 (Cassette Beasts)",
        "Palworld": "幻兽帕鲁 (Palworld)",
    }

    # 宝可梦各世代信息
    POKEMON_GENERATIONS: dict = {
        8: {"name": "第八世代", "games": ["剑/盾", "盾/剑"], "years": "2019-2022"},
        9: {"name": "第九世代", "games": ["朱/紫"], "years": "2022-2024"},
    }

    # Reddit API 配置（用于社区反应采集）
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")


config = Config()

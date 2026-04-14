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

    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

    # OpenRouter / OpenAI Compatible 配置
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # LLM API Key（支持从环境变量或 .env 文件读取）
    @property
    def LLM_API_KEY(cls) -> str:
        """优先从环境变量读取，其次从 .env 文件读取"""
        key = os.getenv("OPENAI_API_KEY", "")
        if not key or key == "sk-your-api-key-here":
            # 尝试读取 .llm_settings.json
            settings_file = Path(__file__).parent.parent / ".llm_settings.json"
            if settings_file.exists():
                try:
                    import json
                    with open(settings_file, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                        return settings.get("api_key", "")
                except:
                    pass
        return key

    # LLM Provider 显示名称映射
    LLM_PROVIDER_OPTIONS: list = [
        {"value": "openai", "label": "OpenAI"},
        {"value": "anthropic", "label": "Anthropic"},
        {"value": "openrouter", "label": "OpenRouter"},
    ]

    # 各 Provider 的默认模型
    LLM_DEFAULT_MODELS: dict = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-sonnet-4-20250514",
        "openrouter": "anthropic/claude-3.5-sonnet",
    }

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

    # 目标游戏列表
    SUPPORTED_GAMES: list = [
        "Pokemon",       # 宝可梦正作
        "Temtem",        #  Temtem
        "Cassette Beasts",  # 磁带妖怪
        "Palworld",      # 幻兽帕鲁
    ]

    # 宝可梦各世代信息
    POKEMON_GENERATIONS: dict = {
        8: {"name": "第八世代", "games": ["剑/盾", "盾/剑"], "years": "2019-2022"},
        9: {"name": "第九世代", "games": ["朱/紫"], "years": "2022-2024"},
    }


config = Config()

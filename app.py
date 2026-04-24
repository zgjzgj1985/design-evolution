"""
梦幻西游Like回合制MMO游戏设计演进研究工具
主应用入口 - Streamlit Web UI

使用方法:
1. 安装依赖: pip install -r requirements.txt
2. 配置环境变量: 在项目根目录创建 .env 文件，设置 OPENAI_API_KEY
3. 运行应用: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from pathlib import Path
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import config
from scrapers.steam_scraper import (
    SteamScraper,
    PokemonSteamScraper,
    TemtemSteamScraper,
    PalworldSteamScraper,
    CassetteBeastsScraper,
)
from scrapers.pokemon_wiki import PokemonWikiScraper
from scrapers.bulbapedia import BulbapediaScraper, PokeAPIScraper
from scrapers.smogon import SmogonScraper, PikalyticsScraper
from scrapers.mhxy_data import MHXYDataProvider
from analyzer.intent_extractor import IntentExtractor
from analyzer.report_generator import EvolutionReportGenerator
from db.sqlite_store import SQLiteStore, db as global_db
from db.vector_store import VectorStore
from data_manager import data_manager

# ──────────────────────────────────────────────────────────────────────────────
# 时间轴数据加载（从 report_data.json 读取，与 docs/index.html 共用同一数据源）
# ──────────────────────────────────────────────────────────────────────────────
_REPORT_DATA_PATH = Path(__file__).parent / "docs" / "report_data.json"


def _get_report_summary(game: str) -> str:
    """获取当前游戏的报告摘要（动态显示设计原则和检查清单数量）"""
    principles_count = data_manager.get_principles_count(game)
    checklist_count = data_manager.get_checklist_count(game)
    return f"{principles_count}条设计原则 / {checklist_count}条检查清单 / 历代时间轴"


@st.cache_data(ttl=3600)
def _load_timeline_data() -> dict:
    """加载 report_data.json 中的时间轴数据（缓存1小时）"""
    if not _REPORT_DATA_PATH.exists():
        return {}
    try:
        with open(_REPORT_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("timelines", {})
    except Exception:
        return {}

# ==================== LLM 配置持久化 ====================
SETTINGS_FILE = Path(__file__).parent / ".llm_settings.json"


def load_llm_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_llm_settings(provider, model, base_url, api_key):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"provider": provider, "model": model, "base_url": base_url, "api_key": api_key}, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="游戏设计演进研究工具",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义样式
st.markdown("""
<style>
    /* 侧边栏按钮统一样式 */
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #334155 0%, #1e3a5f 100%) !important;
        border-color: #3b82f6 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(59,130,246,0.25) !important;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .tag-pvp       { background-color: #B87878; color: white; padding: 2px 8px; border-radius: 4px; }
    .tag-pve       { background-color: #7888B8; color: white; padding: 2px 8px; border-radius: 4px; }
    .tag-mechanic  { background-color: #B8A078; color: white; padding: 2px 8px; border-radius: 4px; }
    .tag-balance   { background-color: #78A098; color: white; padding: 2px 8px; border-radius: 4px; }
    .tab4-step-active {
        background: #1f77b4;
        color: white;
        padding: 6px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    .tab4-step-done {
        background: #27ae60;
        color: white;
        padding: 6px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    .tab4-step-waiting {
        background: #e0e0e0;
        color: #888;
        padding: 6px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    .tab4-topic-card {
        border: 1.5px solid #e0e0e0;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 10px;
        cursor: pointer;
        background: white;
    }
    .tab4-topic-card:hover {
        border-color: #1f77b4;
        background: #f0f8ff;
    }
    .tab4-topic-card.selected {
        border-color: #1f77b4;
        background: #e8f4fd;
        box-shadow: 0 0 0 2px #1f77b4;
    }
    .tab4-topic-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: #222;
        margin-bottom: 4px;
    }
    .tab4-topic-meta {
        font-size: 0.82rem;
        color: #888;
    }
    .tab4-topic-count {
        display: inline-block;
        background: #e8f4fd;
        color: #1f77b4;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-left: 8px;
    }
    .tab4-report-section {
        background: #f9f9f9;
        border-radius: 8px;
        padding: 20px 24px;
        margin-top: 16px;
    }
    .tab4-report-section h4 {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 6px;
        margin-bottom: 12px;
        font-size: 1rem;
    }
    .tab4-report-field {
        margin-bottom: 14px;
    }
    .tab4-report-field strong {
        color: #444;
        font-size: 0.88rem;
        display: block;
        margin-bottom: 4px;
    }
    .tab4-report-field p, .tab4-report-field li {
        font-size: 0.92rem;
        color: #333;
        line-height: 1.6;
    }
    /* 各类型胶囊颜色（低饱和度，与 color_map 一致） */
    .pill-pvp   { background: #B87878; color: white; }
    .pill-pve   { background: #7888B8; color: white; }
    .pill-强化  { background: #B8A078; color: white; }
    .pill-奠基  { background: #88A088; color: white; }
    .pill-社交  { background: #8878B8; color: white; }
    .pill-meta  { background: #78A098; color: white; }
    .pill-other { background: #888898; color: white; }
    .data-source-badge {
        background-color: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        color: #1565c0;
    }
    .patch-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 500;
        margin-right: 4px;
    }
    .patch-tag-mechanic { background-color: #B8A078; color: white; }
    .patch-tag-other    { background-color: #888898; color: white; }
    .patch-tag-pvp      { background-color: #B87878; color: white; }
    .patch-tag-pve      { background-color: #7888B8; color: white; }
    .patch-tag-balance  { background-color: #78A098; color: white; }
    .patch-full-content {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 6px;
        font-size: 0.88rem;
        line-height: 1.7;
        color: #333;
    }
    .insight-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #f0f7ff 100%);
        border-left: 4px solid #1f77b4;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
        font-size: 0.9rem;
        color: #333;
        line-height: 1.6;
    }
    [data-testid="stTabList"] {
        gap: 4px;
        background-color: #f0f4f8;
        padding: 6px 8px;
        border-radius: 8px;
        border: none;
    }
    [data-testid="stTab"] {
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 6px 20px;
        font-weight: 500;
        font-size: 0.88rem;
        color: #555;
        background-color: transparent;
        transition: all 0.2s ease;
    }
    [data-testid="stTab"]:hover {
        background-color: rgba(31, 119, 180, 0.08);
        border-color: rgba(31, 119, 180, 0.3);
        color: #1f77b4;
    }
    [data-testid="stTab"][aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
        border-color: #1f77b4;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(31, 119, 180, 0.35);
    }
</style>
""", unsafe_allow_html=True)


# ==================== 工具函数 ====================

@st.cache_resource
def get_steam_scraper(game: str):
    """获取 Steam 爬虫实例（缓存）"""
    scrapers = {
        "Pokemon": PokemonSteamScraper,
        "Temtem": TemtemSteamScraper,
        "Palworld": PalworldSteamScraper,
        "Cassette Beasts": CassetteBeastsScraper,
    }
    scraper_class = scrapers.get(game, SteamScraper)
    return scraper_class()


@st.cache_resource
def get_wiki_scraper():
    """获取 Wiki 爬虫实例（缓存）"""
    return PokemonWikiScraper()


@st.cache_resource
def get_api_scraper():
    """获取 API 爬虫实例（缓存）"""
    return PokeAPIScraper()


@st.cache_resource
def get_smogon_scraper():
    """获取 Smogon 爬虫实例（缓存）"""
    return SmogonScraper()


@st.cache_resource
def get_pikalytics_scraper():
    """获取 Pikalytics 爬虫实例（缓存）"""
    return PikalyticsScraper()


def get_analyzer():
    """获取分析器实例（每次调用都重新创建以获取最新配置）"""
    return IntentExtractor(
        provider="openrouter",
        model=st.session_state.get("llm_model", config.LLM_MODEL),
        base_url=st.session_state.get("llm_base_url", ""),
        api_key=st.session_state.get("llm_api_key", ""),
    )


def fetch_game_data(game: str, generation: int = None, refresh: bool = False) -> tuple:
    """
    从真实数据源获取游戏数据

    Returns:
        (patches, stats) 元组
    """
    patches = []
    fetch_stats = {"source": "live", "count": 0, "errors": []}

    # 非Steam游戏列表（Nintendo平台）
    non_steam_games = {"Pokemon"}

    # 梦幻西游Like游戏列表（使用内置数据）
    mhxy_like_games = {"梦幻西游", "神武", "大话西游"}

    # 从各数据源获取数据
    try:
        if game in mhxy_like_games:
            # 梦幻西游Like游戏：使用内置数据
            mhxy_patches = MHXYDataProvider.get_all_patches(game)
            patches.extend(mhxy_patches)
            fetch_stats["source"] = "mhxy_builtin"
            fetch_stats["total"] = len(mhxy_patches)
        elif game not in non_steam_games:
            # Steam 游戏：从 Steam 获取更新日志
            steam_scraper = get_steam_scraper(game)
            with st.spinner(f"正在从 Steam API 获取 {game} 更新日志..."):
                steam_patches = steam_scraper.get_patch_notes(count=50)
            multiplayer_patches = steam_scraper.get_multiplayer_patches(count=50)
            patches.extend(multiplayer_patches)
            fetch_stats["steam_count"] = len(steam_patches)
            fetch_stats["multiplayer_count"] = len(multiplayer_patches)
        else:
            # Pokemon 等非Steam游戏：从 Wiki 获取版本数据
            wiki_scraper = get_wiki_scraper()
            patch_notes = wiki_scraper.get_patch_notes_sample(generation or 9)
            detailed_notes = wiki_scraper.get_detailed_patch_notes()
            for patch in patch_notes:
                for change in patch.get("changes", []):
                    version_key = patch["version"]
                    detail = detailed_notes.get(patch["game"], {}).get(version_key, {})

                    patches.append({
                        "title": f"{patch['game']} v{patch['version']} 更新",
                        "date": patch["date"],
                        "content": change.get("content", ""),
                        "detail": change.get("detail", ""),  # 详细改动描述
                        "intent": change.get("intent", ""),
                        "categories": [change.get("category", "其他")],
                        "game": game,
                        "version": patch["version"],
                        "source_url": change.get("source_url") or patch.get("source_url", ""),  # 优先用单条change的URL
                        "full_context": detail.get("full_context", ""),
                        "balance_changes": detail.get("balance_changes", {}),
                        "impact": detail.get("impact", ""),
                        "vgc_relevance": detail.get("vgc_relevance", ""),
                        "official_notes": detail.get("official_notes", patch.get("official_notes", "")),
                        # official_notes 优先从 detailed_db 取，若缺失则降级从 patches_db 取
                    })
            fetch_stats["source"] = "wiki"

    except Exception as e:
        fetch_stats["errors"].append(f"数据获取: {str(e)}")

    fetch_stats["total"] = len(patches)
    fetch_stats["count"] = len(patches)

    # 如果真实数据获取失败，使用空列表
    if not patches:
        fetch_stats["source"] = "no_data"
        patches = []

    return patches, fetch_stats


# ==================== 侧边栏 ====================
with st.sidebar:
    st.header("配置")

    # 预计算各游戏数据量（用于选择器标签）
    import json as _json
    from pathlib import Path as _Path

    def _count_game_patches(game_name: str) -> int:
        """统计游戏在 data/ 目录中的补丁条数"""
        if game_name == "Pokemon":
            # Pokemon 数据来自内置 Wiki，不在 data/ 目录
            return 0
        if game_name in {"梦幻西游", "神武", "大话西游"}:
            # 梦幻西游Like游戏：使用内置数据
            return len(MHXYDataProvider.get_all_patches(game_name))
        _folder = {"Temtem": "temtem", "Palworld": "palworld", "Cassette Beasts": "cassette_beasts"}.get(game_name)
        if not _folder:
            return 0
        _df = _Path(__file__).parent / "data" / _folder / "patches.json"
        if not _df.exists():
            return 0
        try:
            with open(_df, "r", encoding="utf-8") as _f:
                _d = _json.load(_f)
            return len(_d.get("patches", []))
        except Exception:
            return 0

    _game_counts = {g: _count_game_patches(g) for g in config.SUPPORTED_GAMES}

    # 游戏选择（显示数据量提示）
    def _game_label(name: str) -> str:
        base = config.SUPPORTED_GAMES[name]
        count = _game_counts.get(name, 0)
        if count > 0:
            return f"{base}  ({count}条)"
        return base

    selected_game = st.selectbox(
        "选择游戏",
        options=list(config.SUPPORTED_GAMES.keys()),
        format_func=_game_label,
        index=0,
    )

    def _get_game_data_count(game_name: str) -> tuple:
        """返回 (总记录数, 多人相关数, 最新日期)"""
        if game_name == "Pokemon":
            # Pokemon 数据来自内置，直接用当前已加载的 patches
            return None, None, None
        if game_name in {"梦幻西游", "神武", "大话西游"}:
            # 梦幻西游Like游戏：使用内置数据
            patches = MHXYDataProvider.get_all_patches(game_name)
            _mp_keywords = ["PvP", "门派调整", "平衡性调整", "赛事规则", "比武", "华山", "武神坛", "封印", "输出", "辅助"]
            _mp_count = sum(1 for p in patches if any(kw in p.get("categories", []) for kw in _mp_keywords))
            _dates = [p.get("date", "") for p in patches if p.get("date")]
            _latest = sorted(_dates)[-1] if _dates else None
            return len(patches), _mp_count, _latest
        _folder = {"Temtem": "temtem", "Palworld": "palworld"}.get(game_name)
        if not _folder:
            return 0, 0, None
        _df = _Path(__file__).parent / "data" / _folder / "patches.json"
        if not _df.exists():
            return 0, 0, None
        try:
            with open(_df, "r", encoding="utf-8") as _f:
                _d = _json.load(_f)
            _patches = _d.get("patches", [])
            _mp_keywords = ["battle", "pvp", "pve", "multiplayer", "raid", "coop", "versus", "match", "team", "balance", "nerf", "buff", "fix", "patch", "update"]
            _mp_count = 0
            for _p in _patches:
                _raw = (_p.get("title", "") + _p.get("contents", "")).lower()
                if any(_k in _raw for _k in _mp_keywords):
                    _mp_count += 1
            _dates = [p.get("date", "") for p in _patches if p.get("date")]
            _latest = sorted(_dates)[-1] if _dates else None
            return len(_patches), _mp_count, _latest
        except Exception:
            return 0, 0, None

    # 世代选择（仅 Pokemon）
    generation = 9
    if selected_game == "Pokemon":
        generation = st.select_slider(
            "选择世代",
            options=[1, 2, 3, 4, 5, 6, 7, 8, 9],
            value=st.session_state.get("_generation_slider", 1),
            format_func=lambda x: f"第{x}世代 ({config.POKEMON_GENERATIONS[x]['years']})",
            key="_generation_slider",
        )

    # 数据刷新（仅清除 session 缓存，不重新抓取网络）
    st.subheader("数据源")
    st.info("更新日志已预采集到本地 data/ 目录，应用启动时直接读取，不访问网络。如需采集最新数据，请运行 `python fetch_all_data.py` 后重启应用。")
    if st.button("清除缓存", width="stretch"):
        st.cache_resource.clear()
        # 保留 LLM 配置和世代选择状态
        keys_to_preserve = {"llm_provider", "llm_model", "llm_base_url", "llm_api_key", "_generation_slider"}
        # 清除所有 session_state（包括数据和分析结果）
        for k in list(st.session_state.keys()):
            if k not in keys_to_preserve:
                del st.session_state[k]
        st.rerun()

    # 数据来源权威性与新鲜度展示
    st.subheader("数据概览")

    _GAME_SOURCE_INFO = {
        # 宝可梦Like游戏
        "Pokemon": {"source": "Serebii.net + 内置数据", "type": "结构化内置"},
        "Temtem": {"source": "Steam News API（预采集）", "type": "JSON 静态文件"},
        "Palworld": {"source": "Steam News API（预采集）", "type": "JSON 静态文件"},
        "Cassette Beasts": {"source": "Steam（无公开公告）", "type": "数据暂缺"},
        # 梦幻西游Like游戏
        "梦幻西游": {"source": "内置历史数据 + 社区整理", "type": "结构化内置"},
        "神武": {"source": "内置历史数据 + 社区整理", "type": "结构化内置"},
        "大话西游": {"source": "内置历史数据 + 社区整理", "type": "结构化内置"},
    }

    source_info = _GAME_SOURCE_INFO.get(selected_game, {"source": "未知", "type": "未知"})
    st.caption(f"**数据来源**: {source_info['source']}")
    st.caption(f"**存储类型**: {source_info['type']}")

    if source_info["type"] == "数据暂缺":
        st.warning("该游戏暂无公开更新日志数据")
    elif source_info["type"] == "JSON 静态文件":
        _total_count, _mp_count, _latest_date = _get_game_data_count(selected_game)
        if _total_count is not None and _total_count > 0:
            st.caption(f"**本地记录数**: {_total_count} 条")
            if _mp_count is not None and _mp_count > 0:
                _ratio = _mp_count / _total_count * 100
                st.caption(f"**多人相关**: {_mp_count} 条（{_ratio:.0f}%）")
            if _latest_date:
                st.caption(f"**最新记录**: {_latest_date}")

    st.divider()

    # 交互式报告入口
    st.subheader("交互式报告")
    report_summary = _get_report_summary(selected_game)
    st.markdown(
        f"「设计演化档案」完整报告 — {report_summary}",
        unsafe_allow_html=True,
    )
    
    if st.button("打开交互式报告", use_container_width=True):
        import webbrowser, pathlib
        _path = pathlib.Path(__file__).parent / "docs" / "index.html"
        webbrowser.open(f"file:///{_path.as_posix()}")
        st.toast("已在浏览器中打开演进报告")

    # 免责声明
    st.warning(
        "AI 分析结论可能存在偏差，"
        "历史案例引用建议通过权威来源交叉验证。"
    )

    # LLM 连接状态指示（放在设置 expander 外部，每次渲染都可见）
    _llm_init_ok = False
    try:
        _test_ext = IntentExtractor(
            provider="openrouter",
            model=st.session_state.get("llm_model", ""),
            base_url=st.session_state.get("llm_base_url", ""),
            api_key=st.session_state.get("llm_api_key", ""),
        )
        _llm_init_ok = _test_ext._get_llm() is not None
    except Exception:
        pass
    _has_key = bool(st.session_state.get("llm_api_key", ""))
    if _has_key and _llm_init_ok:
        st.caption("**AI 分析**: 已就绪")
    elif _has_key:
        st.caption("**AI 分析**: 连接异常")
    else:
        st.caption("**AI 分析**: 未配置")

    # LLM 配置 - 折叠式按钮（默认折叠，配置已迁移至 Zeabur 环境变量）
    with st.expander("LLM 设置", expanded=False):
        # 优先级：环境变量（Zeabur） > 本地配置文件（本地调试用）
        env_model = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")
        env_base_url = os.getenv("OPENROUTER_BASE_URL", "https://us.novaiapi.com/v1")
        env_api_key = os.getenv("OPENAI_API_KEY", "")

        saved = load_llm_settings()
        defaults = {
            "model": env_model,
            "base_url": env_base_url,
            "api_key": env_api_key,
        }
        if saved:
            for key in defaults:
                val = saved.get(key, "")
                if val:
                    defaults[key] = val

        # 同步最新配置
        st.session_state["llm_provider"] = "openrouter"
        st.session_state["llm_model"] = defaults.get("model")
        st.session_state["llm_base_url"] = defaults.get("base_url")
        st.session_state["llm_api_key"] = defaults.get("api_key")

        has_api_key = bool(st.session_state.get("llm_api_key", ""))
        if not has_api_key:
            st.warning("未配置 API Key，AI 功能无法使用")

        # 诊断信息
        with st.expander("诊断信息", expanded=True):
            st.markdown("**当前 LLM 配置：**")
            st.write(f"- Provider: `{st.session_state.get('llm_provider', '未设置')}`")
            st.write(f"- Model: `{st.session_state.get('llm_model', '未设置')}`")
            st.write(f"- Base URL: `{st.session_state.get('llm_base_url', '未设置')}`")
            api_key_display = st.session_state.get("llm_api_key", "")
            if api_key_display:
                st.write(f"- API Key: `{api_key_display[:8]}...`")
            else:
                st.write("- API Key: **未设置**")

            extractor = IntentExtractor(
                provider=st.session_state.get("llm_provider"),
                model=st.session_state.get("llm_model"),
                base_url=st.session_state.get("llm_base_url") or "",
                api_key=st.session_state.get("llm_api_key") or "",
            )
            llm = extractor._get_llm()
            if llm is None:
                st.error("LLM 初始化失败，请检查上方配置")
            else:
                st.success(f"LLM 初始化成功！模型: {llm.model_name if hasattr(llm, 'model_name') else 'unknown'}")

        # 本地调试用表单（Zeabur 上配置文件不持久化，保存无效）
        with st.form("llm_config_form"):
            st.markdown("**连接设置（本地调试用）**")

            st.text_input(
                "Model",
                value=st.session_state["llm_model"],
                placeholder="输入模型名称",
                key="llm_model_input",
            )

            st.text_input(
                "Base URL",
                value=st.session_state["llm_base_url"] or "",
                placeholder="留空使用官方地址",
                key="llm_base_url_input",
            )

            st.text_input(
                "API Key（云端请在 Zeabur 环境变量中配置）",
                type="password",
                value=st.session_state["llm_api_key"],
                placeholder="sk-...",
                key="llm_api_key_input",
            )

            submitted = st.form_submit_button("保存设置（本地有效）", type="secondary", use_container_width=True)

            if submitted:
                st.session_state["llm_model"] = st.session_state["llm_model_input"]
                st.session_state["llm_base_url"] = st.session_state["llm_base_url_input"]
                st.session_state["llm_api_key"] = st.session_state["llm_api_key_input"]
                ok = save_llm_settings("openrouter", st.session_state["llm_model"], st.session_state["llm_base_url"], st.session_state["llm_api_key"])
                if ok:
                    st.success("配置已保存")
                else:
                    st.error("保存失败")

        # 测试连接按钮（放在表单外面，每次渲染都可点击）
        st.markdown("---")
        if st.button("测试连接", key="btn_test_connection", use_container_width=True):
            with st.spinner("正在测试连接..."):
                test_extractor = IntentExtractor(
                    provider="openrouter",
                    model=st.session_state.get("llm_model", config.LLM_MODEL),
                    base_url=st.session_state.get("llm_base_url", ""),
                    api_key=st.session_state.get("llm_api_key", ""),
                )
                test_result = test_extractor.test_connection()

                if test_result["success"]:
                    st.success(f"连接成功！延迟: {test_result['latency_ms']}ms | 模型: {test_result['model']}")
                else:
                    st.error(f"连接失败: {test_result['message']}")

    # 数据统计
    st.subheader("数据统计")
    try:
        db = SQLiteStore()
        stats = db.get_stats(game=selected_game)
        total_patches = stats.get("total_patches", 0)
        total_analyses = stats.get("total_analyses", 0)

        if total_patches == 0 and total_analyses == 0:
            st.info("暂无本地数据。进入「设计意图分析」或「演进报告」标签页调用 AI 分析后，数据将自动存入本地数据库。")
        else:
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("已存储更新", total_patches)
            with col_stat2:
                st.metric("已分析条目", total_analyses)
    except Exception as e:
        st.caption(f"数据库未初始化: {e}")


# ==================== 主界面 ====================
st.markdown('<h1 class="main-header">游戏设计演进研究工具</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">多人对战游戏设计演进研究 | 本地静态数据</p>', unsafe_allow_html=True)

# 获取数据 - 使用稳定的缓存机制
# 每个 (game, generation) 组合独立缓存，切换时代只驱逐旧世代缓存

def _get_gen_cache_key(game: str, gen: int) -> str:
    return f"_patches_{game}_{gen}"

def _evict_old_gen_caches(game: str, current_gen: int):
    """驱逐同一游戏下旧世代的缓存，只保留当前世代"""
    prefix = f"_patches_{game}_"
    for k in list(st.session_state.keys()):
        if k.startswith(prefix):
            # 解析世代号
            try:
                cached_gen = int(k.replace(prefix, ""))
                if cached_gen != current_gen:
                    del st.session_state[k]
            except ValueError:
                pass

cache_data_key = _get_gen_cache_key(selected_game, generation)

# 检测是否切换了游戏或世代
current_game_key = "_current_game"
current_gen_key = "_current_gen"
prev_game = st.session_state.get(current_game_key)
prev_gen = st.session_state.get(current_gen_key)

# 切换游戏/世代时：清除旧世代缓存，保留其他数据
if prev_game is not None and (prev_game != selected_game or prev_gen != generation):
    # 驱逐同一游戏下旧世代的缓存
    _evict_old_gen_caches(selected_game, generation)
    # 更新当前游戏/世代记录
    st.session_state[current_game_key] = selected_game
    st.session_state[current_gen_key] = generation
    # 强制重渲染，清除旧 widget 占位空白
    st.rerun(scope="app")

if cache_data_key in st.session_state:
    # 使用缓存
    patches, fetch_stats = st.session_state[cache_data_key]
else:
    # 首次加载或缓存被驱逐，加载数据
    with st.spinner("正在加载数据..."):
        patches, fetch_stats = fetch_game_data(selected_game, generation)
    st.session_state[cache_data_key] = (patches, fetch_stats)
    # 更新当前游戏/世代记录
    st.session_state[current_game_key] = selected_game
    st.session_state[current_gen_key] = generation

# 统计信息
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("游戏", selected_game)
with col2:
    st.metric("更新日志", len(patches))
with col3:
    st.metric("世代", f"第{generation}世代" if selected_game == "Pokemon" else "N/A")
with col4:
    source_label = "Wiki 结构化数据" if fetch_stats["source"] == "wiki" else "本地 data/ 目录"
    st.caption(f"数据来源：{source_label}")

# 显示错误信息（如果有）
if fetch_stats.get("errors"):
    with st.expander("数据获取警告", expanded=False):
        for error in fetch_stats["errors"]:
            st.warning(error)

st.divider()

# Tab 界面
tab1, tab2, tab3, tab4 = st.tabs([
    "版本编年史",
    "机制时间轴",
    "设计意图分析",
    "演进报告",
])


# ==================== Tab 1: 版本编年史 辅助函数 ====================
def get_content_hash(patch: dict) -> str:
    import hashlib
    raw = f"{patch.get('content', '')}:{patch.get('title', '')}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _show_report_error(error_msg: str):
    """渲染演进报告生成失败的友好提示"""
    error_lower = error_msg.lower()
    if "timeout" in error_lower or "timed out" in error_lower:
        st.error(
            "**报告生成超时**\n\n"
            "网络连接不稳定或 AI 响应较慢。建议：\n"
            "1. 点击下方按钮重试\n"
            "2. 切换到其他演进枝尝试\n"
            "3. 稍后网络较好时再试"
        )
    elif "rate limit" in error_lower or "429" in error_lower:
        st.error(
            "**请求频率超限**\n\n"
            "AI API 调用频率受限。请等待 10 秒后重试。"
        )
    elif "invalid" in error_lower and "api" in error_lower:
        st.error(
            "**API 配置异常**\n\n"
            "API Key 可能无效或已过期。请在侧边栏重新配置。"
        )
    elif "llm" in error_lower and ("不可用" in error_msg or "未配置" in error_msg):
        st.error(
            "**AI 未连接**\n\n"
            "请先在侧边栏「LLM 设置」中配置并测试 API 连接。"
        )
    elif "none" in error_lower or "null" in error_lower:
        st.error(
            "**生成中断**\n\n"
            "报告生成过程中断，建议重试。"
        )
    else:
        st.error(
            f"**报告生成失败**\n\n"
            f"原因：{error_msg}\n\n"
            f"建议重试，或切换到其他演进枝。如问题持续，请在社区反馈。"
        )


def _render_analysis_result(analysis, pvp_related, source, patch_key, extractor):
    """渲染分析结果卡片"""
    if not any([analysis.get(k) for k in [
        "exact_change", "competitive_impact", "design_rationale",
        "research_direction", "intent_summary", "summary"
    ]]):
        return

    ai_border = "#ff6b6b" if pvp_related else "#1f77b4"
    ai_bg = "#fff5f5" if pvp_related else "#f0f7ff"
    pvp_tag = '<span style="background:#ff6b6b;color:white;padding:2px 8px;border-radius:10px;font-size:11px;margin-left:8px">多人对战相关</span>' if pvp_related else ""
    color = "#52c41a" if source == "新分析" else "#888"
    src_tag = f'<span style="background:{color};color:white;padding:1px 6px;border-radius:6px;font-size:10px;margin-left:8px">{source}</span>'

    st.markdown(
        f'<div style="background:linear-gradient(135deg,{ai_bg} 0%,#e8f4fd 100%);'
        f'border-left:4px solid {ai_border};border-radius:8px;padding:14px;margin:12px 0;">'
        f'<div style="font-size:1rem;font-weight:700;margin-bottom:10px">AI 分析结果{pvp_tag}{src_tag}</div>',
        unsafe_allow_html=True
    )

    fields = [
        ("具体改动", analysis.get("exact_change", "")),
        ("竞技影响", analysis.get("competitive_impact") or analysis.get("intent_summary", "")),
        ("设计理由", analysis.get("design_rationale") or analysis.get("problem_solved", "")),
        ("研究方向", analysis.get("research_direction", "")),
    ]
    for label, val in fields:
        if val:
            st.markdown(f"**{label}**: {val}")

    mechanics = analysis.get("mechanic_tags") or analysis.get("mechanics", [])
    if mechanics:
        if not isinstance(mechanics, list):
            mechanics = [mechanics]
        tags_html = " ".join([f'<span class="patch-tag patch-tag-mechanic">{m}</span>' for m in mechanics[:6]])
        st.markdown(f"**涉及机制**: {tags_html}", unsafe_allow_html=True)

    players = analysis.get("player_impact") or analysis.get("affected_players", "")
    if players:
        if isinstance(players, list):
            players = "、".join(players)
        st.markdown(f"**受影响玩家**: {players}")

    # balance_assessment 直观标签映射
    _ASSESSMENT_LABELS = {
        "恰到好处": ("[力度适中]", "#52c41a"),
        "力度不足": ("[调整不足]", "#faad14"),
        "过犹不及": ("[矫枉过正]", "#ff4d4f"),
        "治标不治本": ("[治标不治本]", "#fa8c16"),
    }

    balance = analysis.get("balance_assessment") or analysis.get("design_pattern", "")
    if balance:
        label, color = next(
            ((lbl, col) for key, (lbl, col) in _ASSESSMENT_LABELS.items() if key in balance),
            (f"[{balance}]", "#666"),
        )
        st.markdown(f"**平衡评估**: <span style='background:{color};color:white;padding:2px 10px;border-radius:12px;font-size:12px'>{label}</span>", unsafe_allow_html=True)

    # 数据置信度展示
    confidence = analysis.get("_data_confidence", "")
    if confidence:
        conf_color = {"高": "#52c41a", "中": "#faad14", "低": "#ff4d4f"}.get(confidence, "#666")
        st.markdown(f"**分析置信度**: <span style='color:{conf_color};font-weight:bold'>[{confidence}]</span>", unsafe_allow_html=True)

    # 免责声明
    disclaimer = analysis.get("_disclaimer", "")
    if disclaimer:
        st.caption(f"⚠️ {disclaimer}")

    similar = analysis.get("similar_historical_cases", [])
    if similar and isinstance(similar, list):
        st.warning("以下历史案例由 AI 推断生成，建议通过 Serebii.net 等权威来源交叉验证")
        st.markdown("**历史参照**:")
        for r in similar[:3]:
            desc = r.get("description", r) if isinstance(r, dict) else str(r)
            st.markdown(f"- {desc}")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("重新分析", key=f"btn_reanal_{patch_key}"):
        st.session_state[patch_key] = None
        st.session_state[f"_rerun_{patch_key}"] = True
        st.rerun()


def _render_patch_detail(patch, patch_key, selected_game, generation, pvp_related, llm_ready, extractor, db):
    """渲染单个补丁的详情区域（分析结果/分析按钮）"""
    result = st.session_state.get(patch_key)
    db_cls = db.get_classification(selected_game, get_content_hash(patch))
    has_db_cls = bool(db_cls)

    if st.session_state.get(f"_rerun_{patch_key}"):
        st.session_state[f"_rerun_{patch_key}"] = False
        with st.spinner("AI 分析中（10-30秒）..."):
            try:
                res = extractor.analyze_intent(
                    game=selected_game,
                    version=patch.get("version", ""),
                    date=patch.get("date", ""),
                    content=patch.get("title", "") + "\n\n" + patch.get("content", ""),
                )
                if res:
                    st.session_state[patch_key] = res
                    db.add_classification(
                        game=selected_game,
                        content_hash=get_content_hash(patch),
                        content_preview=patch.get("content", "")[:200] or patch.get("title", "")[:200],
                        patch_date=patch.get("date", ""),
                        patch_title=patch.get("title", ""),
                        classification_type="混合",
                        mechanics=res.get("mechanic_tags", []),
                        balance_impact="中",
                        summary=(res.get("competitive_impact") or res.get("exact_change", ""))[:500],
                        is_multiplayer_related=any(t in res.get("mechanic_tags", []) for t in ["PvP", "PvE", "2v2"]),
                    )
                    st.rerun()
                else:
                    st.warning("分析未返回结果")
            except Exception as e:
                st.error("分析失败: " + str(e))
        return

    if result:
        _render_analysis_result(result, pvp_related, "新分析", patch_key, extractor)
    elif has_db_cls:
        _render_analysis_result(db_cls, pvp_related, "DB缓存", patch_key, extractor)
    else:
        if llm_ready:
            if st.button("深度分析", type="primary", key=f"btn_analyze_{patch_key}"):
                st.session_state[f"_rerun_{patch_key}"] = True
                st.rerun()
        else:
            st.warning("请在侧边栏配置 LLM API Key 以启用 AI 分析")


def _render_patch_card(patch, selected_game, generation, llm_ready, extractor, db, idx=None, page=None):
    """渲染单个补丁卡片（列表项 + 详情展开）"""
    ch = get_content_hash(patch)
    page_str = f"_p{page}" if page is not None else ""
    idx_str = f"_i{idx}" if idx is not None else ""
    patch_key = f"analysis_{selected_game}_{generation}_{ch}{page_str}{idx_str}"

    raw = (patch.get("title", "") + patch.get("content", "")).lower()
    pvp_related = any(k in raw for k in [
        "集火", "保排", "保护", "守住", "看我嘛", "愤怒粉", "双击", "2v2", "双打", "单打",
        "raid", "团体战", "极巨团体", "太晶团体", "多人", "mega", "极巨化", "太晶化",
        "z招式", "z招", "先制", "速度", "顺风", "高速", "优先度", "vgc", "规则", "ban",
        "分级", "赛季", "pvp", "pve", "对战", "削弱", "增强", "nerf",
    ])

    border_color = "#ff6b6b" if pvp_related else "#1f77b4"
    bg_color = "#fff5f5" if pvp_related else "#ffffff"
    badge = "[研究相关]" if pvp_related else "[更新]"

    type_val = ""
    if any(k in raw for k in ["raid", "团体战", "极巨团体", "太晶团体", "多人", "pve", "合作"]):
        type_val = "PvE"
    elif any(k in raw for k in ["vgc", "pvp", "对战", "双打", "单打", "规则", "ban", "赛季", "分级", "削弱", "增强", "极巨化", "太晶化", "mega", "z招"]):
        type_val = "PvP"

    type_html = ""
    if type_val:
        c = "#4ecdc4" if type_val == "PvE" else "#96ceb4"
        type_html = f'<span style="background:{c};color:white;padding:2px 8px;border-radius:8px;font-size:10px;margin-left:6px">{type_val}</span>'

    pvp_html = '<span style="background:#ff6b6b;color:white;padding:2px 8px;border-radius:10px;font-size:11px;margin-left:6px">多人对战相关</span>' if pvp_related else ''

    preview = patch.get("content", "")[:100]
    preview_html = f'<div style="font-size:0.82rem;color:#555;margin-top:6px;line-height:1.5">{preview}{"..." if len(patch.get("content","")) > 100 else ""}</div>' if preview else ""

    st.markdown(
        f'<div style="border-left:4px solid {border_color};background:{bg_color};'
        f'padding:12px 16px;margin-bottom:8px;border-radius:4px;">'
        f'<div style="font-weight:600;margin-bottom:4px;">'
        f'{badge} <b>{patch.get("date","N/A")}</b> — {patch.get("title","N/A")[:60]}{type_html}{pvp_html}'
        f'</div>'
        f'<div style="font-size:0.82rem;color:#666;">'
        f'版本: {patch.get("version","N/A")}　类别: {" / ".join(patch.get("categories",[])[:3])}'
        f'</div>'
        f'{preview_html}'
        f'</div>',
        unsafe_allow_html=True
    )

    with st.expander("查看详情", expanded=False):
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f"**日期**: {patch.get('date','N/A')}")
        with cols[1]:
            st.markdown(f"**版本**: {patch.get('version','N/A')}")
        with cols[2]:
            cats = patch.get("categories", [])[:3]
            if cats:
                cat_tags = " ".join([f'<span class="patch-tag patch-tag-other">{c}</span>' for c in cats])
                st.markdown(f"**类别**: {cat_tags}", unsafe_allow_html=True)

        content = patch.get("content", "")
        if content:
            st.markdown("**更新摘要**:")
            st.markdown(f'<div class="patch-full-content">{content}</div>', unsafe_allow_html=True)

        detail = patch.get("detail", "")
        if detail:
            st.markdown("**详细改动**:")
            st.markdown(f'<div style="background:#fffef0;padding:12px;border-radius:6px;border-left:3px solid #f0ad4e;margin:10px 0;font-size:0.9rem;line-height:1.7">{detail}</div>', unsafe_allow_html=True)

        has_bg = any([patch.get("full_context"), patch.get("impact"), patch.get("vgc_relevance"), patch.get("balance_changes")])
        if has_bg:
            with st.expander("详细背景信息"):
                if patch.get("full_context"):
                    st.markdown("**背景说明**:")
                    st.markdown(f'<div style="background:#f8f9fa;padding:12px;border-radius:6px;margin:6px 0;font-size:0.88rem;line-height:1.7">{patch.get("full_context")}</div>', unsafe_allow_html=True)
                bc = patch.get("balance_changes", {})
                if bc:
                    st.markdown("**数值改动详情**:")
                    for name, changes in bc.items():
                        if isinstance(changes, dict):
                            st.markdown(f"- **{name}**: {', '.join(f'{k}:{v}' for k, v in changes.items())}")
                        else:
                            st.markdown(f"- **{name}**: {changes}")
                if patch.get("impact"):
                    st.markdown("**影响分析**:")
                    st.markdown(f'<div style="background:#e8f4fd;padding:10px;border-radius:6px;margin:6px 0;font-size:0.88rem">{patch.get("impact")}</div>', unsafe_allow_html=True)
                if patch.get("vgc_relevance"):
                    st.markdown("**VGC相关说明**:")
                    st.markdown(f'<div style="background:#f0f8ff;padding:10px;border-radius:6px;margin:6px 0;font-size:0.88rem">{patch.get("vgc_relevance")}</div>', unsafe_allow_html=True)

        if patch.get("official_notes"):
            st.markdown("#### 官方更新日志原文")
            st.markdown(
                f'<div style="background:#f5f5f5;color:#333;'
                f'padding:16px;border-radius:8px;margin:10px 0;max-height:400px;'
                f'overflow-y:auto;font-size:0.85rem;line-height:1.7">'
                f'{patch.get("official_notes","").replace(chr(10),"<br>")}</div>',
                unsafe_allow_html=True
            )

        if patch.get("intent"):
            st.markdown("**设计意图**:")
            st.info(patch.get("intent"))

        st.markdown("---")
        _render_patch_detail(patch, patch_key, selected_game, generation, pvp_related, llm_ready, extractor, db)

        src_url = patch.get("source_url", "")
        if src_url:
            st.markdown(f"[查看官方原文]({src_url})")


# ==================== Tab 1: 版本编年史 ====================
with tab1:
    st.header("版本编年史")

    # 根据游戏和数据来源显示不同描述
    if selected_game == "Pokemon":
        st.markdown("基于 Wiki 结构化整理的版本更新记录")
    elif selected_game == "梦幻西游":
        st.markdown("来自梦幻西游官方论坛的真实门派调整数据，包含具体数值变化")
    else:
        st.markdown("从 Steam News API 预采集的更新日志记录")

    if not patches:
        st.info("已加载结构化版本数据，可通过侧边栏筛选世代查看详细更新记录。" if selected_game == "Pokemon"
                else "未能从数据源获取更新日志，请检查网络或数据配置。")
    else:
        # ── 排序与筛选（必须在渲染前）──────────────
        # 排序切换器
        sort_key = f"sort_{selected_game}_{generation}"
        sort_mode = st.radio(
            "排序方式",
            options=["研究价值", "时间顺序"],
            horizontal=True,
            key=sort_key,
        )

        def _patch_research_priority(patch: dict) -> int:
            """研究价值优先级：数字越小越重要"""
            raw = (patch.get("title", "") + patch.get("content", "")).lower()
            if any(k in raw for k in ["集火", "保排", "vgc", "双打", "单打", "团体战", "raid", "2v2", "2v1", "对战", "规则", "ban", "分级", "赛季", "pvp", "pve"]):
                return 0
            if any(k in raw for k in ["削弱", "增强", "nerf", "buff", "平衡", "调整"]):
                return 1
            if any(k in raw for k in ["mega", "极巨化", "太晶化", "z招式", "特性", "招式", "道具", "天气"]):
                return 2
            return 3

        if sort_mode == "研究价值":
            filtered = sorted(patches, key=_patch_research_priority)
        else:
            filtered = patches

        col_search, col_cat = st.columns([3, 1])
        with col_search:
            search_term = st.text_input(
                "搜索更新内容",
                placeholder="输入关键词...",
                key=f"search_{selected_game}_{generation}",
            )
        with col_cat:
            all_categories = {c for p in patches for c in p.get("categories", [])}
            category_filter = st.multiselect(
                "类别筛选", options=sorted(all_categories), default=[],
                placeholder="全部", key=f"cat_filter_{selected_game}_{generation}",
            )

        # ── 筛选（必须在渲染前）──────────────
        if search_term:
            s = search_term.lower()
            filtered = [p for p in filtered
                        if s in p.get("title", "").lower() or s in p.get("content", "").lower()]
        if category_filter:
            filtered = [p for p in filtered
                        if any(c in p.get("categories", []) for c in category_filter)]

        PAGE_SIZE = 10
        page_key = f"page_{selected_game}_{generation}"
        if page_key not in st.session_state:
            st.session_state[page_key] = 1

        total_filtered = len(filtered)
        total_pages_f = max(1, (total_filtered + PAGE_SIZE - 1) // PAGE_SIZE)
        current_page = min(st.session_state[page_key], total_pages_f)

        # ── 分页按钮（rerun 全页，key 包含页码，Streamlit 自动替换旧 DOM）────
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("上一页", key=f"prev_{selected_game}_{generation}_{current_page}",
                         disabled=(current_page <= 1)):
                st.session_state[page_key] = current_page - 1
                st.rerun()
        with col_page:
            st.markdown(f"<div style='text-align:center;padding-top:4px'>第 {current_page} / {total_pages_f} 页</div>",
                        unsafe_allow_html=True)
        with col_next:
            if st.button("下一页", key=f"next_{selected_game}_{generation}_{current_page}",
                         disabled=(current_page >= total_pages_f)):
                st.session_state[page_key] = current_page + 1
                st.rerun()

        st.info(f"共 {total_filtered} 条更新记录（第 {current_page}/{total_pages_f} 页）")

        start = (current_page - 1) * PAGE_SIZE
        page_patches = filtered[start:start + PAGE_SIZE]

        extractor = get_analyzer()
        llm_ready = extractor is not None and extractor._get_llm() is not None

        for idx, patch in enumerate(page_patches):
            _render_patch_card(patch, selected_game, generation, llm_ready, extractor, global_db, idx, current_page)


# ==================== Tab 2: 机制时间轴 ====================
def _category_to_type(cat: str) -> str:
    mapping = {
        "foundation": "奠基",
        "pvp": "PvP",
        "enhancement": "强化",
        "pve": "PvE",
        "social": "社交",
        "meta": "Meta",
    }
    return mapping.get(cat, "其他")


with tab2:
    st.header("机制时间轴")
    st.markdown("可视化展示历代多人对战机制的演进过程")

    # 统一从 report_data.json 读取时间轴数据（与 docs/index.html 共用同一数据源）
    all_timelines = _load_timeline_data()

    # 颜色映射（HSL 色相环均匀分布 + 低饱和度，差异大且专业）
    color_map = {
        "PvP":   "#B87878",   # 玫瑰灰，色相 0
        "PvE":   "#7888B8",   # 灰蓝，色相 225
        "强化":  "#B8A078",   # 暖灰金，色相 38
        "奠基":  "#88A088",   # 灰绿，色相 120
        "社交":  "#8878B8",   # 灰紫，色相 270
        "Meta":  "#78A098",   # 灰青，色相 165
        "其他":  "#888898",   # 中性灰，色相 240
    }

    # ── 类型选择区：Pokemon Showdown 风格彩色胶囊按钮（不再使用 expander）──────────────
    # 先计算每个类型在当前数据中的数量
    _type_counts = {}
    _all_games_for_timeline = ["Pokemon", "Temtem", "Palworld", "梦幻西游", "神武", "大话西游"]
    for _game in _all_games_for_timeline:
        _gk = _game.lower().replace(" ", "_").replace("梦幻西游", "mhxy").replace("神武", "shenwu").replace("大话西游", "dhxy")
        if _gk not in all_timelines:
            if _game == "Pokemon" and "pokemon" in all_timelines:
                _gk = "pokemon"
            elif _game == "Palworld" and "palworld" in all_timelines:
                _gk = "palworld"
        if _gk in all_timelines:
            for item in all_timelines[_gk]:
                t = _category_to_type(item.get("category", ""))
                if not item.get("removed"):
                    _type_counts[t] = _type_counts.get(t, 0) + 1

    # session state 管理
    _type_key = f"tab2_types_{selected_game}"
    _game_filter_key = "tab2_game_filter"
    _DEFAULT_GAMES = ["梦幻西游"] if "梦幻西游" in config.SUPPORTED_GAMES else ["Pokemon"]
    _DEFAULT_TYPES = ["PvP", "PvE"]  # 默认只选中 PvP 和 PvE
    if _type_key not in st.session_state:
        st.session_state[_type_key] = _DEFAULT_TYPES
    if _game_filter_key not in st.session_state:
        st.session_state[_game_filter_key] = _DEFAULT_GAMES

    _active_types = st.session_state.get(_type_key, _DEFAULT_TYPES)
    _active_games = st.session_state.get(_game_filter_key, _DEFAULT_GAMES)

    # ── 筛选机制类型区域：7个彩色按钮，点击切换选中状态 ─────────────
    # 使用数字索引绑定 CSS；选中时填满颜色，未选中时淡化，悬停切换效果
    _ALL_MECH_TYPES = list(color_map.keys())
    _css_parts = []
    for _ci, _tname in enumerate(_ALL_MECH_TYPES):
        _tcolor = color_map[_tname]
        _is_act = _tname in _active_types
        _sel = f".st-key-type-btn-{_ci}"
        _bg = _tcolor if _is_act else "transparent"
        _txt = "#fff" if _is_act else _tcolor
        _brd = _tcolor if _is_act else f"rgba({int(_tcolor[1:3],16)},{int(_tcolor[3:5],16)},{int(_tcolor[5:7],16)},0.35)"
        _op = "1 !important;" if _is_act else "0.30 !important;"
        _hover_bg = f"rgba({int(_tcolor[1:3],16)},{int(_tcolor[3:5],16)},{int(_tcolor[5:7],16)},0.85)"
        _css_parts.append(
            f"{_sel} {{"
            f"display:inline-flex !important;"
            f"align-items:center !important;"
            f"padding:0 !important;"
            f"margin:0 !important;"
            f"border:none !important;"
            f"box-shadow:none !important;"
            f"background:transparent !important;"
            f"width:fit-content !important;"
            f"flex:unset !important;"
            f"}}"
            f"{_sel} button {{"
            f"background:{_bg} !important;"
            f"border:1.5px solid {_brd} !important;"
            f"border-radius:3px !important;"
            f"padding:2px 10px !important;"
            f"margin:0 !important;"
            f"box-shadow:none !important;"
            f"min-width:unset !important;"
            f"width:fit-content !important;"
            f"display:inline-flex !important;"
            f"white-space:nowrap !important;"
            f"transition:background 0.12s, color 0.12s, border-color 0.12s !important;"
            f"color:{_txt} !important;"
            f"opacity:{_op}"
            f"flex:unset !important;"
            f"}}"
            f"{_sel} button p {{"
            f"font-size:0.72rem !important;"
            f"font-weight:500 !important;"
            f"margin:0 !important;"
            f"color:inherit !important;"
            f"white-space:nowrap !important;"
            f"line-height:1 !important;"
            f"padding:0 !important;"
            f"border:none !important;"
            f"background:transparent !important;"
            f"box-shadow:none !important;"
            f"display:inline !important;"
            f"}}"
            f"{_sel}:hover button {{"
            f"background:{_tcolor} !important;"
            f"color:#fff !important;"
            f"border-color:{_tcolor} !important;"
            f"opacity:1 !important;"
            f"}}"
            f"{_sel}:hover button p {{"
            f"color:#fff !important;"
            f"}}"
        )
    _css_parts.append(
        "div[data-testid='stHorizontalBlock'] { "
        "display:flex !important; "
        "flex-wrap:wrap !important; "
        "gap:0 !important; "
        "align-items:center !important; "
        "padding:2px 0 !important;"
        "}"
    )
    st.markdown(f"<style>{''.join(_css_parts)}</style>", unsafe_allow_html=True)

    # 7个机制类型按钮，一行排列
    _btn_cols = st.columns(len(_ALL_MECH_TYPES))
    for _ci, _tname in enumerate(_ALL_MECH_TYPES):
        with _btn_cols[_ci]:
            if st.button(_tname, key=f"type-btn-{_ci}"):
                if _tname in _active_types:
                    st.session_state[_type_key] = [t for t in _active_types if t != _tname]
                else:
                    st.session_state[_type_key] = _active_types + [_tname]
                st.rerun()

    # 刷新最终状态
    _active_types = st.session_state.get(_type_key, list(color_map.keys()))
    _active_games = st.session_state.get(_game_filter_key, _DEFAULT_GAMES)
    game_filter = _active_games

    # 从统一数据源构建 display_data
    display_data = []
    for game in game_filter:
        game_key = game.lower().replace(" ", "_")
        # 兼容不同命名方式
        if game_key not in all_timelines:
            if game == "Pokemon" and "pokemon" in all_timelines:
                game_key = "pokemon"
            elif game == "Palworld" and "palworld" in all_timelines:
                game_key = "palworld"
        if game_key in all_timelines:
            for item in all_timelines[game_key]:
                display_data.append({
                    "generation": item.get("gen", "").replace("Gen ", ""),
                    "year": item.get("year", 0),
                    "mechanism": item.get("title", ""),
                    "description": item.get("detail", "")[:80],
                    "type": _category_to_type(item.get("category", "")),
                    "source": game,
                    "confidence": item.get("data_confidence", "unknown"),
                    "removed": item.get("removed", False),
                    "gen_label": item.get("gen", ""),
                    "chain_prev": item.get("chain_prev"),
                    "chain_next": item.get("chain_next"),
                    "chain_related": item.get("chain_related", []),
                    "chain_category": item.get("chain_category"),
                })

    if display_data:
        # 过滤掉已移除条目用于主图表（已移除条目单独展示）
        active_data = [d for d in display_data if not d.get("removed")]
        removed_data = [d for d in display_data if d.get("removed")]

        # ── 甘特图：单一 Plotly 圆点图 + Streamlit 图例表格 ─────────────
        active_filtered = [d for d in active_data if d.get("type") in _active_types]

        if active_filtered:
            # 按世代+年份排序，每世代内按年份编号
            active_filtered.sort(key=lambda x: (
                int(x.get("generation", 0)) if str(x.get("generation", "")).isdigit() else 999,
                x.get("year", 0)
            ))
            _all_gens = sorted(set(
                int(d["generation"]) for d in active_filtered
                if str(d["generation"]).isdigit()
            ))
            _min_year = min(d["year"] for d in active_filtered if d["year"])
            _max_year = max(d["year"] for d in active_filtered if d["year"])

            # 为每个条目分配 row_index（世代内序号）
            _row_map = {}  # item -> row_index
            for gen in _all_gens:
                _g_items = [d for d in active_filtered if str(d.get("generation", "")) == str(gen)]
                _g_items.sort(key=lambda x: x.get("year", 0))
                for _ri, _d in enumerate(_g_items):
                    _row_map[id(_d)] = _ri
            _total_rows = max(_row_map.values()) + 1 if _row_map else 0

            # ── Plotly：单一甘特图 ─────────────
            fig = go.Figure()
            for d in active_filtered:
                _gen = int(d["generation"]) if str(d["generation"]).isdigit() else 999
                _row = _row_map.get(id(d), 0)
                _color = color_map.get(d.get("type", "其他"), "#6b7280")
                _year = d["year"]
                fig.add_trace(go.Scatter(
                    x=[_year],
                    y=[_row],
                    mode="markers",
                    marker=dict(size=14, color=_color, line=dict(width=2, color="white"), symbol="circle"),
                    customdata=[[d.get("description", ""), d.get("confidence", ""), d.get("type", ""), d.get("mechanism", "")]],
                    hovertemplate=(
                        f"<b>{d.get('mechanism', '')}</b><br>"
                        f"Gen {d.get('generation', '')} · {_year}<br>"
                        f"类型: %{{customdata[2]}}<br>"
                        f"说明: %{{customdata[0]}}<extra></extra>"
                    ),
                    name=d.get("mechanism", ""),
                    showlegend=False,
                ))

            # 世代分隔虚线 + 世代 y 轴标签
            _gen_boundaries = {}  # gen -> (top_row, bottom_row)
            _gen_midpoints = {}   # gen -> midpoint row
            for gen in _all_gens:
                _g_items = [d for d in active_filtered if str(d.get("generation", "")) == str(gen)]
                _g_items.sort(key=lambda x: x.get("year", 0))
                if not _g_items:
                    continue
                _top = _row_map.get(id(_g_items[0]), 0)
                _bot = _row_map.get(id(_g_items[-1]), 0)
                _gen_boundaries[gen] = (_top, _bot)
                _gen_midpoints[gen] = (_top + _bot) / 2

            # 世代分隔线（垂直虚线，精确画在分隔处）
            for gen in _all_gens:
                _top, _bot = _gen_boundaries.get(gen, (0, 0))
                if gen != _all_gens[0]:
                    _sep_y = _top - 0.5
                    fig.add_hline(y=_sep_y, line_dash="dot", line_color="#ddd", line_width=1.5)

            # Y 轴世代标签（用 ticktext 模拟）
            _y_ticks = [_gen_midpoints[g] for g in _all_gens if g in _gen_midpoints]
            _y_ticktext = [f"Gen {g}" for g in _all_gens if g in _gen_midpoints]

            fig.update_layout(
                height=max(300, _total_rows * 38 + 30),
                margin=dict(l=8, r=8, t=8, b=36),
                plot_bgcolor="white",
                showlegend=False,
                font=dict(size=12),
                xaxis=dict(
                    range=[_min_year - 1, _max_year + 1],
                    title="年份",
                    showgrid=True,
                    gridcolor="#e8e8e8",
                    dtick=1,
                    tickfont=dict(size=11, color="#555"),
                    zeroline=False,
                ),
                yaxis=dict(
                    range=[_total_rows - 0.5, -0.5],
                    showticklabels=False,
                    showgrid=False,
                    zeroline=False,
                    fixedrange=True,
                ),
            )
            if _y_ticks:
                fig.update_yaxes(
                    tickmode="array",
                    tickvals=_y_ticks,
                    ticktext=_y_ticktext,
                    showticklabels=True,
                    tickfont=dict(size=11, color="#666"),
                )

            st.plotly_chart(fig, use_container_width=True)

            # ── 机制图例表格（Streamlit HTML 渲染）────────────
            _conf_label_map = {
                "official": "官方",
                "community": "社区",
                "inferred_high": "推断",
                "inferred_mid": "推断",
                "inferred_low": "推断",
                "future": "未来",
            }
            # 构建表格行
            _rows_html = ""
            for gen in _all_gens:
                _g_items = [d for d in active_filtered if str(d.get("generation", "")) == str(gen)]
                _g_items.sort(key=lambda x: x.get("year", 0))
                _gen_row_span = len(_g_items)
                _row_bg = "#f8f9fa" if _all_gens.index(gen) % 2 == 0 else "#ffffff"
                # 世代单元格（纵向合并）
                _rows_html += (
                    f'<tr>'
                    f'<td rowspan="{_gen_row_span}" style="background:{_row_bg};color:#888;font-size:11px;font-weight:600;padding:4px 8px;border-right:1px solid #eee;vertical-align:middle;text-align:center;width:50px">Gen {gen}</td>'
                )
                for _di, d in enumerate(_g_items):
                    _type_name = d.get("type", "其他")
                    _type_color = color_map.get(_type_name, "#6b7280")
                    _mech = d.get("mechanism", "")
                    _desc = d.get("description", "")[:60]
                    _conf = _conf_label_map.get(d.get("confidence", ""), d.get("confidence", ""))
                    _year = d.get("year", "")
                    if _di > 0:
                        _rows_html += "<tr>"
                    _rows_html += (
                        f'<td style="padding:5px 8px;border-bottom:1px solid #f0f0f0;width:70px;text-align:center">'
                        f'<span style="background:{_type_color};color:white;padding:1px 6px;border-radius:8px;font-size:10px;font-weight:600;white-space:nowrap">{_type_name}</span>'
                        f'</td>'
                        f'<td style="padding:5px 8px;border-bottom:1px solid #f0f0f0">'
                        f'<div style="font-size:12px;font-weight:600;color:#222">{_mech}</div>'
                        f'<div style="font-size:11px;color:#888;margin-top:1px">{_desc}{"…" if len(d.get("description","")) > 60 else ""}</div>'
                        f'</td>'
                        f'<td style="padding:5px 8px;border-bottom:1px solid #f0f0f0;color:#666;font-size:11px;white-space:nowrap">{_year}</td>'
                        f'</tr>'
                    )

            st.markdown(
                f'<table style="width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed">'
                f'<thead><tr style="background:#f5f5f5">'
                f'<th style="padding:6px 8px;text-align:center;color:#888;font-weight:600;width:50px">世代</th>'
                f'<th style="padding:6px 8px;text-align:center;color:#888;font-weight:600;width:70px">类型</th>'
                f'<th style="padding:6px 8px;color:#888;font-weight:600">机制名称 / 描述</th>'
                f'<th style="padding:6px 8px;text-align:center;color:#888;font-weight:600;width:50px">年份</th>'
                f'</tr></thead>'
                f'<tbody>{_rows_html}</tbody>'
                f'</table>',
                unsafe_allow_html=True
            )

        # 世代颜色映射（灰调，一致且专业）
        gen_color_map = {
            1: "#A0A0A0",  # Gen1
            2: "#B8A088",  # Gen2
            3: "#88A0B8",  # Gen3
            4: "#A8B8A8",  # Gen4
            5: "#888888",  # Gen5
            6: "#B88888",  # Gen6
            7: "#A89888",  # Gen7
            8: "#88A0A8",  # Gen8
            9: "#A0A8A0",  # Gen9
        }

        # 已移除机制单独列表展示
        if removed_data:
            st.subheader(f"已移除机制（{len(removed_data)} 条）")
            for item in sorted(removed_data, key=lambda x: x["year"]):
                conf_color = {
                    "official": "#16a34a",
                    "community": "#0369a1",
                    "inferred_high": "#0f766e",
                    "inferred_mid": "#ca8a04",
                    "inferred_low": "#dc2626",
                    "future": "#6d28d9",
                }.get(item.get("confidence", ""), "#888")
                conf_label = {
                    "official": "官方",
                    "community": "社区",
                    "inferred_high": "推断·高",
                    "inferred_mid": "推断·中",
                    "inferred_low": "推断·低",
                    "future": "未来",
                }.get(item.get("confidence", ""), item.get("confidence", ""))

                # 世代主题色
                gen_val = item.get("generation", "")
                try:
                    gen_num = int(gen_val)
                except (ValueError, TypeError):
                    gen_num = 0
                gen_color = gen_color_map.get(gen_num, "#888888")

                # 演进链信息
                chain_info = ""
                if item.get("chain_prev") or item.get("chain_next"):
                    prev_str = f"← {item['chain_prev']}" if item.get("chain_prev") else ""
                    next_str = f"{item['chain_next']} →" if item.get("chain_next") else ""
                    chain_info = f" <span style='color:#0369a1;font-size:12px'>链接: {prev_str} {next_str}</span>"

                st.markdown(
                    f'- <span style="color:{gen_color};font-size:0.9rem">{item.get("mechanism", "")}</span>（{item.get("gen_label", "")}，{item.get("year", "")}）'
                    f" <span style='color:{conf_color};font-size:12px'>[{conf_label}]</span>"
                    f"{chain_info}"
                    f" — {item.get('description', '')[:60]}...",
                    unsafe_allow_html=True
                )

        # P1-2: 演进链概览
        chain_map = {}
        for item in display_data:
            cc = item.get("chain_category", "")
            if cc:
                if cc not in chain_map:
                    chain_map[cc] = []
                chain_map[cc].append(item)

        if chain_map:
            st.divider()
            st.subheader("演进链概览")
            chain_display_names = {
                "enhancement": "强化机制演进链",
                "protection": "防御/保护机制演进链",
                "weather": "天气系统演进链",
                "core_battle": "核心战斗规则演进链",
                "differentiation": "差异化设计演进链",
                "pve_group": "团体战/PvE演进链",
                "meta_management": "Meta管理演进链",
                "online": "联网/社交演进链",
                "esports": "电竞化演进链",
            }
            for cc, items in sorted(chain_map.items(), key=lambda x: x[0]):
                chain_name = chain_display_names.get(cc, cc)
                chain_items = sorted(items, key=lambda x: (x.get("chain_order", 0), x["year"]))
                chain_titles = [f"{i.get('mechanism','')}" for i in chain_items]
                st.markdown(f"**{chain_name}**：{' → '.join(chain_titles)}")
                if len(chain_items) <= 5:
                    for ci in chain_items:
                        with st.expander(f"  {ci.get('mechanism','')[:40]}", expanded=False):
                            st.caption(f"{ci.get('gen_label','')} {ci.get('year','')} | {ci.get('type','')} | {ci.get('confidence','')}")
                            st.write(ci.get("description", "")[:150] + "...")


    else:
        st.info("当前选择游戏的报告数据暂缺，请联系管理员扩充数据。")
        # 备用：显示数据库中的已分析条目
        st.divider()
        st.subheader("已分析条目（来自本地数据库）")

    # 已分析的 DB 条目补充展示（让图表与真实数据联动）
    _tab2_db_key = f"_tab2_db_patches_{selected_game}_{generation}"
    if _tab2_db_key not in st.session_state:
        try:
            _sdb = SQLiteStore()
            _db_results = _sdb.get_analysis_results(game=selected_game, limit=20) or []
            # 筛选多人相关
            _mp_kws = ["PvP", "PvE", "2v2", "双打", "团体战", "集火", "保排", "raid", "对战", "VGC"]
            _filtered_db = [r for r in _db_results
                           if any(k in str(r.get("summary", "") + r.get("mechanics", "")) for k in _mp_kws)]
            st.session_state[_tab2_db_key] = _filtered_db
        except Exception:
            st.session_state[_tab2_db_key] = []
    else:
        _filtered_db = st.session_state[_tab2_db_key]

    if _filtered_db:
        st.divider()
        st.subheader("已分析条目（来自本地数据库）")
        _dcols = st.columns([1, 3, 2])
        with _dcols[0]:
            st.caption(f"共 {len(_filtered_db)} 条")
        with _dcols[1]:
            _dfilter = st.text_input(
                "筛选分析结果", placeholder="输入关键词...", key=f"_db_filter_{selected_game}_{generation}"
            )
        with _dcols[2]:
            st.button("刷新", key=f"_refresh_db_{selected_game}_{generation}")
            if _dfilter:
                _filtered_db = [r for r in _filtered_db
                               if _dfilter.lower() in (r.get("summary", "") + r.get("mechanics", "")).lower()]

        for _r in _filtered_db[:10]:
            with st.expander(f"{_r.get('summary', 'N/A')[:50]}...", expanded=False):
                st.caption(f"日期: {_r.get('patch_date', 'N/A')} | 机制: {_r.get('mechanics', 'N/A')}")
                if _r.get("summary"):
                    st.markdown(_r.get("summary")[:200])

    # 防御机制演进对比（仅游戏筛选器选中了 Pokemon 时显示）


# ==================== Tab 3: 设计意图分析 ====================
with tab3:
    st.header("设计意图分析")
    st.markdown("""
    <div class="insight-box">
    利用大语言模型分析游戏版本更新背后的设计意图。
    数据来自预采集的本地更新日志，无需网络请求。
    </div>
    """, unsafe_allow_html=True)

    if not patches:
        st.warning("需要先在「版本编年史」中获取到更新数据才能进行分析")
    else:
        # 分析模式选择
        analysis_mode = st.radio(
            "选择分析模式",
            options=["分析已有数据", "语义搜索"],
            horizontal=True,
            key=f"analysis_mode_{selected_game}_{generation}",
        )

        if analysis_mode == "分析已有数据":
            # 显示可分析的数据预览
            st.subheader("待分析更新列表")

            analysis_options = []
            for i, patch in enumerate(patches):
                label = f"{patch.get('date', 'N/A')} - {patch.get('title', 'N/A')[:40]}..."
                analysis_options.append((i, label))

            selected_indices = st.multiselect(
                "选择要分析的更新",
                options=[opt[0] for opt in analysis_options],
                format_func=lambda x: next((opt[1] for opt in analysis_options if opt[0] == x), ""),
                key=f"analysis_indices_{selected_game}_{generation}",
            )

            tab3_results_key = f"_tab3_results_{selected_game}_{generation}"

            # 渲染已有结果（点击按钮后第二次 rerun 时）
            if tab3_results_key in st.session_state:
                results = st.session_state.pop(tab3_results_key)
                st.success(f"分析完成，共 {len(results)} 条结果")
                for i, result in enumerate(results):
                    with st.expander(f"{result.get('original_title', '')[:50]}...", expanded=i < 2):
                        st.markdown(f"**原始标题**: {result.get('original_title', '')}")
                        st.markdown(f"**具体改动**: {result.get('exact_change', result.get('intent_summary', 'N/A'))}")
                        st.markdown(f"**竞技影响**: {result.get('competitive_impact', 'N/A')}")
                        st.markdown(f"**设计理由**: {result.get('design_rationale', result.get('problem_solved', 'N/A'))}")
                        tags = result.get("mechanic_tags", [])
                        if tags:
                            st.markdown("**涉及机制**: " + " ".join([f"`{t}`" for t in tags]))

                        # 平衡评估可视化
                        _bal = result.get("balance_assessment", "") or result.get("design_pattern", "")
                        if _bal:
                            _AMAP = {
                                "恰到好处": ("[力度适中]", "#52c41a"),
                                "力度不足": ("[调整不足]", "#faad14"),
                                "过犹不及": ("[矫枉过正]", "#ff4d4f"),
                                "治标不治本": ("[治标不治本]", "#fa8c16"),
                            }
                            _albl, _acol = next(
                                ((l, c) for k, (l, c) in _AMAP.items() if k in _bal),
                                (f"[{_bal}]", "#666"),
                            )
                            st.markdown(f"**平衡评估**: <span style='background:{_acol};color:white;padding:2px 10px;border-radius:12px;font-size:12px'>{_albl}</span>", unsafe_allow_html=True)

                        # 数据置信度
                        _conf = result.get("_data_confidence", "")
                        if _conf:
                            _cc = {"高": "#52c41a", "中": "#faad14", "低": "#ff4d4f"}.get(_conf, "#666")
                            st.markdown(f"**分析置信度**: <span style='color:{_cc};font-weight:bold'>[{_conf}]</span>", unsafe_allow_html=True)

                        # 历史案例幻觉防护
                        similar = result.get("similar_historical_cases", [])
                        if similar:
                            st.warning("以下历史案例由 AI 推断生成，建议通过 Serebii.net 等权威来源交叉验证")
                            st.markdown("**历史参照**: " + "；".join([str(s) if isinstance(s, str) else s.get('description', '') for s in similar[:2]]))

                        try:
                            db = SQLiteStore()
                            db.add_analysis_result(result)
                        except Exception:
                            pass

            # 提示 + 按钮
            if selected_indices:
                st.info("开始分析将调用 AI 分析所选更新，预计需等待 10-30 秒。")

            if selected_indices and st.button("开始 AI 分析", type="primary"):
                # 立即设置状态并 rerun，spinner 在第二次渲染时出现
                st.session_state["_tab3_analyzing"] = True
                st.session_state["_tab3_indices"] = selected_indices
                st.rerun()

            # 执行分析（第二次 rerun 时）
            if st.session_state.get("_tab3_analyzing"):
                st.session_state["_tab3_analyzing"] = False
                indices = st.session_state.pop("_tab3_indices", [])
                analyzer = get_analyzer()
                results = []
                progress_bar = st.progress(0)

                for i, idx in enumerate(indices):
                    patch = patches[idx]
                    with st.spinner(f"正在分析: {patch.get('title', '')[:30]}..."):
                        result = analyzer.analyze_intent(
                            game=selected_game,
                            version=patch.get("date", ""),
                            date=patch.get("date", ""),
                            content=f"{patch.get('title', '')}\n\n{patch.get('content', '')}",
                        )
                        if result:
                            result["original_title"] = patch.get("title", "")
                            result["original_content"] = patch.get("content", "")[:200]
                            results.append(result)
                        progress_bar.progress((i + 1) / len(indices))

                # 保存结果，触发第三次 rerun 显示
                st.session_state[tab3_results_key] = results
                st.rerun()

        else:
            # 语义搜索
            st.subheader("语义搜索设计意图")

            query = st.text_input(
                "输入研究问题",
                placeholder="例如：如何防止AOE在双打中过于强势？",
                key=f"semantic_query_{selected_game}_{generation}",
            )

            if query:
                analyzer = get_analyzer()
                try:
                    vector_store = VectorStore.get_instance()
                    results = vector_store.search(query, top_k=5, game=selected_game)

                    if results:
                        for result in results:
                            with st.expander(f"{result.get('text', '')[:50]}..."):
                                st.markdown(f"**相似度**: {result.get('similarity', 0):.2f}")
                                st.markdown(f"**内容**: {result.get('text', '')}")
                                st.json(result.get("metadata", {}))
                    else:
                        st.info("向量数据库中暂无相关数据，请先运行分析以建立索引")

                except Exception as e:
                    st.warning(f"语义搜索功能暂不可用: {e}")


# ==================== Tab 4: 演进报告 ====================
def _render_step(step_num, label, state):
    label_html = f'<span class="tab4-step-{state}">{step_num}. {label}</span>'
    st.markdown(label_html, unsafe_allow_html=True)


with tab4:
    st.header("演进报告")
    st.markdown("AI 自动扫描所有更新，构建分层主题树，选择具体演进枝后生成深度分析报告。")

    if not patches:
        st.warning("当前没有可用数据。请先在「版本编年史」中选择游戏和世代加载数据。")
    else:
        # v3 使用新缓存 key，避免与旧版缓存冲突
        cache_key = f"topic_discovery_v3_{selected_game}_{generation}"

        if cache_key not in st.session_state:
            # 优先尝试从 SQLite 持久化缓存读取（避免每次重新调用 AI）
            cached = global_db.get_topic_tree_cache(selected_game, generation)
            cached_info = global_db.get_topic_tree_cache_info(selected_game, generation)
            if cached and cached.get("success"):
                st.session_state[cache_key] = cached
                st.session_state["_topic_tree_cached"] = True
                st.session_state["_topic_tree_cached_at"] = cached_info
            else:
                st.session_state[cache_key] = None
                st.session_state["_topic_tree_cached"] = False

        if st.session_state[cache_key] is None:
            st.session_state["_topic_tree_cached"] = False
            try:
                analyzer = get_analyzer()
                from analyzer.ai_topic_discoverer import AITopicDiscoverer
                discoverer = AITopicDiscoverer(analyzer)
                with st.spinner("AI 正在分析所有更新，构建分层主题树（需等待 15-40 秒）..."):
                    result = discoverer.discover(patches)

                # 成功发现后写入 SQLite 持久化缓存
                if result.get("success"):
                    global_db.save_topic_tree(
                        selected_game, generation,
                        json.dumps(result, ensure_ascii=False),
                    )

                st.session_state[cache_key] = result
            except Exception:
                import traceback
                st.session_state[cache_key] = {
                    "success": False,
                    "discovered_topics": [],
                    "topic_tree": [],
                    "error": "发现过程异常",
                    "traceback": traceback.format_exc(),
                    "total_analyzed": len(patches),
                }
            st.rerun()
        else:
            result = st.session_state[cache_key]

        # 展示缓存状态
        if st.session_state.get("_topic_tree_cached") and st.session_state.get("_topic_tree_cached_at"):
            cached_time = st.session_state["_topic_tree_cached_at"]
            st.caption(f"主题树已缓存（生成于 {cached_time}），切换游戏/世代或点击「重新发现」将更新缓存")

        # 优先使用新格式 topic_tree，兼容旧格式 discovered_topics
        topic_tree = result.get("topic_tree", []) if result.get("success") else []
        flat_topics = result.get("discovered_topics", []) if result.get("success") else []

        # 如果 topic_tree 为空，降级到扁平主题列表
        use_tree = bool(topic_tree)
        has_topics = bool(topic_tree) or bool(flat_topics)

        # 步骤指示器状态
        step1_state = "done" if has_topics else ("active" if result["success"] else "waiting")
        step2_state = "waiting"
        step3_state = "waiting"

        # 获取选择状态
        if use_tree:
            sel_dim = st.session_state.get("sel_dimension_idx")
            sel_branch = st.session_state.get("sel_branch_idx")
            step2_state = "done" if (sel_dim is not None and sel_branch is not None) else (
                "active" if sel_dim is not None else "waiting"
            )
            sel_dim = sel_dim if (sel_dim is not None and sel_dim < len(topic_tree)) else None
            if sel_dim is not None and sel_branch is not None:
                branches = topic_tree[sel_dim].get("branches", [])
                if sel_branch < len(branches):
                    branch_key = f"report_v3_{sel_dim}_{sel_branch}_{selected_game}_{generation}"
                    has_report = bool(st.session_state.get(branch_key))
                    step3_state = "done" if has_report else "active"
                else:
                    sel_branch = None
                    has_report = False
            else:
                sel_branch = None
                has_report = False
        else:
            sel_dim = None
            sel_branch = None
            selected_idx = st.session_state.get("selected_topic_idx")
            has_selection = selected_idx is not None and selected_idx < len(flat_topics)
            if has_selection:
                step2_state = "done"
                report_key = f"report_v2_{selected_idx}_{selected_game}_{generation}"
                has_report = bool(st.session_state.get(report_key))
                step3_state = "done" if has_report else "active"

        col_s1, col_s2, col_s3 = st.columns([1, 1, 2])
        with col_s1:
            _render_step(1, "AI 发现主题", step1_state)
        with col_s2:
            _render_step(2, "选择演进枝", step2_state)
        with col_s3:
            _render_step(3, "生成报告", step3_state)

        st.divider()

        if not result["success"]:
            st.error(f"主题发现失败：{result.get('error', '未知错误')}")
            if st.button("重新尝试", key="retry_discovery"):
                del st.session_state[cache_key]
                st.rerun()

        elif not has_topics:
            st.info("AI 分析完成，但没有发现足够支撑研究主题的数据。可以尝试切换到其他游戏或扩大数据范围。")

        else:
            # ---- Step 1 完成 ----
            col_stat, col_redo = st.columns([4, 1])
            with col_stat:
                total_dims = len(topic_tree) if use_tree else 0
                total_branches = sum(
                    len(t.get("branches", [])) for t in topic_tree
                ) if use_tree else len(flat_topics)
                if use_tree and total_dims > 0:
                    st.success(
                        f"AI 分析了 {result['total_analyzed']} 条更新，构建了 "
                        f"{total_dims} 个设计维度、共 {total_branches} 条演进枝"
                    )
                    if result.get("overview"):
                        st.caption(f"整体方向：{result['overview']}")
                else:
                    st.success(f"AI 分析了 {result['total_analyzed']} 条更新，归纳出 {len(flat_topics)} 个设计主题")
            with col_redo:
                if st.button("重新发现", help="清空缓存，重新调用 AI 分析", key="redo_discovery"):
                    del st.session_state[cache_key]
                    global_db.delete_topic_tree_cache(selected_game, generation)
                    st.rerun()

            st.divider()

            # =============================================
            # 分支A：树形主题 UI（新版）
            # =============================================
            if use_tree:
                st.markdown("**选择研究维度与演进枝**")

                # 渲染每个顶层维度（可折叠卡片）
                for di, dim in enumerate(topic_tree):
                    dim_name = dim.get("name", "未命名维度")
                    dim_desc = dim.get("description", "")
                    dim_why = dim.get("why_important", "")
                    branches = dim.get("branches", [])
                    is_dim_sel = (sel_dim == di)

                    with st.container():
                        dim_expanded = st.expander(
                            f"{'▶' if is_dim_sel else '▶'} {dim_name}  ·  {dim_desc}  ·  {len(branches)}条演进枝",
                            expanded=is_dim_sel,
                        )

                        with dim_expanded:
                            if dim_why:
                                st.caption(f"提示: {dim_why}")

                            if not branches:
                                st.info("该维度下暂无演进枝数据")
                                continue

                            for bi, branch in enumerate(branches):
                                is_branch_sel = (
                                    is_dim_sel and sel_branch == bi
                                )
                                problem = branch.get("problem", "未命名问题")
                                stages = branch.get("evolution_stages", [])
                                key_insight = branch.get("key_insight", "")
                                is_one_way = branch.get("is_one_way", False)

                                stage_labels = " → ".join(
                                    s.get("period", "?") for s in stages
                                ) if stages else "无"

                                badge = "[单向]" if is_one_way else "[演进]"
                                branch_label = f"{badge} {problem}  [{stage_labels}]"

                                col_b, col_r = st.columns([4, 1])
                                with col_b:
                                    st.markdown(f"**{branch_label}**")
                                    if key_insight:
                                        st.caption(f"洞察：{key_insight}")
                                with col_r:
                                    btn_key = f"branch_btn_{di}_{bi}"
                                    if st.button(
                                        "生成" if not is_branch_sel else "已选",
                                        key=btn_key,
                                        type="primary" if is_branch_sel else "secondary",
                                    ):
                                        st.session_state["sel_dimension_idx"] = di
                                        st.session_state["sel_branch_idx"] = bi
                                        st.rerun()

                                st.divider()

                # ---- Step 3: 选中演进枝后生成报告 ----
                if sel_dim is not None and sel_branch is not None:
                    dim = topic_tree[sel_dim]
                    branch = dim["branches"][sel_branch]
                    branch_key = f"report_v3_{sel_dim}_{sel_branch}_{selected_game}_{generation}"

                    st.divider()
                    st.markdown(f"### {branch.get('problem', '演进分析')}")
                    st.caption(f"维度：{dim.get('name', '')}")

                    # 演进时间线预览
                    stages = branch.get("evolution_stages", [])
                    if stages:
                        with st.expander("查看演进时间线"):
                            for s in stages:
                                st.markdown(
                                    f"**{s.get('period', '?')}**  ·  {s.get('solution', '')}"
                                )
                                for pt in s.get("patch_titles", []):
                                    st.caption(f"  · {pt}")

                    if st.session_state.get(f"_generating_{branch_key}"):
                        del st.session_state[f"_generating_{branch_key}"]

                        progress_area = st.empty()
                        progress_bar = progress_area.progress(0, text="正在准备数据...")
                        try:
                            analyzer = get_analyzer()
                            from analyzer.report_generator import EvolutionReportGenerator
                            generator = EvolutionReportGenerator(analyzer)
                            topic_for_report = {
                                "name": branch.get("problem", ""),
                                "_branch": branch,
                                "_top_level": dim,
                                "matched_preview": [
                                    pt
                                    for s in stages
                                    for pt in s.get("patch_titles", [])
                                ],
                            }
                            progress_bar.progress(0.4, text="正在调用 AI 生成报告，请稍候...")

                            report = generator.generate_report(topic_for_report, patches)

                            if report and not report.get("_error"):
                                progress_bar.progress(1.0, text="完成！")
                                import time; time.sleep(0.5)
                                progress_area.empty()
                                st.session_state[branch_key] = report.get("_markdown", "")
                                st.rerun()
                            else:
                                progress_area.empty()
                                error_msg = report.get("_message", "未知错误") if report else "未知错误"
                                _show_report_error(error_msg)
                        except Exception as e:
                            progress_area.empty()
                            _show_report_error(str(e))
                    else:
                        st.info(
                            "生成演进报告将综合分析历代相关更新，内容较详细，"
                            "预计需等待 30-120 秒。如遇超时，请稍后重试，或切换到其他演进枝。"
                        )

                    # 当前位置导航
                    st.caption(
                        f"{dim.get('name', '')} > {branch.get('problem', '')}"
                        f"  ·  共 {len(stages)} 个演进阶段"
                    )

                    if has_report:
                        report_content = st.session_state[branch_key]
                        _report_dict = None
                        if isinstance(report_content, dict):
                            _report_dict = report_content
                            report_content = report_content.get("_markdown", "")
                        elif isinstance(report_content, str):
                            pass
                        else:
                            report_content = ""

                        if report_content:
                            # 报告头部：数据置信度标注
                            _rep_conf = (_report_dict or {}).get("_confidence", "")
                            _rep_count = (_report_dict or {}).get("_matched_count", len(stages))
                            if _rep_conf:
                                _rc = {"高": "#52c41a", "中": "#faad14", "低": "#ff4d4f"}.get(_rep_conf, "#666")
                                st.markdown(f"<span style='background:{_rc};color:white;padding:2px 10px;border-radius:12px;font-size:12px'>[{_rep_conf}]</span> 基于 {_rep_count} 条相关更新", unsafe_allow_html=True)
                            st.markdown(report_content)

                            # P3-1: 时间轴历史验证层
                            _tl_key = selected_game.lower().replace(" ", "_")
                            _tl_data = all_timelines.get(_tl_key, [])
                            if _tl_data:
                                _branch_name = branch.get("problem", "").lower()
                                # 模糊匹配：时间轴中与演进枝主题相关的条目
                                _matched_tl = []
                                for _tl in _tl_data:
                                    _tl_title = _tl.get("title", "").lower()
                                    # 检查标题或描述是否与演进枝相关
                                    _keywords = [
                                        "强化", "超级进化", "极巨化", "太晶化", "z 招式",
                                        "防御", "保护", "嘲讽", "守住", "看我嘛",
                                        "天气", "沙暴", "降雨", "晴天",
                                        "对战", "双打", "三打", "vgc",
                                        "meta", "ban", "禁用",
                                        "简化", "移除", "删除",
                                        "团体战", "raid", "团体战",
                                        "社交", "wifi", "联网",
                                    ]
                                    if any(k in _tl_title or k in _tl.get("detail", "").lower() for k in _keywords):
                                        # 进一步过滤：只保留与演进枝主题相关的
                                        if any(_kw in _tl_title for _kw in ["超级进化", "极巨化", "太晶化", "z 招式", "mega", "dynamax", "tera"]):
                                            if any(k in _branch_name for k in ["强化", "超级进化", "极巨化", "太晶化", "z 招式", "mega", "dynamax", "tera"]):
                                                _matched_tl.append(_tl)
                                        elif any(_kw in _tl_title for _kw in ["天气", "沙暴", "降雨"]):
                                            if any(k in _branch_name for k in ["天气", "沙暴", "降雨", "顺风"]):
                                                _matched_tl.append(_tl)
                                        elif any(_kw in _tl_title for _kw in ["对战", "双打", "三打", "团体战"]):
                                            if any(k in _branch_name for k in ["对战", "双打", "团体", "vgc"]):
                                                _matched_tl.append(_tl)
                                        elif _tl.get("removed"):
                                            if any(k in _branch_name for k in ["移除", "简化", "删除", "meta"]):
                                                _matched_tl.append(_tl)
                                if _matched_tl:
                                    st.divider()
                                    st.markdown("**历史验证：时间轴相关条目**")
                                    _unique_tl = {_tl["title"]: _tl for _tl in _matched_tl}
                                    for _tl in sorted(_unique_tl.values(), key=lambda x: x.get("year", 0))[:8]:
                                        _tl_conf = _tl.get("data_confidence", "unknown")
                                        _conf_color = {"official": "#52c41a", "community": "#1890ff", "inferred_high": "#722ed1", "inferred_mid": "#faad14", "inferred_low": "#ff4d4f", "future": "#eb2f96"}.get(_tl_conf, "#8c8c8c")
                                        _tl_year = _tl.get("year", "")
                                        _tl_gen = _tl.get("gen", _tl.get("version", ""))
                                        _is_removed = _tl.get("removed", False)
                                        _rem_tag = f" | 已移除({_tl.get('removal_year', '')})" if _is_removed else ""
                                        _chain = ""
                                        if _tl.get("chain_prev") or _tl.get("chain_next"):
                                            _prev = f"← {_tl['chain_prev']}" if _tl.get("chain_prev") else ""
                                            _next = f"{_tl['chain_next']} →" if _tl.get("chain_next") else ""
                                            _chain = f" | 演进链: {_prev} {_next}".strip()
                                        st.markdown(
                                            f"- **{_tl.get('title', '')}**（{_tl_gen} · {_tl_year}）"
                                            f"<span style='color:{_conf_color};font-size:12px'>[{_tl_conf}]</span>"
                                            f"{_rem_tag}{_chain}",
                                            unsafe_allow_html=True,
                                        )
                                        st.caption(f"  {str(_tl.get('detail', ''))[:100]}...")


                        st.divider()

                        # P1-4: 报告导出功能
                        _report_raw = report_content if isinstance(report_content, str) else (
                            report_content.get("_markdown", "") if isinstance(report_content, dict) else ""
                        )
                        if _report_raw:
                            col_copy, col_download = st.columns(2)
                            with col_copy:
                                st.code(_report_raw[:2000] + ("..." if len(_report_raw) > 2000 else ""), language="markdown")
                                if st.button("复制报告文本", key=f"copy_report_{branch_key}"):
                                    try:
                                        import pyperclip
                                        pyperclip.copy(_report_raw)
                                        st.success("已复制到剪贴板！")
                                    except ImportError:
                                        st.info("剪贴板功能需要安装 pyperclip：`pip install pyperclip`")
                            with col_download:
                                _filename = f"演进报告_{branch.get('problem', '未知主题')}.md"
                                st.download_button(
                                    "下载 Markdown",
                                    _report_raw.encode("utf-8"),
                                    _filename,
                                    mime="text/markdown",
                                    key=f"download_report_{branch_key}",
                                )

                        st.divider()
                        if st.button("换一个演进枝重新分析", key="change_branch"):
                            st.session_state["sel_branch_idx"] = None
                            st.rerun()
                    else:
                        if st.button("生成演进报告", type="primary", key="gen_branch_report", width="stretch"):
                            st.session_state[f"_generating_{branch_key}"] = True
                            st.rerun()

            # =============================================
            # 分支B：扁平主题 UI（旧版兼容）
            # =============================================
            else:
                st.markdown("**选择研究主题**")
                for idx, topic in enumerate(flat_topics):
                    count = len(topic.get("matched_preview", []))
                    is_sel = (st.session_state.get("selected_topic_idx") == idx)
                    btn_label = f"{topic.get('name', '')}  [{count}条]"
                    clicked = st.button(
                        btn_label,
                        key=f"topic_v2_{idx}",
                        type="primary" if is_sel else "secondary",
                        width="stretch",
                    )
                    if clicked:
                        st.session_state["selected_topic_idx"] = idx
                        st.rerun()

                selected_idx = st.session_state.get("selected_topic_idx")
                has_selection = selected_idx is not None and selected_idx < len(flat_topics)
                report_key = f"report_v2_{selected_idx}_{selected_game}_{generation}"
                has_report = bool(st.session_state.get(report_key))

                if has_selection:
                    topic = flat_topics[selected_idx]
                    st.divider()
                    st.markdown(f"### {topic.get('name', '')}")
                    st.caption(topic.get("description", ""))

                    if topic.get("matched_preview"):
                        with st.expander("查看相关更新列表"):
                            for p in topic["matched_preview"]:
                                st.markdown(f"- {p}")

                    if has_report:
                        report = st.session_state[report_key]
                        _rep_d = report if isinstance(report, dict) else None
                        _rep_str = _rep_d.get("_markdown", "") if _rep_d else (report if isinstance(report, str) else "")
                        if _rep_str:
                            _rc2 = (_rep_d or {}).get("_confidence", "")
                            if _rc2:
                                _rc3 = {"高": "#52c41a", "中": "#faad14", "低": "#ff4d4f"}.get(_rc2, "#666")
                                st.markdown(f"<span style='background:{_rc3};color:white;padding:2px 10px;border-radius:12px;font-size:12px'>[{_rc2}]</span> 基于 {_rep_d.get('_matched_count', '?')} 条相关更新", unsafe_allow_html=True)
                            st.markdown(_rep_str)

                            # P3-1: 时间轴历史验证层（扁平主题路径）
                            _tl_key2 = selected_game.lower().replace(" ", "_")
                            _tl_data2 = all_timelines.get(_tl_key2, [])
                            if _tl_data2 and topic.get("name"):
                                _topic_name2 = topic.get("name", "").lower()
                                _matched_tl2 = [
                                    _tl for _tl in _tl_data2
                                    if any(kw in (_tl.get("title", "").lower() + _tl.get("detail", "").lower())
                                       for kw in [_topic_name2] if len(kw) > 2)
                                ]
                                if _matched_tl2:
                                    st.divider()
                                    st.markdown("**历史验证：时间轴相关条目**")
                                    for _tl in sorted(_matched_tl2, key=lambda x: x.get("year", 0))[:5]:
                                        _tl_conf2 = _tl.get("data_confidence", "unknown")
                                        _conf_c2 = {"official": "#52c41a", "community": "#1890ff", "inferred_high": "#722ed1", "inferred_mid": "#faad14"}.get(_tl_conf2, "#8c8c8c")
                                        _is_rm = _tl.get("removed", False)
                                        _rm_tag = f" | 已移除({_tl.get('removal_year', '')})" if _is_rm else ""
                                        st.markdown(
                                            f"- **{_tl.get('title', '')}**（{_tl.get('gen', _tl.get('version', ''))} · {_tl.get('year', '')})"
                                            f"<span style='color:{_conf_c2};font-size:12px'>[{_tl_conf2}]</span>{_rm_tag}",
                                            unsafe_allow_html=True,
                                        )

                        st.divider()
                        if st.button("换一个主题重新分析", key="btn_change_topic"):
                            st.session_state["selected_topic_idx"] = None
                            st.rerun()
                    else:
                        feedback_placeholder = st.empty()

                        if st.session_state.get(f"_generating_{report_key}"):
                            del st.session_state[f"_generating_{report_key}"]

                            progress_area = st.empty()
                            progress_bar = progress_area.progress(0, text="正在准备数据...")
                            try:
                                analyzer = get_analyzer()
                                generator = EvolutionReportGenerator(analyzer)
                                progress_bar.progress(0.5, text="正在调用 AI 生成报告，请稍候...")
                                report = generator.generate_report(topic, patches)
                                if report and not report.get("_error"):
                                    progress_bar.progress(1.0, text="完成！")
                                    import time; time.sleep(0.5)
                                    progress_area.empty()
                                    st.session_state[report_key] = report.get("_markdown", "")
                                    st.rerun()
                                else:
                                    progress_area.empty()
                                    error_msg = report.get("_message", "未知错误") if report else "未知错误"
                                    _show_report_error(error_msg)
                            except Exception as e:
                                progress_area.empty()
                                _show_report_error(str(e))
                        else:
                            st.info(
                                "生成演进报告将综合分析历代相关更新，内容较详细，"
                                "预计需等待 30-120 秒。如遇超时，请稍后重试，或切换到其他主题。"
                            )

                        if st.button("生成演进报告", type="primary", key="btn_gen_v2", width="stretch"):
                            st.session_state[f"_generating_{report_key}"] = True
                            st.rerun()



# ==================== 底部信息 ====================
render_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.divider()
st.markdown(f"""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    <p>多人对战游戏设计演进研究工具 | v1.8.0</p>
    <p>数据来源: 本地 data/ 目录（预采集）| PokeAPI | Bulbapedia | Smogon</p>
    <p style="font-size: 0.75rem; color: #aaa;">渲染时间: {render_time}</p>
</div>
""", unsafe_allow_html=True)

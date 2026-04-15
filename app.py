"""
宝可梦Like游戏多人机制设计演进研究工具
主应用入口 - Streamlit Web UI

使用方法:
1. 安装依赖: pip install -r requirements.txt
2. 配置环境变量: 在项目根目录创建 .env 文件，设置 OPENAI_API_KEY
3. 运行应用: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
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
from analyzer.intent_extractor import IntentExtractor
from analyzer.report_generator import EvolutionReportGenerator
from db.sqlite_store import SQLiteStore, db as global_db
from db.vector_store import VectorStore

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
    .tag-pvp { background-color: #ff6b6b; color: white; padding: 2px 8px; border-radius: 4px; }
    .tag-pve { background-color: #4ecdc4; color: white; padding: 2px 8px; border-radius: 4px; }
    .tag-mechanic { background-color: #45b7d1; color: white; padding: 2px 8px; border-radius: 4px; }
    .tag-balance { background-color: #96ceb4; color: white; padding: 2px 8px; border-radius: 4px; }
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
    .data-source-badge {
        background-color: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        color: #1565c0;
    }
    /* Tab 标签页按钮化样式 */
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
        (patches, features, stats) 元组
    """
    patches = []
    features = []
    fetch_stats = {"source": "live", "count": 0, "errors": []}

    # 非Steam游戏列表（Nintendo平台）
    non_steam_games = {"Pokemon"}

    # 从各数据源获取数据
    try:
        if game not in non_steam_games:
            # 从 Steam 获取更新日志
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
                        "official_notes": detail.get("official_notes", ""),  # 官方更新日志原文
                    })
            fetch_stats["source"] = "wiki"

    except Exception as e:
        fetch_stats["errors"].append(f"数据获取: {str(e)}")

    try:
        # 从 Wiki 获取机制信息
        wiki_scraper = get_wiki_scraper()
        mechanics = wiki_scraper.get_multiplayer_features(generation or 9)
        if mechanics:
            features.extend(mechanics)

    except Exception as e:
        fetch_stats["errors"].append(f"WIKI: {str(e)}")

    fetch_stats["total"] = len(patches)
    fetch_stats["count"] = len(patches)

    # 如果真实数据获取失败，使用空列表
    if not patches:
        fetch_stats["source"] = "no_data"
        patches = []
        features = []

    return patches, features, fetch_stats


# ==================== 侧边栏 ====================
with st.sidebar:
    st.header("配置")

    # 游戏选择
    selected_game = st.selectbox(
        "选择游戏",
        options=list(config.SUPPORTED_GAMES.keys()),
        format_func=lambda x: config.SUPPORTED_GAMES[x],
        index=0,
    )

    # 世代选择（仅宝可梦）
    generation = 9
    if selected_game == "Pokemon":
        generation = st.select_slider(
            "选择世代",
            options=[8, 9],
            value=9,
            format_func=lambda x: f"第{x}世代 ({config.POKEMON_GENERATIONS[x]['years']})",
        )

    # 数据刷新（仅清除 session 缓存，不重新抓取网络）
    st.subheader("数据源")
    st.info("更新日志已预采集到本地 data/ 目录，应用启动时直接读取，不访问网络。如需采集最新数据，请运行 `python fetch_all_data.py` 后重启应用。")
    if st.button("清除缓存", width="stretch"):
        st.cache_resource.clear()
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith("_cached_patches_")]
        for k in keys_to_delete:
            del st.session_state[k]
        st.rerun()

    # 显示数据源信息
    st.markdown('<p class="data-source-badge">本地静态数据</p>', unsafe_allow_html=True)
    st.caption("""
    - **本地 data/ 目录**: 已采集的更新日志 JSON（不访问网络）
    - **PokeAPI**: 宝可梦版本数据
    - **Bulbapedia**: Wiki 机制信息
    - 如需更新数据，运行 `python fetch_all_data.py`
    """)

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
st.markdown('<p class="sub-header">宝可梦Like游戏多人对战（PvP/PvE）设计迭代分析 | 本地静态数据</p>', unsafe_allow_html=True)

# 获取数据 - 优化：用 session_state 缓存，避免每次 rerun 都重新请求
# 缓存 key 包含游戏和世代，只有切换时才重新获取
cache_data_key = f"_cached_patches_{selected_game}_{generation}"
cache_time_key = f"_cached_patches_time_{selected_game}_{generation}"

if cache_data_key not in st.session_state:
    with st.spinner("正在从数据源获取信息..."):
        patches, features, fetch_stats = fetch_game_data(selected_game, generation)
    st.session_state[cache_data_key] = (patches, features, fetch_stats)
else:
    patches, features, fetch_stats = st.session_state[cache_data_key]

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "版本编年史",
    "机制时间轴",
    "设计意图分析",
    "演进报告",
    "版本对比",
])


# ==================== Tab 1: 版本编年史 ====================
with tab1:
    st.header("版本编年史")
    st.markdown("从 Steam News API 预采集的更新日志记录" if selected_game not in {"Pokemon"} else "基于 Wiki 结构化整理的版本更新记录")

    if not patches:
        if selected_game == "Pokemon":
            st.info("已加载结构化版本数据，可通过侧边栏筛选世代查看详细更新记录。")
        else:
            st.warning("""未能从数据源获取更新日志。

        可能原因:
        - 网络连接问题
        - Steam API 暂时不可用
        - 该游戏没有相关更新

        请稍后重试或检查网络连接。""")
    else:
        # 筛选控件
        col_filter1, col_filter2 = st.columns([3, 1])
        with col_filter1:
            search_term = st.text_input("搜索更新内容", placeholder="输入关键词搜索...")

        with col_filter2:
            all_categories = set()
            for p in patches:
                all_categories.update(p.get("categories", []))
            category_filter = st.multiselect(
                "筛选类别",
                options=sorted(list(all_categories)),
                default=sorted(list(all_categories))[:3] if all_categories else [],
            )

        # 筛选数据
        filtered_patches = patches

        if search_term:
            filtered_patches = [
                p for p in filtered_patches
                if search_term.lower() in p.get("title", "").lower()
                or search_term.lower() in p.get("content", "").lower()
            ]

        if category_filter:
            filtered_patches = [
                p for p in filtered_patches
                if any(cat in p.get("categories", []) for cat in category_filter)
            ]

        # ========== 缓存辅助函数 ==========
        import hashlib

        def get_content_hash(patch: dict) -> str:
            raw = f"{patch.get('content', '')}:{patch.get('title', '')}"
            return hashlib.md5(raw.encode("utf-8")).hexdigest()

        # 检查 LLM 是否可用
        extractor = get_analyzer()
        llm_ready = extractor is not None and extractor._get_llm() is not None

        # ========== 展示数据 ==========
        st.info(f"共 {len(filtered_patches)} 条更新记录")

        # 展开区域样式
        st.markdown("""
        <style>
        .patch-detail-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            background: #fafafa;
        }
        .patch-detail-header {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px dashed #ddd;
        }
        .patch-ai-section {
            border-radius: 8px;
            padding: 14px;
            margin: 12px 0;
        }
        .patch-ai-section h5 {
            color: #1f77b4;
            margin: 0 0 10px 0;
            font-size: 0.95rem;
        }
        .patch-meta-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin: 10px 0;
        }
        .patch-meta-item {
            background: white;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }
        .patch-meta-label {
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            margin-bottom: 2px;
        }
        .patch-meta-value {
            font-size: 0.9rem;
            color: #333;
            font-weight: 500;
        }
        .patch-full-content {
            background: white;
            padding: 14px;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            margin-top: 12px;
            line-height: 1.7;
            font-size: 0.9rem;
        }
        .patch-tag {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            margin: 2px;
        }
        .patch-tag-pvp { background: #ff6b6b; color: white; }
        .patch-tag-pve { background: #4ecdc4; color: white; }
        .patch-tag-mechanic { background: #45b7d1; color: white; }
        .patch-tag-balance { background: #96ceb4; color: white; }
        .patch-tag-other { background: #ddd; color: #666; }
        </style>
        """, unsafe_allow_html=True)

        for idx_patch, patch in enumerate(filtered_patches[:20]):
            # 从数据库读取已缓存的分析结果（如果有）
            ch = get_content_hash(patch)
            cached_cls = global_db.get_classification(selected_game, ch)
            cls = cached_cls

            # 从内容关键词实时判断是否和研究方向相关，不依赖缓存
            # 精确匹配：多人对战机制设计演进的6个研究方向
            raw = (patch.get("title", "") + patch.get("content", "")).lower()
            research_keywords = [
                # 集火/保排
                "集火", "保排", "保护", "守住", "看我嘛", "愤怒粉", "双击",
                "2v2", "双打", "单打",
                # 团体战
                "raid", "团体战", "极巨团体", "太晶团体", "集体", "多人",
                # 爆发资源机制
                "mega", "极巨化", "太晶化", "z招式", "z招",
                # 速度博弈
                "先制", "速度", "顺风", "高速", "优先度",
                # VGC/规则
                "vgc", "规则", "ban", "禁止", "分级", "赛季",
                "规则表", "pvp", "pve", "对战",
                # 平衡性（需配合具体对象）
                "削弱", "增强", " buff", "nerf",
            ]
            pvp_related = any(k in raw for k in research_keywords)

            highlight_border = "#ff6b6b" if pvp_related else "#1f77b4"
            highlight_bg = "#fff5f5" if pvp_related else "#ffffff"
            badge_icon = "[研究相关]" if pvp_related else "[更新]"

            # 实时推断分类类型，不依赖缓存
            type_val = ""
            if any(k in raw for k in ["raid", "团体战", "极巨团体", "太晶团体", "多人", "pve", "合作"]):
                type_val = "PvE"
            elif any(k in raw for k in ["vgc", "pvp", "对战", "双打", "单打", "规则", "ban", "赛季", "分级", "削弱", "增强", "极巨化", "太晶化", "mega", "z招"]):
                type_val = "PvP"
            if type_val:
                color = "#4ecdc4" if type_val == "PvE" else "#96ceb4"
                type_label = f'<span style="background:{color};color:white;padding:2px 8px;border-radius:8px;font-size:10px;margin-left:6px">{type_val}</span>'
            else:
                type_label = ""

            pvp_badge = '<span style="background:#ff6b6b;color:white;padding:2px 8px;border-radius:10px;font-size:11px;margin-left:6px">多人对战相关</span>' if pvp_related else ''

            content_preview = patch.get("content", "")
            content_line = f'<div style="font-size:0.82rem;color:#555;margin-top:6px;line-height:1.5">{content_preview[:100]}{"..." if len(content_preview) > 100 else ""}</div>' if content_preview else ""

            card_html_with_preview = (
                f'<div style="border-left: 4px solid {highlight_border}; background: {highlight_bg};'
                f'padding: 12px 16px; margin-bottom: 8px; border-radius: 4px;">'
                f'<div style="font-weight: 600; margin-bottom: 4px;">'
                f'{badge_icon} <b>{patch.get("date", "N/A")}</b> — {patch.get("title", "N/A")[:60]}{type_label}{pvp_badge}'
                f'</div>'
                f'<div style="font-size: 0.82rem; color: #666;">'
                f'版本: {patch.get("version", "N/A")}　类别: {" / ".join(patch.get("categories", [])[:3])}'
                f'</div>'
                f'{content_line}'
                f'</div>'
            )
            st.markdown(card_html_with_preview, unsafe_allow_html=True)

            with st.expander("查看详情", expanded=False):
                # 使用 session_state 管理每条更新的分析状态
                patch_key = f"patch_analysis_{get_content_hash(patch)}"
                if patch_key not in st.session_state:
                    st.session_state[patch_key] = None

                # 元信息行
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.markdown("**日期**: " + patch.get('date', 'N/A'))
                with col_m2:
                    st.markdown("**版本**: " + patch.get('version', 'N/A'))
                with col_m3:
                    categories = patch.get('categories', [])
                    if categories:
                        cat_tags = " ".join([f'<span class="patch-tag patch-tag-other">{c}</span>' for c in categories[:3]])
                        st.markdown(f"**类别**: {cat_tags}", unsafe_allow_html=True)

                # 完整更新内容
                content = patch.get("content", "")
                detail_content = patch.get("detail", "")
                if content:
                    st.markdown("**更新摘要**:")
                    st.markdown(f'<div class="patch-full-content">{content}</div>', unsafe_allow_html=True)

                # 详细改动（如果有）
                if detail_content:
                    st.markdown("**详细改动**:")
                    st.markdown(f'<div style="background:#fffef0;padding:12px;border-radius:6px;border-left:3px solid #f0ad4e;margin:10px 0;font-size:0.9rem;line-height:1.7">{detail_content}</div>', unsafe_allow_html=True)

                # 详细背景信息
                full_context = patch.get("full_context", "")
                impact = patch.get("impact", "")
                vgc_relevance = patch.get("vgc_relevance", "")
                balance_changes = patch.get("balance_changes", {})

                if full_context or impact or vgc_relevance or balance_changes:
                    st.markdown("#### 详细背景")
                    with st.expander("点击展开详细背景信息"):
                        if full_context:
                            st.markdown("**背景说明**:")
                            st.markdown(f'<div style="background:#f8f9fa;padding:12px;border-radius:6px;margin:6px 0;font-size:0.88rem;line-height:1.7">{full_context}</div>', unsafe_allow_html=True)

                        if balance_changes:
                            st.markdown("**数值改动详情**:")
                            for name, changes in balance_changes.items():
                                change_str = ", ".join([f"{k}: {v}" for k, v in changes.items()])
                                st.markdown(f"- **{name}**: {change_str}")

                        if impact:
                            st.markdown("**影响分析**:")
                            st.markdown(f'<div style="background:#e8f4fd;padding:10px;border-radius:6px;margin:6px 0;font-size:0.88rem">{impact}</div>', unsafe_allow_html=True)

                        if vgc_relevance:
                            st.markdown("**VGC相关说明**:")
                            st.markdown(f'<div style="background:#f0f8ff;padding:10px;border-radius:6px;margin:6px 0;font-size:0.88rem">{vgc_relevance}</div>', unsafe_allow_html=True)

                # 官方更新日志原文（内嵌显示）
                official_notes = patch.get("official_notes", "")
                if official_notes:
                    st.markdown("#### 官方更新日志原文")
                    st.markdown(f"""
                    <div style="background:#1a1a2e;color:#eee;font-family:monospace;padding:16px;border-radius:8px;margin:10px 0;max-height:400px;overflow-y:auto;font-size:0.85rem;line-height:1.6">
                    {official_notes.replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)

                # 设计意图
                if patch.get("intent"):
                    st.markdown("**设计意图**:")
                    st.info(patch.get("intent"))


                # =============================================
                # 检查是否已有分析结果
                # 优先级：session_state（新分析） > DB缓存（可能旧格式）
                if st.session_state.get(f"show_reanalysis_result_{patch_key}"):
                    st.session_state[f"show_reanalysis_result_{patch_key}"] = False
                    existing_analysis = st.session_state.get(patch_key)
                    result_source = "新分析"
                elif st.session_state.get(patch_key):
                    existing_analysis = st.session_state.get(patch_key)
                    result_source = "新分析"
                elif cls:
                    existing_analysis = cls
                    has_new_fields = bool(cls.get("research_direction") or cls.get("mechanic_tags"))
                    result_source = "旧缓存" if not has_new_fields else "DB缓存"
                else:
                    existing_analysis = None
                    result_source = ""
                analysis_result = existing_analysis

                # AI 分析区域
                st.markdown("---")

                # 重新分析优先处理（放在外面，不受 if/else 影响）
                if st.session_state.get(f"reanalysis_triggered_{patch_key}"):
                    st.session_state[f"reanalysis_triggered_{patch_key}"] = False
                    with st.spinner("AI 正在分析中（需等待10-30秒），请稍候..."):
                        try:
                            extractor = get_analyzer()
                            result = extractor.analyze_intent(
                                game=selected_game,
                                version=patch.get("version", ""),
                                date=patch.get("date", ""),
                                content=patch.get("title", "") + "\n\n" + patch.get("content", ""),
                            )
                            if result:
                                st.session_state[patch_key] = result
                                ch = get_content_hash(patch)
                                global_db.add_classification(
                                    game=selected_game,
                                    content_hash=ch,
                                    content_preview=patch.get("content", "")[:200] if patch.get("content") else patch.get("title", "")[:200],
                                    patch_date=patch.get("date", ""),
                                    patch_title=patch.get("title", ""),
                                    classification_type="混合",
                                    mechanics=result.get("mechanic_tags", []),
                                    balance_impact="中",
                                    summary=result.get("competitive_impact", result.get("exact_change", ""))[:500],
                                    is_multiplayer_related=any(t in result.get("mechanic_tags", []) for t in ["PvP", "PvE", "2v2"]),
                                )
                                st.session_state[f"show_reanalysis_result_{patch_key}"] = True
                                st.rerun()
                            else:
                                st.error("分析未能返回结果，请稍后重试")
                        except Exception as e:
                            st.error("分析失败: " + str(e))

                if analysis_result and (
                    analysis_result.get("exact_change")
                    or analysis_result.get("competitive_impact")
                    or analysis_result.get("design_rationale")
                    or analysis_result.get("research_direction")
                    or analysis_result.get("intent_summary")
                    or analysis_result.get("summary")
                ):
                    # 已有分析结果，展示详细卡片
                    ai_border = "#ff6b6b" if pvp_related else "#1f77b4"
                    ai_bg = "#fff5f5" if pvp_related else "#f0f7ff"
                    pvp_badge_ai = '<span style="background:#ff6b6b;color:white;padding:2px 8px;border-radius:10px;font-size:11px;margin-left:8px">多人对战相关</span>' if pvp_related else ""
                    result_color = "#52c41a" if "新" in result_source else "#888"
                    source_tag = '<span style="background:' + result_color + ';color:white;padding:1px 6px;border-radius:6px;font-size:10px;margin-left:8px">' + result_source + '</span>' if result_source else ""

                    st.markdown('<div style="background:linear-gradient(135deg,' + ai_bg + ' 0%,#e8f4fd 100%);border-left:4px solid ' + ai_border + ';border-radius:8px;padding:14px;margin:12px 0;">', unsafe_allow_html=True)
                    st.markdown('<div style="font-size:1rem;font-weight:700;margin-bottom:10px">AI 分析结果' + pvp_badge_ai + source_tag + '</div>', unsafe_allow_html=True)

                    exact = analysis_result.get("exact_change", "")
                    if exact:
                        st.markdown("**具体改动**: " + exact)

                    impact = analysis_result.get("competitive_impact", analysis_result.get("intent_summary", ""))
                    if impact:
                        st.markdown("**竞技影响**: " + impact)

                    rationale = analysis_result.get("design_rationale", analysis_result.get("problem_solved", ""))
                    if rationale:
                        st.markdown("**设计理由**: " + rationale)

                    direction = analysis_result.get("research_direction", "")
                    if direction:
                        st.markdown("**研究方向**: " + direction)

                    mechanics = analysis_result.get("mechanic_tags", analysis_result.get("mechanics", []))
                    if mechanics:
                        mech_list = mechanics if isinstance(mechanics, list) else [mechanics]
                        st.markdown("**涉及机制**: " + " ".join(['<span class="patch-tag patch-tag-mechanic">' + m + '</span>' for m in mech_list[:6]]), unsafe_allow_html=True)

                    players = analysis_result.get("player_impact", analysis_result.get("affected_players", ""))
                    if players:
                        if isinstance(players, list):
                            players = "、".join(players)
                        st.markdown("**受影响玩家**: " + players)

                    balance = analysis_result.get("balance_assessment", analysis_result.get("design_pattern", ""))
                    if balance:
                        st.markdown("**平衡评估**: " + balance)

                    similar = analysis_result.get("similar_historical_cases", [])
                    if similar and isinstance(similar, list):
                        st.markdown("**历史参照**:")
                        for r in similar[:3]:
                            if isinstance(r, dict):
                                st.markdown("- " + str(r.get("description", r)))
                            else:
                                st.markdown("- " + str(r))

                    st.markdown('</div>', unsafe_allow_html=True)

                    if st.button("重新分析", key="reanalysis_" + patch_key):
                        st.session_state["reanalysis_triggered_" + patch_key] = True
                        st.rerun()

                else:
                    # 没有分析结果，显示分析按钮
                    st.markdown('<div style="font-size:1rem;font-weight:700;margin-bottom:4px">AI 分析</div>', unsafe_allow_html=True)

                    if llm_ready:
                        if st.button("深度分析", type="primary", key="analyze_" + patch_key):
                            with st.spinner("AI 正在分析中（需等待10-30秒），请稍候..."):
                                try:
                                    extractor = get_analyzer()
                                    result = extractor.analyze_intent(
                                        game=selected_game,
                                        version=patch.get("version", ""),
                                        date=patch.get("date", ""),
                                        content=patch.get("title", "") + "\n\n" + patch.get("content", ""),
                                    )
                                    if result:
                                        st.session_state[patch_key] = result
                                        ch = get_content_hash(patch)
                                        global_db.add_classification(
                                            game=selected_game,
                                            content_hash=ch,
                                            content_preview=patch.get("content", "")[:200] if patch.get("content") else patch.get("title", "")[:200],
                                            patch_date=patch.get("date", ""),
                                            patch_title=patch.get("title", ""),
                                            classification_type="混合",
                                            mechanics=result.get("mechanic_tags", []),
                                            balance_impact="中",
                                            summary=result.get("competitive_impact", result.get("exact_change", ""))[:500],
                                            is_multiplayer_related=any(t in result.get("mechanic_tags", []) for t in ["PvP", "PvE", "2v2"]),
                                        )
                                        st.rerun()
                                    else:
                                        st.warning("分析未能返回结果，请稍后重试")
                                except Exception as e:
                                    st.error("分析失败: " + str(e))
                    else:
                        st.warning("请先在侧边栏配置 LLM API Key 以启用 AI 分析")
                st.markdown(f"[查看官方原文]({patch.get('url')})")


# ==================== Tab 2: 机制时间轴 ====================
with tab2:
    st.header("机制时间轴")
    st.markdown("可视化展示历代多人对战机制的演进过程")

    # 从 PokeAPI 获取版本信息构建时间轴
    timeline_data = []

    if selected_game == "Pokemon":
        try:
            api_scraper = get_api_scraper()
            version_groups = api_scraper.get_version_changelog(generation)

            for vg in version_groups:
                timeline_data.append({
                    "generation": vg.get("generation", generation),
                    "year": 2019 + (vg.get("generation", generation) - 8),  # 粗略估算
                    "mechanism": vg.get("version", vg.get("version_group", "")),
                    "description": f"版本组: {vg.get('version_group', '')}",
                    "type": "版本",
                })
        except Exception as e:
            st.warning(f"无法从 PokeAPI 获取版本数据: {e}")

    # 机制演进数据（基于真实游戏历史）
    mechanism_evolution = [
        # PvP 机制演进
        {"generation": 6, "year": 2013, "mechanism": "Mega进化", "description": "特定宝可梦可进化为更强形态", "type": "机制"},
        {"generation": 7, "year": 2016, "mechanism": "Z招式", "description": "取代Mega进化的强化系统", "type": "机制"},
        {"generation": 8, "year": 2019, "mechanism": "极巨化", "description": "可让宝可梦巨大化并获得强力招式", "type": "机制"},
        {"generation": 8, "year": 2020, "mechanism": "极巨团体战", "description": "4人合作挑战野生极巨化宝可梦", "type": "PvE"},
        {"generation": 9, "year": 2022, "mechanism": "太晶化", "description": "任何宝可梦都可附着太晶宝石", "type": "机制"},
        {"generation": 9, "year": 2022, "mechanism": "太晶团体战", "description": "半即时制4人合作战斗", "type": "PvE"},
    ]

    # 游戏选择
    game_filter = st.multiselect(
        "选择展示的游戏",
        options=["Pokemon", "Temtem", "Cassette Beasts", "Palworld"],
        default=["Pokemon"],
    )

    # 添加所选游戏的数据
    display_data = []
    if "Pokemon" in game_filter:
        display_data.extend(mechanism_evolution)

    # Temtem 机制
    if "Temtem" in game_filter:
        temtem_data = [
            {"generation": 1, "year": 2020, "mechanism": "2v2核心对战", "description": "游戏核心就是2v2竞技", "type": "PvP"},
            {"generation": 1, "year": 2022, "mechanism": "Ban/Pick系统", "description": "引入电竞化Ban/Pick机制", "type": "PvP"},
        ]
        display_data.extend(temtem_data)

    # Cassette Beasts 机制
    if "Cassette Beasts" in game_filter:
        cb_data = [
            {"generation": 1, "year": 2022, "mechanism": "融合系统", "description": "两只妖怪可融合成更强形态", "type": "机制"},
            {"generation": 1, "year": 2022, "mechanism": "本地双人合作", "description": "支持本地双人合作游玩", "type": "PvE"},
        ]
        display_data.extend(cb_data)

    # Palworld 机制
    if "Palworld" in game_filter:
        pw_data = [
            {"generation": 1, "year": 2024, "mechanism": "多人Raid", "description": "多人合作挑战Boss", "type": "PvE"},
            {"generation": 1, "year": 2024, "mechanism": "帕鲁捕捉", "description": "捕捉并培养帕鲁参与战斗", "type": "机制"},
        ]
        display_data.extend(pw_data)

    if display_data:
        # 创建 DataFrame
        df_timeline = pd.DataFrame(display_data)

        # 颜色映射
        color_map = {
            "PvP": "#ff6b6b",
            "PvE": "#4ecdc4",
            "机制": "#45b7d1",
            "版本": "#96ceb4",
        }

        # 创建时间轴
        fig = px.scatter(
            df_timeline,
            x="year",
            y="generation",
            color="type",
            size=[10] * len(df_timeline),
            hover_name="mechanism",
            hover_data={"description": True, "year": True},
            color_discrete_map=color_map,
            labels={"type": "类型", "generation": "世代"},
        )

        # 添加文字标注
        for idx, row in df_timeline.iterrows():
            desc = row["description"]
            if len(desc) > 20:
                desc = desc[:20] + "..."
            fig.add_annotation(
                x=row["year"],
                y=row["generation"],
                text=f"{row['mechanism']}<br><span style='font-size:11px;color:#555'>{desc}</span>",
                showarrow=False,
                font=dict(size=13),
                yanchor="bottom" if idx % 2 == 0 else "top",
            )

        fig.update_layout(
            title="多人对战机制演进时间轴",
            height=500,
            xaxis_title="年份",
            yaxis_title="世代/版本",
            showlegend=True,
            legend_title="机制类型",
            font=dict(size=13),
        )

        fig.update_yaxes(autorange="reversed")

        st.plotly_chart(fig, width="stretch", key="timeline_chart")
    else:
        st.info("请选择至少一个游戏来显示时间轴")

    # 防御机制演进详情
    st.divider()
    st.subheader("防御/保护机制演进对比")

    comparison_data = {
        "特性": ["保护机制", "持续时间", "使用限制", "多人适用"],
        "守住 (Protect)": ["完全抵挡攻击", "单回合", "可连续使用", "是"],
        "看我嘛 (Follow Me)": ["吸引对方攻击", "持续至切换", "受威吓影响", "2v2核心"],
        "极巨防壁": ["极巨化中自动保护", "极巨化期间", "仅极巨化中", "团体战"],
        "太晶化": ["属性改变+招式", "1回合", "任意宝可梦", "PvP/PvE"],
    }

    df_defense = pd.DataFrame(comparison_data)
    st.dataframe(df_defense, width="stretch", hide_index=True)


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
        )

        if analysis_mode == "分析已有数据":
            # 显示可分析的数据预览
            st.subheader("待分析更新列表")

            analysis_options = []
            for i, patch in enumerate(patches[:10]):
                label = f"{patch.get('date', 'N/A')} - {patch.get('title', 'N/A')[:40]}..."
                analysis_options.append((i, label))

            selected_indices = st.multiselect(
                "选择要分析的更新",
                options=[opt[0] for opt in analysis_options],
                format_func=lambda x: next((opt[1] for opt in analysis_options if opt[0] == x), ""),
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
                        st.markdown(f"**平衡评估**: {result.get('balance_assessment', result.get('design_pattern', 'N/A'))}")
                        similar = result.get("similar_historical_cases", [])
                        if similar:
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
            )

            if query:
                analyzer = get_analyzer()
                try:
                    vector_store = VectorStore()
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
    st.markdown("AI 自动扫描当前所有更新，归纳出值得研究的设计主题，选择后生成历代演进分析。")

    if not patches:
        st.warning("当前没有可用数据。请先在「版本编年史」中选择游戏和世代加载数据。")
    else:
        cache_key = f"topic_discovery_v2_{selected_game}_{generation}"

        if cache_key not in st.session_state:
            st.session_state[cache_key] = None

        if st.session_state[cache_key] is None:
            try:
                analyzer = get_analyzer()
                from analyzer.ai_topic_discoverer import AITopicDiscoverer
                discoverer = AITopicDiscoverer(analyzer)
                with st.spinner("AI 正在分析所有更新，发现设计主题（需等待 10-30 秒）..."):
                    result = discoverer.discover(patches)
                st.session_state[cache_key] = result
            except Exception:
                import traceback
                st.session_state[cache_key] = {
                    "success": False,
                    "discovered_topics": [],
                    "error": "发现过程异常",
                    "traceback": traceback.format_exc(),
                    "total_analyzed": len(patches),
                }
            st.rerun()
        else:
            result = st.session_state[cache_key]

        # 步骤指示器
        topics = result.get("discovered_topics", []) if result["success"] else []
        has_topics = bool(topics)
        selected_idx = st.session_state.get("selected_topic_idx")
        has_selection = selected_idx is not None and selected_idx < len(topics)
        report_key = f"report_v2_{selected_idx}_{selected_game}_{generation}"
        has_report = st.session_state.get(report_key)

        step1_state = "done" if has_topics else ("active" if result["success"] else "waiting")
        step2_state = "done" if has_selection else "waiting"
        step3_state = "done" if has_report else "waiting"

        col_s1, col_s2, col_s3 = st.columns([1, 1, 2])
        with col_s1:
            _render_step(1, "AI 发现主题", step1_state)
        with col_s2:
            _render_step(2, "选择主题", step2_state)
        with col_s3:
            _render_step(3, "生成报告", step3_state)

        st.divider()

        if not result["success"]:
            st.error(f"主题发现失败：{result.get('error', '未知错误')}")
            if st.button("重新尝试"):
                del st.session_state[cache_key]
                st.rerun()
        elif not topics:
            st.info("AI 分析完成，但没有发现足够支撑研究主题的数据。可以尝试切换到 Pokemon Gen9 或其他数据更丰富的游戏/世代。")
        else:
            # Step 1 完成：显示统计 + 重试入口
            col_stat, col_redo = st.columns([4, 1])
            with col_stat:
                st.success(f"AI 分析了 {result['total_analyzed']} 条更新，归纳出 {len(topics)} 个设计主题")
            with col_redo:
                if st.button("重新发现", help="清空缓存，重新调用 AI 分析"):
                    del st.session_state[cache_key]
                    st.rerun()

            # Step 2：主题选择
            st.markdown("**选择研究主题**")

            for idx, topic in enumerate(topics):
                count = len(topic.get("matched_preview", []))
                is_sel = (selected_idx == idx)
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

            # Step 3：选中后生成报告
            if has_selection:
                idx = selected_idx
                topic = topics[idx]
                st.divider()
                st.markdown(f"### {topic.get('name', '')}")
                st.caption(topic.get("description", ""))

                if topic.get("matched_preview"):
                    with st.expander("查看相关更新列表"):
                        for p in topic["matched_preview"]:
                            st.markdown(f"- {p}")

                if has_report:
                    # 已生成报告：展示内容
                    report = st.session_state[report_key]
                    st.divider()

                    # 直接渲染 Markdown 格式的报告（新的深度报告格式）
                    if isinstance(report, str):
                        st.markdown(report)
                    elif isinstance(report, dict) and report.get("_markdown"):
                        st.markdown(report["_markdown"])
                    elif isinstance(report, dict):
                        # 兼容旧的 JSON 格式报告
                        def _report_section(title, content):
                            st.markdown(f"""
                            <div class="tab4-report-section">
                                <h4>{title}</h4>
                                <div class="tab4-report-field">
                                    <p>{content}</p>
                                </div>
                            </div>""", unsafe_allow_html=True)

                        if report.get("evolution_summary"):
                            _report_section("演进总览", report["evolution_summary"])

                        if report.get("generation_analysis"):
                            st.markdown('<div class="tab4-report-section"><h4>历代解决方案</h4></div>', unsafe_allow_html=True)
                            for stage in report["generation_analysis"]:
                                label = stage.get("period", "")
                                st.markdown(f"**{label}**")
                                for k, v in [(k, v) for k, v in stage.items() if k != "period"]:
                                    st.markdown(f"- **{k}**: {v}")
                                st.divider()

                        for key in ["key_insight", "key_insights"]:
                            if key in report:
                                val = report[key]
                                _report_section(
                                    "关键设计洞察",
                                    val if isinstance(val, str) else "<br>".join(f"- {v}" for v in val)
                                )
                                break

                        if report.get("design_principle"):
                            _report_section("可复用的设计原则", report["design_principle"])

                        for k in ["unresolved_problems", "still_unsolved"]:
                            if k in report:
                                _report_section("仍未解决的问题", report[k])
                                break

                    st.divider()
                    if st.button("换一个主题重新分析", key="btn_change_topic"):
                        st.session_state["selected_topic_idx"] = None
                        st.rerun()
                else:
                    # 未生成报告：使用 EvolutionReportGenerator 生成
                    st.divider()

                    # 即时反馈：用 placeholder 在点击时立即显示提示
                    feedback_placeholder = st.empty()

                    # 检查是否刚触发了生成
                    if st.session_state.get(f"_generating_{report_key}"):
                        # 立即显示提示，不需要等 spinner
                        feedback_placeholder.info("正在调用 AI 生成演进报告（内容较丰富，请耐心等待）...")
                        # 清理触发标记，进入生成流程
                        del st.session_state[f"_generating_{report_key}"]

                        with st.spinner("正在调用 AI 生成演进报告（内容较丰富，请耐心等待）..."):
                            try:
                                analyzer = get_analyzer()
                                generator = EvolutionReportGenerator(analyzer)
                                report = generator.generate_report(topic, patches)

                                if report and not report.get("_error"):
                                    st.session_state[report_key] = report.get("_markdown", "")
                                    st.rerun()
                                else:
                                    error_msg = report.get("_message", "生成失败") if report else "未知错误"
                                    feedback_placeholder.error(f"报告生成失败: {error_msg}")
                            except Exception as e:
                                feedback_placeholder.error(f"报告生成失败: {str(e)}")
                    else:
                        feedback_placeholder.info("生成演进报告将综合分析历代相关更新，内容较详细，预计需等待 30-120 秒。如遇超时，请稍后重试。")

                    if st.button("生成演进报告", type="primary", key="btn_gen_v2", width="stretch"):
                        # 立即设置触发标记，触发 rerun
                        st.session_state[f"_generating_{report_key}"] = True
                        st.rerun()


# ==================== Tab 5: 版本对比 ====================
with tab5:
    st.header("版本对比")
    st.markdown("选择不同版本或不同游戏进行设计对比分析")

    # 版本/游戏选择
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("### 版本/游戏 1")
        game1 = st.selectbox(
            "游戏",
            options=list(config.SUPPORTED_GAMES.keys()),
            format_func=lambda x: config.SUPPORTED_GAMES[x],
            key="game1",
        )
        # 获取该游戏的版本列表
        try:
            scraper1 = get_steam_scraper(game1)
            news1 = scraper1.get_news(count=20)
            version_options1 = [(n.get("gid", ""), f"{n.get('date', '')} - {n.get('title', '')[:30]}") for n in news1]
            version1 = st.selectbox(
                "版本",
                options=[v[0] for v in version_options1],
                format_func=lambda x: next((v[1] for v in version_options1 if v[0] == x), ""),
                key="version1",
            )
        except Exception as e:
            st.warning(f"无法获取 {game1} 数据")
            version1 = None

    with col_v2:
        st.markdown("### 版本/游戏 2")
        game2 = st.selectbox(
            "游戏",
            options=list(config.SUPPORTED_GAMES.keys()),
            format_func=lambda x: config.SUPPORTED_GAMES[x],
            key="game2",
        )
        try:
            scraper2 = get_steam_scraper(game2)
            news2 = scraper2.get_news(count=20)
            version_options2 = [(n.get("gid", ""), f"{n.get('date', '')} - {n.get('title', '')[:30]}") for n in news2]
            version2 = st.selectbox(
                "版本",
                options=[v[0] for v in version_options2],
                format_func=lambda x: next((v[1] for v in version_options2 if v[0] == x), ""),
                key="version2",
            )
        except Exception as e:
            st.warning(f"无法获取 {game2} 数据")
            version2 = None

    # 显示对比
    if version1 and version2:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            news_item1 = next((n for n in news1 if n.get("gid") == version1), None)
            if news_item1:
                st.markdown(f"### {game1}")
                st.markdown(f"**日期**: {news_item1.get('date', 'N/A')}")
                st.markdown(f"**标题**: {news_item1.get('title', 'N/A')}")
                st.markdown(f"**内容预览**:")
                st.markdown(news_item1.get("contents", "")[:300])

        with col_c2:
            news_item2 = next((n for n in news2 if n.get("gid") == version2), None)
            if news_item2:
                st.markdown(f"### {game2}")
                st.markdown(f"**日期**: {news_item2.get('date', 'N/A')}")
                st.markdown(f"**标题**: {news_item2.get('title', 'N/A')}")
                st.markdown(f"**内容预览**:")
                st.markdown(news_item2.get("contents", "")[:300])

    st.divider()

    # 机制对比表
    st.subheader("多人机制设计对比")

    comparison_table = {
        "维度": ["核心模式", "PvP赛制", "PvE合作", "Ban/Pick", "强化系统"],
        "Pokemon VGC": ["回合制双打", "VGC官方赛", "团体战", "无", "极巨化/太晶化"],
        "Temtem": ["回合制双打", "2v2竞技", "讨伐战", "有", "无（通过道具）"],
        "Cassette Beasts": ["回合制融合", "本地合作", "融合狩猎", "无", "融合进化"],
        "Palworld": ["动作+回合", "PVP对战", "Raid Boss", "无", "帕鲁装备"],
    }

    df_comparison = pd.DataFrame(comparison_table)
    st.dataframe(df_comparison, width="stretch", hide_index=True)


# ==================== 底部信息 ====================
st.divider()
st.markdown(f"""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    <p>宝可梦Like游戏多人机制设计演进研究工具 | v1.5.0 动态主题发现版</p>
    <p>数据来源: 本地 data/ 目录（预采集）| PokeAPI | Bulbapedia | Smogon</p>
</div>
""", unsafe_allow_html=True)

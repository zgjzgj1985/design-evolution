"""
多人对战游戏设计演进研究工具
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
/* ═══════════════════════════════════════════════════════════
   DESIGN LANGUAGE v6 — 简洁·克制·高级
   核心原则：信息密度优先，视觉噪音归零
═══════════════════════════════════════════════════════════ */

/* ── 全局重置与基础 ── */
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stAppViewContainer"] { background: #fafafa; }

/* ── 主标题区 ── */
.app-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a1a2e;
    letter-spacing: -0.02em;
    margin-bottom: 0.15rem;
}
.app-subtitle {
    font-size: 0.8rem;
    color: #9ca3af;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

/* ── 统计数字行 ── */
.stat-row {
    display: flex;
    gap: 2rem;
    align-items: baseline;
    padding: 0.6rem 0;
    border-bottom: 1px solid #f0f0f0;
    flex-wrap: wrap;
}
.stat-item { display: flex; flex-direction: column; gap: 1px; }
.stat-n { font-size: 1.3rem; font-weight: 700; color: #1a1a2e; line-height: 1; }
.stat-l { font-size: 0.72rem; color: #9ca3af; letter-spacing: 0.04em; }
.stat-sep { width: 1px; height: 28px; background: #e5e7eb; align-self: center; margin: 0 0.5rem; }

/* ── Patch 卡片（列表项）────────────── */
.patch-card {
    border: 1px solid #eeeeee;
    border-left: 3px solid #d1d5db;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    background: #ffffff;
    transition: border-color 0.12s, box-shadow 0.12s;
}
.patch-card:hover {
    border-color: #c0c8d4;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.patch-card.pvp { border-left-color: #6b7280; }

.patch-card-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 0.2rem;
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.patch-date { font-size: 0.72rem; color: #9ca3af; font-weight: 400; font-family: monospace; flex-shrink: 0; }
.patch-meta { font-size: 0.72rem; color: #9ca3af; margin-bottom: 0.25rem; }
.patch-preview { font-size: 0.78rem; color: #6b7280; line-height: 1.5; }

/* 减少 Badge：最多 1 个，仅 PvP 相关时显示 */
.badge-pvp {
    font-size: 0.65rem;
    font-weight: 600;
    padding: 1px 6px;
    border-radius: 3px;
    background: #f3f4f6;
    color: #6b7280;
    border: 1px solid #e5e7eb;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

/* ── 详情展开区 ── */
.detail-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    padding: 0.75rem 0;
    border-top: 1px solid #f0f0f0;
    margin-top: 0.5rem;
}
.detail-item { display: flex; flex-direction: column; gap: 2px; }
.detail-label { font-size: 0.68rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; }
.detail-value { font-size: 0.82rem; color: #374151; }

/* 官方日志原文 */
.official-notes {
    background: #f9f9f9;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    font-size: 0.82rem;
    color: #374151;
    line-height: 1.7;
    max-height: 320px;
    overflow-y: auto;
    border: 1px solid #eeeeee;
    margin: 0.5rem 0;
}

/* 详细改动（黄色高亮区） */
.detail-changes {
    background: #fefce8;
    padding: 0.6rem 0.8rem;
    border-radius: 4px;
    font-size: 0.82rem;
    line-height: 1.7;
    color: #374151;
    border-left: 2px solid #fde047;
    margin: 0.5rem 0;
}

/* ── AI 分析结果卡片 ── */
.ai-card {
    border: 1px solid #eeeeee;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    background: #fafafa;
}
.ai-card.pvp { border-left: 3px solid #9ca3af; }
.ai-card-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9ca3af;
    margin-bottom: 0.5rem;
}

/* 洞察盒子 */
.insight-box {
    background: #ffffff;
    border: 1px solid #eeeeee;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #4b5563;
    line-height: 1.6;
    margin: 0.75rem 0;
}

/* ── 演进报告步骤指示器 ── */
.step-bar {
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 0.5rem;
}
.step-pill {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 20px;
    letter-spacing: 0.02em;
    white-space: nowrap;
}
.step-pill.done { background: #1a1a2e; color: #ffffff; }
.step-pill.active { background: #e5e7eb; color: #1a1a2e; border: 1px solid #d1d5db; }
.step-pill.waiting { background: transparent; color: #d1d5db; }
.step-connector {
    flex: 1;
    height: 1px;
    background: #e5e7eb;
    margin: 0 4px;
    min-width: 20px;
}

/* ── 维度折叠卡（演进报告）── */
.dim-card {
    border: 1px solid #eeeeee;
    border-radius: 6px;
    margin-bottom: 0.75rem;
    overflow: hidden;
    background: #ffffff;
    transition: border-color 0.12s;
}
.dim-card:hover { border-color: #d1d5db; }
.dim-card.selected { border-color: #1a1a2e; }
.dim-header {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: #1a1a2e;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #fafafa;
    border-bottom: 1px solid #eeeeee;
}
.dim-header:hover { background: #f5f5f5; }
.dim-count { font-size: 0.72rem; color: #9ca3af; font-weight: 400; }
.dim-body { padding: 0.75rem 1rem; }

/* ── 演进枝列表项 ── */
.branch-item {
    padding: 0.6rem 0;
    border-bottom: 1px solid #f5f5f5;
}
.branch-item:last-child { border-bottom: none; }
.branch-problem { font-size: 0.875rem; font-weight: 600; color: #1a1a2e; margin-bottom: 0.15rem; }
.branch-meta { font-size: 0.72rem; color: #9ca3af; display: flex; gap: 0.5rem; flex-wrap: wrap; }
.branch-insight { font-size: 0.78rem; color: #6b7280; margin-top: 0.2rem; font-style: italic; }

/* ── 时间轴页面 ── */
.tl-section-title {
    font-size: 0.875rem;
    font-weight: 700;
    color: #1a1a2e;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eeeeee;
    margin: 1.5rem 0 1rem;
    letter-spacing: -0.01em;
}

/* ── Tab 标签页样式 ── */
[data-testid="stTabList"] {
    gap: 2px;
    background: transparent;
    padding: 0 0 1px 0;
    border-bottom: 1px solid #eeeeee;
    border-radius: 0;
}
[data-testid="stTab"] {
    border: none;
    border-radius: 0;
    padding: 6px 16px;
    font-size: 0.82rem;
    font-weight: 500;
    color: #9ca3af;
    background: transparent;
    border-bottom: 2px solid transparent;
    transition: all 0.15s;
    margin-bottom: -1px;
}
[data-testid="stTab"]:hover { color: #374151; background: transparent; }
[data-testid="stTab"][aria-selected="true"] {
    background: transparent;
    color: #1a1a2e;
    border-bottom-color: #1a1a2e;
    font-weight: 700;
}

/* ── Streamlit 原生元素微调 ── */
[data-testid="stExpander"] { border: 1px solid #eeeeee !important; border-radius: 4px !important; }
[data-testid="stExpander"]:hover { border-color: #d1d5db !important; }
.stButton>button { border-radius: 4px !important; font-size: 0.82rem !important; }
.stButton>button.primary { font-weight: 600; }
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stSelectbox"] > div > div > div,
div[data-testid="stMultiselect"] > div > div > div { border-radius: 4px !important; font-size: 0.82rem !important; }
[data-testid="stMetricValue"] { font-size: 1.1rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: #9ca3af !important; }

/* ── 侧边栏 ── */
section[data-testid="stSidebar"] {
    background: #fafafa;
    border-right: 1px solid #eeeeee;
}
.sidebar-section-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #d1d5db;
    padding: 0.75rem 1rem 0.25rem;
}
.sidebar-caption { font-size: 0.75rem; color: #9ca3af; line-height: 1.5; }

/* ── 数据表格 ── */
[data-testid="stDataFrame"] table { font-size: 0.82rem !important; }
[data-testid="stDataFrame"] thead th { font-size: 0.72rem !important; color: #9ca3af !important; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── 进度条 ── */
.stProgress > div > div > div { background: #e5e7eb !important; }
.stProgress > div > div > div > div { background: #1a1a2e !important; }

/* ── Divider ── */
hr { border-color: #eeeeee !important; }
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
    st.markdown('<p class="sidebar-section-label" style="padding-top:0;">配置</p>', unsafe_allow_html=True)

    # 游戏选择
    selected_game = st.selectbox(
        "选择游戏",
        options=list(config.SUPPORTED_GAMES.keys()),
        format_func=lambda x: config.SUPPORTED_GAMES[x],
        index=0,
    )

    # 游戏数据量展示
    import json as _json
    from pathlib import Path as _Path

    def _get_game_data_count(game_name: str) -> tuple:
        """返回 (总记录数, 多人相关数, 最新日期)"""
        if game_name == "Pokemon":
            # Pokemon 数据来自内置，直接用当前已加载的 patches
            return None, None, None
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
    st.markdown('<p class="sidebar-section-label">数据源</p>', unsafe_allow_html=True)
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
    st.markdown('<p class="sidebar-section-label">数据概览</p>', unsafe_allow_html=True)

    _GAME_SOURCE_INFO = {
        "Pokemon": {"source": "Serebii.net + 内置数据", "type": "结构化内置"},
        "Temtem": {"source": "Steam News API（预采集）", "type": "JSON 静态文件"},
        "Palworld": {"source": "Steam News API（预采集）", "type": "JSON 静态文件"},
        "Cassette Beasts": {"source": "Steam（无公开公告）", "type": "数据暂缺"},
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

    # LLM 连接状态（简洁行内显示）
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
        st.caption("AI 分析: **已就绪**")
    elif _has_key:
        st.caption("AI 分析: 连接异常")
    else:
        st.caption("AI 分析: 未配置")

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
    st.markdown('<p class="sidebar-section-label">数据统计</p>', unsafe_allow_html=True)
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
col_title, col_meta = st.columns([2, 1])
with col_title:
    st.markdown('<p class="app-title">游戏设计演进研究</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">多人对战设计 · 版本编年 · 意图分析</p>', unsafe_allow_html=True)
with col_meta:
    source_label = "Wiki 结构化数据" if fetch_stats["source"] == "wiki" else "本地 data/ 目录"
    st.caption(f"数据来源: {source_label}")

st.markdown('<div class="stat-row">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-item"><span class="stat-n">{selected_game}</span><span class="stat-l">当前游戏</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-item"><span class="stat-n">{len(patches)}</span><span class="stat-l">更新记录</span></div>', unsafe_allow_html=True)
with c3:
    if selected_game == "Pokemon":
        st.markdown(f'<div class="stat-item"><span class="stat-n">第{generation}世代</span><span class="stat-l">分析范围</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="stat-item"><span class="stat-n">Steam News</span><span class="stat-l">数据来源</span></div>', unsafe_allow_html=True)
with c4:
    try:
        db = SQLiteStore()
        stats = db.get_stats(game=selected_game)
        total_analyses = stats.get("total_analyses", 0)
        st.markdown(f'<div class="stat-item"><span class="stat-n">{total_analyses}</span><span class="stat-l">已分析</span></div>', unsafe_allow_html=True)
    except:
        st.markdown(f'<div class="stat-item"><span class="stat-n">—</span><span class="stat-l">已分析</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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

    card_class = "ai-card pvp" if pvp_related else "ai-card"
    src_color = "#9ca3af" if source == "DB缓存" else "#6b7280"
    src_tag = f'<span style="font-size:0.65rem;color:{src_color};padding:1px 5px;border:1px solid {src_color};border-radius:3px;margin-left:6px">{source}</span>'

    st.markdown(
        f'<div class="{card_class}">'
        f'<div class="ai-card-label">AI 分析结果{src_tag}</div>',
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
        tags_html = " ".join([f'<span style="font-size:0.72rem;padding:1px 6px;border:1px solid #e5e7eb;border-radius:3px;color:#6b7280;background:#f5f5f5">{m}</span>' for m in mechanics[:6]])
        st.markdown(f"**涉及机制**: {tags_html}", unsafe_allow_html=True)

    players = analysis.get("player_impact") or analysis.get("affected_players", "")
    if players:
        if isinstance(players, list):
            players = "、".join(players)
        st.markdown(f"**受影响玩家**: {players}")

    _ASSESSMENT_LABELS = {
        "恰到好处": ("力度适中", "#52c41a"),
        "力度不足": ("调整不足", "#faad14"),
        "过犹不及": ("矫枉过正", "#ff4d4f"),
        "治标不治本": ("治标不治本", "#fa8c16"),
    }
    balance = analysis.get("balance_assessment") or analysis.get("design_pattern", "")
    if balance:
        label, color = next(
            ((lbl, col) for key, (lbl, col) in _ASSESSMENT_LABELS.items() if key in balance),
            (f"[{balance}]", "#6b7280"),
        )
        st.markdown(f"**平衡评估**: <span style='font-size:0.72rem;font-weight:600;padding:1px 8px;border-radius:3px;background:{color}22;color:{color};border:1px solid {color}44'>{label}</span>", unsafe_allow_html=True)

    confidence = analysis.get("_data_confidence", "")
    if confidence:
        conf_color = {"高": "#52c41a", "中": "#faad14", "低": "#ff4d4f"}.get(confidence, "#9ca3af")
        st.markdown(f"**置信度**: <span style='color:{conf_color};font-weight:700;font-size:0.8rem'>{confidence}</span>", unsafe_allow_html=True)

    disclaimer = analysis.get("_disclaimer", "")
    if disclaimer:
        st.caption(f"⚠ {disclaimer}")

    similar = analysis.get("similar_historical_cases", [])
    if similar and isinstance(similar, list):
        st.caption("以下历史案例由 AI 推断，建议交叉验证")
        st.markdown("**历史参照**:")
        for r in similar[:3]:
            desc = r.get("description", r) if isinstance(r, dict) else str(r)
            st.markdown(f"- {desc}")

    st.markdown("</div>", unsafe_allow_html=True)

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

    card_class = "patch-card pvp" if pvp_related else "patch-card"
    badge_html = '<span class="badge-pvp">PVP相关</span>' if pvp_related else ''

    title_text = patch.get("title", "N/A")[:60]
    preview = patch.get("content", "")[:80]
    categories = patch.get("categories", [])[:2]
    cat_text = " / ".join(categories) if categories else ""
    version = patch.get("version", "")

    st.markdown(
        f'<div class="{card_class}">'
        f'<div class="patch-card-title">'
        f'<span class="patch-date">{patch.get("date","—")}</span>'
        f'{title_text}'
        f'{badge_html}'
        f'</div>'
        f'<div class="patch-meta">版本 {version}{(" · " + cat_text) if cat_text else ""}</div>'
        f'<div class="patch-preview">{preview}{"..." if len(patch.get("content","")) > 80 else ""}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    with st.expander("查看详情", expanded=False):
        st.markdown(f'<div class="detail-grid">'
                    f'<div class="detail-item"><span class="detail-label">日期</span><span class="detail-value">{patch.get("date","N/A")}</span></div>'
                    f'<div class="detail-item"><span class="detail-label">版本</span><span class="detail-value">{patch.get("version","N/A")}</span></div>'
                    f'</div>',
                    unsafe_allow_html=True)

        content = patch.get("content", "")
        if content:
            st.markdown('<p class="detail-label" style="margin-top:0.5rem;margin-bottom:0.2rem;">更新摘要</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="official-notes">{content}</div>', unsafe_allow_html=True)

        detail = patch.get("detail", "")
        if detail:
            st.markdown('<p class="detail-label" style="margin-top:0.5rem;margin-bottom:0.2rem;">详细改动</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-changes">{detail}</div>', unsafe_allow_html=True)

        has_bg = any([patch.get("full_context"), patch.get("impact"), patch.get("vgc_relevance"), patch.get("balance_changes")])
        if has_bg:
            with st.expander("详细背景信息"):
                if patch.get("full_context"):
                    st.markdown('<p class="detail-label">背景说明</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="official-notes">{patch.get("full_context")}</div>', unsafe_allow_html=True)
                bc = patch.get("balance_changes", {})
                if bc:
                    st.markdown('<p class="detail-label" style="margin-top:0.5rem;">数值改动</p>', unsafe_allow_html=True)
                    for name, changes in bc.items():
                        if isinstance(changes, dict):
                            st.markdown(f"- **{name}**: {', '.join(f'{k}:{v}' for k, v in changes.items())}")
                        else:
                            st.markdown(f"- **{name}**: {changes}")
                if patch.get("impact"):
                    st.markdown('<p class="detail-label" style="margin-top:0.5rem;">影响分析</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="official-notes">{patch.get("impact")}</div>', unsafe_allow_html=True)
                if patch.get("vgc_relevance"):
                    st.markdown('<p class="detail-label" style="margin-top:0.5rem;">VGC相关</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="official-notes">{patch.get("vgc_relevance")}</div>', unsafe_allow_html=True)

        if patch.get("official_notes"):
            st.markdown('<p class="detail-label" style="margin-top:0.5rem;">官方原文</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="official-notes">{patch.get("official_notes","").replace(chr(10),"<br>")}</div>',
                unsafe_allow_html=True
            )

        if patch.get("intent"):
            st.markdown('<p class="detail-label" style="margin-top:0.5rem;">设计意图</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="insight-box">{patch.get("intent")}</div>', unsafe_allow_html=True)

        st.markdown('<div style="border-top:1px solid #f0f0f0;padding-top:0.75rem;margin-top:0.5rem;">', unsafe_allow_html=True)
        _render_patch_detail(patch, patch_key, selected_game, generation, pvp_related, llm_ready, extractor, db)

        src_url = patch.get("source_url", "")
        if src_url:
            st.markdown(f'<p style="margin-top:0.5rem;"><a href="{src_url}" target="_blank" style="font-size:0.78rem;color:#9ca3af;">→ 查看官方原文</a></p>', unsafe_allow_html=True)


# ==================== Tab 1: 版本编年史 ====================
with tab1:
    st.markdown('<p class="app-title" style="margin-top:0.5rem;">版本编年史</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="app-subtitle">{"基于 Wiki 结构化的版本更新记录" if selected_game == "Pokemon" else "Steam News 预采集日志"}</p>', unsafe_allow_html=True)

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
with tab2:
    st.markdown('<p class="app-title" style="margin-top:0.5rem;">机制时间轴</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">历代多人对战机制演进可视化</p>', unsafe_allow_html=True)

    # 从 PokeAPI 获取版本信息构建时间轴（session_state 缓存避免重复请求）
    timeline_data = []

    if selected_game == "Pokemon":
        # 使用 session_state 缓存，避免每次渲染都请求 PokeAPI
        # 注意：Pokemon 不同世代的数据不同，但 Pokemon 游戏只有一个，不需要加游戏名
        vgc_cache_key = f"_vgc_timeline_{selected_game}_{generation}"
        if vgc_cache_key not in st.session_state:
            try:
                api_scraper = get_api_scraper()
                version_groups = api_scraper.get_version_changelog(generation)
                st.session_state[vgc_cache_key] = version_groups
            except Exception as e:
                st.session_state[vgc_cache_key] = []
        else:
            version_groups = st.session_state[vgc_cache_key]

        for vg in version_groups:
            timeline_data.append({
                "generation": vg.get("generation", generation),
                "year": 2019 + (vg.get("generation", generation) - 8),  # 粗略估算
                "mechanism": vg.get("version", vg.get("version_group", "")),
                "description": f"版本组: {vg.get('version_group', '')}",
                "type": "版本",
            })

    # 机制演进数据（基于真实游戏历史）
    mechanism_evolution = [
        # 第一/二世代演进
        {"generation": 1, "year": 1996, "mechanism": "基础双打对战", "description": "2v2对战成为标准模式", "type": "PvP"},
        {"generation": 2, "year": 1999, "mechanism": "特性系统", "description": "约80种特性提供被动战术", "type": "机制"},
        {"generation": 2, "year": 1999, "mechanism": "道具系统", "description": "宝可梦可携带道具", "type": "机制"},
        # 第三/四世代演进
        {"generation": 3, "year": 2002, "mechanism": "双打正式确立", "description": "4v4选2成为VGC基础规则", "type": "PvP"},
        {"generation": 3, "year": 2002, "mechanism": "天气系统", "description": "晴/雨/沙/冰雹影响战斗", "type": "机制"},
        {"generation": 4, "year": 2006, "mechanism": "Wi-Fi对战上线", "description": "全球线上双打对战普及", "type": "PvP"},
        {"generation": 4, "year": 2006, "mechanism": "物理特殊分类改革", "description": "招式按物理/特殊分类", "type": "机制"},
        # 第五世代演进
        {"generation": 5, "year": 2011, "mechanism": "赛季制VGC", "description": "Seasonal Tournament正式引入", "type": "PvP"},
        {"generation": 5, "year": 2011, "mechanism": "天气启动机", "description": "雨队/沙暴队成为环境核心", "type": "PvP"},
        {"generation": 5, "year": 2012, "mechanism": "世界锦标赛", "description": "Pokemon World Championships举办", "type": "PvP"},
        # 第六世代演进
        {"generation": 6, "year": 2013, "mechanism": "Mega进化", "description": "特定宝可梦可进化为更强形态", "type": "机制"},
        {"generation": 6, "year": 2014, "mechanism": "三打对战", "description": "3v3轮换对战模式", "type": "PvP"},
        # 第七世代演进
        {"generation": 7, "year": 2016, "mechanism": "Z招式", "description": "取代Mega进化的强化系统", "type": "机制"},
        {"generation": 7, "year": 2017, "mechanism": "究极异兽", "description": "UB系列丰富VGC可用池", "type": "PvP"},
        # 第八世代演进
        {"generation": 8, "year": 2019, "mechanism": "极巨化", "description": "可让宝可梦巨大化并获得强力招式", "type": "机制"},
        {"generation": 8, "year": 2020, "mechanism": "极巨团体战", "description": "4人合作挑战野生极巨化宝可梦", "type": "PvE"},
        # 第九世代演进
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
            height=600,
            xaxis_title="年份",
            yaxis_title="世代/版本",
            showlegend=True,
            legend_title="机制类型",
            font=dict(size=13),
            yaxis=dict(
                tickmode="array",
                tickvals=list(range(1, 10)),
                ticktext=[f"Gen {i}" for i in range(1, 10)],
            ),
        )

        fig.update_yaxes(autorange="reversed")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("请选择至少一个游戏来显示时间轴")

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
        st.markdown('<p class="tl-section-title">已分析条目</p>', unsafe_allow_html=True)
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
    if "Pokemon" in game_filter:
        comparison_data = {
            "特性": ["保护机制", "持续时间", "使用限制", "多人适用"],
            "守住 (Protect)": ["完全抵挡攻击", "单回合", "可连续使用", "是"],
            "看我嘛 (Follow Me)": ["吸引对方攻击", "持续至切换", "受威吓影响", "2v2核心"],
            "极巨防壁": ["极巨化中自动保护", "极巨化期间", "仅极巨化中", "团体战"],
            "太晶化": ["属性改变+招式", "1回合", "任意宝可梦", "PvP/PvE"],
        }
        st.divider()
        st.markdown('<p class="tl-section-title">防御/保护机制演进对比</p>', unsafe_allow_html=True)
        df_defense = pd.DataFrame(comparison_data)
        st.dataframe(df_defense, width="stretch", hide_index=True)


# ==================== Tab 3: 设计意图分析 ====================
with tab3:
    st.markdown('<p class="app-title" style="margin-top:0.5rem;">设计意图分析</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">大语言模型解读版本更新背后的设计动机</p>', unsafe_allow_html=True)

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
            st.markdown('<p class="tl-section-title">待分析更新列表</p>', unsafe_allow_html=True)

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
    label_html = f'<span class="step-pill {state}">{step_num}. {label}</span>'
    st.markdown(label_html, unsafe_allow_html=True)


with tab4:
    st.markdown('<p class="app-title" style="margin-top:0.5rem;">演进报告</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">AI 扫描所有更新 · 分层主题树 · 深度演进分析</p>', unsafe_allow_html=True)

    _report_html_path = Path(__file__).parent / "docs" / "index.html"
    _report_md_path  = Path(__file__).parent / "综合研究报告_宝可梦VGC多人对战设计经验.md"

    if _report_html_path.exists():
        with st.container():
            st.markdown('<div style="border:1px solid #eeeeee;border-radius:6px;padding:1rem 1.25rem;margin:1rem 0;background:#fafafa;">', unsafe_allow_html=True)
            st.markdown('<p class="ai-card-label">综合研究报告</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.875rem;color:#374151;margin-bottom:0.75rem;">宝可梦 VGC 多人对战设计演进 · 10条设计原则 · 历代演进时间轴 · Pokemon vs Palworld 对照 · 设计检查清单</p>', unsafe_allow_html=True)

            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.caption("报告从 Pokemon 29 年历史中提炼可操作的多人对战设计原则")
            with col_btn:
                _report_url = str(_report_html_path.resolve())
                if st.button("在浏览器中打开", key="open_interactive_report"):
                    import webbrowser
                    webbrowser.open_new_tab(f"file:///{_report_url.replace(chr(92), '/')}")
                    st.toast("已在浏览器中打开交互式报告")

            st.markdown('</div>', unsafe_allow_html=True)

            if _report_md_path.exists():
                with st.expander("在 App 内阅读完整 Markdown 报告"):
                    _md_content = _report_md_path.read_text(encoding="utf-8")
                    st.markdown(_md_content[:4000])
                    if len(_md_content) > 4000:
                        st.caption(f"（报告共 {len(_md_content):,} 字符，此处仅显示前 4000 字）")

    st.divider()

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

        _step1 = f'<span class="step-pill {step1_state}">1. 发现主题</span>'
        _step2 = f'<span class="step-pill {step2_state}">2. 选择演进枝</span>'
        _step3 = f'<span class="step-pill {step3_state}">3. 生成报告</span>'
        st.markdown(
            f'<div class="step-bar">{_step1}<div class="step-connector"></div>{_step2}<div class="step-connector"></div>{_step3}</div>',
            unsafe_allow_html=True
        )

        st.divider()

        if not result["success"]:
            st.error(f"主题发现失败：{result.get('error', '未知错误')}")
            if st.button("重新尝试", key="retry_discovery"):
                del st.session_state[cache_key]
                st.rerun()

        elif not has_topics:
            st.info("AI 分析完成，但没有发现足够支撑研究主题的数据。可以尝试切换到 Pokemon Gen9 或其他数据更丰富的游戏/世代。")

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

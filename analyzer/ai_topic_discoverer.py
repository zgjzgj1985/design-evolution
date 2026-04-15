"""
AI 主题发现器
调用 LLM 扫描所有更新，自动归纳值得研究的设计主题
完全动态化：基于数据本身发现主题，不预设任何游戏特定知识
"""

import json
import re
from typing import Optional


MAX_PATCHES_FOR_DISCOVERY = 80


class AITopicDiscoverer:
    """AI 驱动的主题发现器 - 完全动态化"""

    def __init__(self, extractor):
        self.extractor = extractor

    def _summarize_patches(self, patches: list) -> str:
        """
        将更新列表格式化为简短的摘要文本
        每次最多处理 MAX_PATCHES_FOR_DISCOVERY 条
        """
        if len(patches) > MAX_PATCHES_FOR_DISCOVERY:
            step = len(patches) // MAX_PATCHES_FOR_DISCOVERY
            patches = patches[::step][:MAX_PATCHES_FOR_DISCOVERY]

        lines = []
        for i, p in enumerate(patches):
            version = p.get("version") or p.get("date", "N/A")
            title = p.get("title", "").strip()
            content = p.get("content", "").strip()
            game = p.get("game", "")
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"[{i+1}] 游戏:{game} 版本:{version} | {title} | {content}")

        return "\n".join(lines)

    def _parse_json_response(self, text: str) -> Optional[list]:
        """解析 LLM 返回的 JSON 数组"""
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = text.strip()

        json_str = json_str.strip()

        if not json_str.startswith("["):
            arr_match = re.search(r"\[[\s\S]*\]", json_str)
            if arr_match:
                json_str = arr_match.group(0)

        try:
            result = json.loads(json_str)
            if isinstance(result, list):
                return result
            if isinstance(result, dict) and "themes" in result:
                return result["themes"]
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}，原始响应前200字: {text[:200]}")
            return None

    def _detect_game_context(self, patches: list) -> dict:
        """
        从数据中检测当前游戏的上下文信息
        帮助后续分析报告时理解游戏特性
        """
        games = set()
        has_multiplayer = False
        has_pvp = False
        has_pve = False
        keywords = set()

        for p in patches[:30]:
            text = (p.get("title", "") + " " + p.get("content", "")).lower()
            for kw in ["双打", "单打", "对战", "pvp", "pve", "raid", "团体战",
                       "2v2", "multiplayer", "competitive", "battle"]:
                if kw in text:
                    keywords.add(kw)
            if any(k in text for k in ["pvp", "对战", "双打", "单打", "competitive", "vgc"]):
                has_pvp = True
            if any(k in text for k in ["raid", "团体战", "多人", "pve", "boss", "合作"]):
                has_pve = True
            if any(k in text for k in ["多人", "multiplayer", "co-op", "2v2"]):
                has_multiplayer = True
            game = p.get("game", "")
            if game:
                games.add(game)

        return {
            "games": list(games),
            "has_multiplayer": has_multiplayer,
            "has_pvp": has_pvp,
            "has_pve": has_pve,
            "keywords": list(keywords)[:10],
        }

    def discover(self, patches: list) -> dict:
        """
        调用 AI 分析所有更新，发现值得研究的主题

        完全动态化：
        - 不预设任何游戏特定主题
        - 不预设任何关键词
        - 从数据本身涌现研究主题

        Returns:
            {
                "success": bool,
                "discovered_topics": list[TopicCard],
                "error": str,
                "total_analyzed": int,
                "game_context": dict,  # 新增：检测到的游戏上下文
            }
        """
        if not patches:
            return {
                "success": False,
                "discovered_topics": [],
                "error": "没有可用数据",
                "total_analyzed": 0,
                "game_context": {},
            }

        total = len(patches)
        patches_text = self._summarize_patches(patches)
        game_context = self._detect_game_context(patches)

        system_prompt = """你是一位专业的游戏设计研究员。你的任务是分析一系列游戏版本更新日志，归纳出其中蕴含的核心设计主题。

**核心原则**：完全从数据出发，不预设任何"正确答案"。你的价值在于发现数据中真正有趣的模式，而非套用已知的框架。

**你将看到的**：一批游戏更新日志，每条包含：游戏名称 | 版本号 | 标题 | 内容摘要

**你的任务**：
1. 仔细阅读所有更新，识别出 3~5 个最重要的设计主题
2. 每个主题需要：
   - 一个清晰的主题名称（10字以内）
   - 一句话描述这个主题研究什么问题（20字以内）
   - 至少 2 条相关的更新作为证据（按相关度排序）
   - 该主题在数据中的出现频率评估（低/中/高）
   - 一句话说明"为什么这个主题值得研究"

**输出格式**：直接输出 JSON 数组，不要有其他内容。

**注意事项**：
- 主题应该是"设计问题"而非"技术实现"（比如"如何在多人战斗中平衡攻击强度"比"伤害数值调整"更好）
- 如果某条更新涉及多个主题，可以在多个主题下都引用
- 如果数据中没有足够支撑某个主题的更新（少于2条），不要勉强提出
- 主题按"覆盖广度"降序排列
- 输出 JSON 数组"""

        games_str = ', '.join(game_context['games']) if game_context['games'] else '未知'
        user_prompt = f"""以下是要分析的 {total} 条版本更新：

检测到的游戏上下文：
- 游戏: {games_str}
- 多人对战: {'是' if game_context['has_multiplayer'] else '否'}
- PvP: {'是' if game_context['has_pvp'] else '否'}
- PvE: {'是' if game_context['has_pve'] else '否'}
- 关键词: {', '.join(game_context['keywords']) if game_context['keywords'] else '无'}

---

{games_str}游戏版本更新列表：

{patches_text}

请输出 JSON 数组，格式如下：
[
  {{
    "name": "主题名称（10字以内）",
    "description": "这个主题研究什么问题（20字以内）",
    "matched_preview": ["相关更新标题1", "相关更新标题2"],
    "frequency": "中",
    "why_important": "为什么这个主题值得研究（1句话）"
  }}
]"""

        llm = self.extractor._get_llm()
        if llm is None:
            return {
                "success": False,
                "discovered_topics": [],
                "error": "LLM 不可用，请检查 API 配置",
                "total_analyzed": total,
                "game_context": game_context,
            }

        try:
            from langchain_core.runnables import RunnableConfig
            config = RunnableConfig(
                timeout=180.0,
                max_retries=2,
            )
            response = llm.invoke(
                [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                config=config
            )
            text = response.content if hasattr(response, "content") else str(response)
            topics = self._parse_json_response(text)

            if topics is None:
                return {
                    "success": False,
                    "discovered_topics": [],
                    "error": "AI 返回格式无法解析，请重试",
                    "total_analyzed": total,
                    "game_context": game_context,
                }

            topics = [t for t in topics if t.get("name") and t.get("description")]
            topics.sort(key=lambda x: len(x.get("matched_preview", [])), reverse=True)

            return {
                "success": True,
                "discovered_topics": topics,
                "total_analyzed": total,
                "game_context": game_context,
                "error": None,
            }

        except Exception as e:
            import traceback
            error_str = str(e)
            if "rate limit" in error_str.lower() or "429" in error_str:
                user_error = "OpenRouter 频率限制，请等待几秒后重试"
            elif "connection" in error_str.lower():
                user_error = "网络连接失败，请检查网络和代理设置"
            elif "api key" in error_str.lower() or "auth" in error_str.lower():
                user_error = "API Key 无效或已过期"
            elif "timeout" in error_str.lower():
                user_error = "请求超时，请重试或切换到更快的模型"
            else:
                user_error = f"AI 调用失败: {e}"

            return {
                "success": False,
                "discovered_topics": [],
                "error": user_error,
                "error_detail": error_str,
                "traceback": traceback.format_exc(),
                "total_analyzed": total,
                "game_context": game_context,
            }

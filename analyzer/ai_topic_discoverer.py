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

    def _parse_json_response(self, text: str) -> Optional[dict]:
        """解析 LLM 返回的 JSON（支持树形结构和旧数组格式）"""
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = text.strip()

        json_str = json_str.strip()

        # 优先尝试树形结构
        if not json_str.startswith("["):
            obj_match = re.search(r"\{[\s\S]*\}", json_str)
            if obj_match:
                try:
                    result = json.loads(obj_match.group(0))
                    if isinstance(result, dict):
                        return result
                except json.JSONDecodeError:
                    pass

        # 降级尝试数组格式（向后兼容）
        if not json_str.startswith("["):
            arr_match = re.search(r"\[[\s\S]*\]", json_str)
            if arr_match:
                json_str = arr_match.group(0)

        try:
            result = json.loads(json_str)
            if isinstance(result, list):
                return {"topic_tree": result}
            if isinstance(result, dict):
                return result
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

        system_prompt = """你是一位专业的游戏设计研究员。你的任务是分析一系列游戏版本更新日志，构建一个**分层主题树**，揭示历代设计师如何逐步迭代某个设计问题。

## 核心原则

完全从数据出发，不预设任何"正确答案"。你的价值在于发现数据中真正有趣的**演进路径**，而非统计频率最高的泛泛话题。

## 你将看到的

一批游戏更新日志，每条包含：游戏名称 | 版本号 | 标题 | 内容摘要

## 你的任务：构建分层主题树

第一层（顶层主题）：识别 2~3 个**设计维度**，每个维度代表一类核心设计矛盾（如"攻击强度与生存时间的平衡"、"规则框架与玩家自由的边界"）。这些维度之间应有明显差异，共同覆盖数据中的主要设计意图。

第二层（演进枝）：每个顶层主题下，展开 2~3 条**演进枝**，每条演进枝对应一个具体的设计问题在该游戏历代中的演变路径。

每条演进枝必须包含：
- **问题定义**：这个具体设计问题是什么？（5~15字，如"Mega进化强度控制"）
- **历代解法**：按时间顺序，列出各代/版本采取的具体解法（用补丁标题原文支撑）
- **核心洞察**：设计师在这一问题上最关键的决策是什么？背后可能的考量？
- **相关补丁**：至少 2 条相关补丁标题（精确匹配）

## 关键要求

1. **演进枝必须体现"变化"**：如果某问题在所有版本中的解法都相同，那不是一条好的演进枝
2. **演进枝之间要有区分度**：不同枝解决的问题应明显不同，避免重叠
3. **补丁引用要精确**：使用补丁标题原文，不要自己编造补丁标题
4. **优先挖掘独特设计尝试**：设计师在某一代做的独特实验，往往比统计数字更能揭示设计意图
5. **如果数据不支撑演进（某问题历代解法相同），将该演进枝标记为"单向强化"并说明为何**

## 输出格式

输出一个 JSON 对象（不要用 JSON 数组），结构如下：

```json
{
  "overview": "整体主题树的一句话概括",
  "top_level": [
    {
      "name": "维度名称（如：爆发资源的博弈深度设计）",
      "description": "这个维度研究什么（10~20字）",
      "why_important": "为什么这个维度值得研究（1句话）",
      "branches": [
        {
          "problem": "具体设计问题（如：Mega进化持续时间对站场收益的影响）",
          "evolution_stages": [
            {
              "period": "世代/版本（如：Gen6）",
              "solution": "当时的解法描述",
              "patch_titles": ["补丁标题1", "补丁标题2"]
            }
          ],
          "key_insight": "这一演进中最关键的决策洞察（1句话）",
          "is_one_way": false
        }
      ]
    }
  ]
}
```

请直接输出 JSON，不要有其他内容。"""

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

请输出 JSON 对象，格式如上述说明："""

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
            parsed = self._parse_json_response(text)

            if parsed is None:
                return {
                    "success": False,
                    "discovered_topics": [],
                    "error": "AI 返回格式无法解析，请重试",
                    "total_analyzed": total,
                    "game_context": game_context,
                }

            # 提取主题树
            topic_tree = parsed.get("topic_tree", parsed.get("top_level", []))
            if isinstance(topic_tree, dict) and "top_level" in topic_tree:
                topic_tree = topic_tree["top_level"]

            # 兼容旧格式：转换为扁平主题列表供降级使用
            flat_topics = self._flatten_topic_tree(topic_tree) if isinstance(topic_tree, list) else []

            return {
                "success": True,
                "topic_tree": topic_tree if isinstance(topic_tree, list) else [],
                "overview": parsed.get("overview", ""),
                "discovered_topics": flat_topics,
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

    def _flatten_topic_tree(self, tree: list) -> list:
        """
        将分层主题树扁平化为旧格式的 topic 列表（用于向后兼容）
        每条演进枝展平为一个扁平 topic
        """
        flat = []
        for top in tree:
            branches = top.get("branches", [])
            for branch in branches:
                patch_titles = []
                for stage in branch.get("evolution_stages", []):
                    patch_titles.extend(stage.get("patch_titles", []))
                flat.append({
                    "name": branch.get("problem", "未命名问题"),
                    "description": f"{top.get('name', '')} → {branch.get('problem', '')}",
                    "matched_preview": list(dict.fromkeys(patch_titles))[:5],
                    "frequency": "中",
                    "why_important": top.get("why_important", ""),
                    "_parent": top.get("name", ""),
                    "_branch": branch,
                    "_top_level": top,
                })
        return flat

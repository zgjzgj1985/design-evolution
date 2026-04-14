"""
AI 主题发现器
调用 LLM 扫描所有更新，自动归纳值得研究的设计主题
"""

import json
import re
from typing import Optional
from analyzer.intent_extractor import IntentExtractor


# 每次最多传给 AI 的更新数量（防止 token 爆掉）
MAX_PATCHES_FOR_DISCOVERY = 80


class AITopicDiscoverer:
    """AI 驱动的主题发现器"""

    def __init__(self, extractor: IntentExtractor):
        self.extractor = extractor

    def _summarize_patches(self, patches: list) -> str:
        """
        将更新列表格式化为简短的摘要文本
        每次最多处理 MAX_PATCHES_FOR_DISCOVERY 条
        """
        # 如果更新太多，采样 + 压缩
        if len(patches) > MAX_PATCHES_FOR_DISCOVERY:
            step = len(patches) // MAX_PATCHES_FOR_DISCOVERY
            patches = patches[::step][:MAX_PATCHES_FOR_DISCOVERY]

        lines = []
        for i, p in enumerate(patches):
            version = p.get("version") or p.get("date", "N/A")
            title = p.get("title", "").strip()
            content = p.get("content", "").strip()
            # 标题截断到 100 字
            if len(content) > 150:
                content = content[:150] + "..."
            lines.append(f"[{i+1}] 版本:{version} | {title} | {content}")

        return "\n".join(lines)

    def _parse_json_response(self, text: str) -> Optional[list]:
        """解析 LLM 返回的 JSON 数组"""
        # 尝试从 code block 中提取
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 直接尝试整个文本
            json_str = text.strip()

        # 去掉前后的空白
        json_str = json_str.strip()

        # 如果不是以 [ 开头，找第一个 [ 的位置
        if not json_str.startswith("["):
            arr_match = re.search(r"\[[\s\S]*\]", json_str)
            if arr_match:
                json_str = arr_match.group(0)

        try:
            result = json.loads(json_str)
            if isinstance(result, list):
                return result
            # 如果是 dict 且有 themes 字段
            if isinstance(result, dict) and "themes" in result:
                return result["themes"]
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}，原始响应前200字: {text[:200]}")
            return None

    def discover(self, patches: list) -> dict:
        """
        调用 AI 分析所有更新，发现值得研究的主题

        Args:
            patches: 所有更新列表

        Returns:
            {
                "success": bool,
                "discovered_topics": list[TopicCard],  # 发现的主题列表
                "error": str,  # 错误信息（如果失败）
                "total_analyzed": int,  # 分析了多少条更新
            }
        """
        if not patches:
            return {
                "success": False,
                "discovered_topics": [],
                "error": "没有可用数据",
                "total_analyzed": 0,
            }

        total = len(patches)
        patches_text = self._summarize_patches(patches)

        system_prompt = """你是一位专业的游戏设计研究员。你的任务是分析一系列版本更新日志，归纳出其中蕴含的核心设计主题。

你会看到一批游戏版本更新，每条包含：版本号 | 标题 | 内容摘要

请仔细阅读，识别出 3~5 个最重要的设计主题，每个主题需要：
1. 一个清晰的主题名称
2. 一句话描述这个主题研究什么问题
3. 至少 3 条相关的更新作为证据（按相关度排序，最相关的放前面）
4. 该主题在数据中的出现频率评估（低/中/高）

请分析时注意：
- 主题应该是"设计问题"而非"技术实现"（比如"爆发资源的博弈设计"比"极巨化代码"更好）
- 如果某条更新涉及多个主题，可以在多个主题下都引用
- 如果数据中没有足够支撑某个主题的更新（少于3条），不要勉强提出
- 输出时主题按"覆盖广度"降序排列（即相关更新越多越靠前）

直接输出 JSON 数组，不要有其他内容。"""

        user_prompt = f"""以下是要分析的 {total} 条版本更新：

{patches_text}

请输出 JSON 数组，格式如下：
[
  {{
    "name": "主题名称（10字以内）",
    "description": "这个主题研究什么问题（20字以内）",
    "matched_preview": ["相关更新标题1", "相关更新标题2", "相关更新标题3"],
    "frequency": "中",
    "why_important": "为什么这个主题值得研究（1句话）"
  }}
]
"""

        llm = self.extractor._get_llm()
        if llm is None:
            return {
                "success": False,
                "discovered_topics": [],
                "error": "LLM 不可用，请检查 API 配置（provider/model/base_url）",
                "total_analyzed": total,
            }

        try:
            response = llm.invoke(
                [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            text = response.content if hasattr(response, "content") else str(response)
            topics = self._parse_json_response(text)

            if topics is None:
                return {
                    "success": False,
                    "discovered_topics": [],
                    "error": "AI 返回格式无法解析，请重试",
                    "total_analyzed": total,
                }

            # 过滤空主题
            topics = [t for t in topics if t.get("name") and t.get("description")]

            # 按 matched_preview 数量降序排列
            topics.sort(key=lambda x: len(x.get("matched_preview", [])), reverse=True)

            return {
                "success": True,
                "discovered_topics": topics,
                "total_analyzed": total,
                "error": None,
            }

        except Exception as e:
            import traceback
            error_str = str(e)
            # 判断具体错误类型
            if "rate limit" in error_str.lower() or "429" in error_str:
                user_error = "OpenRouter 频率限制，请等待几秒后重试，或在侧边栏切换到 OpenAI"
            elif "connection" in error_str.lower():
                user_error = "网络连接失败，请检查网络和代理设置"
            elif "api key" in error_str.lower() or "auth" in error_str.lower():
                user_error = "API Key 无效或已过期，请在侧边栏重新配置"
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
            }
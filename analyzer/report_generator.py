"""
演进报告生成器
将研究主题 + 过滤后的更新 → 一次性发给 AI → 输出 Markdown 深度报告
"""

import re
from typing import Optional
from analyzer.prompts import GAME_DESIGN_CONTEXT
from analyzer.research_topics import (
    RESEARCH_TOPICS,
    get_topic_by_id,
    filter_patches_for_topic,
)
from analyzer.intent_extractor import IntentExtractor
from utils.config import config


class EvolutionReportGenerator:
    """演进报告生成器"""

    def __init__(self, extractor: IntentExtractor):
        self.extractor = extractor

    def _format_patches_for_prompt(self, patches: list) -> str:
        """将更新列表格式化为 Prompt 文本"""
        lines = []
        for i, patch in enumerate(patches):
            lines.append(f"### 更新 {i + 1}")
            lines.append(f"版本: {patch.get('version', patch.get('date', 'N/A'))}")
            lines.append(f"日期: {patch.get('date', 'N/A')}")
            lines.append(f"标题: {patch.get('title', 'N/A')}")
            lines.append(f"内容: {patch.get('content', 'N/A')}")
            lines.append("")
        return "\n".join(lines)

    def _extract_markdown_response(self, text: str) -> str:
        """提取 LLM 返回的 Markdown 报告"""
        # 去掉可能的 markdown code block 包裹
        md_match = re.search(r"```(?:markdown)?\s*([\s\S]*?)\s*```", text)
        if md_match:
            return md_match.group(1).strip()
        # 如果不是 code block，直接返回，可能是 AI 直接输出 Markdown
        return text.strip()

    def generate_report(
        self,
        topic_id: str,
        all_patches: list,
    ) -> Optional[dict]:
        """
        为指定研究主题生成演进报告

        Args:
            topic_id: 研究主题 ID
            all_patches: 所有可用更新

        Returns:
            包含 "_markdown" 字段的报告字典，失败返回 None
        """
        topic = get_topic_by_id(topic_id)
        if topic is None:
            print(f"未知的研究主题: {topic_id}")
            return None

        # 过滤相关更新
        matched = filter_patches_for_topic(all_patches, topic)

        if not matched:
            return {
                "_error": True,
                "_message": f"在当前数据中没有找到与「{topic['name']}」相关的更新",
                "research_question": topic["description"],
                "key_insight": "暂无数据支撑分析",
            }

        # 格式化更新文本
        updates_text = self._format_patches_for_prompt(matched)

        # 构建 Prompt
        prompt = topic["analysis_prompt"].format(
            updates_text=updates_text,
            game_context=GAME_DESIGN_CONTEXT + "\n\n" + topic["game_context"],
        )

        # 调用 LLM
        llm = self.extractor._get_llm()
        if llm is None:
            return {
                "_error": True,
                "_message": "LLM 不可用，无法生成演进报告",
                "research_question": topic["description"],
                "matched_count": len(matched),
            }

        try:
            response = llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            markdown = self._extract_markdown_response(text)

            if markdown:
                return {
                    "_markdown": markdown,
                    "_topic": topic["name"],
                    "_matched_count": len(matched),
                    "_topic_description": topic["description"],
                }
            else:
                return {
                    "_error": True,
                    "_message": "AI 未返回有效报告内容",
                    "research_question": topic["description"],
                    "matched_count": len(matched),
                }

        except Exception as e:
            print(f"演进报告生成失败: {e}")
            return {
                "_error": True,
                "_message": f"生成失败: {e}",
                "research_question": topic["description"],
                "matched_count": len(matched),
            }

    def get_available_topics(self) -> list:
        """获取所有研究主题列表"""
        return [
            {
                "id": t["id"],
                "name": t["name"],
                "description": t["description"],
            }
            for t in RESEARCH_TOPICS
        ]

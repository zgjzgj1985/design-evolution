"""
演进报告生成器
将研究主题 + 过滤后的更新 → 一次性发给 AI → 输出结构化报告
"""

import json
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
            lines.append(f"--- 更新 {i + 1} ---")
            lines.append(f"版本: {patch.get('version', patch.get('date', 'N/A'))}")
            lines.append(f"日期: {patch.get('date', 'N/A')}")
            lines.append(f"标题: {patch.get('title', 'N/A')}")
            lines.append(f"内容: {patch.get('content', 'N/A')}")
            lines.append("")
        return "\n".join(lines)

    def _parse_json_response(self, text: str) -> Optional[dict]:
        """解析 LLM 返回的 JSON 响应"""
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = text.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            obj_match = re.search(r"\{[\s\S]*\}", json_str)
            if obj_match:
                try:
                    return json.loads(obj_match.group(0))
                except json.JSONDecodeError:
                    pass
            print(f"JSON 解析失败，原始响应（前200字）: {text[:200]}")
            return None

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
            报告字典，失败返回 None
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
            result = self._parse_json_response(text)

            if result:
                result["_topic"] = topic["name"]
                result["_matched_count"] = len(matched)
                result["_topic_description"] = topic["description"]

            return result

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

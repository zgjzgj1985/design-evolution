"""
研究主题配置

注意：此模块已不再使用，预置主题已被动态主题发现取代。
保留此文件仅用于向后兼容。

新版流程：
1. AI 自动扫描所有更新，动态发现设计主题
2. 用户选择感兴趣的主题
3. 基于选中的主题和实际数据生成演进报告

不再需要预置的 keywords、game_context 等硬编码知识。
"""

from typing import TypedDict


class ResearchTopic(TypedDict):
    """
    保留类型定义以确保兼容性，但不再使用此结构
    """
    id: str
    name: str
    description: str
    keywords: list[str]
    exclude_keywords: list[str]
    game_context: str
    analysis_prompt: str


RESEARCH_TOPICS: list[ResearchTopic] = []


def get_topic_by_id(topic_id: str) -> ResearchTopic | None:
    """根据 ID 获取研究主题（保留兼容性）"""
    for topic in RESEARCH_TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None


def filter_patches_for_topic(patches: list, topic: ResearchTopic) -> list:
    """
    根据研究主题的关键词过滤更新（保留兼容性）
    新流程中使用 match_patches_by_keywords 代替
    """
    return patches

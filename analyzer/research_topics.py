"""
研究主题配置（已废弃）

此模块已废弃，预置主题机制已被动态主题发现完全取代。
保留此文件是为了避免残留的 import 引用报错。

新版流程由 `analyzer/ai_topic_discoverer.py` 中的 AITopicDiscoverer 驱动，
它通过 LLM 自动扫描数据动态发现主题，不再依赖预置主题列表。

废弃说明：
- RESEARCH_TOPICS 已清空，不再使用
- get_topic_by_id() 已废弃，保留以防残留引用
- filter_patches_for_topic() 已废弃，保留以防残留引用
"""


def get_topic_by_id(topic_id: str):
    """已废弃，请使用 AITopicDiscoverer 进行动态主题发现"""
    return None


def filter_patches_for_topic(patches: list, topic: dict) -> list:
    """已废弃，请使用 EvolutionReportGenerator.match_patches_by_keywords()"""
    return patches

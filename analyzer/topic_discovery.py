"""
主题发现器
自动扫描数据，发现哪些研究主题在当前数据集中有相关内容
"""

from typing import TypedDict
from analyzer.research_topics import RESEARCH_TOPICS, get_topic_by_id


class TopicDiscovery(TypedDict):
    """主题发现结果"""
    id: str
    name: str
    description: str
    matched_count: int
    matched_summaries: list[str]  # 匹配到的更新的摘要预览
    match_ratio: float  # 匹配数 / 总更新数（反映主题的占比）


def discover_topics(patches: list) -> list[TopicDiscovery]:
    """
    自动扫描所有更新，发现哪些研究主题在数据中有相关内容

    Args:
        patches: 所有更新列表

    Returns:
        按匹配数量排序的主题发现列表
    """
    if not patches:
        return []

    results = []

    for topic in RESEARCH_TOPICS:
        topic_obj = get_topic_by_id(topic["id"])
        if not topic_obj:
            continue

        # 复用 filter_patches_for_topic
        from analyzer.research_topics import filter_patches_for_topic
        matched = filter_patches_for_topic(patches, topic_obj)

        if matched:
            # 提取每条匹配的标题/摘要预览
            summaries = []
            for p in matched[:5]:  # 最多取5条
                title = p.get("title", "")
                version = p.get("version", p.get("date", ""))
                if title:
                    summaries.append(f"[{version}] {title}" if version else title)

            results.append({
                "id": topic["id"],
                "name": topic["name"],
                "description": topic["description"],
                "matched_count": len(matched),
                "matched_summaries": summaries,
                "match_ratio": len(matched) / len(patches),
            })

    # 按匹配数量降序排列
    results.sort(key=lambda x: x["matched_count"], reverse=True)
    return results

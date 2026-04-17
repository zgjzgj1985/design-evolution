"""
演进报告生成器
将动态发现的主题 + 相关更新 → 发送给 AI → 输出 Markdown 深度报告
支持分层主题树结构：当主题包含演进枝数据时，直接利用结构化信息生成报告
"""

import re
from typing import Optional


# 分层主题树报告模板（优先使用）
TREE_TOPIC_REPORT_TEMPLATE = """你是游戏设计演进研究专家，专注于分析游戏更新背后的设计逻辑和迭代规律。

## 研究主题

**维度**：「{dimension_name}」
**具体问题**：「{problem_name}」
**核心意义**：{why_important}

## 演进枝数据（由 AI 预先结构化，请严格基于此数据进行分析）

{evolution_data}

## 相关补丁原文

{matched_patches_text}

---

## 输出要求

**【字数】2000+ 中文字符。如果数据不足，明确说明后尽力展开分析。**
**【格式】直接输出 Markdown 格式报告，不要用 JSON，不要用代码块包裹。**
**【报告结构】按以下六节展开：**

# {problem_name}——设计演进深度分析报告

## 一、研究问题的本质
深度阐述这个设计问题的核心矛盾是什么，设计师在试图解决什么问题。

## 二、历代解决方案的深度拆解
对每一个世代/版本区间（严格基于上述演进枝数据）：
- **具体机制**：用了什么机制来解决这个问题？
- **设计意图**：设计师当时想达到什么目标？
- **实际效果**：玩家社区的反馈如何？有没有数据支撑？
- **局限性**：为什么这个方案最终不够好？
- **后续演进**：设计师从这个方案中学到了什么？

## 三、设计师的决策逻辑演变
从历代方案中，提炼设计师思路的变化规律。特别关注：
- 每一代的设计师是如何借鉴或否定前一代方案的？
- 是否有某些设计原则从未改变？为什么？

## 四、跨游戏对比
如果有数据，对比其他类似游戏在类似问题上的解法。

## 五、问题的本质与未来方向
这个问题的根本矛盾在哪里？历代方案是在治标还是治本？未来应该如何设计？

## 六、关键设计洞察
总结 3~5 条可指导未来设计的原则，每条原则要写清楚"在什么情况下适用"和"可能的边界"。

---

请基于上述数据，生成深度分析报告：
"""


# 传统扁平主题报告模板（向后兼容）
ANALYSIS_PROMPT_TEMPLATE = """你是游戏设计演进研究专家，专注于分析游戏更新背后的设计逻辑和迭代规律。

## 研究目标
- **主题**：「{topic_name}」
- **研究问题**：{topic_description}
- **核心意义**：{why_important}

## 数据基础
以下是从真实更新日志中提取的 {patch_count} 条相关更新，请基于这些数据进行分析。
{has_context_note}

---

{matched_patches_text}

---

## 输出要求

**【字数】2000+ 中文字符。如果数据不足，明确说明后尽力展开分析。**
**【格式】直接输出 Markdown 格式报告，不要用 JSON，不要用代码块包裹。**
**【深度】这是研究型报告，要说清楚：**
- 这个设计问题在每一代/每一个版本中具体是怎么表现的？
- 设计师尝试了哪些不同的解法？
- 每种解法为什么有效或无效？
- 玩家社区对每种解法的真实反馈是什么？
- 设计师在后续版本中是如何基于之前的经验迭代的？
- 这个问题的本质是什么？有没有根本性的解决方案？
- 跨游戏的比较：其他类似游戏有没有类似的设计尝试？效果如何？

## 报告结构

# {topic_name}——设计演进深度分析报告

## 一、研究问题的本质
深度阐述这个设计问题的核心矛盾是什么

## 二、历代解决方案的深度拆解
对每一个世代/版本区间：
- **具体机制**：用了什么机制来解决这个问题？
- **设计意图**：设计师当时想达到什么目标？
- **实际效果**：玩家社区的反馈如何？
- **局限性**：为什么这个方案最终不够好？
- **后续演进**：设计师从这个方案中学到了什么？

## 三、设计师的决策逻辑演变
从历代方案中，提炼设计师思路的变化

## 四、跨游戏对比
如果有数据，对比其他类似游戏在类似问题上的解法

## 五、问题的本质与未来方向
这个问题的根本矛盾在哪里？理想状态下应该怎么设计？

## 六、关键设计洞察
总结 3-5 条可指导未来设计的原则

---

请基于上述数据，生成深度分析报告：
"""


class EvolutionReportGenerator:
    """演进报告生成器 - 支持分层主题树"""

    def __init__(self, extractor):
        self.extractor = extractor

    MAX_PATCH_CONTENT_LENGTH = 800

    def _format_patches_for_prompt(self, patches: list) -> str:
        """将更新列表格式化为 Prompt 文本"""
        lines = []
        for i, patch in enumerate(patches):
            lines.append(f"### 更新 {i + 1}")
            lines.append(f"版本: {patch.get('version', patch.get('date', 'N/A'))}")
            lines.append(f"日期: {patch.get('date', 'N/A')}")
            lines.append(f"游戏: {patch.get('game', 'N/A')}")
            lines.append(f"标题: {patch.get('title', 'N/A')}")
            content = patch.get('content', 'N/A')
            if len(content) > self.MAX_PATCH_CONTENT_LENGTH:
                content = content[:self.MAX_PATCH_CONTENT_LENGTH] + "..."
            lines.append(f"内容: {content}")
            lines.append("")
        return "\n".join(lines)

    def _extract_markdown_response(self, text: str) -> str:
        """提取 LLM 返回的 Markdown 报告"""
        md_match = re.search(r"```(?:markdown)?\s*([\s\S]*?)\s*```", text)
        if md_match:
            return md_match.group(1).strip()
        return text.strip()

    def match_patches_by_keywords(self, all_patches: list, keywords: list) -> list:
        """
        根据关键词从所有更新中匹配相关更新
        支持模糊匹配：关键词出现在标题或内容中即匹配
        """
        if not keywords:
            return all_patches[:10]

        matched = []
        for patch in all_patches:
            text = (patch.get("title", "") + " " + patch.get("content", "")).lower()
            for kw in keywords:
                if kw.lower() in text:
                    matched.append(patch)
                    break
        return matched

    def _build_evolution_data_text(self, branch: dict) -> str:
        """将演进枝数据格式化为可读的文本段落"""
        stages = branch.get("evolution_stages", [])
        if not stages:
            return "（无历代演进数据）"

        lines = []
        for stage in stages:
            period = stage.get("period", "未知时期")
            solution = stage.get("solution", "无描述")
            patch_titles = stage.get("patch_titles", [])
            lines.append(f"**{period}**：{solution}")
            if patch_titles:
                lines.append(f"  - 相关补丁：{'、'.join(patch_titles)}")
            lines.append("")
        return "\n".join(lines)

    def _extract_patch_titles_from_branch(self, branch: dict) -> list:
        """从演进枝中提取所有相关补丁标题"""
        titles = []
        for stage in branch.get("evolution_stages", []):
            titles.extend(stage.get("patch_titles", []))
        return list(dict.fromkeys(titles))

    def generate_report(
        self,
        topic: dict,
        all_patches: list,
    ) -> Optional[dict]:
        """
        为动态发现的研究主题生成演进报告

        支持两种主题格式：
        1. 树形主题：包含 _branch 和 _top_level 字段，直接利用演进枝结构
        2. 扁平主题：传统的 name + matched_preview 格式

        Returns:
            包含 "_markdown" 字段的报告字典，失败返回 None
        """
        # ---- 检测主题格式 ----
        branch = topic.get("_branch")
        top_level = topic.get("_top_level")

        if branch and top_level:
            # ---- 树形主题路径：利用预结构化的演进枝数据 ----
            dimension_name = top_level.get("name", "未命名维度")
            problem_name = branch.get("problem", topic.get("name", "未命名问题"))
            why_important = top_level.get("why_important", topic.get("why_important", ""))

            evolution_data = self._build_evolution_data_text(branch)
            patch_titles = self._extract_patch_titles_from_branch(branch)
            matched = self.match_patches_by_keywords(all_patches, patch_titles)

            if not matched:
                matched = self.match_patches_by_keywords(all_patches, topic.get("matched_preview", []))

            matched_text = self._format_patches_for_prompt(matched)
            patch_count = len(matched)

            has_context_note = ""
            if patch_count < 3:
                has_context_note = f"[数据较少，仅 {patch_count} 条相关更新，分析可能不够全面]"
            elif patch_count > 50:
                has_context_note = f"[数据丰富，{patch_count} 条相关更新，可以进行深入分析]"

            prompt = TREE_TOPIC_REPORT_TEMPLATE.format(
                dimension_name=dimension_name,
                problem_name=problem_name,
                why_important=why_important,
                evolution_data=evolution_data,
                matched_patches_text=matched_text,
                has_context_note=has_context_note,
                patch_count=patch_count,
            )
            topic_name = problem_name
        else:
            # ---- 扁平主题路径（向后兼容）----
            topic_name = topic.get("name", "未命名主题")
            topic_desc = topic.get("description", "")
            why_important = topic.get("why_important", "帮助理解历代设计师如何解决同类问题")
            matched_preview = topic.get("matched_preview", [])

            matched = self.match_patches_by_keywords(all_patches, matched_preview)
            if not matched:
                matched = all_patches[:10]

            matched_text = self._format_patches_for_prompt(matched)
            patch_count = len(matched)

            has_context_note = ""
            if patch_count < 3:
                has_context_note = f"[数据较少，仅 {patch_count} 条相关更新，分析可能不够全面]"
            elif patch_count > 50:
                has_context_note = f"[数据丰富，{patch_count} 条相关更新，可以进行深入分析]"

            prompt = ANALYSIS_PROMPT_TEMPLATE.format(
                topic_name=topic_name,
                topic_description=topic_desc,
                why_important=why_important,
                patch_count=patch_count,
                has_context_note=has_context_note,
                matched_patches_text=matched_text,
            )

        llm = self.extractor._get_llm()
        if llm is None:
            return {
                "_error": True,
                "_message": "LLM 不可用，无法生成演进报告",
                "research_question": topic_name,
                "matched_count": patch_count,
            }

        try:
            from langchain_core.runnables import RunnableConfig
            config = RunnableConfig(
                timeout=180.0,
                max_retries=2,
            )
            response = llm.invoke(prompt, config=config)
            text = response.content if hasattr(response, "content") else str(response)
            markdown = self._extract_markdown_response(text)

            if markdown:
                _conf = "高" if patch_count >= 10 else ("中" if patch_count >= 3 else "低")
                return {
                    "_markdown": markdown,
                    "_topic": topic_name,
                    "_matched_count": patch_count,
                    "_topic_description": topic.get("description", ""),
                    "_is_tree_topic": branch is not None,
                    "_confidence": _conf,
                }
            else:
                return {
                    "_error": True,
                    "_message": "AI 未返回有效报告内容",
                    "research_question": topic_name,
                    "matched_count": patch_count,
                }

        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str or "timed out" in error_str:
                error_msg = "生成超时：请求时间过长，建议稍后重试"
            elif "rate limit" in error_str or "429" in error_str:
                error_msg = "请求频率超限，请等待几秒后重试"
            else:
                error_msg = f"生成失败: {e}"
            return {
                "_error": True,
                "_message": error_msg,
                "research_question": topic_name,
                "matched_count": patch_count,
            }

    def get_available_topics(self) -> list:
        """
        获取预置主题列表（保留兼容性，仅用于展示）
        新流程中不再使用预置主题，而是动态发现
        """
        return []

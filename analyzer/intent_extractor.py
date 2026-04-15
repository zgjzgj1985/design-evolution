"""
LLM 设计意图提取器
调用大语言模型分析游戏版本更新的设计意图
"""

import json
import os
import re
from typing import Optional
from utils.config import config
from analyzer.prompts import DESIGN_INTENT_PROMPT, GAME_DESIGN_CONTEXT, SIMPLE_EXTRACT_PROMPT


class IntentExtractor:
    """设计意图提取器"""

    def __init__(self, provider: str = None, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化提取器

        Args:
            provider: LLM 提供商 ("openai" | "anthropic" | "openrouter")
            api_key: API Key（优先于 config）
            base_url: API 地址（留空用对应 provider 默认地址）
            model: 模型名称（留空用 provider 默认模型）
        """
        self.provider = provider or "openrouter"
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._llm = None
        self._embedding = None
        # 禁用自动代理检测，避免代理认证问题
        # 如果需要使用代理，请在 .env 中手动配置 HTTP_PROXY / HTTPS_PROXY
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)

    def _get_llm(self):
        """延迟初始化 LLM（节省 API 调用）"""
        if self._llm is None:
            api_key = self._api_key if self._api_key else config.LLM_API_KEY

            if not api_key or api_key in ("sk-your-api-key-here", "your-api-key", ""):
                print(f"警告: 未配置 API Key | provider={self.provider}, api_key={repr(api_key)}")
                return None

            print(f"初始化 LLM: provider={self.provider}, model={self._model or config.LLM_MODEL}, base_url={self._base_url}")
            model = self._model or config.LLM_MODEL

            if self.provider == "anthropic":
                try:
                    from langchain_anthropic import ChatAnthropic
                    self._llm = ChatAnthropic(
                        model=model,
                        anthropic_api_key=api_key,
                        temperature=0.7,
                    )
                    return self._llm
                except ImportError:
                    print("警告: langchain-anthropic 未安装")
                    return None
                except Exception as e:
                    print(f"连接 Anthropic 失败: {e}")
                    return None

            base = self._base_url
            if not base:
                if self.provider == "openrouter":
                    base = config.OPENROUTER_BASE_URL
                elif self.provider == "openai":
                    base = None

            print(f"初始化 LLM: provider={self.provider}, model={self._model}, base_url={base}")

            try:
                from langchain_openai import ChatOpenAI
                model_kwargs = {
                    "temperature": 0.7,
                    "request_timeout": 180,
                    "max_retries": 3,
                    "default_headers": {"api-version": "2024-01-01"},
                }
                if base:
                    model_kwargs["base_url"] = base
                self._llm = ChatOpenAI(
                    model=model,
                    api_key=api_key,
                    **model_kwargs,
                )
                if base:
                    api_url = base.rstrip("/") + "/chat/completions"
                    print(f"  → 实际调用 URL: {api_url}")
                return self._llm
            except ImportError:
                print("警告: langchain-openai 未安装")
                return None
            except Exception as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "429" in str(e):
                    print(f"OpenRouter 频率限制: {e}")
                elif "connection" in error_msg or "timeout" in error_msg:
                    print(f"连接失败: {e}")
                elif "invalid" in error_msg and "api key" in error_msg:
                    print(f"API Key 无效: {e}")
                else:
                    print(f"LLM 初始化失败: {e}")
                return None

        return self._llm

    def _get_embedding(self):
        """延迟初始化 Embedding 模型"""
        if self._embedding is None:
            try:
                from langchain_openai import OpenAIEmbeddings
                model_kwargs = {}
                if self._base_url:
                    model_kwargs["base_url"] = self._base_url
                self._embedding = OpenAIEmbeddings(
                    model=config.EMBEDDING_MODEL,
                    api_key=self._api_key or "",
                    **model_kwargs,
                )
            except ImportError:
                print("警告: Embedding 模型初始化失败")
        return self._embedding

    def analyze_intent(
        self,
        game: str,
        version: str,
        date: str,
        content: str,
    ) -> Optional[dict]:
        """
        分析单条更新日志的设计意图

        Args:
            game: 游戏名称
            version: 版本号
            date: 发布日期
            content: 更新内容

        Returns:
            包含分析结果的字典，如果失败返回 None
        """
        llm = self._get_llm()
        if llm is None:
            print(f"[analyze_intent] LLM 不可用，返回降级分析 | provider={self.provider}, model={self._model}")
            return None

        prompt = DESIGN_INTENT_PROMPT.format(
            game=game,
            version=version,
            date=date,
            content=content,
            GAME_DESIGN_CONTEXT=GAME_DESIGN_CONTEXT,
        )

        try:
            print(f"[analyze_intent] 正在调用 LLM 分析...")
            response = llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            result = self._parse_json_response(text)
            if result is None:
                print(f"[analyze_intent] 解析 LLM 响应失败 | text[:100]={text[:100]}")
            return result
        except Exception as e:
            print(f"[analyze_intent] LLM 调用失败: {e}")
            return None

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
            print("JSON 解析失败，原始响应:", text[:200])
            return None

    def _fallback_analysis(self, game: str, version: str, content: str) -> dict:
        """当 LLM 不可用时的降级分析"""
        content_lower = content.lower()

        tags = []
        if any(kw in content_lower for kw in ["vgc", "对战", "双打", "单打", "规则", "ban"]):
            tags.append("PvP")
        if any(kw in content_lower for kw in ["团体战", "raid", "合作", "多人"]):
            tags.append("PvE")
        if any(kw in content_lower for kw in ["极巨化", "太晶化", "特性", "技能"]):
            tags.append("机制")
        if any(kw in content_lower for kw in ["调整", "修改", "nerf", "buff"]):
            tags.append("平衡性")

        problem = "改善游戏体验"
        if "削弱" in content_lower or "nerf" in content_lower:
            problem = "降低某机制/宝可梦的过强表现"
        elif "增强" in content_lower or "buff" in content_lower:
            problem = "提升某机制/宝可梦的竞争力"

        # Infer player sentiment from keywords
        if any(kw in content_lower for kw in ["bug", "修复", "崩溃", "错误"]):
            sentiment = "修复类改动通常获得正面或中性反应——取决于修复的严重程度"
        elif any(kw in content_lower for kw in ["削弱", "限制", "禁止", "ban", "负面"]):
            sentiment = "削弱类改动通常引发竞技玩家负面反应，休闲玩家可能无感知或正面"
        elif any(kw in content_lower for kw in ["新增", "添加", "扩展", "免费"]):
            sentiment = "新增内容通常获得正面反应"
        else:
            sentiment = "无明显情感倾向的改动，玩家反应取决于具体内容"

        return {
            "exact_change": f"[降级分析] {content[:50]}...",
            "competitive_impact": "无法评估（LLM 不可用）",
            "design_rationale": problem,
            "player_feedback": sentiment,
            "player_impact": ["所有玩家"],
            "mechanic_tags": tags if tags else ["其他"],
            "design_pattern": "优化性设计",
            "risk_assessment": "无法评估（LLM 不可用）",
            "related_changes": [],
            "_fallback": True,
        }

    def classify_patch(self, content: str, game: str = "Pokemon") -> Optional[dict]:
        """
        轻量分类：判断更新是否与多人对战相关（复用 SIMPLE_EXTRACT_PROMPT）

        Args:
            content: 更新内容
            game: 游戏名称

        Returns:
            分类结果 dict，包含 is_multiplayer_related / type / mechanics / balance_impact / summary
            如果 LLM 不可用返回 None
        """
        llm = self._get_llm()
        if llm is None:
            return None

        prompt = SIMPLE_EXTRACT_PROMPT.format(content=content)
        try:
            response = llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            result = self._parse_json_response(text)
            if result:
                # 补充 is_multiplayer_related 字段
                # 只严格标记纯 PvP / PvE，"混合"不算（研究主题是"多人对战机制"，混合内容容易误报）
                type_val = result.get("type", "其他")
                result["is_multiplayer_related"] = type_val in ("PvP", "PvE")
                # mechanics 如果是字符串则转列表
                if isinstance(result.get("mechanics"), str):
                    result["mechanics"] = [result["mechanics"]]
            return result
        except Exception as e:
            print(f"LLM 分类失败: {e}")
            return None

    def batch_analyze(
        self,
        updates: list,
        game: str = "Pokemon",
    ) -> list:
        """批量分析多条更新日志"""
        results = []
        for update in updates:
            if "changes" in update:
                for change in update["changes"]:
                    result = self.analyze_intent(
                        game=game,
                        version=update.get("version", ""),
                        date=update.get("date", ""),
                        content=change.get("content", ""),
                    )
                    if result:
                        result["category"] = change.get("category", "其他")
                        result["original_content"] = change.get("content", "")
                        results.append(result)
            else:
                result = self.analyze_intent(
                    game=game,
                    version=update.get("version", ""),
                    date=update.get("date", ""),
                    content=update.get("content", ""),
                )
                if result:
                    result["original_content"] = update.get("content", "")
                    results.append(result)
        return results

    def get_vector_store(self):
        """获取向量存储（用于语义搜索）"""
        try:
            from db.vector_store import VectorStore
            return VectorStore()
        except Exception as e:
            print(f"向量存储初始化失败: {e}")
            return None

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list:
        """语义搜索相关设计意图"""
        store = self.get_vector_store()
        if store is None:
            return []
        return store.search(query, top_k)

    def test_connection(self) -> dict:
        """
        测试 LLM 连接状态

        Returns:
            dict: {
                "success": bool,
                "message": str,
                "latency_ms": int or None,
                "model": str,
                "provider": str,
            }
        """
        import time
        result = {
            "success": False,
            "message": "",
            "latency_ms": None,
            "model": None,
            "provider": self.provider,
        }

        api_key = self._api_key if self._api_key else config.LLM_API_KEY
        if not api_key or api_key in ("sk-your-api-key-here", "your-api-key", ""):
            result["message"] = "未配置 API Key"
            return result

        model = self._model or config.LLM_MODEL
        base = self._base_url
        if not base:
            if self.provider == "openrouter":
                base = config.OPENROUTER_BASE_URL
            elif self.provider == "openai":
                base = None

        result["model"] = model

        try:
            from langchain_openai import ChatOpenAI
            model_kwargs = {
                "temperature": 0,
                "request_timeout": 60,
                "max_retries": 2,
            }
            if base:
                model_kwargs["base_url"] = base

            llm = ChatOpenAI(model=model, api_key=api_key, **model_kwargs)

            start = time.time()
            response = llm.invoke("你好，请回复 OK")
            latency = int((time.time() - start) * 1000)

            result["latency_ms"] = latency
            text = response.content if hasattr(response, "content") else str(response)

            if "ok" in text.lower() or text.strip():
                result["success"] = True
                result["message"] = f"连接成功 | 延迟: {latency}ms"
            else:
                result["message"] = f"响应异常: {text[:50]}"

        except Exception as e:
            error_msg = str(e)
            result["message"] = error_msg
            # 分类常见错误
            error_lower = error_msg.lower()
            if "blocked" in error_lower or "forbidden" in error_lower or "403" in error_msg:
                result["message"] = f"请求被拒绝 (blocked) | {error_msg[:100]}"
            elif "401" in error_msg or "unauthorized" in error_lower:
                result["message"] = "API Key 无效或已过期"
            elif "429" in error_msg or "rate limit" in error_lower:
                result["message"] = "请求频率超限，请稍后再试"
            elif "connection" in error_lower or "timeout" in error_lower:
                result["message"] = f"连接超时或网络问题 | {error_msg[:100]}"
            else:
                result["message"] = f"连接失败: {error_msg[:200]}"

        return result

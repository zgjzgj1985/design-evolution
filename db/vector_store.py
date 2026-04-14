"""
ChromaDB 向量数据库模块
用于存储和检索设计意图的语义向量
"""

from pathlib import Path
from typing import List, Optional
import json
from utils.config import config


class VectorStore:
    """向量数据库管理类"""

    def __init__(self, persist_dir: Path = None):
        self.persist_dir = persist_dir or config.CHROMA_PERSIST_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None

    def _get_client(self):
        """获取 ChromaDB 客户端"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                self._client = chromadb.PersistentClient(
                    path=str(self.persist_dir),
                    settings=Settings(anonymized_telemetry=False),
                )
            except ImportError:
                print("警告: ChromaDB 未安装，语义搜索功能不可用")
                return None
        return self._client

    def _get_collection(self, name: str = "design_intents"):
        """获取或创建集合"""
        client = self._get_client()
        if client is None:
            return None

        if self._collection is None:
            self._collection = client.get_or_create_collection(
                name=name,
                metadata={"description": "游戏设计意图向量存储"},
            )
        return self._collection

    def add_intent(
        self,
        text: str,
        metadata: dict,
        intent_id: str = None,
    ) -> str:
        """
        添加设计意图到向量库

        Args:
            text: 要向量化的文本（通常是设计意图摘要）
            metadata: 关联的元数据
            intent_id: 可选的 ID

        Returns:
            添加的 ID
        """
        collection = self._get_collection()
        if collection is None:
            return None

        # 生成 ID
        if intent_id is None:
            import uuid
            intent_id = str(uuid.uuid4())

        # 转换 metadata 中的列表为字符串
        clean_metadata = {}
        for k, v in metadata.items():
            if isinstance(v, (list, dict)):
                clean_metadata[k] = json.dumps(v, ensure_ascii=False)
            else:
                clean_metadata[k] = str(v)

        try:
            collection.add(
                documents=[text],
                metadatas=[clean_metadata],
                ids=[intent_id],
            )
        except Exception as e:
            print(f"添加向量失败: {e}")
            return None

        return intent_id

    def search(
        self,
        query: str,
        top_k: int = 5,
        game: str = None,
        filter_tags: list = None,
    ) -> List[dict]:
        """
        语义搜索设计意图

        Args:
            query: 搜索查询
            top_k: 返回结果数量
            game: 可选的游戏过滤
            filter_tags: 可选的标签过滤

        Returns:
            搜索结果列表
        """
        collection = self._get_collection()
        if collection is None:
            return []

        # 构建过滤条件
        where_filter = None
        if game or filter_tags:
            conditions = []
            if game:
                conditions.append({"game": game})
            if filter_tags:
                for tag in filter_tags:
                    conditions.append({"mechanic_tags": {"$contains": tag}})

            if conditions:
                where_filter = {"$and": conditions} if len(conditions) > 1 else conditions[0]

        try:
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter,
            )

            # 格式化结果
            formatted = []
            if results and results["ids"]:
                for i, doc_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0

                    # 解析 JSON 字段
                    parsed_metadata = {}
                    for k, v in metadata.items():
                        if isinstance(v, str) and v.startswith("["):
                            try:
                                parsed_metadata[k] = json.loads(v)
                            except json.JSONDecodeError:
                                parsed_metadata[k] = v
                        else:
                            parsed_metadata[k] = v

                    formatted.append({
                        "id": doc_id,
                        "text": results["documents"][0][i] if results["documents"] else "",
                        "metadata": parsed_metadata,
                        "similarity": 1 - distance if distance <= 1 else 0,
                    })

            return formatted
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def get_by_tag(self, tag: str, top_k: int = 20) -> List[dict]:
        """按标签获取设计意图"""
        collection = self._get_collection()
        if collection is None:
            return []

        try:
            results = collection.get(
                where={"mechanic_tags": {"$contains": tag}},
                limit=top_k,
            )

            formatted = []
            if results and results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    metadata = results["metadatas"][i] if results["metadatas"] else {}
                    formatted.append({
                        "id": doc_id,
                        "text": results["documents"][i] if results["documents"] else "",
                        "metadata": metadata,
                    })

            return formatted
        except Exception as e:
            print(f"按标签查询失败: {e}")
            return []

    def delete(self, intent_id: str) -> bool:
        """删除设计意图"""
        collection = self._get_collection()
        if collection is None:
            return False

        try:
            collection.delete(ids=[intent_id])
            return True
        except Exception as e:
            print(f"删除失败: {e}")
            return False

    def count(self) -> int:
        """获取向量库中的条目数量"""
        collection = self._get_collection()
        if collection is None:
            return 0

        try:
            return collection.count()
        except Exception:
            return 0

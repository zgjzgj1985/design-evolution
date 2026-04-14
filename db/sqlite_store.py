"""
SQLite 结构化数据存储模块
存储版本信息、更新日志、分析结果等结构化数据
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from utils.config import config


class SQLiteStore:
    """SQLite 数据库管理类"""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or config.SQLITE_DB_PATH
        self._init_db()

    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 游戏表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 版本/世代表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                version TEXT NOT NULL,
                release_date TEXT,
                region TEXT,
                generation INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(id),
                UNIQUE(game_id, version)
            )
        """)

        # 更新日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id INTEGER,
                game TEXT,
                patch_date TEXT,
                patch_title TEXT,
                content TEXT,
                categories TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (version_id) REFERENCES versions(id)
            )
        """)

        # 设计意图分析结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patch_id INTEGER,
                game TEXT,
                version TEXT,
                content TEXT,
                intent_summary TEXT,
                problem_solved TEXT,
                affected_players TEXT,
                mechanic_tags TEXT,
                design_pattern TEXT,
                risk_assessment TEXT,
                related_changes TEXT,
                raw_response TEXT,
                is_fallback BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patch_id) REFERENCES patches(id)
            )
        """)

        # 索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patches_game ON patches(game)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_game ON analysis_results(game)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_tags ON analysis_results(mechanic_tags)")

        # AI 分类结果表（缓存，避免重复调用 LLM）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patch_classifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                content_preview TEXT,
                patch_date TEXT,
                patch_title TEXT,
                classification_type TEXT,
                mechanics TEXT,
                balance_impact TEXT,
                summary TEXT,
                is_multiplayer_related INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(game, content_hash)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classifications_hash ON patch_classifications(content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classifications_game ON patch_classifications(game)")

        conn.commit()
        conn.close()

    def _dict_to_json(self, d: dict) -> str:
        """字典转 JSON 字符串"""
        return json.dumps(d, ensure_ascii=False)

    def _json_to_dict(self, json_str: str) -> dict:
        """JSON 字符串转字典"""
        if not json_str:
            return {}
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {}

    # ========== 游戏管理 ==========

    def add_game(self, name: str, display_name: str = None, description: str = None) -> int:
        """添加游戏"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO games (name, display_name, description) VALUES (?, ?, ?)",
            (name, display_name or name, description),
        )
        cursor.execute("SELECT id FROM games WHERE name = ?", (name,))
        game_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return game_id

    def get_games(self) -> List[dict]:
        """获取所有游戏"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, display_name, description FROM games")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "display_name": r[2], "description": r[3]} for r in rows]

    # ========== 版本管理 ==========

    def add_version(
        self,
        game_id: int,
        version: str,
        release_date: str = None,
        generation: int = None,
        region: str = None,
        notes: str = None,
    ) -> int:
        """添加版本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR IGNORE INTO versions
               (game_id, version, release_date, generation, region, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (game_id, version, release_date, generation, region, notes),
        )
        cursor.execute("SELECT id FROM versions WHERE game_id = ? AND version = ?", (game_id, version))
        version_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return version_id

    def get_versions(self, game_id: int) -> List[dict]:
        """获取游戏的版本列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, version, release_date, generation, region FROM versions WHERE game_id = ? ORDER BY release_date",
            (game_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "version": r[1], "release_date": r[2], "generation": r[3], "region": r[4]} for r in rows]

    # ========== 更新日志管理 ==========

    def add_patch(
        self,
        version_id: int,
        game: str,
        patch_date: str,
        patch_title: str,
        content: str,
        categories: list = None,
        url: str = None,
    ) -> int:
        """添加更新日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO patches
               (version_id, game, patch_date, patch_title, content, categories, url)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (version_id, game, patch_date, patch_title, content, self._dict_to_json(categories or []), url),
        )
        patch_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return patch_id

    def get_patches(self, game: str = None, limit: int = 100) -> List[dict]:
        """获取更新日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if game:
            cursor.execute(
                "SELECT id, version_id, patch_date, patch_title, content, categories FROM patches WHERE game = ? ORDER BY patch_date DESC LIMIT ?",
                (game, limit),
            )
        else:
            cursor.execute("SELECT id, version_id, patch_date, patch_title, content, categories FROM patches ORDER BY patch_date DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "version_id": r[1],
                "patch_date": r[2],
                "patch_title": r[3],
                "content": r[4],
                "categories": self._json_to_dict(r[5]),
            }
            for r in rows
        ]

    # ========== 分析结果管理 ==========

    def add_analysis_result(self, result: dict) -> int:
        """保存分析结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO analysis_results
               (patch_id, game, version, content, intent_summary, problem_solved,
                affected_players, mechanic_tags, design_pattern, risk_assessment,
                related_changes, raw_response, is_fallback)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result.get("patch_id"),
                result.get("game"),
                result.get("version"),
                result.get("original_content", result.get("content")),
                result.get("intent_summary"),
                result.get("problem_solved"),
                self._dict_to_json(result.get("affected_players", [])),
                self._dict_to_json(result.get("mechanic_tags", [])),
                result.get("design_pattern"),
                result.get("risk_assessment"),
                self._dict_to_json(result.get("related_changes", [])),
                self._dict_to_json(result),
                1 if result.get("_fallback") else 0,
            ),
        )
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id

    def get_analysis_results(
        self,
        game: str = None,
        tags: list = None,
        limit: int = 100,
    ) -> List[dict]:
        """获取分析结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM analysis_results WHERE 1=1"
        params = []

        if game:
            query += " AND game = ?"
            params.append(game)

        if tags:
            # 简单的标签过滤（使用 LIKE，实际项目可用全文索引）
            tag_conditions = " OR ".join(["mechanic_tags LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f'%{tag}%' for tag in tags])

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        columns = [
            "id", "patch_id", "game", "version", "content", "intent_summary",
            "problem_solved", "affected_players", "mechanic_tags", "design_pattern",
            "risk_assessment", "related_changes", "raw_response", "is_fallback",
            "created_at",
        ]
        return [dict(zip(columns, row)) for row in rows]

    def get_analysis_by_version(self, game: str, version: str) -> List[dict]:
        """获取特定版本的分析结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM analysis_results WHERE game = ? AND version = ? ORDER BY created_at",
            (game, version),
        )
        rows = cursor.fetchall()
        conn.close()

        columns = [
            "id", "patch_id", "game", "version", "content", "intent_summary",
            "problem_solved", "affected_players", "mechanic_tags", "design_pattern",
            "risk_assessment", "related_changes", "raw_response", "is_fallback",
            "created_at",
        ]
        return [dict(zip(columns, row)) for row in rows]

    def search_analysis(self, keyword: str) -> List[dict]:
        """搜索分析结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        search_term = f"%{keyword}%"
        cursor.execute(
            """SELECT * FROM analysis_results
               WHERE content LIKE ? OR intent_summary LIKE ? OR problem_solved LIKE ?
               ORDER BY created_at DESC LIMIT 50""",
            (search_term, search_term, search_term),
        )
        rows = cursor.fetchall()
        conn.close()

        columns = [
            "id", "patch_id", "game", "version", "content", "intent_summary",
            "problem_solved", "affected_players", "mechanic_tags", "design_pattern",
            "risk_assessment", "related_changes", "raw_response", "is_fallback",
            "created_at",
        ]
        return [dict(zip(columns, row)) for row in rows]

    def get_stats(self, game: str = None) -> dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        if game:
            cursor.execute("SELECT COUNT(*) FROM patches WHERE game = ?", (game,))
            stats["total_patches"] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM analysis_results WHERE game = ?", (game,))
            stats["total_analyses"] = cursor.fetchone()[0]
        else:
            cursor.execute("SELECT COUNT(*) FROM patches")
            stats["total_patches"] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            stats["total_analyses"] = cursor.fetchone()[0]

        conn.close()
        return stats

    # ========== AI 分类缓存相关方法 ==========

    def add_classification(
        self,
        game: str,
        content_hash: str,
        content_preview: str,
        patch_date: str,
        patch_title: str,
        classification_type: str,
        mechanics: list,
        balance_impact: str,
        summary: str,
        is_multiplayer_related: bool = False,
    ) -> int:
        """保存 AI 分类结果（存在则忽略，保持唯一性）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT OR IGNORE INTO patch_classifications
                   (game, content_hash, content_preview, patch_date, patch_title,
                    classification_type, mechanics, balance_impact, summary, is_multiplayer_related)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    game,
                    content_hash,
                    content_preview[:200] if content_preview else "",
                    patch_date,
                    patch_title,
                    classification_type,
                    self._dict_to_json(mechanics or []),
                    balance_impact,
                    summary,
                    1 if is_multiplayer_related else 0,
                ),
            )
            cid = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()
        return cid

    def get_classification(self, game: str, content_hash: str) -> Optional[dict]:
        """通过内容哈希查询缓存的分类结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM patch_classifications WHERE game = ? AND content_hash = ?",
            (game, content_hash),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        columns = [
            "id", "game", "content_hash", "content_preview", "patch_date", "patch_title",
            "classification_type", "mechanics", "balance_impact", "summary",
            "is_multiplayer_related", "created_at",
        ]
        result = dict(zip(columns, row))
        result["mechanics"] = self._json_to_dict(result["mechanics"])
        result["is_multiplayer_related"] = bool(result["is_multiplayer_related"])
        
        # 字段映射：将数据库字段映射为应用期望的格式
        result["intent_summary"] = result.get("summary", "")
        result["mechanic_tags"] = result.get("mechanics", [])
        result["summary"] = result.get("summary", "")  # 保留兼容
        
        return result

    def get_multiplayer_patches(self, game: str) -> List[dict]:
        """获取标记为多人对战的更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM patch_classifications WHERE game = ? AND is_multiplayer_related = 1 ORDER BY patch_date DESC",
            (game,),
        )
        rows = cursor.fetchall()
        conn.close()
        columns = [
            "id", "game", "content_hash", "content_preview", "patch_date", "patch_title",
            "classification_type", "mechanics", "balance_impact", "summary",
            "is_multiplayer_related", "created_at",
        ]
        return [dict(zip(columns, r)) for r in rows]


# 全局数据库实例
db = SQLiteStore()

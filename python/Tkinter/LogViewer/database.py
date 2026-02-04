import sqlite3
import re

class LogDatabase:
    """SQLiteを使用したログストレージ。GUIには一切依存しない。"""
    
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        # SQLiteで正規表現を使用するためのカスタム関数
        self.conn.create_function("REGEXP", 2, self._regexp_callback)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, content TEXT)")

    def _regexp_callback(self, expr, item):
        """SQLiteから呼び出される正規表現バリデータ"""
        try:
            if not expr: return True
            return re.search(expr, item, re.IGNORECASE) is not None
        except Exception:
            return False

    def clear_and_import(self, lines):
        """データを全削除して一括挿入（高速化のためトランザクション使用）"""
        self.cursor.execute("DELETE FROM logs")
        self.conn.execute("BEGIN TRANSACTION")
        self.cursor.executemany("INSERT INTO logs (content) VALUES (?)", [(line,) for line in lines])
        self.conn.commit()

    def query_logs(self, patterns, limit, offset):
        """検索条件に基づいたログの取得"""
        where_sql, params = self._build_where(patterns)
        query = f"SELECT content FROM logs {where_sql} LIMIT ? OFFSET ?"
        self.cursor.execute(query, params + [limit, offset])
        return [row[0] for row in self.cursor.fetchall()]

    def get_total_count(self, patterns):
        """ヒット件数の取得（スクロール計算用）"""
        where_sql, params = self._build_where(patterns)
        self.cursor.execute(f"SELECT COUNT(*) FROM logs {where_sql}", params)
        return self.cursor.fetchone()[0]

    def _build_where(self, patterns):
        """複数の検索キーワードからWHERE句を動的に生成"""
        active_patterns = [p for p in patterns if p]
        if not active_patterns:
            return "", []
        where_sql = "WHERE " + " OR ".join(["content REGEXP ?" for _ in active_patterns])
        return where_sql, active_patterns

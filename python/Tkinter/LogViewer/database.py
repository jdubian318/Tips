import sqlite3
import re

class LogDatabase:
    """SQLiteを使用したログストレージ。GUIやスレッド管理には依存しない。"""
    
    def __init__(self, db_path=":memory:"):
        # check_same_thread=False は、マルチスレッド(非同期処理)でDBを扱う際に必須
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.create_function("REGEXP", 2, self._regexp_callback)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, content TEXT)")

    def _regexp_callback(self, expr, item):
        """正規表現のバリデーションロジック"""
        try:
            if not expr: return True
            return re.search(expr, item, re.IGNORECASE) is not None
        except Exception:
            return False

    def clear_and_import(self, lines):
        """データを一括挿入。コンテキストマネージャでトランザクションを安全に管理。"""
        try:
            with self.conn:  # 自動的に BEGIN / COMMIT / ROLLBACK を行う
                self.cursor.execute("DELETE FROM logs")
                self.cursor.executemany(
                    "INSERT INTO logs (content) VALUES (?)", 
                    [(line,) for line in lines]
                )
        except sqlite3.Error as e:
            raise RuntimeError(f"DBへの書き込みに失敗しました: {e}")

    def query_logs(self, patterns, limit, offset, mode="OR"):
        """フィルタリングされたログを指定範囲で取得"""
        where_sql, params = self._build_where(patterns, mode)
        query = f"SELECT content FROM logs {where_sql} LIMIT ? OFFSET ?"
        self.cursor.execute(query, params + [limit, offset])
        return [row[0] for row in self.cursor.fetchall()]

    def get_total_count(self, patterns, mode="OR"):
        """ヒット件数の合計を取得"""
        where_sql, params = self._build_where(patterns, mode)
        self.cursor.execute(f"SELECT COUNT(*) FROM logs {where_sql}", params)
        return self.cursor.fetchone()[0]

    def fetch_all_filtered(self, patterns, mode="OR"):
        """全件抽出用（エクスポートで使用）。ジェネレータでメモリを節約。"""
        where_sql, params = self._build_where(patterns, mode)
        # 直接executeの結果を回すことで、数百万行あっても一度にメモリに載せない
        query = self.conn.execute(f"SELECT content FROM logs {where_sql}", params)
        for row in query:
            yield row[0]

    def _build_where(self, patterns, mode="OR"):
        """検索キーワードからSQLのWHERE句を動的に生成"""
        active_patterns = [p for p in patterns if p]
        if not active_patterns:
            return "", []
        
        # AND検索かOR検索かを切り替え
        connector = " AND " if mode == "AND" else " OR "
        where_sql = "WHERE " + connector.join(["content REGEXP ?" for _ in active_patterns])
        return where_sql, active_patterns

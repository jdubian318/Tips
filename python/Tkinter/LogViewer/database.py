import sqlite3
import re

class LogDatabase:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.create_function("REGEXP", 2, self._regexp_callback)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, content TEXT)")

    def _regexp_callback(self, expr, item):
        try:
            if not expr: return True
            return re.search(expr, item, re.IGNORECASE) is not None
        except Exception:
            return False

    def clear_and_import(self, lines):
        with self.conn:
            self.cursor.execute("DELETE FROM logs")
            self.cursor.executemany("INSERT INTO logs (content) VALUES (?)", [(line,) for line in lines])

    def append_logs(self, lines):
        if not lines: return
        with self.conn:
            self.cursor.executemany("INSERT INTO logs (content) VALUES (?)", [(line,) for line in lines])

    def query_logs(self, patterns, limit, offset, mode="OR"):
        where_sql, params = self._build_where(patterns, mode)
        query = f"SELECT content FROM logs {where_sql} LIMIT ? OFFSET ?"
        self.cursor.execute(query, params + [limit, offset])
        return [row[0] for row in self.cursor.fetchall()]

    def get_total_count(self, patterns, mode="OR"):
        where_sql, params = self._build_where(patterns, mode)
        self.cursor.execute(f"SELECT COUNT(*) FROM logs {where_sql}", params)
        return self.cursor.fetchone()[0]

    def fetch_all_filtered(self, patterns, mode="OR"):
        where_sql, params = self._build_where(patterns, mode)
        query = self.conn.execute(f"SELECT content FROM logs {where_sql}", params)
        for row in query:
            yield row[0]

    def _build_where(self, patterns, mode="OR"):
        active = [p for p in patterns if p]
        if not active: return "", []
        connector = " AND " if mode == "AND" else " OR "
        where_sql = "WHERE " + connector.join(["content REGEXP ?" for _ in active])
        return where_sql, active

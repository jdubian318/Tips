import threading

class LogService:
    """ビジネスロジックを担当。ページング計算やファイルI/Oの管理。"""
    
    def __init__(self, db, page_limit=500):
        self.db = db
        self.page_limit = page_limit

    def get_display_data(self, patterns, raw_offset, mode="OR"):
        """現在のフィルタとスクロール位置から、表示に必要な情報を一括計算。"""
        total = self.db.get_total_count(patterns, mode)
        
        # オフセットを範囲内に収める(Clamping)
        max_offset = max(0, total - self.page_limit)
        safe_offset = max(0, min(raw_offset, max_offset))
        
        logs = self.db.query_logs(patterns, self.page_limit, safe_offset, mode)
        
        # スクロールバーの相対位置計算 (0.0 - 1.0)
        scroll_start = safe_offset / total if total > 0 else 0
        scroll_end = (safe_offset + self.page_limit) / total if total > 0 else 1
        
        return {
            "logs": logs,
            "total": total,
            "offset": safe_offset,
            "scroll_pos": (scroll_start, scroll_end)
        }

    def async_import(self, file_path, callback):
        """ファイルを別スレッドで読み込む（GUIを固まらせないため）"""
        def task():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f]
                self.db.clear_and_import(lines)
                callback(True, None) # 成功
            except Exception as e:
                callback(False, str(e)) # 失敗

        threading.Thread(target=task, daemon=True).start()

    def export_data(self, file_path, patterns, mode="OR"):
        """フィルタ結果をテキストファイルに書き出す"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in self.db.fetch_all_filtered(patterns, mode):
                    f.write(line + "\n")
            return True, None
        except Exception as e:
            return False, str(e)

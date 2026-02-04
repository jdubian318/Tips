import logging

# ロギングの設定（ファイルに出力するようにすれば、アプリ自体の不具合調査が容易に）
logging.basicConfig(level=logging.INFO, filename="app_debug.log")

class LogService:
    """UIとDBの仲介役。表示データやスクロール位置の計算を行う。"""
    
    def __init__(self, db, page_limit=500):
        self.db = db
        self.page_limit = page_limit

    def get_display_state(self, patterns, raw_offset):
        """
        現在のフィルター条件と希望オフセットから、
        実際に表示すべきデータと調整済みのオフセットを返す。
        """
        total = self.db.get_total_count(patterns)
        
        # オフセットが範囲外にならないよう調整 (Clamping)
        max_offset = max(0, total - self.page_limit)
        safe_offset = max(0, min(raw_offset, max_offset))
        
        logs = self.db.query_logs(patterns, self.page_limit, safe_offset)
        
        # スクロールバーの表示位置を0.0〜1.0で計算
        scroll_start = safe_offset / total if total > 0 else 0
        scroll_end = (safe_offset + self.page_limit) / total if total > 0 else 1
        
        return {
            "logs": logs,
            "total": total,
            "offset": safe_offset,
            "scroll_pos": (scroll_start, scroll_end)
        }

    def safe_import(self, file_path):
        """例外処理をラップしたインポート処理"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f]
            self.db.clear_and_import(lines)
            logging.info(f"Successfully imported {len(lines)} lines from {file_path}")
            return True, None
        except UnicodeDecodeError:
            return False, "文字コードがUTF-8ではありません。"
        except Exception as e:
            logging.error(f"Import error: {str(e)}")
            return False, f"予期せぬエラー: {str(e)}"

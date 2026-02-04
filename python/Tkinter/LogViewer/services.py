import threading
import time
import os

class LogService:
    def __init__(self, db, page_limit=500):
        self.db = db
        self.page_limit = page_limit
        self.tail_enabled = False
        self.last_filesize = 0
        self.current_file = None

    def get_display_data(self, patterns, raw_offset, mode="OR"):
        total = self.db.get_total_count(patterns, mode)
        max_offset = max(0, total - self.page_limit)
        safe_offset = max(0, min(raw_offset, max_offset))
        logs = self.db.query_logs(patterns, self.page_limit, safe_offset, mode)
        return {"logs": logs, "total": total, "offset": safe_offset}

    def async_import(self, file_path, callback):
        self.current_file = file_path
        def task():
            try:
                self.last_filesize = os.path.getsize(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f]
                self.db.clear_and_import(lines)
                callback(True, None)
            except Exception as e:
                callback(False, str(e))
        threading.Thread(target=task, daemon=True).start()

    def start_tail_worker(self, on_update_callback):
        self.tail_enabled = True
        def watch():
            while self.tail_enabled:
                if self.current_file and os.path.exists(self.current_file):
                    new_size = os.path.getsize(self.current_file)
                    if new_size > self.last_filesize:
                        self._read_diff(new_size, on_update_callback)
                time.sleep(1)
        threading.Thread(target=watch, daemon=True).start()

    def stop_tail(self):
        self.tail_enabled = False

    def _read_diff(self, new_size, callback):
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                f.seek(self.last_filesize)
                new_lines = [line.strip() for line in f if line.strip()]
                self.db.append_logs(new_lines)
                self.last_filesize = new_size
                callback()
        except Exception as e:
            print(f"Tail error: {e}")

    def export_data(self, file_path, patterns, mode="OR"):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in self.db.fetch_all_filtered(patterns, mode):
                    f.write(line + "\n")
            return True, None
        except Exception as e:
            return False, str(e)

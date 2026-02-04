import pytest
import os
import time
from database import LogDatabase
from services import LogService

def test_tail_append_logic(tmp_path):
    # 1. 初期ファイル作成
    log_file = tmp_path / "tail_test.log"
    log_file.write_text("Line 1\nLine 2\n", encoding='utf-8')
    
    db = LogDatabase(":memory:")
    service = LogService(db)
    
    # 2. 初回インポート
    service.async_import(str(log_file), lambda s, e: None)
    time.sleep(0.1) # 非同期処理待ち
    assert db.get_total_count([]) == 2
    
    # 3. ファイルに追記
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("Line 3\nLine 4\n")
    
    # 4. 差分読み込みの実行
    new_size = os.path.getsize(log_file)
    update_called = False
    def mock_callback(): nonlocal update_called; update_called = True
    
    service._read_diff(new_size, mock_callback)
    
    # 5. 検証
    assert db.get_total_count([]) == 4
    assert update_called is True
    # 元のデータが維持されているか確認
    logs = db.query_logs([], 4, 0)
    assert logs[0] == "Line 1"
    assert logs[3] == "Line 4"

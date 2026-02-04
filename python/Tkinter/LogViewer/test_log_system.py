import pytest
import os
from database import LogDatabase
from services import LogService

@pytest.fixture
def service():
    """テスト用の基本セットアップ。メモリDBを使用。"""
    db = LogDatabase(":memory:")
    # テストデータをインポート
    db.clear_and_import([
        "ERROR 2026-01-01 DB connection failed",
        "INFO  2026-01-01 System start",
        "ERROR 2026-01-02 Authentication failed",
        "DEBUG 2026-01-02 Trace data"
    ])
    return LogService(db, page_limit=2)

def test_or_search(service):
    """OR検索が正しく機能するか"""
    patterns = ["DB", "Auth"]
    # DB または Auth が含まれる2件がヒットするはず
    state = service.get_display_data(patterns, 0, mode="OR")
    assert state["total"] == 2
    assert any("DB connection" in log for log in state["logs"])

def test_and_search(service):
    """AND検索が正しく機能するか"""
    patterns = ["ERROR", "failed"]
    # ERROR かつ failed が含まれるのは2件
    state = service.get_display_data(patterns, 0, mode="AND")
    assert state["total"] == 2
    
    # どちらか一方だけだとヒットしない
    patterns_no_hit = ["INFO", "failed"]
    state_no_hit = service.get_display_data(patterns_no_hit, 0, mode="AND")
    assert state_no_hit["total"] == 0

def test_export_functionality(service, tmp_path):
    """エクスポートがファイルを正しく生成するか"""
    test_file = tmp_path / "export_test.txt"
    patterns = ["ERROR"]
    
    success, err = service.export_data(str(test_file), patterns)
    assert success is True
    
    with open(test_file, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 2
        assert "DB connection failed" in lines[0]

def test_clamping_logic(service):
    """大量のオフセットを指定しても末尾で止まるか"""
    state = service.get_display_data([], 9999) # 全件4件、ページ制限2
    # 最大オフセットは (4 - 2 = 2) になるはず
    assert state["offset"] == 2
    assert len(state["logs"]) == 2

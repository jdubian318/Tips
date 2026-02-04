import pytest
from database import LogDatabase
from services import LogService

@pytest.fixture
def mock_service():
    """テスト用のDBとサービスをセットアップ"""
    db = LogDatabase(":memory:")
    db.clear_and_import(["Error: Timeout", "Info: Success", "Debug: Logic", "Error: Crash"])
    return LogService(db, page_limit=2) # テスト用に表示制限を2に

def test_filtering(mock_service):
    """特定のキーワードで正しくフィルタリングされるか"""
    patterns = ["Error"]
    state = mock_service.get_display_state(patterns, 0)
    assert len(state["logs"]) == 2
    assert "Error: Timeout" in state["logs"]
    assert "Error: Crash" in state["logs"]

def test_pagination_clamping(mock_service):
    """オフセットが範囲外の時に正しく丸められるか"""
    patterns = [] # 全件表示
    # 4件あるログに対してオフセットを100にする
    state = mock_service.get_display_state(patterns, 100)
    # 最大オフセット (4 - 2 = 2) に丸められるはず
    assert state["offset"] == 2

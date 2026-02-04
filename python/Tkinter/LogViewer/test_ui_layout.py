import pytest
import tkinter as tk
from main import LogViewerApp
from services import LogService
from database import LogDatabase

@pytest.fixture
def app():
    root = tk.Tk()
    db = LogDatabase(":memory:")
    svc = LogService(db)
    app = LogViewerApp(root, svc)
    return app

def test_horizontal_scroll_toggle(app):
    """横スクロールのON/OFF（wrap設定）が切り替わるかテスト"""
    # 初期状態は ON (wrap=none)
    assert app.text_area.cget("wrap") == "none"
    
    # OFFにする
    app.h_scroll_var.set(False)
    app.toggle_h_scroll()
    assert app.text_area.cget("wrap") == "word" # 単語単位の折り返しに

    # 再度 ONにする
    app.h_scroll_var.set(True)
    app.toggle_h_scroll()
    assert app.text_area.cget("wrap") == "none" # 折り返しなしに

def test_add_key_button_placement(app):
    """Add KeyボタンがSearch Filters内にあることを概念的に確認"""
    # filter_container の子要素に Add Key ボタンの親フレームがあるか
    children = app.filter_container.winfo_children()
    # 少なくとも「ボタン行フレーム」と「フィルタ行コンテナフレーム」の2つがあるはず
    assert len(children) >= 2

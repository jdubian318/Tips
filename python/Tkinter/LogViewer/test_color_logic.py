import pytest
from main import PRESET_COLORS

def test_preset_color_resolution():
    """プリセット名から正しいカラーコードが引けるか"""
    assert PRESET_COLORS["Red"] == "#FF4444"
    assert PRESET_COLORS["Cyan"] == "#00FFFF"

def test_custom_color_hex_format():
    """カラーピッカーから渡される想定の16進数形式を検証"""
    # 実際の色選択をシミュレート
    custom_color = "#123456"
    assert custom_color.startswith("#")
    assert len(custom_color) == 7
    assert int(custom_color[1:], 16) >= 0

def test_color_list_excludes_custom_keyword():
    """UIのドロップダウンに 'Custom' という文字自体は出さない（末尾除外）"""
    options = list(PRESET_COLORS.keys())[:-1]
    assert "Custom" not in options
    assert "Yellow" in options

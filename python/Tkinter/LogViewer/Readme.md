# 準備

```bash
$ lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.5 LTS
Release:        22.04
Codename:       jammy

$ python3 --version
Python 3.13.5

$ apt install python3-pip
$ apt install python3-tk
$ pipenv --python 3.10
$ pipenv install tk
```

そのままインストールしたらうまく行かなかったので、
仮想環境にPython3.10を構築して実行。



# 実行

```bash
$ pipenv shell
(LogViewer) $ python main.py

```



# テスト実行

```bash
(LogViewer) $ pytest test_log_system.py
```



# 取説

## Professional Log Viewer

SQLiteエンジンを搭載した、高速・安全なエンジニア向けログ解析ツール。
数百万行のファイルもフリーズさせず、柔軟に検索・監視が可能です。

---

### ✨ 主な機能

- **高性能検索**: SQLite `REGEXP` による高速フィルタリング（AND/OR対応）。
- **ReadOnly設計**: 元のログファイルを一切変更・ロックしない安全設計。
- **Tail -f モード**: ファイルの追記をリアルタイムで自動検知。
- **デュアルスクロール**: 縦横スクロール対応（折り返し設定の切替可能）。
- **高度なハイライト**: プリセット色 + RGBカラーピッカーによる色分け。
- **エクスポート**: 抽出結果をフィルタリングした状態で保存。

---

### 🚀 使い方

1. **起動**: `python main.py` を実行。
2. **読込**: `Import File` からログを選択。
3. **検索**: `Search Filters` 内でキーワードを入力（正規表現可）。
4. **設定**: `Tail -f` や `Horizontal Scroll` で表示を最適化。
5. **保存**: 必要に応じて `Export Result` で書き出し。

---

### 🛠 プロジェクト構成

- **main.py**: GUI制御 (Tkinter)
- **services.py**: 非同期処理・Tail監視ロジック
- **database.py**: SQLite検索エンジン

---

### 🛡️ ライセンス
MIT License / 自由に変更・配布してご利用いただけます。

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



# 出だし

```python
import TkEasyGUI as eg
```


# 実行

```bash
$ pipenv shell
(simpleSample) $ python main.py

```


# テスト実行

```bash
$ pytest test_log_system.py
```


## OKパターン

```bash
(LogViewer) ken@ken-ThinkPad-X1-Carbon-6th:~/VBoxShare/code/Tips/python/Tkinter/LogViewer$ pytest test_log_system.py 
================================================================================================= test session starts ==================================================================================================
platform linux -- Python 3.10.12, pytest-9.0.2, pluggy-1.6.0
rootdir: /home/ken/VBoxShare/code/Tips/python/Tkinter/LogViewer
collected 2 items                                                                                                                                                                                                      

test_log_system.py ..                                                                                                                                                                                            [100%]

================================================================================================== 2 passed in 0.01s ===================================================================================================
```



## NGパターン

```bash
(LogViewer) ken@ken-ThinkPad-X1-Carbon-6th:~/VBoxShare/code/Tips/python/Tkinter/LogViewer$ pytest test_log_system.py 
================================================================================== test session starts ===================================================================================
platform linux -- Python 3.10.12, pytest-9.0.2, pluggy-1.6.0
rootdir: /home/ken/VBoxShare/code/Tips/python/Tkinter/LogViewer
collected 2 items                                                                                                                                                                        

test_log_system.py EE                                                                                                                                                              [100%]

========================================================================================= ERRORS =========================================================================================
____________________________________________________________________________ ERROR at setup of test_filtering ____________________________________________________________________________

    @pytest.fixture
    def mock_service():
        """テスト用のDBとサービスをセットアップ"""
        db = LogDatabase(":memory:")
>       db.clear_and_import(["Error: Timeout", "Info: Success", "Debug: Logic", "Error: Crash"])

test_log_system.py:9: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <database.LogDatabase object at 0x790949a9a3b0>, lines = ['Error: Timeout', 'Info: Success', 'Debug: Logic', 'Error: Crash']

    def clear_and_import(self, lines):
        """データを全削除して一括挿入（高速化のためトランザクション使用）"""
        self.cursor.execute("DELETE FROM logs")
>       self.conn.execute("BEGIN TRANSACTION")
E       sqlite3.OperationalError: cannot start a transaction within a transaction

database.py:28: OperationalError
_______________________________________________________________________ ERROR at setup of test_pagination_clamping _______________________________________________________________________

    @pytest.fixture
    def mock_service():
        """テスト用のDBとサービスをセットアップ"""
        db = LogDatabase(":memory:")
>       db.clear_and_import(["Error: Timeout", "Info: Success", "Debug: Logic", "Error: Crash"])

test_log_system.py:9: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <database.LogDatabase object at 0x790949a9aa40>, lines = ['Error: Timeout', 'Info: Success', 'Debug: Logic', 'Error: Crash']

    def clear_and_import(self, lines):
        """データを全削除して一括挿入（高速化のためトランザクション使用）"""
        self.cursor.execute("DELETE FROM logs")
>       self.conn.execute("BEGIN TRANSACTION")
E       sqlite3.OperationalError: cannot start a transaction within a transaction

database.py:28: OperationalError
================================================================================ short test summary info =================================================================================
ERROR test_log_system.py::test_filtering - sqlite3.OperationalError: cannot start a transaction within a transaction
ERROR test_log_system.py::test_pagination_clamping - sqlite3.OperationalError: cannot start a transaction within a transaction
=================================================================================== 2 errors in 0.08s ====================================================================================
(LogViewer) ken@ken-ThinkPad-X1-Carbon-6th:~/VBoxShare/code/Tips/python/Tkinter/LogViewer$ 
```

AIにログを読ませた結果。

```text
このエラーメッセージ sqlite3.OperationalError: cannot start a transaction within a transaction は、**「既にトランザクションが開始されているのに、重ねて BEGIN TRANSACTION を実行しようとした」**というエラーです。

Pythonの sqlite3 モジュールには、SQL（INSERTやDELETE）を実行すると自動的にトランザクションを開始するというデフォルトの挙動（分離レベル）があるため、明示的な BEGIN TRANSACTION と衝突してしまいました。
```

### 修正方法

database.py の clear_and_import メソッドを以下のように書き換えてください。


```python
def clear_and_import(self, lines):
        """データを全削除して一括挿入（高速化のためトランザクション使用）"""
        # autocommitモードでない場合、executeを実行した時点で自動的にトランザクションが始まります。
        # 明示的な "BEGIN TRANSACTION" を削除し、コンテキストマネージャを使うのがPython流で安全です。
        try:
            with self.conn:  # これだけで自動的に BEGIN / COMMIT / ROLLBACK を管理してくれます
                self.cursor.execute("DELETE FROM logs")
                self.cursor.executemany(
                    "INSERT INTO logs (content) VALUES (?)", 
                    [(line,) for line in lines]
                )
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
```

### なぜエラー（E）が出たのか？（解説）

1. 暗黙の開始: self.cursor.execute("DELETE FROM logs") を実行した瞬間、PythonのSQLiteライブラリが「あ、書き込みをするんだね」と判断して、勝手にトランザクションを開始します。

2. 重複の禁止: その直後の self.conn.execute("BEGIN TRANSACTION") は、SQLiteからすると「もう始まってるのに、また始めようとしてるぞ？」という二重定義になり、エラーを吐きました。

3. テスト結果の EE: test_log_system.py の結果が . (Pass) でも F (Fail) でもなく E (Error) になっているのは、「テストの中身を確認する前の『準備段階（fixture）』で壊れた」ことを示しています。




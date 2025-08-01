#!python3
# 上記を「Magic comment」という。

from itertools import product
from logical_caluculator import *

def 真理値表のヘッダー部を作成する(*命題記号リスト):
    項目名リスト = 命題記号リスト + ("Ans",)
    項目名の最大文字列長 = max( [len(項目名) for 項目名 in 項目名リスト] )
    # 全項目の文字幅を揃える
    # →末尾に空白文字を追加
    表ヘッダー項目リスト = []

    for 項目名 in 項目名リスト:
        n = 項目名の最大文字列長 - len(項目名)
        表ヘッダー項目リスト.append(項目名 + " " * n)

    tmp = "-" * 項目名の最大文字列長
    ライン = f"-{ tmp }-"
    # ライン = f"-{ "-" * 項目名の最大文字列長 }-"
    ラインリスト = (ライン,) * len(表ヘッダー項目リスト)

    # テーブルヘッダーの出力
    print(f"  { " | ".join(表ヘッダー項目リスト) }  ")
    print(f" { "+".join(ラインリスト) } ")
    
    return 項目名の最大文字列長


def 真理値表を表示する(*命題記号リスト, 論理式):
    # テーブルヘッダー
    項目名の最大文字列長 = 真理値表のヘッダー部を作成する(*命題記号リスト)

    # テーブルの中身
    tpl = (True, False)
    追加する空白文字 = " " * (項目名の最大文字列長 - 1)
    # ↑ "T" or "F" の1文字より長い分の空白を追加する

    # ------------------------------------------------------------
    # 論理式によって変更を加える箇所
    dic = { True: "T", False: "F" }
    for p, q in product(tpl, tpl):
        rows = (
            f"{ dic[p] + 追加する空白文字 }",
            f"{ dic[q] + 追加する空白文字 }",
            f"{ dic[論理式(p, q)] + 追加する空白文字 }",
        )
        print(f"  { " | ".join(rows) }  ")
    # ------------------------------------------------------------


def main():
    説明文A = """推論A
    前提1 : 日本人ならば、東洋人である。
    前提2 : 太郎は東洋人ではない。
    ゆえに
    結論 : 太郎は日本人ではない。
    ------------------------------
    P : 日本人である。
    Q : 東洋人である。
    ------------------------------
    (1) P ⇒ Q
    (2) ¬Q
    (3) ¬P
    """
    説明文_論理式A = """論理式
    (P ⇒ Q) ∧ ¬Q ⇒ ¬P
    """

    print("\n==================================================")
    print(説明文A)
    print(説明文_論理式A)
    真理値表を表示する("P", "Q", 論理式=論理式_推論A)
    # 真理値表を表示する("P", "Q", 論理式=lambda p, q: imp(all([imp(p,q), not q]), not p))


    説明文B = """推論B
    前提1 : 日本人ならば、東洋人である。
    前提2 : 太郎は日本人ではない。
    ゆえに
    結論 : 太郎は東洋人ではない。
    ------------------------------
    P : 日本人である。
    Q : 東洋人である。
    ------------------------------
    (1) P ⇒ Q
    (2) ¬P
    (3) ¬Q
    """
    説明文_論理式B = """論理式
    (P ⇒ Q) ∧ ¬P ⇒ ¬Q
    """

    print("\n==================================================")
    print(説明文B)
    print(説明文_論理式B)
    # 真理値表を表示する("P", "Q", 論理式=論理式_推論B)
    真理値表を表示する("P", "Q", 論理式=lambda p, q: imp(all([imp(p,q), not p]), not q))


# ------------------------------------------------------------
# 論理式によって変更を加える箇所
def 論理式_推論A(P, Q):
    前提条件 = all([imp(P, Q), not Q])
    結論 = not P
    return imp(前提条件, 結論)

def 論理式_推論B(P, Q):
    前提条件 = all([imp(P, Q), not P])
    結論 = not Q
    return imp(前提条件, 結論)
# ------------------------------------------------------------


if __name__ == "__main__":
    main()
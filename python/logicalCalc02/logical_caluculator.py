#!python3
# 上記を「Magic comment」という。

from typing import Callable

def imp(A, B) -> bool:
    """含意(implication), imp, ならば<br>
    A ⇒ B : ¬A ∨ B"""
    return (not A) or B

def iff(A, B) -> bool:
    """同値(equivalent), EQ, iff(if and only if)<br>
    A ⇔ B : ¬(A xor B)<br>
    A ⇔ B : (A ⇒ B) ∧ (B ⇒ A)"""
    return not (A ^ B)
    # 同上
    # return imp(A, B) and imp(B, A)

def forall(arr: list, P: Callable[[object], bool]) -> bool:
    """全称限量<br>
    ∀a ∈ A, P(a)<br>"""
    return all( P(a) for a in arr )

def exists(arr: list, P: Callable[[object], bool]) -> bool:
    """存在限量<br>
    ∃a ∈ A, P(a)<br>"""
    return any( P(a) for a in arr )

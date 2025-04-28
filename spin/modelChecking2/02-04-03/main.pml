/* LTL式定義 */
// LTL式：

/* 型定義 */
mtype = {s1, s2, s3, sa, sb, sc};
mtype = {M};

/* 変数宣言 */
chan c = [0] of {mtype}
mtype s=s1, t=sa;

/* 関数定義 */
active proctype p1()
{
    do
    ::s==s1 ->
    L1: atomic {
        c!M;
        s=s2
    }
    ::s==s2 ->
    L2: s=s3
    ::s==s3 ->
    L3: s=s1
    od
}

active proctype p2()
{
    do
    ::t==sa ->
    La: t=sb
    ::t==sb ->
    Lb: t=sc
    ::t==sc ->
    Lc: atomic {
        if
        ::c?M -> t=sa;
        ::true -> t=sc;
        fi
    }
    od
}
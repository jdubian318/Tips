/* LTL式定義 */
#if 0
// SWがoffならいずれonになる
// → OK
#define p (sw==off)
#define q (sw==on)
#endif

#if 1
// SWがonならいずれoffになる
// → NG
#define p (sw==on)
#define q (sw==off)
#endif

/* 型定義 */
mtype = {on, off};

/* 変数宣言 */
int a, b;
mtype sw;

int Na, Nb;
mtype Nsw;

/* 関数定義 */
active proctype alpha()
{
    a = 0;
    b = 0;
    sw = off;

    do
    ::true ->
        /* 次の瞬間の「a」の決定 */
        if
        ::(b==1) -> Na = a
        ::else ->
            if
            ::(a==0) -> Na = 1
            ::(a==1) -> Na = 2
            ::(a==2) -> Na = 0
            fi
        fi;
        /* 次の瞬間の「b」の決定 */
        if
        ::(a==b) -> Nb = b
        ::else ->
            if
            ::(b==0) -> Nb = 1
            ::(b==1) -> Nb = 2
            ::(b==2) -> Nb = 0
            fi
        fi;
        /* 次の瞬間の「sw」の決定 */
        if
        ::(a==2&&b==2) -> Nsw = on
        ::(a==1&&b==1) -> Nsw = off
        ::else         -> Nsw = sw
        fi;
        /* 値の更新 */
        atomic
        {
            a = Na;
            b = Nb;
            sw = Nsw;
        }
    od
}
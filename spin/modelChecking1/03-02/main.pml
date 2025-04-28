/* LTL式定義 */
// LTL式：F(p1∧P2∧(p3∨p4))
#define p1 (Sw1 == On)
#define p2 (Sw2 == On)
#define p3 (Sw3 == On)
#define p4 (Sw4 == On)

/* 型定義 */
mtype = {On, Off};

/* 変数宣言 */
mtype Sw1, Sw2, Sw3, Sw4;
int Tmr1, Tmr2, Tmr3, Tmr4;

/* 関数定義 */
active proctype circuit()
{
    /*** 初期設定 ***/
    Sw1 = Off;
    Sw2 = Off;
    Sw3 = Off;
    Sw4 = Off;
    Tmr1 = 2;
    Tmr2 = 3;
    Tmr3 = 1;
    Tmr4 = 2;

    /*** メインループ ***/
    do
    ::true ->
        atomic {
            if
            ::(Tmr1==5) -> Tmr1 = 1; Sw1 = On
            ::else      -> Tmr1 = Tmr1+1; Sw1 = Off
            fi;
            if
            ::(Tmr2==4) -> Tmr2 = 1; Sw2 = On
            ::else      -> Tmr2 = Tmr2+1; Sw2 = Off
            fi;
            if
            ::(Tmr3==6) -> Tmr3 = 1; Sw3 = On
            ::else      -> Tmr3 = Tmr3+1; Sw3 = Off
            fi;
            if
            ::(Tmr4==3) -> Tmr4 = 1; Sw4 = On
            ::else      -> Tmr4 = Tmr4+1; Sw4 = Off
            fi;
        }
    od
}
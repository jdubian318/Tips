/******************************************************************************
 * include宣言
 */
#include <stdio.h>


/******************************************************************************
 * 基本データ型 定義など
 */
typedef unsigned char UB;
typedef unsigned short UH;
typedef unsigned long UW;
typedef char    B;
typedef short   H;
typedef long    W;


#define TRUE    0xff
#define FALSE   0x00


// 入力系
static int sw_;
#define OFF             (0)
#define ON              (1)
#define SW_STAT_ON()    ((sw_ == ON) ? 1 : 0)


// 出力系
static int led_;
#define LED_ON()        { led_ = ON;  }
#define LED_OFF()       { led_ = OFF; }
#define LED_STAT_ON()   ((led_ == ON) ? 1 : 0)


// 出力マクロ
#define PRINT_MACRO(arg1, arg2) \
    do { \
        printf("arg1 = %d, arg2 = %d\n", arg1, arg2); \
    } while (0)


// 可変長引数マクロ
#define LPrint(args)    (printf args)

#define DEBUG
#ifdef DEBUG
    #define DLPrint(args)   (LPrint(args))
#else
    #define DLPrint(args)
#endif


/******************************************************************************
 * 型宣言
 */


/******************************************************************************
 * メイン
 */
int main(void)
{
    // 入力系
    sw_ = OFF;
    if (SW_STAT_ON()) {
        printf("SW_ON --> call LED_ON()\n");
        LED_ON();
    }
    else {
        printf("SW_OFF --> call LED_OFF()\n");
        LED_OFF();
    }

    // 出力系
    if (LED_STAT_ON()) {
        printf("LED ON\n");
    }
    else {
        printf("LED OFF\n");
    }

    // 出力マクロ
    PRINT_MACRO(1, 2);

    // 可変長引数マクロ
    LPrint(("LPrint Test: %d\n", 10));
    DLPrint(("DLPrint Test: %d\n", 10));

    return 0;
}


/******************************************************************************
<実行結果>

SW_OFF --> call LED_OFF()
LED OFF
arg1 = 1, arg2 = 2
LPrint Test: 10
DLPrint Test: 10

******************************************************************************/

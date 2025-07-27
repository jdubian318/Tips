/******************************************************************************
 * include宣言
 */
#include <stdio.h>      // perror
#include <stdlib.h>     // atoi, mkstemp, EXIT_SUCCESS, EXIT_FAILURE
#include <string.h>     // strlen, strcpy, strncpy, strtok, strcat, memset, memcpy
#include <sys/time.h>   // gettimeofday
#include <math.h>       // log10


/******************************************************************************
 * 基本データ型 定義など
 */

typedef unsigned char UB;
typedef unsigned short UH;
typedef unsigned long UW;
typedef char    B;
typedef short   H;
typedef long    W;


#define ARRAY_SIZE(arr) ( sizeof(arr) / sizeof(arr[0]) )

#define TRUE    (0xff)
#define FALSE   (0x00)

#define C_OK    TRUE
#define C_NG    FALSE

enum {
    KEYWORD  = 1,
    EXTERNAL = 2,
    STATIC   = 4,
};


/******************************************************************************
 * メイン
 */
int main(void)
{
    UH flags;

    printf("1. EXTERNAL と STATIC のビットを共にオンする\n");
    flags = 0;
    printf("before: 0x%04X\n", flags);
    flags |= EXTERNAL | STATIC;
    printf("after : 0x%04X\n", flags);
    printf("\n");

    printf("2. EXTERNAL と STATIC のビットをいずれもオフする\n");
    flags = 0xFFFF;
    printf("before: 0x%04X\n", flags);
    flags &= ~(EXTERNAL | STATIC);
    printf("after : 0x%04X\n", flags);
    printf("\n");

    printf("3. EXTERNAL と STATIC のいずれのビットもオフならば真\n");
    printf("target value: 0x%04X\n", flags);
    if ((flags & (EXTERNAL | STATIC)) == 0) {
        printf("EXTERNAL bit and STATIC bit is OFF\n");
    }
    else {
        printf("EXTERNAL bit or STATIC bit is ON\n");
    }
    printf("\n");

    return 0;
}


/******************************************************************************
<実行結果>

1. EXTERNAL と STATIC のビットを共にオンする
before: 0x0000
after : 0x0006

2. EXTERNAL と STATIC のビットをいずれもオフする
before: 0xFFFF
after : 0xFFF9

3. EXTERNAL と STATIC のいずれのビットもオフならば真
target value: 0xFFF9
EXTERNAL bit and STATIC bit is OFF

******************************************************************************/

/******************************************************************************
 * include宣言
 */
#include <stdio.h>  // perror
#include <stdlib.h> // atoi, mkstemp, EXIT_SUCCESS, EXIT_FAILURE
#include <string.h> // strlen, strcpy, strncpy, strtok, strcat, memset, memcpy


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
#define C_UnitLog_BuffSize  (128)
#define C_MessageQueSize    (100)


/******************************************************************************
 * 変数定義
 */
typedef struct {
    B String[C_UnitLog_BuffSize];
} LogString_t;

typedef struct {
    UH Wp;
    UH Rp;
    LogString_t LineData[C_MessageQueSize];
} Message_t;

static Message_t sendMessage;


/******************************************************************************
 * メッセージ・キュー初期化
 */
static void Init_Message(Message_t *trg)
{
    trg->Wp = 0;
    trg->Rp = 0;
}


/******************************************************************************
 * メッセージ・キューの空チェック
 */
static UB Check_MessageEmpty(Message_t *trg)
{
    return (trg->Wp == trg->Rp);
}


/******************************************************************************
 * メッセージ・キューに書き込み
 */
static void Put_Message(Message_t *trg, B *msg, size_t msgSize)
{
    H wpMax = ARRAY_SIZE(trg->LineData);

    memcpy(trg->LineData[trg->Wp].String, msg, msgSize);
    trg->Wp++;
    if (trg->Wp >= wpMax) {
        trg->Wp = 0;
    }
}


/******************************************************************************
 * メッセージ・キューから取り出し
 */
static UB Get_Message(Message_t *trg, B *msg, size_t msgSize)
{
    H rpMax = ARRAY_SIZE(trg->LineData);

    if (Check_MessageEmpty(trg)) {
        return C_NG;
    }

    memcpy(msg, trg->LineData[trg->Rp].String, msgSize);
    trg->Rp++;
    if (trg->Rp >= rpMax) {
        trg->Rp = 0;
    }

    return C_OK;
}


/******************************************************************************
 * メイン
 */
int main(void)
{
    UB ret;
    B msg[128];

    // メッセージ・キュー初期化＆チェック
    Init_Message(&sendMessage);
    if (Check_MessageEmpty(&sendMessage)) {
        printf("Send message is empty! -> OK\n");
    }
    else {
        printf("Send message is not empty! -> NG\n");
    }
    printf("\n");

    // メッセージ・キューに５メッセージ設定
    printf("Put 5 messages...\n");
    for (int i = 0; i < 5; i++) {
        memset(msg, 0, ARRAY_SIZE(msg));
        sprintf(msg, "Add message %d.", i);
        printf("  %s\n", msg);

        Put_Message(&sendMessage, msg, ARRAY_SIZE(msg));
    }
    printf("\n");

    // メッセージ・キューから６メッセージ取り出し
    printf("Get 6 messages...\n");
    for (int i = 0; i < 6; i++) {
        memset(msg, 0, ARRAY_SIZE(msg));
        ret = Get_Message(&sendMessage, msg, ARRAY_SIZE(msg));

        if (ret == C_OK) {
            printf("  Success: %s\n", msg);
        }
        else {
            printf("  Failed: Empty\n");
        }
    }

    return 0;
}


/******************************************************************************
<実行結果>

Send message is empty! -> OK

Put 5 messages...
  Add message 0.
  Add message 1.
  Add message 2.
  Add message 3.
  Add message 4.

Get 6 messages...
  Success: Add message 0.
  Success: Add message 1.
  Success: Add message 2.
  Success: Add message 3.
  Success: Add message 4.
  Failed: Empty

******************************************************************************/

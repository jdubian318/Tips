#include <stdio.h>
#include "calc.h"
#include "minunit.h"

// 通常関数
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
// ダミー関数
int dummy_add(int a, int b) { return 0; }
int dummy_sub(int a, int b) { return 0; }

int tests_run;

// スタブとして通常関数を使用したテスト
static char* test_normal_addsub()
{
    calc_set_add_func(add);
    calc_set_sub_func(sub);
    mu_assert("error, calc_addsub(3, 2) != 6", calc_addsub(3, 2) == 6);
    return 0;
}

// スタブとしてダミー関数を使用したテスト
static char* test_dummy_addsub()
{
    calc_set_add_func(dummy_add);
    calc_set_sub_func(dummy_sub);
    mu_assert("error, calc_addsub(3, 2) != 0", calc_addsub(3, 2) == 0);
    return 0;
}

static char* all_tests()
{
    mu_run_test(test_normal_addsub);
    mu_run_test(test_dummy_addsub);
    return 0;
}

int main(int argc, char* argv[])
{
    char *result = all_tests();
    if (result != 0) {
        printf("%s\n", result);
    }
    else {
        printf("ALL TESTS PASSED\n");
    }
    printf("Tests run: %d\n", tests_run);
    return result != 0;
}
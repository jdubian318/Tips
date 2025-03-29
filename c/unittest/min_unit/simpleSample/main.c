#include <stdio.h>
#include "minunit.h"

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

int tests_run;

static char* test_add()
{
    mu_assert("error, add(1, 2) != 3", add(1, 2) == 3);
    return 0;
}

static char* test_sub()
{
    mu_assert("error, sub(4, 1) != 3", sub(4, 1) == 3);
    return 0;
}

static char* all_tests()
{
    mu_run_test(test_add);
    mu_run_test(test_sub);
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
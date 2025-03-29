#include "calc.h"


static CalcFunc_t add_func;
static CalcFunc_t sub_func;

void calc_set_add_func(CalcFunc_t func)
{
    add_func = func;
}

void calc_set_sub_func(CalcFunc_t func)
{
    sub_func = func;
}

int calc_addsub(int a, int b)
{
    return add_func(a, b) + sub_func(a, b);
}
#ifndef _CALC_H_
#define _CALC_H_

typedef int (*CalcFunc_t)(int, int);

void calc_set_add_func(CalcFunc_t func);
void calc_set_sub_func(CalcFunc_t func);

int calc_addsub(int a, int b);

#endif /* _CALC_H_ */
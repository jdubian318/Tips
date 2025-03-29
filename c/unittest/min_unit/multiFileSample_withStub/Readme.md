# 概要

このサンプルは、MinUnitというFrameworkを使った
複数ファイルを使用したサンプル。


# build & exec

```bash
$ make
gcc -Wall -O2 -c main.c
gcc -Wall -O2 -c calc.c
gcc -o main main.o calc.o

$ ./main
ALL TESTS PASSED
Tests run: 2
```

# clean

```bash
$ make clean
rm -f main main.o calc.o
```
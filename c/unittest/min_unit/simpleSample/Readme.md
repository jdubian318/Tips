# 概要

このサンプルは、MinUnitというFrameworkを使った
１ファイルのみのシンプルなサンプル。


# build & exec

```bash
$ make
gcc -Wall -O2 -c main.c
gcc -o main main.o

$ ./main
ALL TESTS PASSED
Tests run: 2
```

# clean

```bash
$ make clean
rm -f main main.o depend.inc
```
# 概要

このサンプルは、MinUnitというFrameworkを使った
複数ファイルを使用したサンプル。


# build & exec

```bash
$ make
gcc -Wall -O2 -g -coverage -c main.c
gcc -Wall -O2 -g -coverage -c calc.c
gcc -Wall -O2 -g -coverage -o main main.o calc.o
==============================
./main
ALL TESTS PASSED
Tests run: 2
==============================
--- gcov ---
find . -type f -name "*.gcda" | xargs -I@ gcov -b @
File 'calc.c'
Lines executed:100.00% of 8
No branches
Calls executed:100.00% of 2
Creating 'calc.c.gcov'

Lines executed:100.00% of 8
File 'main.c'
Lines executed:95.45% of 22
Branches executed:100.00% of 10
Taken at least once:50.00% of 10
Calls executed:91.67% of 12
Creating 'main.c.gcov'

File '/usr/include/x86_64-linux-gnu/bits/stdio2.h'
Lines executed:100.00% of 2
No branches
Calls executed:66.67% of 3
Creating 'stdio2.h.gcov'

Lines executed:95.83% of 24
==============================
--- lcov ---
lcov -c -d --rc lcov_branch_coverage=1 . -o lcov.info
Capturing coverage data from .
Subroutine read_intermediate_text redefined at /usr/bin/geninfo line 2623.
Subroutine read_intermediate_json redefined at /usr/bin/geninfo line 2655.
Subroutine intermediate_text_to_info redefined at /usr/bin/geninfo line 2703.
Subroutine intermediate_json_to_info redefined at /usr/bin/geninfo line 2792.
Subroutine get_output_fd redefined at /usr/bin/geninfo line 2872.
Subroutine print_gcov_warnings redefined at /usr/bin/geninfo line 2900.
Subroutine process_intermediate redefined at /usr/bin/geninfo line 2930.
Found gcov version: 11.4.0
Using intermediate gcov format
Scanning . for .gcda files ...
Found 2 data files in .
Processing calc.gcda
Processing main.gcda
Finished .info-file creation
==============================
--- genhtml ---
genhtml lcov.info --branch-coverage -o ./info
Reading data file lcov.info
Found 3 entries.
Found common filename prefix "/home/ken/VBoxShare/code/Tips/c/unittest/min_unit"
Writing .css and .png files.
Generating output.
Processing file multiFileSample_withStub/calc.c
Processing file multiFileSample_withStub/main.c
Processing file /usr/include/x86_64-linux-gnu/bits/stdio2.h
Writing directory view page.
Overall coverage rate:
  lines......: 96.9% (31 of 32 lines)
  functions..: 100.0% (11 of 11 functions)
  branches...: 50.0% (5 of 10 branches)
```

# clean

```bash
$ make clean
rm -f -rf main main.o calc.o *.gcno *.gcov *.gcda *.info info/
```
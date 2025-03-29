# プログラム名とオブジェクトファイル名
PROGRAM = main
OBJS = main.o calc.o
TEST_OBJS = *.gcno *.gcov *.gcda *.info info/

# 定義済みマクロの再定義
CC = gcc
CFLAGS = -Wall -O2 -g -coverage

# サフィックスルール適用対象の拡張子の定義
.SUFFIXES: .c .o

# プライマリターゲット
.PHONY: all
all: $(PROGRAM) test

# プログラムの生成ルール
$(PROGRAM): $(OBJS)
	$(CC) $(CFLAGS) -o $(PROGRAM) $^

# サフィックスルール
.c.o:
	$(CC) $(CFLAGS) -c $<

# 依存関係
main.o: calc.h
calc.o: calc.h

# 実行
.PHONY: test
test:
	@echo ==============================
	./$(PROGRAM)
	@echo ==============================
	@echo --- gcov ---
	find . -type f -name "*.gcda" | xargs -I@ gcov -b @
	@echo ==============================
	@echo --- lcov ---
	lcov -c -d --rc lcov_branch_coverage=1 . -o lcov.info
	@echo ==============================
	@echo --- genhtml ---
	genhtml lcov.info --branch-coverage -o ./info

# ファイル削除用ターゲット
.PHONY: clean
clean:
	$(RM) -rf $(PROGRAM) $(OBJS) $(TEST_OBJS)
# プログラム名とオブジェクトファイル名
PROGRAM = main
OBJS = main.o

# 定義済みマクロの再定義
CC = gcc
CFLAGS = -Wall -O2

# サフィックスルール適用対象の拡張子の定義
.SUFFIXES: .c .o

# プライマリターゲット
.PHONY: all
all: $(PROGRAM)

# プログラムの生成ルール
$(PROGRAM): $(OBJS)
	$(CC) -o $(PROGRAM) $^

# サフィックスルール
.c.o:
	$(CC) $(CFLAGS) -c $<

# ファイル削除用ターゲット
.PHONY: clean
clean:
	$(RM) $(PROGRAM) $(OBJS)
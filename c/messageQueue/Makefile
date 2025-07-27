SRCDIR = ./
OBJDIR = obj/

CC = gcc
CFLAG = -Wall -g
INCLUDE = ${addprefix -I, $(SRCDIR)}
LFLAGS = 
# LFLAGS = -L<ライブラリディレクトリ> -l<ライブラリファイル>
VPATH = 


TARGET = main
SRCS = ${wildcard $(SRCDIR)*.c}
OBJS = $(patsubst %.c, %.o, $(SRCS))
OBJECTS = ${addprefix ${OBJDIR}, ${notdir ${OBJS}}}

# $(warning ==============================)
# $(warning INCLUDE = $(INCLUDE))
# $(warning SRCS = $(SRCS))
# $(warning OBJS = $(OBJS))
# $(warning OBJECTS = $(OBJECTS))
# $(warning ==============================)


.PHONY: all clean run

# 余分なコミットをしないようにcleanを最後に配置
all: $(TARGET) run clean

.SUFFIXES: .c .o
.c.o:
	$(CC) $(CFLAG) $(INCLUDE) -c $< -o ${addprefix ${OBJDIR}, ${notdir $@}}

$(TARGET): $(OBJDIR) $(OBJS)
	$(CC) $(CFLAG) $(INCLUDE) $(OBJECTS) -o $(OBJDIR)$(TARGET) $(LFLAGS)

$(OBJDIR):
	mkdir -p $(OBJDIR)

run:
	@echo ==============================
	@./$(OBJDIR)$(TARGET)
	@echo

clean:
	@$(RM) -rf $(OBJDIR)


TARGET = main
# 検査したいLTL式の「否定」を記述したファイル
FORMULA = formula
OBJDIR = obj/
OBJS = $(OBJDIR)*

$(TARGET):
	mkdir -p $(OBJDIR)
	spin -a -F $(FORMULA).prp $(TARGET).pml -d $(OBJDIR)
	mv pan.* $(OBJDIR)
	gcc -o $(OBJDIR)pan $(OBJDIR)pan.c
	$(OBJDIR)pan -a
	@if [ -f *.trail ];then mv *.trail $(OBJDIR); fi
# -----------------------------------------------------------------------------
# 上記と同じ。
# never claim自体をファイルに書き出して確認したい場合は
# 以下のようにSPINに対してpmlファイルなしで"-F"オプションを与えればよい。
# 拡張子には通例"ltl"が用いられる。
# 読み込む際には"-N"オプションを指定すればよい。
# $(TARGET):
# 	spin -F $(FORMULA).prp > $(FORMULA).ltl -d $(OBJDIR)
# 	spin -a -N $(OBJDIR)$(FORMULA).ltl $(TARGET).pml
#	gcc -o $(OBJDIR)pan $(OBJDIR)pan.c
#	$(OBJDIR)pan -a
# -----------------------------------------------------------------------------

# 反例出力
counter:
	spin -g -l -p -r -s -t -X -u250 $(TARGET).pml

clean:
	rm -f $(OBJS)



#define p (sw==on)

mtype = {on, off};
mtype sw = on;

active proctype P() {
  do
  ::(sw==on) -> sw=off
  ::(sw==off) -> sw=on
  od
}

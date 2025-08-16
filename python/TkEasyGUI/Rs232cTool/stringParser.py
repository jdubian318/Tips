#!python3
# 上記を「Magic comment」という。

from enum import IntEnum, auto


class State(IntEnum):
    WaitHexHead = auto()
    WaitHexTail = auto()


class StringParser:
    @classmethod
    def toBytes(cls, text:str) -> list[bytes]:
        chars: list[tuple[str, bool]] = [] # (string, isHexString)
        hex_str:str = ""

        stat = State.WaitHexHead
        for s in text:
            if stat == State.WaitHexHead:
                if s == '<':
                    stat = State.WaitHexTail
                    hex_str = ""
                else:
                    chars.append((s, False))
            else:
                if s == '>':
                    chars.append((hex_str, True))
                    stat = State.WaitHexHead
                else:
                    hex_str += s

        str2bytes = {
            "NULL": b"\x00",
            "STX": b"\x02",
            "ETX": b"\x03",
            "ACK": b"\x06",
            "NAK": b"\x15",
        }
        bytes_list:list[bytes] = []
        for str, isHexString in chars:
            if isHexString:
                if str in str2bytes:
                    bytes_list.append(str2bytes[str])
                else:
                    import re
                    if re.match(r"^[0-9a-fA-F]{2}$", str):
                        n = int(str, 16)
                        bytes_list.append(n.to_bytes(1, 'big'))
                    else:
                        print(f"[ERROR] Cannot convert hex param '{str}'.")
            else:
                bytes_list.append(str.encode("ascii"))

        return bytes_list

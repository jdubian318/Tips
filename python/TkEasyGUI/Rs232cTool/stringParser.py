#!python3
# 上記を「Magic comment」という。

from enum import IntEnum, auto


class State(IntEnum):
    WaitHexHead = auto()
    WaitHexTail = auto()


class StringParser:
    @classmethod
    # def toBytes(cls, text:str) -> list[bytes]:
    def toBytes(cls, text:str) -> bytearray:
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
        # bytes_list:list[bytes] = []
        bytes_list:bytearray = bytearray()
        for s, isHexString in chars:
            if isHexString:
                if s in str2bytes:
                    # bytes_list.append(str2bytes[str])
                    bytes_list.extend(str2bytes[s])
                else:
                    import re
                    if re.match(r"^[0-9a-fA-F]{2}$", s):
                        n = int(s, 16)
                        # bytes_list.append(n.to_bytes(1, 'big'))
                        bytes_list.extend(n.to_bytes(1, 'big'))
                    else:
                        print(f"[ERROR] Cannot convert hex param '{s}'.")
            else:
                # bytes_list.append(str.encode("ascii"))
                bytes_list.extend(s.encode("ascii"))

        return bytes_list

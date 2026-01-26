#!python3
# 上記を「Magic comment」という。


class BytesParser:
    @classmethod
    # def toString(cls, data:bytes, isHex:bool):
    def toString(cls, data:bytearray, isHex:bool):
        text_list:list[str] = []
        for d in data:
            if type(d) == int:
                int_val = d
            else:
                int_val = int.from_bytes(d, 'big')
            if isHex:
                text_list.append(f"<{int_val:02X}>")
            else:
                # if (d >= b'0' and d <= b'9') or (d >= b'a' and d <= b'f') or (d >= b'A' and d <= b'F'):
                if (d >= ord('0') and d <= ord('9')) or (d >= ord('a') and d <= ord('f')) or (d >= ord('A') and d <= ord('F')):
                    text_list.append(f"{chr(int_val)}")
                else:
                    text_list.append(".")

        return "".join(text_list)


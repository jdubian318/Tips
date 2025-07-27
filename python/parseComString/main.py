#!python3
# 上記を「Magic comment」という。

from stringParser import StringParser
from bytesParser import BytesParser


def main():
    text = "<STX>0123abCD<ETX><12><AB><ef>"
    print(f"text: {text}")
    parsed_bytes = StringParser.toBytes(text)
    print(f"bytes: {parsed_bytes}")
    parsed_text_ascii = BytesParser.toString(parsed_bytes, isHex=False)
    parsed_text_hex = BytesParser.toString(parsed_bytes, isHex=True)
    print(f"text: {parsed_text_ascii}")
    print(f"text: {parsed_text_hex}")

if __name__ == "__main__":
    main()

# =============================================================================================================
# 実行結果
# ------------------------------------------------------------------------------------------------------------
# text: <STX>0123abCD<ETX><12><AB><ef>
# bytes: [b'\x02', b'0', b'1', b'2', b'3', b'a', b'b', b'C', b'D', b'\x03', b'\x12', b'\xab', b'\xef']
# text: .0123abCD....
# text: <02><30><31><32><33><61><62><43><44><03><12><AB><EF>
# =============================================================================================================

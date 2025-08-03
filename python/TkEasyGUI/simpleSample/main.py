#!python3

import TkEasyGUI as eg

layout = [
    [eg.Text("名前は？")],
    [eg.InputText()],
    [eg.Button("OK"), eg.Button("Cancel")]
]

window = eg.Window("SimpleSample", layout)

while True:
    event, values = window.read()

    if event == eg.WIN_CLOSED or event == "Cancel":
        # ウィンドウの「ｘ」ボタンか「Cancel」ボタンを押下したとき
        break

    print(f"Hello {values[0]}!")

window.close()

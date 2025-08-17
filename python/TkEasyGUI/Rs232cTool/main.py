#!python3
# 上のやつは Magic comment という。
# Python3 の場合、ソースが UTF-8 の場合は以下の記載は不要（むしろ非推奨）。
# -*- coding: utf_8 -*-

import serial
from serial.tools import list_ports
from threading import Thread
from queue import Queue
from pathlib import Path
import TkEasyGUI as eg

from stringParser import StringParser
from bytesParser import BytesParser


listBoxItems = []

file_path = "./SendData.txt"
if Path(file_path).exists():
    with open(file_path, "r") as f:
        for l in f:
            listBoxItems.append(l.rstrip('\n'))


frame_setting_names_col = eg.Column(
    [
        [ eg.Text("Port: ") ],
        [ eg.Text("BaudRate:"),],
        [ eg.Text("DataBits: "),],
        [ eg.Text("Parity: "),],
        [ eg.Text("StopBits: "),],
    ],
    key="col1",
    expand_y=True,
)

frame_setting_items_col = eg.Column(
    [
        [
            eg.Combo(
                [],
                key="-cmbPort-",
                readonly=True
            ),
        ],
        [
            eg.Combo(
                ["9600", "19200", "38400", "115200"],
                default_value="38400",
                key="-cmbBaudRate-",
                readonly=True
            ),
        ],
        [
            eg.Combo(
                ["7 bit", "8 bit"],
                default_value="8 bit",
                key="-cmbDataBits-",
                readonly=True
            ),
        ],
        [
            eg.Combo(
                ["None", "Odd", "Even", "Mark", "Space"],
                default_value="None",
                key="-cmbParity-",
                readonly=True
            ),
        ],
        [
            eg.Combo(
                ["1 bit", "2 bit"],
                default_value="1 bit",
                key="-cmbStopBits-",
                readonly=True
            ),
        ],
    ],
    key="col2",
    expand_y=True,
)

frame_setting_button = [
    eg.Button("Connect", key="-btnConnect-", expand_x=True),
]

frame_setting = eg.Frame(
    "Settings",
    [
        [frame_setting_names_col, frame_setting_items_col],
        frame_setting_button,
    ],
)

frame_send = eg.Frame(
    "Send",
    [
        [
            eg.Text("SendData: "),
            eg.Input("", key="-txtSendData-", expand_x=True),
            eg.Button("Send", key="-btnSend-", disabled=True),
        ],
        [
            eg.Button("↓↓↓", key="-btnAdd-", expand_x=True),
            eg.Button("↑↑↑", key="-btnChange-", expand_x=True),
        ],
        [
            eg.Column(
                [
                    [
                        eg.Listbox(values=listBoxItems, key="-lstSendData-", expand_x=True)
                    ],
                ],
                expand_x=True
            ),
            eg.Column(
                [
                    [
                        eg.Button("↑", key="-btnUp-")
                    ],
                    [
                        eg.Button("↓", key="-btnDown-")
                    ],
                    [
                        eg.Button("Delete", key="-btnDelete-", expand_x=True),
                    ],
                ],
            ),
        ],
    ],
    expand_x=True,
)

frame_log = eg.Frame(
    "Log",
    [
        [ eg.Button("Clear", key="-btnClear-") ],
        [ eg.Multiline("", key="-txtLog-", readonly=True, expand_x=True, expand_y=True) ],
    ],
    expand_x=True, expand_y=True,
)

layout = [
    [ frame_setting ],
    [ frame_send ],
    [ frame_log ],
]


def getComParams(values) -> tuple[str, int, str, int]:
    port = values['-cmbPort-']
    baudrate = values['-cmbBaudRate-']
    data_bits = int(values['-cmbDataBits-'].replace(" bit", ""))
    parity = serial.PARITY_NONE

    if values['-cmbParity-'] == "Odd":
        parity = serial.PARITY_ODD
    elif values['-cmbParity-'] == "Even":
        parity = serial.PARITY_EVEN
    elif values['-cmbParity-'] == "Mark":
        parity = serial.PARITY_MARK
    elif values['-cmbParity-'] == "Space":
        parity = serial.PARITY_SPACE

    stop_bits = int(values['-cmbStopBits-'].replace(" bit", ""))

    return (port, baudrate, data_bits, parity, stop_bits)


logQue: Queue = Queue()
def appendLog(txt: str) -> None:
    # print(f"{txt}")
    logQue.put(txt)

def appendCOMLog(type:str, dt: bytes) -> None:
    parsed_text = BytesParser.toString(dt, isHex=True)
    appendLog(f"{type} {parsed_text}")


def serialReceiveThread(ser: serial.Serial) -> None:
    import time
    while isRecvRunning:
        try:
            if ser.in_waiting() <= 0:
                time.sleep(0.01)
                continue
            appendCOMLog("[RECV]", ser.readall())
        except serial.SerialException as e:
            time.sleep(0.1)
            appendLog(f"[RECV] シリアルポートエラー：{e}")
        except Exception as e:
            time.sleep(0.1)
            appendLog(f"[RECV] その他エラー：{e}")


def changeControls(connected: bool) -> None:
    controls = [
        "-cmbPort-",
        "-cmbBaudRate-",
        "-cmbDataBits-",
        "-cmbParity-",
        "-cmbStopBits-",
    ]
    for ctrl in controls:
        window[ctrl].update(disabled=connected)
        if not connected:
            window[ctrl].update(readonly=True)

    window["-btnSend-"].update(disabled=not connected)
    if connected:
        window["-btnConnect-"].update(text="Disconnect")
    else:
        window["-btnConnect-"].update(text="Connect")



isRecvRunning: bool = False

with eg.Window("App", layout, resizable=True, size=(600, 800)) as window:
    ser: serial.Serial = None
    recv_thread: Thread = None

    ports = list_ports.comports()
    devices = [info.device for info in ports]
    window["-cmbPort-"].update(values=devices)

    while window.is_alive():
        for event, values in window.event_iter(timeout=100, timeout_key="-timeout-"):
            if event == "-btnConnect-":
                if window["-btnConnect-"].text == "Connect":
                    port, baudrate, data_bits, parity, stop_bits = getComParams(values)
                    if port == "":
                        eg.popup("ポートを選択してください")
                        continue

                    try:
                        ser = serial.Serial(port, baudrate, data_bits, parity, stop_bits)
                        isRecvRunning = True
                        recv_thread = Thread(target=serialReceiveThread, args=(ser,))
                        recv_thread.start()
                        appendLog(f"[OPEN] Success.")
                        changeControls(True)
                    except serial.SerialException as e:
                        appendLog(f"[OPEN] シリアルポートエラー：{e}")
                    except Exception as e:
                        appendLog(f"[OPEN] その他エラー：{e}")
                else:
                    isRecvRunning = False
                    if recv_thread is not None:
                        recv_thread.join()
                    if ser is not None:
                        ser.close()
                    appendLog(f"[CLOSE] Success.")
                    changeControls(False)

            elif event == "-btnSend-":
                new_item = values['-txtSendData-']
                parsed_bytes = StringParser.toBytes(new_item)
                appendCOMLog("[SEND]", parsed_bytes)
                try:
                    ser.write(parsed_bytes)
                except serial.SerialException as e:
                    appendLog(f"[SEND] シリアルポートエラー：{e}")
                except Exception as e:
                    appendLog(f"[SEND] その他エラー：{e}")

            elif event == "-btnAdd-":
                new_item = values['-txtSendData-']
                if not new_item in listBoxItems:
                    listBoxItems.append(new_item)
                    window["-lstSendData-"].update(values=listBoxItems)

                    with open(file_path, "w") as f:
                        for item in listBoxItems:
                            f.write(f"{item}\n")

            elif event == "-btnChange-":
                if len(values['-lstSendData-']) > 0:
                    val = values['-lstSendData-'][0]
                    window["-txtSendData-"].update(text=val)

            elif event == "-btnDelete-":
                if len(values['-lstSendData-']) > 0:
                    val = values['-lstSendData-'][0]
                    if val in listBoxItems:
                        listBoxItems.remove(val)
                        window["-lstSendData-"].update(values=listBoxItems)

                    with open(file_path, "w") as f:
                        for item in listBoxItems:
                            f.write(f"{item}\n")

            elif event == "-btnUp-":
                if len(values['-lstSendData-']) > 0:
                    val = values['-lstSendData-'][0]
                    cur_idx = listBoxItems.index(val)
                    if val in listBoxItems:
                        listBoxItems.remove(val)
                    new_idx = cur_idx - 1
                    if new_idx < 0:
                        new_idx = 0
                    listBoxItems.insert(new_idx, val)
                    window["-lstSendData-"].update(values=listBoxItems)
                    window["-lstSendData-"].set_cursor_index(new_idx)

                    with open(file_path, "w") as f:
                        for item in listBoxItems:
                            f.write(f"{item}\n")

            elif event == "-btnDown-":
                if len(values['-lstSendData-']) > 0:
                    val = values['-lstSendData-'][0]
                    cur_idx = listBoxItems.index(val)
                    if val in listBoxItems:
                        listBoxItems.remove(val)
                    new_idx = cur_idx + 1
                    if new_idx > len(listBoxItems):
                        new_idx = len(listBoxItems)
                    listBoxItems.insert(new_idx, val)
                    window["-lstSendData-"].update(values=listBoxItems)
                    window["-lstSendData-"].set_cursor_index(new_idx)

                    with open(file_path, "w") as f:
                        for item in listBoxItems:
                            f.write(f"{item}\n")

            elif event == "-btnClear-":
                window["-txtLog-"].update("")

            elif event == "-timeout-":
                if not logQue.empty():
                    log_txt = logQue.get()
                    window["-txtLog-"].update(readonly=False)
                    window["-txtLog-"].print(text=f"{log_txt}", autoscroll=True)
                    window["-txtLog-"].update(readonly=True)

            elif event == eg.WINDOW_CLOSED:
                isRecvRunning = False
                if recv_thread is not None:
                    recv_thread.join()
                if ser is not None:
                    ser.close()
                break

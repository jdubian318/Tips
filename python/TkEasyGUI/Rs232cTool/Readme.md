# 準備

```bash
$ lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.5 LTS
Release:        22.04
Codename:       jammy

$ python3 --version
Python 3.13.5

$ apt install python3-pip
$ apt install python3-tk
$ pipenv --python 3.10
$ pipenv install tk
$ pipenv install TkEasyGUI
```

そのままインストールしたらうまく行かなかったので、
仮想環境にPython3.10を構築して実行。


# 出だし

```python
import TkEasyGUI as eg
```


# 実行

```bash
$ pipenv shell
(simpleSample) $ python main.py

```

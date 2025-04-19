# 概要

このサンプルは、PCUnitというFrameworkを使った
１ファイルのみのシンプルなサンプル。


# 準備

## PCUnitのクローン

```bash
$ git clone https://github.com/katono/PCUnit.git
```


## クローンした中のPCUnitフォルダをコピー

* フォルダ構成
    ```
    code
        - PCUnit ←Cloneしたデータ
            - PCUnit
            - sample
            - test
        - simpleSample ←作業するフォルダ
            - Readme.md
            - ...
    ```

* フォルダコピー
    ```bash
    $ cd simpleSample
    $ cp -r ../PCUnit/PCUnit ./
    ```


# build & exec

```bash
$ make

$ ./main
```


# clean

```bash
$ make clean
rm -f main main.o
```
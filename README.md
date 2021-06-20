# Clochur
A Scheme-like typesetting LISP interpreter and editor that using SILE typesetting Engine.

## Screenshot
![screenshot](https://user-images.githubusercontent.com/184107/122680547-47c8e000-d222-11eb-8ac3-be02df28e4b0.png)

## License
GPLv3 (except those inside `thirdparty/`)

## Dependencies
* Python3
* PyQt5>=5.15
* QScintilla>=2.12
* SILE>=0.10

## Install
It's recommended to install the wheel file (.whl) of it with pip3:

  `pip3 install Clochur-x.y.z-py3-none-any.whl`

## Manual

see `src/example.pdf`

## Packaging

To make a wheel package, run the following command in the root folder:

  `python3 setup.py bdist_wheel`

and then:

  `cd dist; ls`

`Clochur-x.y.z-py3-none-any.whl` will be in it.

# Clochur
A Scheme-like typesetting LISP interpreter and editor that using SILE typesetting Engine.


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

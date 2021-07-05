# Clochur
A Scheme-like typesetting LISP interpreter and editor that using SILE typesetting Engine.

## Screenshot
![screenshot](https://user-images.githubusercontent.com/184107/123665795-322f6800-d86b-11eb-9d0b-55067ae3a50c.png)

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

## Command

`clochur`

Just type it in your CLI terminal.

## Manual

see `src/manual.pdf`

## Packaging

### Python Wheel file (.whl)

To make a wheel package, run the following command in the root folder:

  `python3 setup.py bdist_wheel`

and then:

  `cd dist; ls`

`Clochur-x.y.z-py3-none-any.whl` will be in it.

### Ubuntu/Debian .deb file

Before package it, you should install [Stdeb](https://pypi.org/project/stdeb) first.

    python3 setup.py sdist
    cd dist
    py2dsc -x ../stdeb.cfg Clochur-x.y.z.tar.gz
    cd deb_dist/clochur-x.y.z
    cd dpkg-buildpackage -rfakeroot -uc -us
    cd ..; ls
    ...
    clochur_x.y.z-1_all.deb
    ...

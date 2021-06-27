import os
import pdb  # 先 import 今天要介紹的套件

from glob import glob
from setuptools import find_packages, setup

about = {}
with open("./src/Clochur/__about__.py") as about_info:
    exec(about_info.read(), about)

third_party_files_and_dir = glob('thirdparty/**',recursive=True)
third_party_files = [x for x in third_party_files_and_dir if not os.path.isdir(x)]

setup(
    name="Clochur",
    version=about['version_no'],
    author="Yoxem Chen",
    author_email="yoxem.tem98@nctu.edu.tw",
    description='''A S-expression like typesetting language powered by SILE engine
                   with a simple editor''',

    url="http://yoxem.github.com",

    install_requires=['PyQt5>=5.15', 'QScintilla>=2.12'],

    

    classifiers = [

        'Development Status :: 2 - Pre-Alpha'
        'Environment :: X11 Applications :: Qt'
        'Programming Language :: Lisp'
        'Intended Audience :: Developers',
        'Topic :: Text Editors',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',

    ],

    entry_points={
        'gui_scripts': [
            'clochur = Clochur.__init__:entry_point'
        ]
    },

	packages=find_packages(where='src'),
    package_dir={'Clochur': 'src/Clochur'},
    package_data={'Clochur': ['*.pdf', '*.qrc',
                             '../resources/*.svg',
                             '../../example/*.clc',
                             '../../example/*.png',
							 '../thirdparty/pdfjs/**',
                             '../thirdparty/pdfjs/**/**',
                             '../thirdparty/pdfjs/**/**/**',
                             '../thirdparty/pdfjs/**/**/**/**']},

    


)





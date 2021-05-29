#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
import qrc_resources

filename = "untitled"

dirname = os.path.abspath(os.path.dirname(__file__)) #os.path.dirname('__file__')
PDFJS = os.path.join(dirname, 'thirdparty/pdfjs/web/viewer.html')
PDF = os.path.join(dirname, 'example.pdf')

font_family = 'Noto Sans Mono'
font_size = 11

'''Widget for PDF file viewer'''
class PDFJSWidget(QtWebEngineWidgets.QWebEngineView):
    def __init__(self):
        super(PDFJSWidget, self).__init__()
        self.load(QUrl.fromUserInput("file://%s?file=file://%s"  % (PDFJS, PDF)))
        print((dirname,PDFJS, PDF))

class CustomQsciEditor(QsciScintilla):
    def __init__(self, parent=None):
        super(CustomQsciEditor, self).__init__(parent)

        font = QFont()
        font.setFamily(font_family)
        font.setPointSize(font_size)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 for line numbers

        fontMetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontMetrics.width("000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # brace matching

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # current line color

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#fdffce"))

        # set horizonal scrollbar unvisible
        #self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

class Window(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self._createActions()
        self._createMenuBar()
        self._createEditToolBar()
        self._createFormatToolBar()

    def _createActions(self):
        self.new_action = QAction(QIcon(":new.svg"), "&New", self)
        self.open_action = QAction(QIcon(":open.svg"), "&Open...", self)
        self.save_action = QAction(QIcon(":save.svg"), "&Save", self)
        self.save_as_action = QAction(QIcon(":save-as.svg"), "Save as...", self)

        self.exit_action = QAction("&Exit", self)
        self.undo_action = QAction(QIcon(":undo.svg"), "&Undo", self)
        self.redo_action = QAction(QIcon(":redo.svg"), "&Redo", self)
        self.copy_action = QAction(QIcon(":copy.svg"), "&Copy", self)
        self.paste_action = QAction(QIcon(":paste.svg"), "&Paste", self)
        self.cut_action = QAction(QIcon(":cut.svg"), "C&ut", self)
        self.convert_action = QAction(QIcon(":convert.svg"), "Con&vert", self) 

        self.about_action = QAction("&About", self)

        self.bold_action = QAction(QIcon(":text-bold.svg"), "&Bold", self)
        self.italic_action = QAction(QIcon(":text-italic.svg"), "&Italic", self) 
        self.strike_action = QAction(QIcon(":text-strikethrough.svg"), "Stri&ke", self) 
        self.underline_action = QAction(QIcon(":text-underline.svg"), "&Underline", self) 

    def _createMenuBar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        file_menu = menuBar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addAction(self.exit_action)

        edit_menu = menuBar.addMenu("&Edit")
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addAction(self.cut_action)

        edit_menu.addSeparator()

        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        edit_menu.addAction(self.convert_action)



        format_menu = menuBar.addMenu("&Format")
        format_menu.addAction(self.bold_action)
        format_menu.addAction(self.italic_action)
        format_menu.addAction(self.strike_action)
        format_menu.addAction(self.underline_action)

        help_menu = menuBar.addMenu("&Help")
        help_menu.addAction(self.about_action)

    def _createEditToolBar(self):
        editToolBar = QToolBar("Edit", self)
        editToolBar.toolButtonStyle = Qt.ToolButtonTextOnly
        self.addToolBar(Qt.TopToolBarArea, editToolBar)

        editToolBar.addAction(self.new_action)
        editToolBar.addAction(self.open_action)
        editToolBar.addAction(self.save_action)
        editToolBar.addAction(self.save_as_action)


        tool_bar_separator = editToolBar.addAction('|')
        tool_bar_separator.setEnabled(False)

        editToolBar.addAction(self.undo_action)
        editToolBar.addAction(self.redo_action)

        tool_bar_separator = editToolBar.addAction('|')
        tool_bar_separator.setEnabled(False)


        editToolBar.addAction(self.cut_action)
        editToolBar.addAction(self.copy_action)
        editToolBar.addAction(self.paste_action)

        tool_bar_separator = editToolBar.addAction('|')
        tool_bar_separator.setEnabled(False)

        editToolBar.addAction(self.convert_action)


    def _createFormatToolBar(self):
        self.addToolBarBreak() # Toolber newline
        formatToolBar = QToolBar("Format", self)
        formatToolBar.toolButtonStyle = Qt.ToolButtonTextOnly
        self.addToolBar(Qt.TopToolBarArea, formatToolBar)

        formatToolBar.addAction(self.bold_action)
        formatToolBar.addAction(self.italic_action)
        formatToolBar.addAction(self.strike_action)
        formatToolBar.addAction(self.underline_action)

        '''create font adder'''
        self.font_widget = QHBoxLayout()
        font_combo_box = QComboBox()
        font_database = QFontDatabase()
        font_families = font_database.families()

        font_combo_box.addItems(font_families)
        line_edit = font_combo_box.lineEdit()
        #line_edit.setFont(QFont(font_combo_box.currentText(),11))
        #print(type(font_combo_box.lineEdit()).__name__)

        font_button = QPushButton("Insert font")

        formatToolBar.addWidget(font_combo_box)
        formatToolBar.addWidget(font_button)


if __name__ == '__main__':
    app = QApplication([])

    app.setApplicationName("Clochur - %s" % filename)

    editor = CustomQsciEditor()
    editor.setMinimumWidth(200)
    #editor.resize(QSize(500, 2000))

    pdf_viewer = PDFJSWidget()
    pdf_viewer.setMinimumWidth(200)
    #pdf_viewer.resize(QSize(500, 2000))
    
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(editor)
    splitter.addWidget(pdf_viewer)
    splitter.setStretchFactor(0, 1)
    splitter.setSizes([500, 500])
    splitter.setChildrenCollapsible(False) # make the editor and the PDF reader uncollapsible.

    main_layout = QHBoxLayout()

    main_layout.addWidget(splitter)
    #main_layout.addWidget(pdf_viewer)

    window = Window()
    
    main_widget = QWidget()
    main_widget.setLayout(main_layout)

    window.setCentralWidget(main_widget)
    window.show()
    app.exec_()
#!/usr/bin/env python3
#-*-coding:utf-8-*-

import os
import re
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerCustom
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

    def set_word_wrap(self):
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
    def set_no_word_wrap(self):
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)

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
        self.setMarginWidth(0, fontMetrics.width("00") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # brace matching

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # current line color

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#fdffce"))

        # set word wrap
        self.set_word_wrap()

        # set encoding
        self.SendScintilla(QsciScintilla.SCI_SETCODEPAGE, QsciScintilla.SC_CP_UTF8)



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

class ClochurLexer(QsciLexerCustom):

    def __init__(self, parent=None):
        QsciLexerCustom.__init__(self, parent)
        self._styles = {
            0: 'Default',
            1: 'Keyword',
            2: 'Comment',
            3: 'String', 
            4: 'Rainbow0',
            5: 'Rainbow1',
            6: 'Rainbow2',   
            7: 'Rainbow3',  
            8: 'Rainbow4',
            9: 'Rainbow5',
            10: 'Rainbow6',
        }

        for (k,v) in self._styles.items():
            setattr(self, v, k)

        self.QUOTES = ['"', "'"]
        self.PARENTHESIS = ["[", "]"]

        self.PRIMARY = ['define', 'let' , '#t', '#f', 'lambda', '@', 'cond', 'if', 'docu']


    def language(self):
        return "Clochur"

    def description(self, style):
        ret = "Lexer for Clochur - a S-expression-like" + \
            "typesetting Language. %s, %s" % (style, self._styles.get(style, ''))
        return ret
    
    def defaultColor(self, style):
        if style == self.Default:
            return QColor("#000000")
        elif style == self.Keyword:
            return QColor("#0000ff")
        elif style == self.Comment:
            return QColor("#005500")
        elif style == self.String:
            return QColor("#ce5c00")
        elif style == self.Rainbow0:
            return QColor("#ff5500")
        elif style == self.Rainbow1:
            return QColor("#ffaa00")
        elif style == self.Rainbow2:
            return QColor("#dede00")
        elif style == self.Rainbow3:
            return QColor("#00ff00")
        elif style == self.Rainbow4:
            return QColor("#00aaff")
        elif style == self.Rainbow5:
            return QColor("#0000ff")
        elif style == self.Rainbow6:
            return QColor("#aa00ff")
                                                                                
        else:
            return QsciLexerCustom.defaultColor(self, style)

    def defaultRainbowColor(self, index):
        return QColor(self.rainbow_color[index])

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        SCI = editor.SendScintilla
        set_style = self.setStyling

        source = ''
        if end > editor.length():
            end = editor.length()
        if end > start:
            source = bytearray(end - start)
            SCI(QsciScintilla.SCI_GETTEXTRANGE, start, end, source)
        if not source:
            return


        self.startStyling(start, 0x1f)
        rainbow_state = 0

        index = SCI(QsciScintilla.SCI_LINEFROMPOSITION, start)

        for line in source.splitlines(True):
            print("%s, %d" % (line, rainbow_state))
            length = len(line)

            i = 0

            new_state = self.Default

            line_utf8 = line.decode('utf-8')

            split_pattern = re.compile(r'(\s+|\\%|%|\\\[|\\\]|[[]|[]])')

            line_utf8_splitted = split_pattern.split(line_utf8)

            line_utf8_splitted_len_pair = [{"str": item, "len" : len(bytearray(item, "utf-8"))} for item in line_utf8_splitted]


            print(line_utf8_splitted_len_pair)

            is_comment = False

            i = 0
            if index > 0:
                pos = SCI(QsciScintilla.SCI_GETLINEENDPOSITION, index - 1)
                rainbow_state = SCI(QsciScintilla.SCI_GETSTYLEAT, pos) + 0
                print(rainbow_state)

            for item in line_utf8_splitted_len_pair:

                '''comment'''
                if item["str"] == "%":
                    is_comment = True
                if is_comment == True:
                    new_state = self.Comment # end of comment
                elif item["str"] in self.PRIMARY: # keywords
                    new_state = self.Keyword
                # string
                elif re.match(r'^["]([^"]|\\\")*["]$' ,item["str"]) or re.match(r"^[']([^']|\\\')*[']$" ,item["str"]):
                    new_state = self.String
                #parenthesis: rainbow mode
                elif item["str"] == "[":
                    new_state = getattr(self, "Rainbow" + str(rainbow_state))
                    rainbow_state += 1
                elif item["str"] == "]":
                    rainbow_state -= 1
                    new_state = getattr(self, "Rainbow" + str(rainbow_state))
                else:
                    pass

                word_length = item["len"]
                i += word_length
                set_style(word_length, new_state)

                if new_state != self.Comment:
                    new_state = self.Default
        



            '''while i < length:
                
                
                
                
                word_length = 1

                
                
                
                
                
                if line[i:].startswith(b"\\"):
                    prev_is_slash = True
                else:
                    # convert byte array to utf-8, and match comment to color it.
                    if line[i:].startswith(b'%') and prev_is_slash == False:
                        new_state = self.Comment
                        word_length = len(line[i:])

                        print(line[i:].decode('utf-8'))

                    #keywords_joined = "^(" + "|".join(self.PRIMARY) + ")$"

                    for keyword in self.PRIMARY:
                        if line[i:].startswith(bytearray(keyword, 'utf-8')):
                    #if re.match(keywords_joined , line[i:].decode('utf-8')):
                        #matched = re.match(keywords_joined , line[i:].decode('utf-8'))
                        #word_length = len(matched.group(0))
                            word_length = len(keyword)
                            new_state = self.Keyword


                    prev_is_slash = False
                
                i += word_length
                set_style(word_length, new_state)'''

            index += 1

if __name__ == '__main__':
    app = QApplication([])

    app.setApplicationName("Clochur - %s" % filename)

    editor = CustomQsciEditor()
    editor.setMinimumWidth(200)
    #editor.resize(QSize(500, 2000))

    lexer = ClochurLexer(editor)
    editor.setLexer(lexer)

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
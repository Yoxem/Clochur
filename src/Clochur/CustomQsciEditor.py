#!/usr/bin/env python3
#-*-coding:utf-8-*-

from PyQt5.QtGui import *
from PyQt5.Qsci import QsciScintilla, QsciAPIs

from Clochur.ClochurLexer import ClochurLexer

class CustomQsciEditor(QsciScintilla):
    def __init__(self, parent=None):
        super(CustomQsciEditor, self).__init__(parent)

        self.font_family = parent.font_family
        self.font_size = parent.font_size

        self.tab_width = 4

       

        # Margin 0 for line numbers
        font = QFont()
        font.setFamily(self.font_family)
        font.setPointSize(self.font_size)
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
        self.setUtf8(True)

        # set Auto indent
        self.setAutoIndent(True)
        self.setIndentationWidth(self.tab_width)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setBackspaceUnindents(True)

        #  set auto complete 
        
        #set lexer
        self.lexer = ClochurLexer(self)
        self.auto_complete_api = QsciAPIs(self.lexer) # autocomplete function
        self.setLexer(self.lexer)
        
        self.setAutoCompletionCaseSensitivity(True)

        self.setAutoCompletionReplaceWord(False)

        # Use the predefined APIs as the source. 
        self.setAutoCompletionSource(QsciScintilla.AcsAll)



        # after 1 character, show completetion
        self.setAutoCompletionThreshold(1)

        # add autocompletion items
        autocompletions = self.lexer.PRIMARY
    
        
        for ac in autocompletions:
            self.auto_complete_api.add(ac)

        # "prepare" the QsciAPIs-object: 
        self.auto_complete_api.prepare()

    def append_autocompletion_item(self, item):
        self.auto_complete_api.add(item)
        self.auto_complete_api.prepare()

    def set_word_wrap(self):
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
    def set_no_word_wrap(self):
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)

from PyQt5.QtGui import *
from PyQt5.Qsci import QsciScintilla

from .ClochurLexer import ClochurLexer

class CustomQsciEditor(QsciScintilla):
    def __init__(self, parent=None):
        super(CustomQsciEditor, self).__init__(parent)

        self.font_family = parent.font_family
        self.font_size = parent.font_size

        self.tab_width = 4

        lexer = ClochurLexer(self)
        self.setLexer(lexer)

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

    def set_word_wrap(self):
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
    def set_no_word_wrap(self):
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)

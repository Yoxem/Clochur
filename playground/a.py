#-*-coding:utf-8-*-
import sys, re
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MyHighlighter( QSyntaxHighlighter ):

    def __init__( self, parent, theme ):

        QSyntaxHighlighter.__init__( self, parent )
        self.parent = parent

        self.parenthesis_color = [Qt.red, Qt.green, Qt.blue]

    def textFormat(self, color):
        init_format = QTextCharFormat()
        brush = QBrush( color, Qt.SolidPattern )
        init_format.setForeground( brush )
        return init_format
        

    def highlightBlock( self, text ):

        '''                   (     (    )    )
         paren_level   ___0___|__1__|__2_|__1_|__0
        '''

        paren_level = self.previousBlockState()
        if paren_level == -1: # 若是沒有上次的狀態，就設為0
             paren_level = 0
        paren_size = 1

            
        
        iterator = re.finditer("[()]", text)

        paran_and_offset = [{"paren": match.group(0), "offset": match.start()} for match in iterator]
        
        print(paran_and_offset)
        for i in paran_and_offset:
                if i["paren"] == QString('('):
                    print("paren_level %d" % paren_level)
                    self.setFormat( i["offset"], paren_size , self.textFormat(self.parenthesis_color[paren_level]) )
                    paren_level += 1
                elif i["paren"] == QString(')'):
                    print(paren_level)
                    paren_level -= 1
                    self.setFormat( i["offset"], paren_size , self.textFormat(self.parenthesis_color[paren_level]) )
                else:
                    pass
            
        self.setCurrentBlockState(paren_level)

class HighlightingRule():

    def __init__( self, pattern, format ):

        self.pattern = pattern
        self.format = format

class TestApp( QMainWindow ):

    def __init__(self):

        QMainWindow.__init__(self)
        font = QFont()
        font.setFamily( "Noto Sans Mono" )
        font.setFixedPitch( True )
        font.setPointSize( 11 )
        editor = QTextEdit()
        editor.setFont( font )
        highlighter = MyHighlighter( editor, "Classic" )
        self.setCentralWidget( editor )
        self.setWindowTitle( "Syntax Highlighter" )


if __name__ == "__main__":
    app = QApplication( sys.argv )
    window = TestApp()
    window.show()
    sys.exit( app.exec_() )


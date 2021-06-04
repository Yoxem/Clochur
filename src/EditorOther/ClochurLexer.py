
import re
from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtGui import *



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

        font = QFont()
        font.setFamily(parent.font_family)
        font.setPointSize(parent.font_size)
        self.setDefaultFont(font)

        # set indent style
        self.setAutoIndentStyle(QsciScintilla.AiMaintain)

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
            #print("%s, %d" % (line, rainbow_state))
            length = len(line)

            i = 0

            new_state = self.Default

            line_utf8 = line.decode('utf-8')

            split_pattern = re.compile(r'(\s+|\\%|%|\\\[|\\\]|[[]|[]])')

            line_utf8_splitted = split_pattern.split(line_utf8)

            line_utf8_splitted_len_pair = [{"str": item, "len" : len(bytearray(item, "utf-8"))} for item in line_utf8_splitted]


            #print(line_utf8_splitted_len_pair)

            is_comment = False

            i = 0
            if index > 0:
            #    pos = SCI(QsciScintilla.SCI_GETLINEENDPOSITION, index - 1)
                rainbow_state = SCI(QsciScintilla.SCI_GETLINESTATE, index - 1)
            #    print(rainbow_state)

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
                    rainbow_state = (rainbow_state + 1) % 7
                elif item["str"] == "]":
                    rainbow_state = (rainbow_state - 1) % 7
                    new_state = getattr(self, "Rainbow" + str(rainbow_state))
                else:
                    pass

                word_length = item["len"]
                i += word_length
                set_style(word_length, new_state)

                if new_state != self.Comment:
                    new_state = self.Default

                SCI(QsciScintilla.SCI_SETLINESTATE, index, rainbow_state)

            index += 1

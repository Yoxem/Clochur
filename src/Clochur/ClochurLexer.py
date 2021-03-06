#!/usr/bin/env python3
#-*-coding:utf-8-*-

import re
from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtGui import *
from Clochur.Parser import Parser




class ClochurLexer(QsciLexerCustom):

    def __init__(self, parent=None):
        QsciLexerCustom.__init__(self, parent)
        self._styles = {
            0: 'Default',
            1: 'Keyword',
            2: 'Comment',
            3: 'Number',
            4: 'String',
            5: 'Rainbow0',
            6: 'Rainbow1',
            7: 'Rainbow2',
            8: 'Rainbow3',
            9: 'Rainbow4',
            10: 'Rainbow5',
            11: 'Rainbow6',
        }

        for (k,v) in self._styles.items():
            setattr(self, v, k)

        self.QUOTES = ['"']
        self.PARENTHESIS = ["[", "]"]

        self.parent = parent

        
        macro_list = ['docu', 'font', 'font-family','font-size','underline','bold','italic']
        boolean_list = ['True', 'False']
        operator_list = [ '-', '+', '*', '/', '>' ,'=','<','>=','<=']
        # SILE and SILE-STRING-ADD! is internal, so they're not added.
        function_list = ['if', 'docu', 'docu-para', 'script', 'call','xml-to-string', 'begin',
            'str','str-append', 'str-append-many','set!','print', 'define', 'def-syntax', 'lambda', 'eval','cons',
            'car','cdr','ls-ref','ls']
        self.PRIMARY = macro_list + boolean_list + operator_list + function_list

        self.split_pattern = re.compile(r'(\s+|\\%|%|\\\[|\\\]|[[]|[]]|\\\"|\")')

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
            return QColor("#85cf65")
        elif style == self.Number:
            return QColor("#00aaff")
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
        rainbow_state = 0 # 0~6  = Rainbowmode ; 0~6 + 10 (i.e. 10~16)  = Rainbowmode with string

        index = SCI(QsciScintilla.SCI_LINEFROMPOSITION, start)

        for line in source.splitlines(True):
            #print("%s, %d" % (line, rainbow_state))
            length = len(line)

            i = 0

            new_state = self.Default

            line_utf8 = line.decode('utf-8')

            line_utf8_splitted = self.split_pattern.split(line_utf8)

            line_utf8_splitted_len_pair = [{"str": item, "len" : len(bytearray(item, "utf-8"))} for item in line_utf8_splitted]


            #print(line_utf8_splitted_len_pair)

            is_comment = False
            next_is_defined_var = False

            i = 0
            if index > 0:
            #    pos = SCI(QsciScintilla.SCI_GETLINEENDPOSITION, index - 1)
                rainbow_state = SCI(QsciScintilla.SCI_GETLINESTATE, index - 1)
            #    print(rainbow_state)

            tmp_parser = Parser()

            for item in line_utf8_splitted_len_pair:

                ## add to complete list
                #if item["str"] in [ "define", "def-syntax"]:
                #    next_is_defined_var = True
                #elif next_is_defined_var == True and not (item["str"] in ["[","]"]):
                #    print(next_is_defined_var,item["str"])
                #    self.parent.append_autocompletion_item(item["str"])
                #    next_is_defined_var = False
                #else:
                #    pass

                '''comment'''
                if item["str"] == "%" and rainbow_state < 10:
                    is_comment = True
                if is_comment == True:
                    new_state = self.Comment # end of comment
                
                # string
                elif re.match(tmp_parser.string_pattern ,item["str"]):
                    new_state = self.String
                elif (re.match(r"[\"]([^\"\\]|[\\][\"nt]|[\\][\\])+?", item["str"]) or re.match(r'["]' ,item["str"])) \
                    and rainbow_state < 10:
                    rainbow_state += 10
                    new_state = self.String
                elif (re.match(r"([^\"\\]|[\\][\"nt]|[\\][\\])+?[\"]" ,item["str"]) or re.match(r'["]' ,item["str"])) \
                    and rainbow_state >= 10:
                    new_state = self.String
                    rainbow_state -= 10
                
                elif item["str"] == "]" and rainbow_state >= 10:
                    new_state = self.String
                elif rainbow_state >= 10:
                    new_state = self.String

                elif item["str"] in self.PRIMARY: # keywords
                    new_state = self.Keyword

                # number
                elif re.match(tmp_parser.int_pattern,item["str"]):
                    new_state = self.Number
                elif re.match(tmp_parser.float_pattern, item["str"]):
                    new_state = self.Number

                #parenthesis: rainbow mode
                elif item["str"] == "[":
                    if rainbow_state >= 10:
                        new_state = self.String
                    elif rainbow_state < 7:
                        new_state = getattr(self, "Rainbow" + str(rainbow_state))
                        rainbow_state = (rainbow_state + 1) % 7
                    else:
                        pass
                elif item["str"] == "]":
                    if rainbow_state >= 10:
                        new_state = self.String
                    elif rainbow_state < 7:
                        rainbow_state = (rainbow_state - 1) % 7
                        new_state = getattr(self, "Rainbow" + str(rainbow_state))
                    else:
                        pass
                else:
                    pass

                word_length = item["len"]
                i += word_length
                set_style(word_length, new_state)

                if new_state != self.Comment:
                    new_state = self.Default

                SCI(QsciScintilla.SCI_SETLINESTATE, index, rainbow_state)

            index += 1

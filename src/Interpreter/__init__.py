#-*-coding:utf-8-*-

import re

class Parser():

    def __init__(self):
        float_pattern  =r"(?P<flo>[+-]?\d+[.]\d+)"
        int_pattern  =r"(?P<int>[+-]?\d+)"
        symbol_pattern = r"(?P<sym>[_a-zA-Z][_0-9a-zA-Z]+)"
        string_pattern = r"(?P<str>[\"]([^\"\\]|[\\][\"\\nt])+[\"])"
        parenthesis_pattern = r"(?P<paren>[[]|[]])"
        percent_pattern = r"(?P<percent>[%])"
        space_pattern  = r"(?P<space>[ \t]+)"
        newline_pattern = r"(?P<nl>)\n"
        inside_docu_pattern = r"(?P<other>([^%\[\]\n\s\\]|[\\][%\[\]]?)+)"


        self.total_pattern = re.compile("|".join([float_pattern,int_pattern,symbol_pattern,string_pattern,parenthesis_pattern,
                                                percent_pattern,inside_docu_pattern,space_pattern,newline_pattern]))

        self.clc_sexp = None
        self.tokenized = None
        self.index = None
    

    def get_clc_sexp(self, clc):
        self.clc_sexp = clc
        self.tokenized = self.remove_comment(self.tokenize(self.clc_sexp))
        print(self.parse_main(self.tokenized))

    def tokenize(self, clc):
        line_no = 1
        column = 0
        column_offset = 0
        find_iterator = re.finditer(self.total_pattern, self.clc_sexp)
        result = []
        for i in find_iterator:
            column = i.start() - column_offset

            if i.group(0) == '\n':
                item = {"token" : i.group(0), "line": line_no, "col" : column, "type": i.lastgroup}
                line_no += 1
                column_offset  = i.end()
            else:
                item = {"token" : i.group(0), "line": line_no, "col" : column, "type": i.lastgroup}
        
            

            result.append(item)

        [print(i["token"]) for i in result]

        return result
    def remove_comment(self, series):
        result = []
        is_comment_token = False
        for i in series:
            if i["token"] == "%":
                is_comment_token = True
            elif i["token"] == "\n":
                if is_comment_token == True:
                    is_comment_token = False
                else:
                    result.append(i)
            elif is_comment_token == True:
                pass
            else:
                result.append(i)
        
        return result


    def move_forward(self):
        self.index += 1

    def parse_main(self, series):
        self.index = 0

        processed_series = [{"token": "[", "line": None, "col": None, "type": None}] + series + \
                            [{"token": "]", "line": None, "col": None, "type": None}]
        result = self.parse(processed_series)

        if self.index < len(processed_series):
            raise Exception("the parenthesis ] is not balanced.")
        else:
            return result

    def atom(self, series):
        result = series[self.index]
        if result["type"] == "int":
            result["token"] = int(result["token"])
        elif result["type"] == "flo":
            result["token"] = float(result["token"])
        else:
            pass
        self.move_forward()
        return result

    def parse(self, series):
        result = None
        if series[self.index]["token"] == "[":
            result = []
            self.move_forward()
            try:
                while series[self.index]["token"] != "]":
                    item = self.parse(series)
                    result.append(item)

                self.move_forward()

                return result
            except IndexError:
                raise Exception("the parenthesis [ is not balanced.")


        else:
            result = self.atom(series)
            return result
            

'''test'''
a = Parser()
text = '''[[[ 123 1.23 abc "\\123\\"喵喵"] 我是貓，喵\[喵\]貓\%。喵喵%喵
]]'''

a.get_clc_sexp(text)
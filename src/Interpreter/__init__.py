#-*-coding:utf-8-*-

import re

class Parser():

    def __init__(self):
        float_pattern  =r"(?P<flo>[+-]?\d+[.]\d+)"
        int_pattern  =r"(?P<int>[+-]?\d+)"
        symbol_pattern = r"(?P<sym>[_a-zA-Z][!._0-9a-zA-Z]*)"
        string_pattern = r"(?P<str>[\"]([^\"\\]|[\][\\\"\n\t])*[\"])"
        parenthesis_pattern = r"(?P<paren>[[]|[]])"
        percent_pattern = r"(?P<percent>[%])"
        space_pattern  = r"(?P<space>[ \t]+)"
        newline_pattern = r"(?P<nl>)\n"
        inside_docu_pattern = r"(?P<other>([^%\[\]\n\s\\]|[\\][%\[\]]?)+)"


        self.total_pattern = re.compile("|".join([float_pattern,int_pattern,symbol_pattern,string_pattern,parenthesis_pattern,
                                                percent_pattern,inside_docu_pattern,space_pattern,newline_pattern]))

        self.clc_sexp = None
        self.tokenized = None
        self.parse_tree = None
        self.index = None
    

    def get_clc_sexp(self, clc):
        self.clc_sexp = clc
        self.tokenized = self.remove_comment(self.tokenize(self.clc_sexp))
        self.parse_tree = self.parse_main(self.tokenized)

    def generate_printable_sexp(self, sexp):
        if isinstance(sexp, list):
            result = "["
            for i in sexp:
                result += (self.generate_printable_sexp(i) + " ")
            result += "]"

            return result
        else:
            if sexp["type"] == "str":
                result = sexp["token"].replace("\\", "\\\\")
                result = "\""+ result[1:-1].replace("\"", "\\\"") + "\""
                return result
            else:
                return str(sexp["token"])

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
text = '''[+[- 2 3][* 5.0 6]]
[define var1 [+[- 2 3][* 5.0 6]]]
[set! var1 [* 10 2]]
[define foo [lambda [x y] [begin [+ x y][set! var1 10] 7]]]
[foo 12 5]
[print [+ var1 5]]
'''

"""text = '''[[[ 123 1.23 abc "\\123\\\"貓貓貓"] 我是貓，喵\[喵\]貓\%。喵喵%喵
]]'''
"""

a.get_clc_sexp(text)

#print(a.parse_tree)
print(a.generate_printable_sexp(a.parse_tree))


'''
macro expansion for example:

the eclipsis (...) shouldn't be seperated from variable.
[def-syntax foo #:with-space
    [[_ x y] [+ x y]]
    [[_ x y z...] [+ x [foo y z...]]]
]
'''

class Intepreter:
    def __init__(self):

        self.macro_env = [dict()] # {"foo": {"before":[_ x y], "after":[+ x y]}, ...}
        # environment
        self.env = [dict()] 
        self.macro_list = dict()


    def remove_spaces_and_newlines(self, sexp):
        if isinstance(sexp, list):
            if isinstance(sexp[0], dict) and sexp[0]["token"] == "docu":
                result = []
                for i in sexp[1:]:
                    if i["type"] in ["space", "nl"]:
                        result.append(i)
                    else:
                        result.append(self.remove_spaces_and_newlines(i))

                    result = sexp[0] + result
            else:
                result = [self.remove_spaces_and_newlines(i)
                            for i in sexp if not isinstance(i, dict) or (i["type"] not in ["space", "nl"])]
            return result
        else:
            return sexp

    

    def interprete(self, sexps):
        sexps = self.remove_spaces_and_newlines(sexps)

        #environment = [dict()]
        for sexp in sexps:
            self.interprete_aux(sexp)
    
    def interprete_aux(self, sexp):
        if isinstance(sexp, dict):
            if sexp["type"] == "sym":
                res = None
                for i in reversed(self.env):
                    if sexp["token"] in i.keys():
                        res = i[sexp["token"]]
                        break
                
                if res == None:
                    raise Exception("Ln %d, Col %d: the variable is not found!" % (sexp["line"], sexp["col"], sexp["token"]))
                else:
                    return res

            else:
                return sexp["token"]
        elif sexp[0]["token"] in ["+", "-", "*", "/"]:
            if len(sexp) != 3:
                raise Exception("Ln %d, Col %d: the argument length %d of %s is not correct." %
                        (sexp[0]["line"], sexp[0]["col"], len(sexp), a.generate_printable_sexp(sexp)))
            else:
                if sexp[0]["token"] == "+":
                    return self.interprete_aux(sexp[1]) + self.interprete_aux(sexp[2])
                elif sexp[0]["token"] == "-":
                    return self.interprete_aux(sexp[1]) - self.interprete_aux(sexp[2])
                elif sexp[0]["token"] == "*":
                    return self.interprete_aux(sexp[1]) * self.interprete_aux(sexp[2])
                else:
                    return self.interprete_aux(sexp[1]) / self.interprete_aux(sexp[2])
        elif sexp[0]["token"] == "define":
            if sexp[1]["type"] != "sym":
                raise Exception("Ln %d, Col %d: the type of %s should be symbol, not %s" %
                        (sexp[1]["line"], sexp[1]["col"], sexp[1], sexp[1]["type"]))
            else:        
                self.env[-1][sexp[1]["token"]] = self.interprete_aux(sexp[2])
        elif sexp[0]["token"] == "print":
            if len(sexp) != 2:
                raise Exception("Ln %d, Col %d: the argument number of print should be 1" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                print(str(self.interprete_aux(sexp[1])))
        elif sexp[0]["token"] == "set!":
            if sexp[1]["type"] != "sym":
                raise Exception("Ln %d, Col %d: the type of %s should be symbol, not %s" %
                        (sexp[1]["line"], sexp[1]["col"], sexp[1], sexp[1]["type"]))
            else:
                is_found = False  
                for i in reversed(self.env):
                    if sexp[1]["token"] in i.keys():
                        i[sexp[1]["token"]] = self.interprete_aux(sexp[2])
                        is_found = True
                        break
                
                if not is_found:
                    raise Exception("Ln %d, Col %d: the variable %s is not found!" % (sexp[1]["line"], sexp[1]["col"], sexp[1]["token"]))

                
        elif sexp[0]["token"] == "begin":
            if len(sexp) == 1:
                raise Exception("Ln %d, Col %d: begin should have argument(s)!" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                for i in sexp[1:]:
                    self.interprete_aux(i)
        
        elif sexp[0]["token"] == "lambda":
            if not isinstance(sexp[1], list):
                raise Exception("Ln %d, Col %d: %s should be a variable list" %
                        (sexp[1]["line"], sexp[1]["col"], sexp[1]))
            else:
                return Lambda(sexp[1], sexp[2], self.env)
        else:
            sexp_new = [self.interprete_aux(x) for x in sexp]
            
            if isinstance(sexp_new[0], Lambda):
                vars = sexp_new[0].vars
                env = sexp_new[0].env
                body = sexp_new[0].body
                vars_input = sexp_new[1:]

                if len(vars) != len(vars_input):
                    raise Exception("Ln %d, Col %d: argument length is not matched." %
                        (self.get_first_item(sexp[0])["line"], self.get_first_item(sexp[0])["col"]))
                
                new_env_block = dict()
                for i in range(len(vars)):
                    new_env_block[vars[i]] = vars_input[i]
                
                new_env = [new_env_block] + env

                old_env = self.env
                self.env = new_env
                ret = self.interprete_aux(body)
                self.env = old_env
                return ret
                



    def get_first_item(self, sexp):
        if isinstance(sexp, list):
            sexp = sexp[0]

        return sexp


class Lambda:
    def __init__(self, vars, body, env):
        for i in vars:
            if i["type"] != "sym":
                raise Exception("Line %d, Col %d: the variable of lambda should be a variable, not %s"
                                    % (i["line"], i["col"], str(i["token"])))
            else:
                self.vars = [i["token"] for i in vars]
                self.body = body
                self.env = env

interp = Intepreter()

interp.interprete(a.parse_tree)



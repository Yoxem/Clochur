#-*-coding:utf-8-*-

import re

class Parser():

    def __init__(self):
        float_pattern  =r"(?P<flo>[+-]?\d+[.]\d+)"
        int_pattern  =r"(?P<int>[+-]?\d+)"
        symbol_pattern = r"(?P<sym>[_a-zA-Z][-!._0-9a-zA-Z]*)"
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


            






'''
macro expansion for example:

the eclipsis (...) shouldn't be seperated from variable.
[def-syntax foo
    [[_ x y] [+ x y]]
    [[_ x y z...] [+ x [foo y z...]]]]'''

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
        
        # macro expanding
        elif sexp[0]["token"] in self.macro_list.keys():
            macro_pair = self.macro_list[sexp[0]["token"]]
            
            is_found = False
            macro_len = len(sexp)

            unification = dict()

            for i in macro_pair:
                if len(i["before"]) == macro_len:
                    unification = self.unify(sexp, i["before"], unification)
                    syntax_after = i["after"]
                    is_found = True
                    break
                elif len(i["before"]) < macro_len and re.match(r".+[.]{3}$", i["before"][-1]["token"]):
                    unification = self.unify(sexp, i["before"], unification)
                    syntax_after = i["after"]
                    is_found = True
                    break
                else:
                    pass
            
            if not is_found:
                raise Exception("The syntax pattern for %s is not found." % a.generate_printable_sexp(sexp))
            else:
                new_sexp = self.macro_expand(syntax_after, unification)
                
                return self.interprete_aux(new_sexp)

                
                #elif len(i["before"]) < macro_len and 

        elif sexp[0]["token"] == "define":
            if sexp[1]["type"] != "sym":
                raise Exception("Ln %d, Col %d: the type of %s should be symbol, not %s" %
                        (sexp[1]["line"], sexp[1]["col"], sexp[1], sexp[1]["type"]))
            else:        
                self.env[-1][sexp[1]["token"]] = self.interprete_aux(sexp[2])
        elif sexp[0]["token"] == "str":
            if len(sexp) != 2:
                raise Exception("Ln %d, Col %d: the argument number of str should be 1" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                return str(self.interprete_aux(sexp[1]))
        elif sexp[0]["token"] == "print":
            if len(sexp) != 2:
                raise Exception("Ln %d, Col %d: the argument number of print should be 1" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                print(self.interprete_aux(sexp[1]))
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
                    raise Exception("Ln %d, Col %d: the variable %s is not found!" %
                            (sexp[1]["line"], sexp[1]["col"], sexp[1]["token"]))
        
        
        elif sexp[0]["token"] == "def-syntax":
            if len(sexp) < 3:
                raise Exception("Ln %d, Col %d: def-syntax should have 2 or more arguments!" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                syntax_name = sexp[1]["token"] # {"foo": {"before":[_ x y], "after":[+ x y]}, ...}
                #removed_dict_form = self.remove_dict_form(sexp[2:])

                result_list = []
                
                for i in sexp[2:]:
                #for i in removed_dict_form:
                    syntax_before = i[0]
                    syntax_after = i[1]
                    item = {"before": syntax_before, "after": syntax_after}
                    result_list.append(item)
                
                self.macro_list[syntax_name] = result_list

        elif sexp[0]["token"] == "begin":
            if len(sexp) == 1:
                raise Exception("Ln %d, Col %d: begin should have argument(s)!" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                for i in sexp[1:]:
                    ret = self.interprete_aux(i)
                return ret
        
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
                

    def remove_dict_form(self, sexp):
        if isinstance(sexp, list):
            return [self.remove_dict_form(x) for x in sexp]
        else:
            return sexp["token"]

    def get_first_item(self, sexp):
        if isinstance(sexp, list):
            sexp = sexp[0]

        return sexp

    def unify(self, sexp, before_stx, unification):
        for i in range(len(before_stx)):
            if isinstance(before_stx[i], list):
                unification = unify(sexp[i], before_stx[i], unification)
            elif before_stx[i]["token"] in unification.keys():
                raise Exception("the variable %s is double defined." % before-stx[i])
            elif re.match(r".+[.]{3}$", before_stx[i]["token"]):
                if i == len(before_stx) - 1:
                    unification[before_stx[i]["token"]] = {"content": sexp[i:], "dotted":True}
                else:
                    raise Exception("the variable %s is put in the wrong position." % before_stx[i])
            else:
                unification[before_stx[i]["token"]] = {"content": sexp[i], "dotted": False}
        
        return unification

    def macro_expand(self, after_stx, unification):
        if isinstance(after_stx, list):
            raw_list = [self.macro_expand(i, unification) for i in after_stx]

            result_list = []

            for i in raw_list:
                if isinstance(i, list):
                    result_list.append(i)
                elif "dotted" not in i.keys():
                    result_list.append(i)
                elif i["dotted"] == True:
                    result_list += i["content"]
                else:
                    result_list.append(i["content"])
            
            return result_list

        else:
            if after_stx["token"] in unification.keys():
                return unification[after_stx["token"]]
            else:
                return after_stx




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





'''test'''
a = Parser()
text = '''
[def-syntax bar
    [[_ x y] [+ x y]]
    [[_ x y z...] [+ x [bar y z...]]]]

[print[str[bar 156 6546 146514 10 6]]]

[+[- 2 3][* 5.0 6]]
[define var1 [+[- 2 3][* 5.0 6]]]
[set! var1 [* 10 2]]
[define foo [lambda [x y] [begin [+ x y][set! var1 10] 7]]]
[foo 12 5]
[print [+ var1 5]]
'''

"""text = '''[[[ 123 1.23 abc "\\123\\\"貓貓貓"] 我是貓，喵\[喵\]貓\%。喵喵%喵
]]'''
"""

interp = Intepreter()

a.get_clc_sexp(text)

interp.interprete(a.parse_tree)

#print(a.parse_tree)
print(a.generate_printable_sexp(a.parse_tree))
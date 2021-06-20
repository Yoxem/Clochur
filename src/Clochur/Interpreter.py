#-*-coding:utf-8-*-

import re
import xml.etree.ElementTree as ET
import itertools
from Clochur.Parser import Parser

'''
macro expansion for example:

the eclipsis (...) shouldn't be seperated from variable.
[def-syntax foo
    [[_ x y] [+ x y]]
    [[_ x y z...] [+ x [foo y z...]]]]'''

class Interpreter:
    def __init__(self):

        self.macro_env = [dict()] # {"foo": {"before":[_ x y], "after":[+ x y]}, ...}
        # environment
        self.env = [dict()] 
        self.macro_list = dict()
        self.silexml = ET.Element('sile')

        #self.editor = None

        #if "editor" in kwargs.keys():
        #    self.editor = kwargs["editor"]

        self.preprocessing_commands = '''[def-syntax docu
    [[_ x] [SILE[docu-aux x]]]
    [[_ x y...] [SILE[docu-aux x y...]]]]

[def-syntax docu-aux
    [[_ x] [SILE-STRING-ADD![str x]]]
    [[_ [x...]] [SILE-STRING-ADD![str [x...]]]]
    [[_ x y...] [begin[docu-aux x] [docu-aux y...]]]]

[def-syntax font
[[_ [para...] inner] [call font [para...] inner]]
]

[def-syntax font-family
[[_ font-f text] [font [[family font-f]] text]]
]

[def-syntax font-size
[[_ sz text] [font [[size sz]] text]]
]

[script "packages/rules"] % for underline

[def-syntax underline
[[_ text] [call underline text]]
]

[def-syntax bold
[[_ text] [font [[weight 900]] text]]
]

[def-syntax italic
[[_ text] [font [[style "italic"]] text]]
]
'''
        self.prepocess()

    def prepocess(self):
        tmp_parser = Parser()
        parse_tree = tmp_parser.get_clc_sexp(self.preprocessing_commands)
        self.interprete(parse_tree)


    def remove_spaces_and_newlines(self, sexp):
        is_inside_defstx = False
        return self.remove_spaces_and_newlines_aux(sexp, is_inside_defstx)

    def remove_spaces_and_newlines_aux(self, sexp, is_inside_defstx):
        if isinstance(sexp, list):
            result = []
            if isinstance(sexp[0], dict) and sexp[0]["token"] == "def-syntax":
                is_inside_defstx = True
            if isinstance(sexp[0], dict) and sexp[0]["token"] == "docu" \
                and is_inside_defstx == False:
                result = []
                # the sexp[1] is a space, so skip it.
                for i in sexp[2:]:
                    if isinstance(i, list):
                        result.append(self.remove_spaces_and_newlines_aux(i, is_inside_defstx))
                    elif i["type"] in ["space", "nl"]:
                        result.append(i)
                    else:
                        result.append(self.remove_spaces_and_newlines_aux(i, is_inside_defstx))

                result = sexp[0:1] + result

            else:
                result = [self.remove_spaces_and_newlines_aux(i, is_inside_defstx)
                            for i in sexp if not isinstance(i, dict) or (i["type"] not in ["space", "nl"])]
            return result
        else:
            return sexp

    def destring(self, string):
        tmp_parser = Parser()
        string_pattern = tmp_parser.string_pattern
        if isinstance(string, dict):
            string = string["token"]
        if not isinstance(string, str):
            string = str(string)
        if re.match(string_pattern, string):
            # reverse the escape characters
            while True:
                string_before = string
                string = re.sub(r'\\"(.+)',r'"\1',string)
                if string_before == string:
                    break
            return string[1:-1]
        else:
            return string

    # \[ => [ ; \] => ] ; \\ => \
    def remove_escaping_chars(self, sexp):
        if isinstance(sexp, list):
            sexp = [self.remove_escaping_chars(x) for x in sexp]
        elif not sexp["type"] in ["int", "flo"]:
            sexp_word = sexp["token"]
            sexp_word = sexp_word.replace("\\[", "[")
            sexp_word = sexp_word.replace("\\]", "]")
            sexp_word = sexp_word.replace("\\\\", "\\")
            sexp["token"] = sexp_word
        else:
            pass
        
        return sexp


    def interprete(self, sexps):
        sexps = self.remove_escaping_chars(sexps)
        sexps = self.remove_spaces_and_newlines(sexps)
        result = None

        #environment = [dict()]
        for sexp in sexps:
            result = self.interprete_aux(sexp)
        
        return result
    
    def interprete_aux(self, sexp):
        if isinstance(sexp, dict):
            if sexp["type"] == "sym":
                res = None
                for i in reversed(self.env):
                    if sexp["token"] in i.keys():
                        res = i[sexp["token"]]
                        break
                
                if res == None:
                    raise Exception("Ln %d, Col %d: the variable %s is not found!" % (sexp["line"], sexp["col"], sexp["token"]))
                else:
                    return res

            else:
                return sexp["token"]
        
        elif isinstance(sexp, Lambda):
            return sexp
        
        # lambda apply
        elif isinstance(sexp[0], Lambda):
            return self.apply(sexp)

        # count sexp[0] first.
        elif isinstance(sexp[0], list):
            new_sexp_0 = self.interprete_aux(sexp[0])
            new_sexp = [new_sexp_0] + sexp[1:]
            return self.interprete_aux(new_sexp)
        

        elif sexp[0]["token"] in ["+", "-", "*", "/", "<", "=", ">", "<=", ">="]:
            if len(sexp) != 3:
                parser = Parser()
                raise Exception("Ln %d, Col %d: the argument length %d of %s is not correct." %
                        (sexp[0]["line"], sexp[0]["col"], len(sexp), parser.generate_printable_sexp(sexp)))
            else:
                if sexp[0]["token"] == "+":
                    return self.interprete_aux(sexp[1]) + self.interprete_aux(sexp[2])
                elif sexp[0]["token"] == "-":
                    return self.interprete_aux(sexp[1]) - self.interprete_aux(sexp[2])
                elif sexp[0]["token"] == "*":
                    return self.interprete_aux(sexp[1]) * self.interprete_aux(sexp[2])
                elif sexp[0]["token"] == "/":
                    return self.interprete_aux(sexp[1]) / self.interprete_aux(sexp[2])
                elif sexp[0]["token"] == "<":
                    return self.interprete_aux(sexp[1]) < self.interprete_aux(sexp[2])
                elif sexp[0]["token"] == "=":
                    return self.interprete_aux(sexp[1]) == self.interprete_aux(sexp[2])
                elif sexp[0]["token"] == ">":
                    return self.interprete_aux(sexp[1]) > self.interprete_aux(sexp[2]) 
                elif sexp[0]["token"] == ">=":
                    return self.interprete_aux(sexp[1]) <= self.interprete_aux(sexp[2])
                else:
                    return self.interprete_aux(sexp[1]) >= self.interprete_aux(sexp[2]) 
                                        
        
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
                elif len(i["before"]) < macro_len and isinstance(i["before"][-1], dict) \
                    and re.match(r".+[.]{3}$", i["before"][-1]["token"]):
                    unification = self.unify(sexp, i["before"], unification)
                    syntax_after = i["after"]
                    is_found = True
                    break
                else:
                    pass
            
            if not is_found:
                parser = Parser()
                raise Exception("The syntax pattern for %s is not found." % parser.generate_printable_sexp(sexp))
            else:
                new_sexp = self.macro_expand(syntax_after, unification)
                
                return self.interprete_aux(new_sexp)

                
                #elif len(i["before"]) < macro_len and 

        elif sexp[0]["token"] == "define":
            if sexp[1]["type"] != "sym":
                raise Exception("Ln %d, Col %d: the type of %s should be symbol, not %s" %
                        (sexp[1]["line"], sexp[1]["col"], sexp[1], sexp[1]["type"]))
            else:
                defined_var = sexp[1]["token"]   
                self.env[-1][defined_var] = self.interprete_aux(sexp[2])
                
                #if self.editor != None:
                #    self.editor.append_autocompletion_item(defined_var)
            return ""
            
        elif sexp[0]["token"] == "if":
            if len(sexp) != 4:
                raise Exception("Ln %d, Col %d: the number of argument of if should be 3." %
                        (sexp[0]["line"], sexp[0]["col"]))
            cond = self.interprete_aux(sexp[1])
            if cond:
                return self.interprete_aux(sexp[2])
            else:
                return self.interprete_aux(sexp[3])

        elif sexp[0]["token"] == "str":
            if len(sexp) != 2:
                raise Exception("Ln %d, Col %d: the argument number of str should be 1" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                vars_frame = [frame.keys() for frame in self.env]
                vars_list = list(itertools.chain.from_iterable(vars_frame))
                macro_vars = self.macro_list.keys()
                if isinstance(sexp[1], dict) and \
                    (not (sexp[1]["token"] in macro_vars)) and \
                    (not (sexp[1]["token"] in vars_list)) :
                    return str(self.destring(sexp[1]["token"]))
                else:
                    return str(self.destring(self.interprete_aux(sexp[1])))

        elif sexp[0]["token"] == "str-append":
            if len(sexp) != 3:
                raise Exception("Ln %d, Col %d: the argument number of str should be 2" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                return self.interprete_aux(sexp[1]) + self.interprete_aux(sexp[2])

        elif sexp[0]["token"] == "print":
            if len(sexp) != 2:
                raise Exception("Ln %d, Col %d: the argument number of print should be 1" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                result = self.interprete_aux(sexp[1])
                print(result)
                return ""
        elif sexp[0]["token"] == 'eval':
            if len(sexp) != 2:
                raise Exception("Ln %d, Col %d: the argument number of eval should be 1" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                result = self.interprete_aux(sexp[1])
                return result
        
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

            return ""
        
        
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

                # add to auto completion list
                #if self.editor != None:
                #    self.editor.append_autocompletion_item(defined_var)

            return ""

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
        # [script "packages/font-fallback"]
        elif sexp[0]["token"] == "script":
            if not len(sexp) == 2:
                raise Exception("Ln %d, Col %d: argument length of script should be 1" %
                        (sexp[0]["line"], sexp[0]["col"]))
            else:
                script_xml = ET.Element('script')
                script_xml.attrib["src"] = self.destring(sexp[1]["token"])
                self.silexml.append(script_xml)

        elif sexp[0]["token"] == "docu-para":
            if not len(sexp) == 2:
                raise Exception("Ln %d, Col %d: argument length of docu-para should be 1" %
                        (sexp[0]["line"], sexp[0]["col"]))
            attrib_dict = dict()
            for i in sexp[1]:
                attrib_name = i[0]["token"]
                attrib_value = self.destring(i[1]["token"])
                self.silexml.attrib[attrib_name] = attrib_value
        
        # [call callee {[[attr1 val1] [attr2 val2] ...]} {inner_val}]
        elif sexp[0]["token"] == "call":
            callee = sexp[1]["token"]
            call_xml = ET.Element(callee)
            if len(sexp) == 4 or (len(sexp) == 3 and isinstance(sexp[2], list)):
                for i in sexp[2]:
                    attrib_name = i[0]["token"]
                    attrib_value = self.destring(self.interprete_aux(i[1]))
                    call_xml.attrib[attrib_name] = attrib_value

                if len(sexp) == 4:
                    call_xml.text = self.destring(self.interprete_aux(sexp[3]))
                
                self.silexml.append(call_xml)
                return SubXMLElement(call_xml)
            elif len(sexp) == 3:
                call_xml.text = self.destring(self.interprete_aux(sexp[2]))
                self.silexml.append(call_xml)
                return SubXMLElement(call_xml)
            elif len(sexp) == 2:
                self.silexml.append(call_xml)
                return SubXMLElement(call_xml)
            else:
                raise Exception("Line %d, Col. %d, the form of call is mal-formed." % (sexp[0]["line"], sexp[0]["col"]))
        
        # make a List class object
        elif sexp[0]["token"] == "ls":
            result = []

            if len(sexp) == 1:
                return result
            else:
                result = [self.interprete_aux(x) for x in sexp[1:]]

            return List(result)

        # (car List)
        elif sexp[0]["token"] == "car":
            if len(sexp) != 2:
                raise Exception("Line %d, Col. %d, the argument length should be 1" % (sexp[0]["line"], sexp[0]["col"]))
            elif not isinstance(sexp[1], List):
                raise Exception("Line %d, Col. %d, the argument is not a list." % (sexp[1]["line"], sexp[1]["col"]))
            else:
                ls = sexp[1].ls
                return ls[0]

        # (cdr List)
        elif sexp[0]["token"] == "cdr":
            if len(sexp) != 2:
                raise Exception("Line %d, Col. %d, the argument length should be 1" % (sexp[0]["line"], sexp[0]["col"]))
            elif not isinstance(sexp[1], List):
                raise Exception("Line %d, Col. %d, the argument is not a list." % (sexp[1]["line"], sexp[1]["col"]))
            else:
                ls = sexp[1].ls
                return ls[1:]

        # (cons any List)
        elif sexp[0]["token"] == "cons":
            if len(sexp) != 3:
                raise Exception("Line %d, Col. %d, the argument length should be 2" % (sexp[0]["line"], sexp[0]["col"]))
            elif not isinstance(sexp[2], List):
                raise Exception("Line %d, Col. %d, the 2nd argument of cons is not a list." % (sexp[2]["line"], sexp[2]["col"]))
            else:
                car = sexp[1]
                cdr = sexp[2].ls
                result_ls = List([sexp[1]]+cdr)
                return result_ls
        

        elif sexp[0]["token"] == "ls-ref":
            if len(sexp) != 3:
                raise Exception("Line %d, Col. %d, the argument length should be 1" % (sexp[0]["line"], sexp[0]["col"]))
            elif not isinstance(sexp[1], List):
                raise Exception("Line %d, Col. %d, the 2nd argument of cons is not a list." % (sexp[2]["line"], sexp[2]["col"]))


        
        # if it's a sub-xml-element, show the string form of it, or return the input unchanged.
        # It's recommended to use it only print it in terminal with 'print'
        elif sexp[0]["token"] == "xml-to-string":
            if len(sexp) != 2:
                raise Exception("Line %d, Col. %d, the argument of SHOW-XML-TREE is mal-formed" % (sexp[0]["line"], sexp[0]["col"]))
            else:
                res = self.interprete_aux(sexp[1])
                if isinstance(res, SubXMLElement):
                    return ET.tostring(res.element, encoding='unicode')
                else:
                    return res

        # append string to <sile>
        elif sexp[0]["token"] == "SILE-STRING-ADD!":
            subelements_found = [x for x in self.silexml.iter() if x != self.silexml]
            if subelements_found:
                if subelements_found[-1].tail == None:
                    subelements_found[-1].tail = self.interprete_aux(sexp[1])
                else:
                    subelements_found[-1].tail += self.interprete_aux(sexp[1])
            else:
                if self.silexml.text == None:
                    self.silexml.text = self.interprete_aux(sexp[1])
                else:
                    self.silexml.text += self.interprete_aux(sexp[1])


        elif sexp[0]["token"] == "SILE":
            inner = self.interprete_aux(sexp[1])
            
            return ET.tostring(self.silexml, encoding="unicode")

        else:
            ret = self.apply(sexp)
            return ret

    def apply(self, sexp):
            
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
                unification = self.unify(sexp[i], before_stx[i], unification)
            elif before_stx[i]["token"] in unification.keys():
                raise Exception("the variable %s is double defined." % before_stx[i])
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


# a sub xml element that is shown as a empty string, but inside it is a xml element
class SubXMLElement:
    def __init__(self, element):
        self.element = element
    
    def __str__(self):
        return ""

# closure
class List:
    def __init__(self, ls):
        self.ls = ls

# closure
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

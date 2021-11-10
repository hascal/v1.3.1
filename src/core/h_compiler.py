# The Hascal Compiler
#
# The Hascal Programming Language
# Copyright 2019-2022 Hascal Development Team,
# all rights reserved.

from .h_error import HascalException
from .h_lexer import Lexer
from .h_parser import Parser
import sys

class Generator(object):
      def __init__(self,BASE_DIR):
            self.BASE_DIR = BASE_DIR
            self.src_includes = ""
            self.src_pre_main = ""
            #init standard types
            self.types = {
                  'int' : Type('int',True),
                  'float' : Type('float',True),
                  'bool' : Type('bool',True),
                  'char' : Type('char',True),
                  'string' : Type('string',True),
                  # 'File' : Type('File',True),
            }

            self.vars = { } # global vars
            self.consts = { } # global consts

            # functions
            self.funcs = {
                  'print' : Function('print',{'...':'...'},'void')
            }

            # list of imported libraries
            self.imported = []

      def generate(self, tree,use=False):
            _expr = self.walk(tree)
            result = ""
            for e in _expr :
                  result += e['expr']

            if use :
                  return f"\n{self.src_pre_main}\n"
            else :
                  runtime = open(self.BASE_DIR+"/hlib/d/std.d").read()
                  runtime_h = open(self.BASE_DIR+"/hlib/d/std.h").read()
                  return f"{runtime_h}\n{runtime}\n{self.src_includes}\n{self.src_pre_main}\n{result}\n"
      
      def exists(self,name):
            if name in self.funcs:
                  return True
            elif name in self.types :
                  return True
            elif name in self.vars :
                  return True
            if name in self.consts:
                  return True
            return False

      def add_to_output(self,d_code,dh_code):
            self.src_includes += '\n' + dh_code + '\n'
            self.src_pre_main += '\n' + d_code + '\n'

      def walk(self, node):
            # {
            #     <statements>
            # }
            if node[0] == 'block':
                  result = [ ] # list of exprs and statements
                  for statement in node[1:]:
                        result.append(self.walk(statement))
                  return result
            if node[0] == 'in_block':
                  result = [ ] # list of exprs and statements
                  for statement in node[1:]:
                        result.append(self.walk(statement))
                  return result
            if node[0] == 'block_struct':
                  current_vars = self.vars
                  self.vars = { }
                  result = [ ] # list of exprs and statements
                  for statement in node[1:]:
                        result.append(self.walk(statement))
                  self.vars = current_vars
                  return result
            #-------------------------------------
            # statement declares :
            
            # var <name> : <return_type>
            if node[0] == 'declare' and node[1] == "no_equal":
                  _name = node[3]
                  _type = node[2]
                  _line = node[4]
                  if _name in self.vars or _name in self.consts :
                        HascalException(f"'{_name}' exists ,cannot redefine it:{_line}")
                        sys.exit(1)
                  elif _name in self.types :
                        HascalException(f"'{_name}' defined as a type ,cannot redefine it as a variable:{_line}")
                        sys.exit(1)
                  elif not _type in self.types :
                        HascalException(f"Type '{_type}' not defined:{_line}")
                        sys.exit(1)
                  else:
                        self.vars[_name] = Var(_name,_type)
                        res = ""
                        if not self.types[_type].stdtype : res = "%s %s = {} ;\n" % (_type,_name)
                        else : res = "%s %s;\n" % (_type,_name)
                        expr = {
                              'expr' : res,
                              'type' : _type,
                              'name' : _name,
                        }
                        return expr

            # var <name> : <return_type> = <expr>
            if node[0] == 'declare' and node[1] == "equal2":
                  _name = node[3]
                  _type = node[2]
                  _expr = self.walk(node[4])
                  _line = node[4]

                  if _name in self.vars or _name in self.consts  :
                        HascalException(f"'{_name}' exists ,cannot redefine it:{_line}")
                        sys.exit(1)
                  elif _name in self.types :
                        HascalException(f"'{_name}' defined as a type ,cannot redefine it as a variable:{_line}")
                        sys.exit(1)
                  elif _type != _expr['type'] :
                        HascalException(f"Mismatched type {_type} and {_expr['type']}:{_line}")
                        sys.exit(1)
                  elif not _type in self.types :
                        HascalException(f"Type '{_type}' not defined:{_line}")
                        sys.exit(1)
                  else:
                        self.vars[_name] = Var(_name,_type)
                        expr = {
                              'expr' : "%s %s = %s;\n" % (_type,_name,_expr['expr']),
                              'type' : _type,
                              'name' : _name,
                        }
                        return expr
                        
            
            # var <name> : [<return_type>]
            if node[0] == 'declare_array' and node[1] == "no_equal":
                  _name = node[3]
                  _type = node[2]
                  _line = node[4]

                  if _name in self.vars or _name in self.consts :
                        HascalException(f"'{_name}' exists ,cannot redefine it:{_line}")
                        sys.exit(1)
                  elif _name in self.types :
                        HascalException(f"'{_name}' defined as a type ,cannot redefine it as a variable:{_line}")
                        sys.exit(1)
                  elif not _type in self.types :
                        HascalException(f"Type '{_type}' not defined:{_line}")
                        sys.exit(1)
                  else:
                        self.vars[_name] = Var(_name,_type,is_array=True)
                        res = ""
                        if self.types[_type].stdtype : res = "%s[] %s = {} ;\n" % (_type,_name)
                        else : res = "%s[] %s;\n" % (_type,_name)
                        expr = {
                              'expr' : res,
                              'type' : _type,
                              'name' : _name,
                        }
                        return expr

            # var <name> : [<return_type>] = <expr>
            if node[0] == 'declare_array' and node[1] == "equal2":
                  _name = node[3]
                  _type = node[2]
                  _expr = self.walk(node[4])
                  _line = node[5]

                  if _name in self.vars or _name in self.consts :
                        HascalException(f"'{_name}' exists ,cannot redefine it:{_line}")
                        sys.exit(1)
                  elif _name in self.types :
                        HascalException(f"'{_name}' defined as a type ,cannot redefine it as a variable:{_line}")
                        sys.exit(1)
                  elif _type != _expr['type'] :
                        HascalException(f"Mismatched type {_type} and {_expr['type']}:{_line}")
                        sys.exit(1)
                  elif not _type in self.types :
                        HascalException(f"Type '{_type}' not defined:{_line}")
                        sys.exit(1)
                  else:
                        self.vars[_name] = Var(_name,_type,is_array=True)
                        expr = {
                              'expr' : "%s[] %s = %s ;\n" % (_type,_name,_expr['expr']),
                              'type' : _type,
                              'name' : _name,
                        }
                        return expr
                              
            # const <name> : <return_type> = <expr> ;
            if node[0] == 'declare' and node[1] == "const":
                  _name = node[3]
                  _type = node[2]
                  _expr = self.walk(node[4])
                  _line = node[5]

                  if _name in self.vars or _name in self.consts :
                        HascalException(f"'{_name}' exists ,cannot redefine it:{_line}")
                        sys.exit(1)
                  elif _name in self.types :
                        HascalException(f"'{_name}' defined as a type ,cannot redefine it as a constant:{_line}")
                        sys.exit(1)
                  elif _type != _expr['type'] :
                        HascalException(f"Mismatched type {_type} and {_expr['type']}:{_line}")
                        sys.exit(1)
                  elif not _type in self.types :
                        HascalException(f"Type '{_type}' not defined:{_line}")
                        sys.exit(1)
                  else:
                        self.consts[_name] = Const(_name,_type,is_array=True)
                        expr = {
                              'expr' : "const %s %s = %s ;\n" % (node[2],node[3],_expr['expr']),
                              'type' : _type,
                              'name' : _name,
                        }
                        return expr
            #-------------------------------------
            # <name> = <expr> ;         
            if node[0] == 'assign':
                  _name = node[1][0]
                  _expr = self.walk(node[2])
                  _line = node[3]

                  if len(node[1]) == 1:
                        if _name in self.consts :
                              HascalException(f"'{_name}'is a constant, cannot change it")
                              sys.exit(1)
                        elif _name in self.types:
                              HascalException(f"'{_name}'is a type, cannot assign it")
                              sys.exit(1)
                        elif not _name in self.vars :
                              HascalException(f"Variable '{_name}' not defined")
                              sys.exit(1) 
                        elif _name in self.vars and (self.vars[_name].type != _expr['type']):
                              HascalException(f"Mismatched type {self.vars[_name].type} and {_expr['type']}:{_line}")
                              sys.exit(1)
                        else :
                              expr = {
                                    'expr' :  "%s = %s;\n" % (_name,_expr['expr']),
                                    'type' : self.vars[_name].type,
                              }
                              return expr
                  else :
                        _full_name = '.'.join(arg for arg in node[1])
                        if _name in self.consts :
                              HascalException(f"'{_name}'is a constant, cannot change it")
                              sys.exit(1)
                        elif _name in self.types:
                              HascalException(f"'{_name}'is a type, cannot assign it")
                              sys.exit(1)
                        elif not _name in self.vars :
                              HascalException(f"Variable '{_name}' not defined")
                              sys.exit(1) 
                        # this code have bug. because search name in struct members
                        elif _full_name in self.vars and (self.vars[_name].type != _expr['type']):
                              HascalException(f"Mismatched type {self.vars[_name].type} and {_expr['type']}:{_line}")
                              sys.exit(1)
                        else :
                              expr = {
                                    'expr' : "%s = %s;\n" % (_full_name,_expr['expr']),
                                    'type' : self.vars[_name].type,
                              }
                              return expr

            # <name>[<expr>] = <expr>;
            if node[0] == 'assign_var_index':
                  _name = node[1][0]
                  _expr_index = self.walk(node[2])
                  _expr = self.walk(node[3])
                  _line = node[3]

                  if len(node[1]) == 1:
                        if _name in self.consts :
                              HascalException(f"'{_name}'is a constant, cannot change it")
                              sys.exit(1)
                        elif _name in self.types:
                              HascalException(f"'{_name}'is a type, cannot assign it")
                              sys.exit(1)
                        elif not _name in self.vars :
                              HascalException(f"Variable '{_name}' not defined")
                              sys.exit(1) 
                        elif _name in self.vars and (self.vars[_name].type != _expr['type']):
                              HascalException(f"Mismatched type {self.vars[_name].type} and {_expr['type']}:{_line}")
                              sys.exit(1)
                        else :
                              expr = {
                                    'expr' : "%s[%s] = %s;\n" % (_name,_expr_index['expr'],_expr['expr']),
                                    'type' : self.vars[_name].type,
                              }
                              return expr
                  else :
                        _full_name = '.'.join(arg for arg in node[1])
                        if _name in self.consts :
                              HascalException(f"'{_name}'is a constant, cannot change it")
                              sys.exit(1)
                        elif _name in self.types:
                              HascalException(f"'{_name}'is a type, cannot assign it")
                              sys.exit(1)
                        elif not _name in self.vars :
                              HascalException(f"Variable '{_name}' not defined")
                              sys.exit(1) 
                        # this code have bug. because search name in struct members
                        elif _full_name in self.vars and (self.vars[_name].type != _expr['type']):
                              HascalException(f"Mismatched type {self.vars[_name].type} and {_expr['type']}:{_line}")
                              sys.exit(1)
                        else :     
                              expr = {
                                    'expr' : "%s[%s] = %s;\n" % (_full_name,_expr_index['expr'],_expr['expr']),
                                    'type' : self.vars[_name].type,
                              }
                              return expr
            #-----------------------------------------
            # return <expr>
            if node[0] == 'return':
                  _expr = self.walk(node[1])
                  expr = {
                        'expr' : "return %s;\n" %  _expr['expr'],
                        'type' : _expr['type']
                  }
                  return expr 
            #-----------------------------------------
            # break
            if node[0] == 'break':
                  expr = {
                        'expr' : 'break;\n',
                        'type' : 'void', # todo
                  }
                  return expr
            
            # continue
            if node[0] == 'continue':
                  expr = {
                        'expr' : 'continue;\n',
                        'type' : 'void', # todo
                  }
                  return expr
            #-----------------------------------------
            # use <lib_name> ;
            if node[0] == 'use':
                  if sys.platform.startswith('win32'):
                        if node[1] in self.imported :
                              ...
                        else :
                              name = '.'.join(name for name in node[1])
                              if name.startswith("d.") :
                                    path = node[1]
                                    final_path = str(self.BASE_DIR+"\\hlib\\")

                                    ends_of_path = path[-1]
                                    for x in path[:-1]:
                                          final_path += x + "\\"
                                    final_path_h = final_path + ends_of_path + ".h"
                                    final_path += ends_of_path + ".d"
                                    try:
                                          with open(final_path, 'r') as fd:
                                                d_code = fd.read()
                                                with open(final_path_h,'r') as fh :
                                                      dh_code = fh.read()
                                                      self.imported.append(name)
                                                      self.add_to_output(d_code,dh_code)
                                    except FileNotFoundError:
                                          HascalException(f"cannot found '{name}' library. Are you missing a library ?")
                                          sys.exit(1)
                              else :
                                    path = node[1]
                                    final_path = str(self.BASE_DIR+"\\hlib\\")

                                    ends_of_path = path[-1]
                                    for x in path[:-1]:
                                          final_path += x + "\\"
                                    final_path += ends_of_path + ".has"

                                    try:
                                          with open(final_path, 'r') as f:
                                                parser = Parser()
                                                tree = parser.parse(Lexer().tokenize(f.read()))
                                                generator = Generator()
                                                output_d = generator.generate(tree,True)

                                                self.imported.append(name)
                                                self.imported += generator.imported
                                                self.add_to_output(output_d,generator.src_includes)
                                                self.funcs += generator.funcs
                                                self.types += generator.types
                                    except FileNotFoundError:
                                          HascalException(f"cannot found '{name}' library. Are you missing a library ?")
                                          sys.exit(1)

                  else :
                        if node[1] in self.imported :
                              ...
                        else :
                              name = '.'.join(name for name in node[1])
                              if name.startswith("d.") :
                                    path = node[1]
                                    final_path = str(self.BASE_DIR+"/hlib/")

                                    ends_of_path = path[-1]
                                    for x in path[:-1]:
                                          final_path += x + "/"
                                    final_path_h = final_path + ends_of_path + ".h"
                                    final_path += ends_of_path + ".d"
                                    try:
                                          with open(final_path, 'r') as fd:
                                                d_code = fd.read()
                                                with open(final_path_h,'r') as fh :
                                                      dh_code = fh.read()
                                                      self.imported.append(name)
                                                      self.add_to_output(d_code,dh_code)
                                    except FileNotFoundError:
                                          HascalException(f"cannot found '{name}' library. Are you missing a library ?")
                                          sys.exit(1)
                              else :
                                    path = node[1]
                                    final_path = str(self.BASE_DIR+"/hlib/")

                                    ends_of_path = path[-1]
                                    for x in path[:-1]:
                                          final_path += x + "/"
                                    final_path += ends_of_path + ".has"

                                    try:
                                          with open(final_path, 'r') as f:
                                                parser = Parser()
                                                tree = parser.parse(Lexer().tokenize(f.read()))
                                                generator = Generator()
                                                output_d = generator.generate(tree,True)

                                                self.imported.append(name)
                                                self.imported += generator.imported
                                                self.add_to_output(output_d,generator.src_includes)
                                                self.funcs += generator.funcs
                                                self.types += generator.types
                                    except FileNotFoundError:
                                          HascalException(f"cannot found '{name}' library. Are you missing a library ?")
                                          sys.exit(1)
            
            # local use <lib_name> ;
            if node[0] == 'use_local':
                  if sys.platform.startswith('win32'):
                        if node[1] in self.imported :
                              ...
                        else :
                              name = '.'.join(name for name in node[1])
                              if name.startswith("d."):
                                    path = name.split('.')
                                    final_path = ""

                                    ends_of_path = path[-1]
                                    for x in path[:-1]:
                                          final_path += x + "\\"
                                    final_path_h = final_path + ends_of_path + ".h"
                                    final_path += ends_of_path + ".d"

                                    try:
                                          with open(final_path, 'r') as fd:
                                                d_code = fd.read()
                                                with open(final_path_h,'r') as fh :
                                                      dh_code = fh.read()
                                                      self.imported.append(name)
                                                      self.add_to_output(d_code,dh_code)
                                    except FileNotFoundError:
                                          HascalException(f"cannot found '{name}' library. Are you missing a library ?")

                              else :
                                    tmp = '.'.join(name for name in node[1])
                                    path = tmp.split('.')
                                    final_path = ""

                                    ends_of_path = path[-1]
                                    for x in path[:-1]:
                                          final_path += x + "\\"
                                    final_path += ends_of_path + ".has"

                                    try:
                                          with open(final_path, 'r') as f:
                                                parser = Parser()
                                                tree = parser.parse(Lexer().tokenize(f.read()))
                                                generator = Generator()
                                                output_d = generator.generate(tree,True)

                                                self.imported.append(name)
                                                self.imported += generator.imported
                                                self.add_to_output(output_d, generator.src_includes)
                                                self.funcs += generator.funcs
                                    except FileNotFoundError:
                                          HascalException(f"cannot found '{name}' library. Are you missing a library ?")
                              
                  elif sys.platform.startswith('linux'):
                        name = '.'.join(name for name in node[1])
                        if name.startswith("d."):
                              path = name.split('.')
                              final_path = ""

                              ends_of_path = path[-1]
                              for x in path[:-1]:
                                    final_path += x + "/"
                              final_path_h = final_path + ends_of_path + ".h"
                              final_path += ends_of_path + ".d"

                              try:
                                    with open(final_path, 'r') as fd:
                                          d_code = fd.read()
                                          with open(final_path_h,'r') as fh :
                                                dh_code = fh.read()
                                                self.imported.append(name)
                                                self.add_to_output(d_code,dh_code)
                              except FileNotFoundError:
                                    HascalException(f"cannot found '{name}' library. Are you missing a library ?")

                        else :
                              tmp = '.'.join(name for name in node[1])
                              path = tmp.split('.')
                              final_path = ""

                              ends_of_path = path[-1]
                              for x in path[:-1]:
                                    final_path += x + "/"
                              final_path += ends_of_path + ".has"

                              try:
                                    with open(final_path, 'r') as f:
                                          parser = Parser()
                                          tree = parser.parse(Lexer().tokenize(f.read()))
                                          generator = Generator()
                                          output_d = generator.generate(tree,True)

                                          self.imported.append(name)
                                          self.imported += generator.imported
                                          self.add_to_output(output_d, generator.src_includes)
                                          self.funcs += generator.funcs
                              except FileNotFoundError:
                                    HascalException(f"cannot found '{name}' library. Are you missing a library ?")
            #-----------------------------------------
            # function <name> {
            #     <block>
            # }
            # or :
            # function <name> : <return_type> {
            #     <block>
            # }

            # function <name>() {
            #     <block>
            # }
            # or :
            # function <name>() : <return_type> {
            #     <block>
            # }

            # function <name>(<args>) {
            #     <block>
            # }
            # or :
            # function <name>(<args>) : <return_type> {
            #     <block>
            # }
            if node[0] == 'function':
                  current_vars = self.vars
                  _name = node[2]
                  _return_type = node[1]
                  _params = { }

                  params = node[3].split(',')
                  if len(params) != 1:
                        for p in params:
                              param = p.split(' ')
                              _params[param[1]] = param[0]
                              if param[0].endswith(']'): self.vars[param[1]] = Var(param[1],param[0],is_array=True)
                              else : self.vars[param[1]] = Var(param[1],param[0])
                  elif len(params) == 1 and params[0] != '' and params[0] != None: 
                        param = params[0].split(' ')
                        _params[param[1]] = param[0]
                        self.vars[param[1]] = Var(param[1],param[0])

                  self.funcs[_name] = Function(_name,_params,_return_type)
                  _name = node[2]
                  _type = node[1]
                  _compiled_params = node[3]
                  _expr = self.walk(node[4])
                  res = ""
                  for e in _expr :
                        res += e['expr']
                  res =  "%s %s(%s) {\n%s\n}\n" % (_type,_name,_compiled_params,res) 
                  self.vars = current_vars
                  
                  expr = {
                        'expr' : res,
                        'type' : _type,
                  }
                  return expr
            #-------------------------------------
            if node[0] == "inline_function" :
                  _name = node[2]
                  _return_type = node[1]
                  _params = { }

                  params = node[3].split(',')
                  if len(params) != 1:
                        for p in params:
                              param = p.split(' ')
                              _params[param[1]] = param[0]
                  elif len(params) == 1 and (params[0] != '' or params[0] != None) : 
                        param = params[0].split(' ')
                        _params[param[1]] = param[0]

                  self.funcs[_name] = Function(_name,_params,_return_type)
            #-------------------------------------
            # struct <name> {
            #     <struct_declares>
            # }
            if node[0] == 'struct':
                  _name = node[1]
                  _body = self.walk(node[2])
                  _members = { } # todo
                  # generate output code and member
                  res = ""
                  for e in _body :
                        res += e['expr']
                        _members[e['name']] = self.types[e['type']]
                  self.types[_name] = Struct(_name,_members)
                  expr = {
                        'expr' : 'struct %s{\n%s\n}\n' % (_name,res),
                        'type' : _name,
                  } 
                  return expr
            #-------------------------------------
            # enum <name> {
            #     <enum_names>
            # }
            if node[0] == 'enum':
                  _name = node[1]
                  _members = node[2]
                  self.types[_name] = Enum(_name,_members)
                  expr = {
                        'expr' : 'enum %s{\n%s\n}\n' % (_name,_members),
                        'type' : _name,
                  } 
                  return expr
            #-------------------------------------
            # if <condition> {
            #     <block>
            # }   

            # or : 

            # if <condition> {
            #     <block>
            # }else {
            #     <block>
            # }

            # or :

            # if <condition> {
            #     <block>
            # }else if <condition> {
            #     <block>
            # }
            if node[0] == 'if':
                  cond = self.walk(node[1])
                  body = self.walk(node[2])

                  res = ""
                  for e in body :
                        res += e['expr']

                  expr = {
                        'expr' : 'if(%s){\n%s\n}\n' % (cond['expr'],res),
                        'type' : '',
                  }
                  return expr
            if node[0] == 'if_else':
                  cond = self.walk(node[1])
                  body = self.walk(node[2])
                  body2 = self.walk(node[3])
                  res = ""
                  for e in body :
                        res += e['expr']
                  res2 = ""
                  for e in body2 :
                        res += e['expr']
                  expr = {
                        'expr' : 'if(%s){\n%s\n}else {\n%s\n}\n' % (cond['expr'],res,res2),
                        'type' : '',
                  }
                  return expr
            if node[0] == 'if_else2':
                  cond = self.walk(node[1])
                  body = self.walk(node[2])
                  body2 = self.walk(node[3])
                  res = ""
                  for e in body :
                        res += e['expr']
                  expr = {
                        'expr' : 'if(%s){\n%s\n}else %s\n' % (cond['expr'],res,body2['expr']),
                        'type' : '',
                  }
                  return expr
            #------------------------------------
            # for <name> to <expr> {
            #     <block>
            # }
            if node[0] == 'for':      
                  name = node[1]
                  expr0 = self.walk(node[2])
                  expr1 = self.walk(node[3])
                  body = self.walk(node[4])
                  res = ""
                  for e in body :
                        res += e['expr']
                  expr = {
                        'expr' : 'for(%s=%s;%s<=%s;%s++){\n%s\n}\n' % (name,expr0['expr'],name,expr1['expr'],name,res),
                        'type' : '',
                  }
                  return expr
            
            # for <name> downto <expr> {
            #     <block>
            # }
            if node[0] == 'for_down':      
                  name = node[1]
                  expr0 = self.walk(node[2])
                  expr1 = self.walk(node[3])
                  body = self.walk(node[4])
                  res = ""
                  for e in body :
                        res += e['expr']
                  expr = {
                        'expr' :  'for(%s=%s;%s>=%s;%s--){\n%s\n}\n' % (name,expr0['expr'],name,expr1['expr'],name,res),
                        'type' : '',
                  }
                  return expr
            #--------------------------------------
            # while <condition> {
            #     <block>
            # }
            if node[0] == 'while':      
                  cond = self.walk(node[1])
                  body = self.walk(node[2])
                  res = ""
                  for e in body :
                        res += e['expr']
                  expr = {
                        'expr' : 'while(%s){\n%s\n}\n' % (cond['expr'],res),
                        'type' : '',
                  }
                  return expr
            #---------------------------------------
            # <expr> ;                    
            if node[0] == 'expr':
                  _expr = self.walk(node[1])
                  expr = {
                        'expr' : "%s;\n" % (_expr['expr']),
                        'type' : _expr['type'],
                  }
                  return expr
            #---------------------------------------
            # <expr>(<params>);
            if node[0] == 'call':
                  _name = node[1]
                  if self.exists(_name):
                        if _name == "print":
                              expr = {
                                    'expr' : 'writeln(%s)' % (', '.join(self.walk(arg)['expr'] for arg in node[2])),
                                    'type' : self.funcs['print'].return_type,
                              }
                              return expr
                        else :
                              expr = {
                                    'expr' : "%s(%s)" % (_name, ', '.join(self.walk(arg)['expr'] for arg in node[2])),
                                    'type' : self.funcs[_name].return_type,
                              }
                              return expr
                  else :
                        HascalException(f"Function '{_name}' not defined")
                        sys.exit(1)
            # --------------operators-----------------
            if node[0] == 'add':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s + %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            if node[0] == 'add_cont':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s ~ %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            if node[0] == 'sub':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s - %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            if node[0] == 'mul':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s * %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            if node[0] == 'div':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s / %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            if node[0] == 'pow':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s ^ %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            if node[0] == 'paren_expr':
                  _expr0 = self.walk(node[1])

                  expr = {
                        'expr' : '(%s)' % (_expr0['expr']),
                        'type' : _expr0['type'] 
                  }
                  return expr
            if node[0] == 'cond':
                  _expr0 = self.walk(node[1])

                  expr = {
                        'expr' : '%s' % (_expr0['expr']),
                        'type' : _expr0['type'] 
                  }
                  return expr

            if node[0] == 'not':
                  _expr0 = self.walk(node[1])

                  expr = {
                        'expr' : '!%s' % (_expr0['expr']), # may have bug
                        'type' : _expr0['type'] 
                  }
                  return expr

            if node[0] == 'and':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])
                  _line = node[3]

                  expr = {
                        'expr' : '%s && %s' % (_expr0['expr'],_expr1['expr']),
                        'type' : _expr0['type'] # or : _expr1['type']
                  }
                  return expr

            if node[0] == 'or':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])
                  _line = node[3]
                  expr = {
                        'expr' : '%s || %s' % (_expr0['expr'],_expr1['expr']),
                        'type' : _expr0['type'] # or : _expr1['type']
                  }
                  return expr
            # --------------end of operators-----------------  

            # ---------------conditions---------------------
            # <expr> == <expr>
            if node[0] == 'equals':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s == %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            # <expr> != <expr>
            if node[0] == 'not_equals':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s != %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            # <expr> >= <expr>
            if node[0] == 'greater_equals':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s >= %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            # <expr> <= <expr>
            if node[0] == 'less_equals':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s <= %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr
            
            # <expr> > <expr>
            if node[0] == 'greater':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s > %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            # <expr> < <expr>
            if node[0] == 'less':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type'] :
                        HascalException(f"Mismatched type {_expr0['type']} and {_expr1['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s < %s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            # not <expr>
            if node[0] == 'not_cond':
                  _expr0 = self.walk(node[1])

                  expr = {
                        'expr' : '!%s' % (_expr0['expr']), # may have bug
                        'type' : _expr0['type'] 
                  }
                  return expr

            # true / false
            if node[0] == 'bool_cond':
                  expr = {
                        'expr' : '%s' % (node[1]),
                        'type' : 'bool',
                  }
                  return expr
            
            # <expr>
            if node[0] == 'expr_cond':
                  _expr = self.walk(node[1])

                  expr = {
                        'expr' : '!%s' % (_expr['expr']), # may have bug
                        'type' : _expr['type'] 
                  }
                  return expr
            
            # <expr>
            if node[0] == 'paren_cond':
                  _expr = self.walk(node[1])

                  expr = {
                        'expr' : '(%s)' % (_expr['expr']), # may have bug
                        'type' : _expr['type'] 
                  }
                  return expr
            # ---------------end of conditions---------------------     
            # <name>
            if node[0] == 'var':
                  _name = node[1][0]
                  _line = node[2]
                  if len(node[1]) == 1:
                        
                        if _name in self.vars:
                              expr = {
                                    'expr' : "%s" % (_name),
                                    'type' : self.vars[_name].type,
                              }
                              return expr
                        elif _name in self.consts :
                              expr = {
                                    'expr' : "%s" % (_name),
                                    'type' : self.consts[_name].type,
                              }
                              return expr
                        elif _name in self.types :
                              expr = {
                                    'expr' : "%s" % (_name),
                                    'type' : self.types[_name],
                              }
                              return expr
                        # todo : pass function name
                        else :
                              HascalException(f"'{_name}' was not declared in this scope:{_line}")
                              sys.exit(1)
                        
                  else :
                        _full_name = '.'.join(arg for arg in node[1])
                        # todo : should return member's type not struct
                        if _name in self.vars:
                              expr = {
                                    'expr' : "%s" % (_full_name),
                                    'type' : self.vars[_name].type,
                              }
                              return expr
                        elif _name in self.consts :
                              expr = {
                                    'expr' : "%s" % (_full_name),
                                    'type' : self.consts[_name].type,
                              }
                              return expr
                        elif _name in self.types :
                              expr = {
                                    'expr' : "%s" % (_full_name),
                                    'type' : self.types[_name],
                              }
                              return expr
                        # todo : pass function name
                        else :
                              HascalException(f"'{_name}' was not declared in this scope:{_line}")
                              sys.exit(1)
            
            # <name>[<expr>]
            if node[0] == 'var_index':
                  _name = node[1][0]
                  _expr = self.walk(node[2])
                  _line = node[3]
                  if len(node[1]) == 1:
                        
                        if _name in self.vars:
                              expr = {
                                    'expr' : "%s" % (_name,_expr['expr']),
                                    'type' : self.vars[_name].type,
                              }
                              return expr
                        elif _name in self.consts :
                              expr = {
                                    'expr' : "%s" % (_name,_expr['expr']),
                                    'type' : self.consts[_name].type,
                              }
                              return expr
                        elif _name in self.types :
                              expr = {
                                    'expr' : "%s" % (_name,_expr['expr']),
                                    'type' : self.types[_name],
                              }
                              return expr
                        # todo : pass function name
                        else :
                              HascalException(f"'{_name}' was not declared in this scope:{_line}")
                              sys.exit(1)
                        
                  else :
                        # todo : type checker between expr and name type

                        _full_name = '.'.join(arg for arg in node[1])
                        # todo : should return member's type not struct
                        if _name in self.vars:
                              expr = {
                                    'expr' : "%s" % (_full_name,_expr['expr']),
                                    'type' : self.vars[_name].type,
                              }
                              return expr
                        elif _name in self.consts :
                              expr = {
                                    'expr' : "%s" % (_full_name,_expr['expr']),
                                    'type' : self.consts[_name].type,
                              }
                              return expr
                        elif _name in self.types :
                              expr = {
                                    'expr' : "%s" % (_full_name,_expr['expr']),
                                    'type' : self.types[_name],
                              }
                              return expr
                        else :
                              HascalException(f"'{_name}' was not declared in this scope:{_line}")
                              sys.exit(1)

            #-------------------------------------------
            # <expr> , <expr>
            if node[0] == 'exprs':
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[2])

                  if _expr0['type'] != _expr1['type']:
                        HascalException(f"Mismatched type {_type} and {_expr['type']}:{_line}")
                        sys.exit(1)
                  else :
                        expr = {
                              'expr' : '%s,%s' % (_expr0['expr'],_expr1['expr']),
                              'type' : _expr0['type'] # or : _expr1['type']
                        }
                        return expr

            # [<expr>]
            if node[0] == 'list':
                  _expr = self.walk(node[1])
                  expr = {
                        'expr' : '[%s]' % (_expr['expr']),
                        'type' : _expr['type'],
                  }
                  return expr
            #-------------------------------------------
            # <expr>.<name>
            if node[0] == '.':
                  _expr = self.walk(node[1])
                  _name = node[2]

                  expr = {
                        'expr' : '%s.%s' % (_expr['expr'],_name),
                        'type' : _expr['type'],
                  }
                  return expr
            # <expr>.<name>
            if node[0] == '.2':
                  # todo : name type and index type check
                  _expr0 = self.walk(node[1])
                  _expr1 = self.walk(node[3])
                  _name = node[2]

                  expr = {
                        'expr' : '%s.%s[%s]' % (_expr0['expr'],_name,_expr1['expr']),
                        'type' : _expr['type'],
                  }
                  return expr
            #--------------------------------------------
            if node[0] == 'string':
                  expr = {
                        'expr' : '"%s".dup' % node[1],
                        'type' : node[0],
                  }
                  return expr

            if node[0] == 'bool' or node[0] == 'float' or node[0] == 'int':
                  expr = {
                        'expr' : '%s' % node[1],
                        'type' : node[0],
                  }
                  return expr

            if node[0] == 'char':
                  expr = {
                        'expr' : '\'%s\'' % node[1],
                        'type' : node[0],
                  }
                  return expr

class Var(object):
      def __init__(self,name,type,is_array=False):
            self.name = name
            self.type = type
            self.is_array = is_array

class Const(Var):
      ...

class Function(object):
      def __init__(self,name,params,return_type):
            self.name = name
            self.params = params # type : dict
            self.return_type = return_type

class Struct(object):
      def __init__(self,name,members):
            self.name = name
            self.members = members
            self.stdtype = False

class Enum(Struct):
      ...

class Type(object):
      def __init__(self,type_name,stdtype):
            self.type_name = type_name
            self.stdtype = stdtype
      def __str__(self):
            return "%s" % (self.type_name)
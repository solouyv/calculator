#!/usr/bin/env python
'''
A module containing the main computing core for the calculator.

'''
import os
import re
import math
import operator
import importlib
import sys
from math import *
from decimal import Decimal as Dec
from distutils.util import strtobool

FUNKS, MUL_DIV, ADD_SUB, BOOL = range(4)

simpl_operations_order = ('^', '*', '/', '//', '%', '+', '-', '(', ')', 'abs',
                          'round', '<', '<=', '==', '!=', '>=', '>', ',',
                          'True', 'False')
funcshion = (operator.pow, operator.mul, operator.truediv, operator.floordiv,
             operator.mod, operator.add, operator.sub, '', '', abs, round,
             operator.lt, operator.le, operator.eq, operator.ne, operator.ge,
             operator.gt, '', '', '')

for oper, func in (zip(simpl_operations_order, funcshion)):
    globals()[oper] = func


class OperatorError(ArithmeticError):
    '''
    Custom exception handling class
    '''
    pass


class Import_module:
    '''
    Class for adding additional modules
    '''
    def __init__(self, modules):
        '''
        Accepts a list of imported modules
        '''
        self.modules = modules

    def import_module(self):
        '''
        Method for importing each module from the list
        both by relative name and full name
        '''
        for module in self.modules:
            if '/' in module or '\\' in module:
                path, name = os.path.split(module)
                if name.endswith('.py'):
                    name = name[:-3]
                if path not in sys.path:
                    sys.path.append(path)
                mod = importlib.import_module(name)
                for key, value in mod.__dict__.items():
                    globals()[key] = value
            else:
                mod = importlib.import_module(module.strip())
                for key, value in mod.__dict__.items():
                    globals()[key] = value


class My_str(str):
    '''
    Adds an additional art attribute to the standard str class
    '''
    def attr(self, attr):
        '''
        int: attr - the number of arguments passed to the math function
        '''
        self.attr = attr


class Parser:
    '''
    Class for parsing a string into elements
    '''
    def __init__(self, string):
        self.string = string
        self.pattern = (
            r'\d+\.\d+|\d+|\*+|\^+|/+|%+|\++|\-+|\(|\)|\w+|[<=!>]+|\,+')

    def pars(self):
        '''
        str: '-9+2+3' -> list: ['-', '9', '+', '2', '+', '3']

        Method for simple parsing of a string into list of elements

        '''
        self.form = re.findall(self.pattern, self.string)

    def hendling(self):
        '''
        list: ['-', '9', '+', '2', '+', '3'] ->
        list: ['-9', '+', '2', '+', '3']

        Method for hendling the list

        '''
        if self.form[0] == '+':
            del(self.form[0])
        elif self.form[0] == '-':
            self.form[0] = self.form.pop(0) + self.form[0]
        for index, item in enumerate(self.form):
            if item == '-' and self.form[index - 1] in {'(', ','}:
                self.form[index] = self.form.pop(index) + self.form[index]

    def get_list(self):
        '''
        Method to start hendling a string

        '''
        self.pars()
        self.hendling()
        return self.form


class Calculator:
    '''
    Calculator(str: form)

    Calculating the given str: expression
    '''
    def __init__(self, form):
        '''
        list: self.list_form - a list of elements obtained
            after processing by the Parser class
        list: self.opetations - a list of mathematical operators
            from self.list_form
        list: self.constants - a list of constants from the math module
            included in self.list_form
        tuple: self.simpl_operations - a tuple of lists:
            list: FUNKS - a list of math functions included in self.list_form
            list: MUL_DIV - a list of mathematical operators (^, *, /, //, %)
                in the order of their precedence
            list: ADD_SUB - a list of mathematical operators (+, -) in order
                of occurrence in self.list_form
            list: BOOL - a list of boolean operators (<, <=, ==,
                !=, >=, >) in order of occurrence in self.list_form

        '''
        self.list_form = [My_str(a) for a in Parser(form).get_list()]
        self.operations = [a for a in self.list_form if not self.is_number(a)]
        self.constants = [a for a in math.__dict__ if not a.startswith('_')
                          and not callable(math.__dict__[a])]
        self.simpl_operations = (
            [a for a in self.operations if a.isalpha() and
             a not in self.constants and a not in {'False', 'True'}],
            simpl_operations_order[0: 5],
            [a for a in self.operations if a in {'-', '+'}],
            [a for a in self.operations if a in {'<', '<=', '==',
                                                 '!=', '>=', '>'}])

    def is_number(self, item):
        '''
        is_number(str: '-9568.45') -> True
        is_number(str: 'asd') -> False

        Method for determining if the data in the string is a number
        '''
        if item.replace('.', '').replace('-', '').isdecimal():
            return True

    def checking(self):
        '''
        checking('5 - (9 / (-3)') -> ERROR: brackets are not balanced
        checking('foo') -> ERROR: unknown function 'foo'
        checking('9-3') -> True

        Data validation
        '''
        if self.list_form.count('(') != self.list_form.count(')'):
            raise OperatorError('ERROR: brackets are not balanced')
        for operator_ in self.operations:
            if operator_ not in globals():
                if operator_.startswith('-') and operator_[1:] in globals():
                    pass
                else:
                    raise OperatorError(
                        'ERROR: unknown function \'{}\''.format(operator_))
        return True

    def func_calc(self, oper):
        '''
        My_str: 'hypot(3, 4, 5, 6)' -> My_str

        Calculating mathematical functions
        '''
        index = self.list_form.index(oper)
        if oper in {'log', 'sqrt'} and float(self.list_form[index + 1]) < 0:
            raise OperatorError('ERROR: a negative number under the\
 \'{}\' function: {}'.format(oper, self.list_form[index + 1]))
        try:
            start = index + 1
            finish = start + self.list_form[index].attr
            arguments_of_func = [
                Dec(a) for a in self.list_form[start: finish] if a != ','
            ]
            self.list_form[start - 1: finish] = [
                My_str(globals()[oper](*arguments_of_func))
            ]
        except TypeError:
            arguments_of_func[-1] = int(arguments_of_func[-1])
            self.list_form[start - 1: finish] = [
                My_str(globals()[oper](*arguments_of_func))
            ]

    def mul_div_add_sub(self, oper):
        '''
        My_str: '5 * 2' -> My_str: '10'

        Calculation of mathematical operators (+, -, *, etc...)
        '''
        try:
            index = self.list_form.index(oper)
            item_1 = self.list_form[index - 1]
            item_2 = self.list_form[index + 1]
            self.list_form[index - 1: index + 2] = [My_str(
              globals()[oper](Dec(item_1), Dec(item_2)))]
        except ZeroDivisionError:
            raise OperatorError('ERROR: division by zero \'{}\''.format(
                ' '.join(self.list_form[index - 1: index + 2])))

    def logical_computation(self):
        '''
        My_str: '3 > 5' -> My_str: 'False'
        My_str: '3 > True' -> My_str: 'True'

        Calculation of boolean operators (<, <=, == etc...)

        '''
        for oper in self.simpl_operations[BOOL]:
            index = self.list_form.index(oper)
            if self.list_form[index - 1] in {'True', 'False'} and \
                    self.list_form[index + 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [My_str(
                      globals()[oper](strtobool(self.list_form[index - 1]),
                                      strtobool(self.list_form[index + 1])))]
            elif self.list_form[index - 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [My_str(
                      globals()[oper](strtobool(self.list_form[index - 1]),
                                      Dec(self.list_form[index + 1])))]
            elif self.list_form[index + 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [My_str(
                      globals()[oper](Dec(self.list_form[index - 1]),
                                      strtobool(self.list_form[index + 1])))]
            else:
                self.list_form[index - 1: index + 2] = [My_str(
                      globals()[oper](Dec(self.list_form[index - 1]),
                                      Dec(self.list_form[index + 1])))]

    def order_calculate(self):
        '''
        The order of execution of mathematical operators and functions
        '''
        for order in range(4):
            for oper in self.simpl_operations[order]:
                if order == FUNKS and oper in self.list_form:
                    self.func_calc(oper)
                    continue
                elif order == MUL_DIV and oper in self.list_form:
                    while oper in self.list_form:
                        self.mul_div_add_sub(oper)
                elif order == ADD_SUB and oper in self.list_form:
                    self.mul_div_add_sub(oper)
                elif order == BOOL and oper in self.list_form:
                    self.logical_computation()

    def chenge_constants(self):
        '''
        My_str: 'pi' -> My_str: '3.1415...'
        My_str: '-inf' -> My_str: '-inf'

        Replacing constants with their numerical values
        '''
        for index, item in enumerate(self.list_form):
            if item.startswith('-') and item[1:] in self.constants:
                temp_item = My_str(- globals()[item[1:]])
                self.list_form[index] = temp_item
            elif item in self.constants:
                self.list_form[index] = My_str(globals()[item])

    def search_brackets(self):
        '''
        My_str: '9-(8/(-2))' -> tuple: [2, 10]

        Finding the first paired brackets
        '''
        index_left_bracket = self.list_form.index('(')
        stat = 0
        for count, item in enumerate(self.list_form):
            if item == '(':
                stat += 1
            elif item == ')':
                stat -= 1
                if stat == 0:
                    index_right_bracket = count + 1
                    return index_left_bracket, index_right_bracket

    def calculate(self):
        '''
        Recursive search for parentheses and evaluation of expressions in them
        '''
        if self.checking():
            if '(' not in self.list_form:
                self.order_calculate()
            else:
                start, stop = self.search_brackets()
                list_form, self.list_form = (self.list_form,
                                             self.list_form
                                             [start + 1: stop - 1])
                self.calculate()
                try:
                    if list_form[start - 1] in self.simpl_operations[FUNKS]:
                        list_form[start - 1].attr = len(self.list_form)
                except IndexError:
                    pass
                list_form[start: stop] = self.list_form
                self.list_form = list_form
                self.calculate()

    def start(self):
        '''
        Method for starting calculations and handling incoming exceptions.
        Returns the result of a calculation or a description
        of the occurred exception.
        '''
        try:
            self.chenge_constants()
            self.calculate()
            if len(self.list_form) > 1:
                raise Exception()
            self.answer = self.list_form[0]
        except OperatorError as err:
            self.answer = str(err)
        except Exception:
            self.answer = 'ERROR: incorrect expression \'{}\''.format(
                ' '.join(self.list_form))
        finally:
            return self.answer

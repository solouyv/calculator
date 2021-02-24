#!/usr/bin/env python

import os
import re
import math
import operator
import importlib
import sys
from math import *
from decimal import Decimal as Dec

FUNKS, MUL_DIV, ADD_SUB, BOOL = range(4)

simpl_operations_order = ('^', '*', '/', '//', '%', '+', '-', '(', ')', 'abs',
                          'round', '<', '<=', '==', '!=', '>=', '>', ',')
funcshion = (operator.pow, operator.mul, operator.truediv, operator.floordiv,
             operator.mod, operator.add, operator.sub, '', '', abs, round,
             operator.lt, operator.le, operator.eq, operator.ne, operator.ge,
             operator.gt, '')

for oper, func in (zip(simpl_operations_order, funcshion)):
    globals()[oper] = func


class OperatorError(ArithmeticError):
    pass


class Impoprt_module:
    def __init__(self, modules):
        self.modules = modules

    def import_module(self):
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

    def attr(self, attr):
        self.attr = attr


class Parser:
    def __init__(self, string):
        self.string = string
        self.pattern = (
            r'\d+\.\d+|\d+|\*+|\^+|/+|%+|\++|\-+|\(|\)|\w+|[<=!>]+|\,+')

    def pars(self):
        self.form = re.findall(self.pattern, self.string)

    def hendling(self):
        if self.form[0] == '+':
            del(self.form[0])
        elif self.form[0] == '-':
            self.form[0] = self.form.pop(0) + self.form[0]
        for index, item in enumerate(self.form):
            if item == '-' and self.form[index - 1] in {'(', ','}:
                self.form[index] = self.form.pop(index) + self.form[index]

    def get_list(self):
        self.pars()
        self.hendling()
        return self.form


class Calculator:
    def __init__(self, form):
        self.list_form = [My_str(a) for a in Parser(form).get_list()]
        self.operations = [a for a in self.list_form if not self.is_number(a)]
        self.constants = [a for a in math.__dict__ if not a.startswith('_')
                          and not callable(math.__dict__[a])]
        self.simpl_operations = (
            [a for a in self.operations if a.isalpha() and
             a not in self.constants],
            simpl_operations_order[0: 5],
            [a for a in self.operations if a in {'-', '+'}],
            [a for a in self.operations if a in {'<', '<=', '==',
                                                 '!=', '>=', '>'}])

    def is_number(self, item):
        if item.replace('.', '').replace('-', '').isdecimal():
            return True

    def checking(self):
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
        for oper in self.simpl_operations[BOOL]:
            index = self.list_form.index(oper)
            if self.list_form[index - 1] in {'True', 'False'} and \
                    self.list_form[index + 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [My_str(
                      globals()[oper](bool(self.list_form[index - 1]),
                                      bool(self.list_form[index + 1])))]
            elif self.list_form[index - 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [My_str(
                      globals()[oper](bool(self.list_form[index - 1]),
                                      Dec(self.list_form[index + 1])))]
            elif self.list_form[index + 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [My_str(
                      globals()[oper](Dec(self.list_form[index - 1]),
                                      bool(self.list_form[index + 1])))]
            else:
                self.list_form[index - 1: index + 2] = [My_str(
                      globals()[oper](Dec(self.list_form[index - 1]),
                                      Dec(self.list_form[index + 1])))]

    def order_calculate(self):
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
        for index, item in enumerate(self.list_form):
            if item.startswith('-') and item[1:] in self.constants:
                temp_item = My_str(- globals()[item[1:]])
                self.list_form[index] = temp_item
            elif item in self.constants:
                self.list_form[index] = My_str(globals()[item])

    def search_brackets(self):
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

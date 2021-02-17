#!/usr/bin/env python

import re
import math
import operator
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


class My_str(str):
    def attr(self, attr):
        self.attr = attr


class Parser:
    def __init__(self, string):
        self.string = string
        self.pattern = (
            r'\d+\.\d+|\d+|\*+|\^+|/+|%+|\++|\-+|\(|\)|\w+|[<=!>]+|\,+')

    def hendling(self):
        if self.form[0] == '+':
            del(self.form[0])
        elif self.form[0] == '-':
            self.form[0] = self.form.pop(0) + self.form[0]
        for index, item in enumerate(self.form):
            if item == '-' and self.form[index - 1] == '(':
                self.form[index] = self.form.pop(index) + self.form[index]

    def pars(self):
        self.form = re.findall(self.pattern, self.string)
        self.hendling()
        return self.form


class Calculator:
    def __init__(self, form):
        self.list_form = [My_str(a) for a in Parser(form).pars()]
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
                raise OperatorError(
                    'ERROR: unknown function \'{}\''.format(operator_))
        return True

# ------------------------------------------------------------------------------

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
            if self.list_form[index - 1] == ')':
                item_1 = self.list_form[index - 2]
                start = index - 3
            else:
                item_1 = self.list_form[index - 1]
                start = index - 1
            if self.list_form[index + 1] == '(':
                item_2 = self.list_form[index + 2]
                finish = index + 5
            else:
                item_2 = self.list_form[index + 1]
                finish = index + 2
            if self.list_form[0] == '(' and self.list_form[-1] == ')':
                self.list_form[start - 1: finish + 1] = [My_str(
                  globals()[oper](Dec(item_1), Dec(item_2)))]
            else:
                self.list_form[start: finish] = [My_str(
                  globals()[oper](Dec(item_1), Dec(item_2)))]
        except ZeroDivisionError:
            raise OperatorError('ERROR: division by zero \'{}\''.format(
                ' '.join(self.list_form[start: finish])))

    def order_calculate(self):
        for order in range(3):
            for oper in self.simpl_operations[order]:
                if order == FUNKS and oper in self.list_form:
                    self.func_calc(oper)
                    continue
                elif order == MUL_DIV and oper in self.list_form:
                    while oper in self.list_form:
                        self.mul_div_add_sub(oper)
                elif order == ADD_SUB and oper in self.list_form:
                    self.mul_div_add_sub(oper)

# ------------------------------------------------------------------------------

    def chenge_constants(self):
        for index, item in enumerate(self.list_form):
            if item in self.constants:
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

    def start(self):
        try:
            self.chenge_constants()
            self.calculate()
            self.logical_computation()
            if len(self.list_form) > 1:
                raise Exception()
            self.answer = self.list_form[0]
        except OperatorError as err:
            self.answer = My_str(err)
        except Exception:
            self.answer = 'ERROR: incorrect expression \'{}\''.format(
                ' '.join(self.list_form))
        finally:
            return self.answer

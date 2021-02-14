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

functions_with_two_arguments = {'atan2', 'comb', 'copysign', 'dist', 'fmod',
                                'ldexp', 'log', 'nextafter', 'remainder'}

functions_with_integers_arguments = {'gcd', 'hypot', 'lcm', 'prod'}


class OperatorError(ArithmeticError):
    pass


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
                self.form[index] = self.form.pop(
                    index) + self.form[index]

    def pars(self):
        self.form = re.findall(self.pattern, self.string)
        self.hendling()
        return self.form


class Calculator:
    def __init__(self, form):
        self.list_form = Parser(form).pars()
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

    def func_calc(self, oper):
        for index, item in enumerate(self.list_form):
            if item == oper:
                index_1 = index
        try:
            start = index_1 + 1
            finish = index_1 + 2
            for index_2, item in enumerate(self.list_form):
                if index_2 > index_1 and item == ',' and self.is_number(
                        self.list_form[index_2 + 1]):
                    finish += 2
            print(self.list_form)
            print(self.list_form[start: finish])
            arguments_of_func = [
                Dec(a) for a in self.list_form[start: finish] if a != ','
            ]
            print(arguments_of_func)
            self.list_form[index_1: finish] = [
                str(globals()[oper](*arguments_of_func))
            ]
        except TypeError:
            arguments_of_func[-1] = int(arguments_of_func[-1])
            print(arguments_of_func)
            self.list_form[index_1: finish] = [
                str(globals()[oper](*arguments_of_func))
            ]

    def simpl_calculate(self):
        for order in range(3):
            for oper in self.simpl_operations[order]:

                if order == FUNKS and oper in self.list_form:
                    index = self.list_form.index(oper)
                    if oper in {'log', 'sqrt'} and \
                            float(self.list_form[index + 1]) < 0:
                        raise OperatorError('ERROR: a negative number under the\
 \'{}\' function: {}'.format(oper, self.list_form[index + 1]))
                    # elif oper in {'round', 'log', 'perm'}:
                    self.func_calc(oper)
                    continue
                    # self.list_form[index: index + 2] = [str(
                    #       globals()[oper](Dec(self.list_form[index + 1])))]

                elif order == MUL_DIV and oper in self.list_form:
                    while oper in self.list_form:
                        index = self.list_form.index(oper)
                        if oper in {'/', '//'} and \
                                float(self.list_form[index + 1]) == 0:
                            raise OperatorError('ERROR: division by zero\
 \'{}\''.format(' '.join(self.list_form[index - 1: index + 2])))
                        self.list_form[index - 1: index + 2] = [str(
                          globals()[oper](Dec(self.list_form[index - 1]),
                                          Dec(self.list_form[index + 1])))]

                elif order == ADD_SUB and oper in self.list_form:
                    index = self.list_form.index(oper)
                    self.list_form[index - 1: index + 2] = [str(
                          globals()[oper](Dec(self.list_form[index - 1]),
                                          Dec(self.list_form[index + 1])))]

    def chenge_constants(self):
        for index, item in enumerate(self.list_form):
            if self.list_form[index] in self.constants:
                self.list_form[index] = globals()[self.list_form[index]]

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
                self.simpl_calculate()
            else:
                start, stop = self.search_brackets()
                list_form, self.list_form = (self.list_form,
                                             self.list_form
                                             [start + 1: stop - 1])
                self.calculate()
                list_form[start: stop] = self.list_form
                self.list_form = list_form
                self.calculate()

    def logical_computation(self):
        for oper in self.simpl_operations[BOOL]:
            index = self.list_form.index(oper)
            if self.list_form[index - 1] in {'True', 'False'} and \
                    self.list_form[index + 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [str(
                      globals()[oper](bool(self.list_form[index - 1]),
                                      bool(self.list_form[index + 1])))]
            elif self.list_form[index - 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [str(
                      globals()[oper](bool(self.list_form[index - 1]),
                                      Dec(self.list_form[index + 1])))]
            elif self.list_form[index + 1] in {'True', 'False'}:
                self.list_form[index - 1: index + 2] = [str(
                      globals()[oper](Dec(self.list_form[index - 1]),
                                      bool(self.list_form[index + 1])))]
            else:
                self.list_form[index - 1: index + 2] = [str(
                      globals()[oper](Dec(self.list_form[index - 1]),
                                      Dec(self.list_form[index + 1])))]

    def answer(self):
        try:
            self.chenge_constants()
            self.calculate()
            self.logical_computation()
            if len(self.list_form) > 1:
                raise Exception()
            self.answer = self.list_form[0]
        except OperatorError as err:
            self.answer = str(err)
        except Exception:
            # print(self.list_form)
            self.answer = 'ERROR: incorrect expression \'{}\''.format(
                ' '.join(self.list_form))
        finally:
            return self.answer

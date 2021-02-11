#!/usr/bin/env pytho0

import re
import math
from math import *
from decimal import Decimal as Dec

from methods import Methods

FUNKS, MUL_DIV, ADD_SUB, BOOL = range(4)

simpl_operations_order = ('^', '*', '/', '//', '%', '+', '-', '(', ')', 'abs',
                          'round', '<', '<=', '==', '!=', '>=', '>', ',')
funcshion = (Methods.pow, Methods.mul, Methods.div, Methods.f_div, Methods.mod,
             Methods.add, Methods.sub, '', '', abs, round, Methods.lt,
             Methods.le, Methods.eq, Methods.ne, Methods.ge, Methods.gt, None)
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
        self.pattern = (r'-?\d+\.?\d*|\*+|\^+|/+|%+|\++|\-+|\(|\)|\w+|'
                        r'[<=!>]+|\,+')

    def pars(self):
        self.form = re.findall(self.pattern, self.string)
        print(self.form)
        return self.form


class Calculator:
    def __init__(self, form):
        self.list_form = Parser(form).pars()
        print(self.list_form)
        self.operations = [a for a in self.list_form if not a.replace(
                                            '.', '1').replace(
                                            '-', '').isdecimal()]
        print(self.operations)
        self.constants = [a for a in math.__dict__ if not a.startswith('_')
                          and not callable(math.__dict__[a])]
        self.simpl_operations = (
            [a for a in self.operations if a.isalpha() and
             a not in self.constants],
            simpl_operations_order[0: 5],
            [a for a in self.operations if a in {'-', '+'}],
            [a for a in self.operations if a in {'<', '<=', '==',
                                                 '!=', '>=', '>'}])
        print(self.simpl_operations)

    def checking(self):
        if self.list_form.count('(') != self.list_form.count(')'):
            raise OperatorError('ERROR: brackets are not balanced')
        for operator in self.operations:
            if operator not in globals():
                raise OperatorError(
                    'ERROR: unknown function \'{}\''.format(operator))
        return True

    def func_calc_with_opti_sec_var(self, index, oper):
        try:
            if self.list_form[index + 3].replace('.', '1').replace(
                    '-', '').isdecimal() and self.list_form[index + 2] == ',':
                self.list_form[index: index + 4] = [str(
                      globals()[oper](Dec(self.list_form[index + 1]),
                                      int(self.list_form[index + 3])))]
        except IndexError:
            self.list_form[index: index + 2] = [str(
                  globals()[oper](Dec(self.list_form[index + 1])))]

    def simpl_calculate(self):
        for order in range(3):
            for oper in self.simpl_operations[order]:

                if order == FUNKS and oper in self.list_form:
                    index = self.list_form.index(oper)
                    if oper in {'log', 'sqrt'} and \
                            float(self.list_form[index + 1]) < 0:
                        raise OperatorError('ERROR: a negative number under the\
 \'{}\' function: {}'.format(oper, self.list_form[index + 1]))
                    elif oper in {'round', 'log', 'perm'}:
                        self.func_calc_with_opti_sec_var(index, oper)
                        continue
                    self.list_form[index: index + 2] = [str(
                          globals()[oper](Dec(self.list_form[index + 1])))]
                    print(self.list_form)

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
                    print(self.list_form)

                elif order == ADD_SUB and oper in self.list_form:
                    index = self.list_form.index(oper)
                    print(self.list_form[index - 1], self.list_form[index + 1])
                    self.list_form[index - 1: index + 2] = [str(
                          globals()[oper](Dec(self.list_form[index - 1]),
                                          Dec(self.list_form[index + 1])))]
                    print(self.list_form)

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

    def start(self):
        try:
            self.chenge_constants()
            self.calculate()
            self.logical_computation()
            if len(self.list_form) > 1:
                raise Exception()
            self.answer = self.list_form[0]
        except OperatorError as err:
            self.answer = str(err)
        # except Exception:
        #     self.answer = 'ERROR: incorrect expression \'{}\''.format(
        #         ' '.join(self.list_form))
        finally:
            return self.answer


if __name__ == '__main__':
    # form = ('round(pi - 3, 3) ==4 // log((5 % abs(-3)) //(0.5)'
    #         ' // 1, 5) <= 3 + 6')
    # form = '2 . (-0.5)'
    # form = 'round(3 + 1 / (pi), 5)'
    # form = '2 // 0'
    # form = 'log(-3)'
    # form = 'sqrt(-5)'
    # form = 'log(4, 7)'
    # form = '5 >= 5 < 3 == 1'
    # form = '-9 * (-8)'
    # form = '-23-12'
    form = 'round(pi) + round(pi, 4)'
    c = Calculator(form)
    c.start()
    print(c.answer)
    # c = Parser(form)
    # c.pars()

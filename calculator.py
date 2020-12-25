#!/usr/bin/env python

import re
import math
from methods import Methods
from math import *
from decimal import Decimal as Dec


simpl_operations_order = ('^', '*', '/', '//', '%', '+', '-', '(', ')')
funcshion = (Methods.pow, Methods.mul, Methods.div, Methods.f_div,
             Methods.mod, Methods.add, Methods.sub, '', '')

for oper, func in (zip(simpl_operations_order, funcshion)):
    globals()[oper] = func


class OperatorError(ArithmeticError):
    pass


form = '2 + (-3) * sin(4 - (5 - 2)) + pi ^ (2 - 3) * tan (5 * ((-2 / 1) - (-3)))'


class Calculator:

    pattern = r'-?\d+[.,]*\d*|\*+|\^+|/+|%+|\++|\-+|\(|\)|\w+'

    def __init__(self, form):
        self.list_form = re.findall(Calculator.pattern,
                                    form.replace(',', '.'))
        print(self.list_form)
        self.operations = [a for a in self.list_form if not a.replace(
                                            '.', '1').replace(
                                            '-', '').isdecimal()]
        self.constants = [a for a in math.__dict__ if not a.startswith('_') and
                          not callable(math.__dict__[a])]
        self.simpl_operations = (
            [a for a in self.operations if a.isalpha() and
             a not in self.constants],
            simpl_operations_order[0: 4],
            [a for a in self.operations if a in {'-', '+'}])
        print(self.simpl_operations)

    def checking(self, show=True):
        try:
            for operator in self.operations:
                for oper in operator:
                    if operator not in globals():
                        raise OperatorError(
                            'Недопустимый оператор "{}"'.format(operator))
        except OperatorError as err:
            if show:
                print(err)
            return False
        else:
            return True

    def simpl_calculate(self):
        for n in range(3):
            for oper in self.simpl_operations[n]:
                if n == 0 and oper in self.list_form:
                    index = self.list_form.index(oper)
                    self.list_form[index: index + 2] = [str(
                          globals()[oper](Dec(self.list_form[index + 1])))]
                    print(self.list_form)
                elif n == 1 and oper in self.list_form:
                    while oper in self.list_form:
                        index = self.list_form.index(oper)
                        self.list_form[index - 1: index + 2] = [str(
                              globals()[oper](Dec(self.list_form[index - 1]),
                                              Dec(self.list_form[index + 1])))]
                        print(self.list_form)
                elif n == 2 and oper in self.list_form:
                    print(oper)
                    index = self.list_form.index(oper)
                    self.list_form[index - 1: index + 2] = [str(
                          globals()[oper](Dec(self.list_form[index - 1]),
                                          Dec(self.list_form[index + 1])))]
                    print(self.list_form)

    def chenge_constants(self):
        for item in range(len(self.list_form)):
            if self.list_form[item] in self.constants:
                self.list_form[item] = globals()[self.list_form[item]]

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
            self.chenge_constants()
            if '(' not in self.list_form:
                self.simpl_calculate()
            else:
                start, stop = self.search_brackets()
                list_form, self.list_form = (self.list_form,
                                             self.list_form
                                             [start + 1: stop - 1])
                print(self.list_form)
                self.calculate()
                list_form[start: stop] = self.list_form
                self.list_form = list_form
                self.calculate()


if __name__ == '__main__':
    c = Calculator(form)
    c.calculate()
    if c.checking(False):
        print(c.list_form[0])

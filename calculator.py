#!/usr/bin/env python

import re
import math
import sys
from methods import Methods
from math import *
from decimal import Decimal as Dec


simpl_operations_order = ('^', '*', '/', '//', '%',
                          '+', '-', '(', ')', 'abs', 'round')
funcshion = (Methods.pow, Methods.mul, Methods.div, Methods.f_div,
             Methods.mod, Methods.add, Methods.sub, '', '', abs, round)

for oper, func in (zip(simpl_operations_order, funcshion)):
    globals()[oper] = func


class OperatorError(ArithmeticError):
    pass


class Calculator:

    pattern = r'-?\d+[.,]*\d*|\*+|\^+|/+|%+|\++|\-+|\(|\)|\w+'

    def __init__(self, form):
        self.form = form
        self.list_form = re.findall(Calculator.pattern,
                                    form.replace(',', '.'))
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

    def checking(self, show=False):
        try:

            if self.list_form.count('(') != self.list_form.count(')'):
                raise OperatorError(
                    'ERROR: brackets are not balanced')

            for operator in self.operations:
                for oper in operator:
                    if operator not in globals():
                        raise OperatorError(
                            'ERROR: unknown function \'{}\''.format(operator))
        except OperatorError as err:
            if show:
                print(err)
            return False
        except OperatorError as err:
            if show:
                print(err)
            return False
        else:
            return True

    def simpl_calculate(self):
        try:
            for n in range(3):
                for oper in self.simpl_operations[n]:
                    if n == 0 and oper in self.list_form:
                        index = self.list_form.index(oper)
                        if oper == 'round' and len(self.list_form) > 1:
                            self.list_form[index: index + 3] = [str(
                                  globals()[oper](
                                      Dec(self.list_form[index + 1]),
                                      int(self.list_form[index + 2])))]
                            continue
                        self.list_form[index: index + 2] = [str(
                              globals()[oper](Dec(self.list_form[index + 1])))]
                    elif n == 1 and oper in self.list_form:
                        while oper in self.list_form:
                            index = self.list_form.index(oper)
                            if oper in {'/', '//'} and \
                                    self.list_form[index + 1] == '0':
                                raise OperatorError('ERROR: division by zero')
                            self.list_form[index - 1: index + 2] = [str(
                              globals()[oper](Dec(self.list_form[index - 1]),
                                              Dec(self.list_form[index + 1])))]
                    elif n == 2 and oper in self.list_form:
                        index = self.list_form.index(oper)
                        self.list_form[index - 1: index + 2] = [str(
                              globals()[oper](Dec(self.list_form[index - 1]),
                                              Dec(self.list_form[index + 1])))]
        except OperatorError as err:
            print(err)
            sys.exit(0)
        except Exception:
            print('ERROR: incorrect expression \'{}\''.format(self.form))
            sys.exit(0)

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
                self.calculate()
                list_form[start: stop] = self.list_form
                self.list_form = list_form
                self.calculate()


if __name__ == '__main__':
    form = 'abs(round(-3 * round(pi ^ (2 - 3), 3), 3))'
    c = Calculator(form)
    c.calculate()
    if c.checking(True):
        print(c.list_form[0])

#!/usr/bin/env python

from calculator import *

form = 'round(-3 * round(pi ^ (2 / 0), 3), 3)'

c = Calculator(form)
b = c.calculate()
print(c.list_form[0])

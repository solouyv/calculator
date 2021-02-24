#!/usr/bin/env python3

import argparse
import calculator

usage = 'pycalc [-h] EXPRESSION [-m MODULE [MODULE ...]]'
description = 'Pure-python command-line calculator.'
parser = argparse.ArgumentParser(usage=usage, description=description)
parser.add_argument('expression', metavar='EXPRESSION',
                    help='expression strig to evaluate', type=str)
parser.add_argument('-m', '--use-modules',
                    type=str, nargs='+', metavar='MODULE',
                    help=('additional modules to use'), dest='module')
args = parser.parse_args()

if args.module:
    calculator.Impoprt_module(args.module).import_module()

expression = calculator.Calculator(args.expression).start()
print(expression)

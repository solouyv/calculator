#!/usr/bin/env python

import unittest
import calculator
import cProfile
import argparse
from unittest.mock import Mock
from contextlib import contextmanager


A = '-23-12'
B = '+23.12/3-12+8.56*2'
C = '-9*(-8)'
D = '2. (3, -0.5)'
E = '2//0'
F = '5>=5<3==1'
G = 'round(3+1/(pi + 1),5)'
H = 'round(pi)+round(pi,4)'
J = 'round(hypot(pi,12.456,15.987,20)+hypot(4),3)'
K = 'round(pi-3,3)==4//log((5%abs(-3))//(0.5)//1,5)<=3+6'
L = 'round(round(pi)^(log(hypot(12.32,-65.12)//12,10))+round(pi,4),6)'
M = 'e + (-inf) + nan + (-pi) + tau'
N = '(3+2(-1)'
P = 'foo(-123)'


class Test_Parser_pars(unittest.TestCase):
    def setUp(self):
        self.A = calculator.Parser(A)
        self.B = calculator.Parser(B)
        self.C = calculator.Parser(C)
        self.D = calculator.Parser(D)

    def test_Parser_pars(self):
        self.A.pars()
        self.assertEqual(self.A.form, ['-', '23', '-', '12'])
        self.B.pars()
        self.assertEqual(
            self.B.form,
            ['+', '23.12', '/', '3', '-', '12', '+', '8.56', '*', '2']
        )
        self.C.pars()
        self.assertEqual(self.C.form, ['-', '9', '*', '(', '-', '8', ')'])
        self.D.pars()
        self.assertEqual(self.D.form, ['2', '(', '3', ',', '-', '0.5', ')'])


class Test_Parser_Hendling(unittest.TestCase):
    form = Mock()
    form.side_effect = [
        ['-', '23', '-', '12'],
        ['+', '23.12', '/', '3', '-', '12', '+', '8.56', '*', '2'],
        ['-', '9', '*', '(', '-', '8', ')'],
        ['2', '(', '3', ',', '-', '0.5', ')']
    ]

    def setUp(self):
        self.Hendling = calculator.Parser(A)
        self.Hendling.form = Test_Parser_Hendling.form()

    def test_Parser_hendling_1(self):
        self.Hendling.hendling()
        self.assertEqual(self.Hendling.form, ['-23', '-', '12'])

    def test_Parser_hendling_2(self):
        self.Hendling.hendling()
        self.assertEqual(
            self.Hendling.form,
            ['23.12', '/', '3', '-', '12', '+', '8.56', '*', '2']
        )

    def test_Parser_hendling_3(self):
        self.Hendling.hendling()
        self.assertEqual(self.Hendling.form, ['-9', '*', '(', '-8', ')'])

    def test_Parser_hendling_4(self):
        self.Hendling.hendling()
        self.assertEqual(
            self.Hendling.form, ['2', '(', '3', ',', '-0.5', ')'])


class Test_Calculator_init(unittest.TestCase):
    def setUp(self):
        self.K = calculator.Calculator(K)

    def test_calculator__init__(self):
        self.assertEqual(
            [self.K.operations, self.K.constants, self.K.simpl_operations],
            [
                [
                    'round', '(', 'pi', '-', ',', ')', '==', '//', 'log', '(',
                    '(', '%', 'abs', '(', ')', ')', '//', '(', ')', '//', ',',
                    ')', '<=', '+'
                ],
                ['pi', 'e', 'tau', 'inf', 'nan'],
                (
                    ['round', 'log', 'abs'],
                    ('^', '*', '/', '//', '%'),
                    ['-', '+'],
                    ['==', '<=']
                )
            ]
        )


class Test_Calculator_chenge_constants(unittest.TestCase):
    def setUp(self):
        self.M = calculator.Calculator(M)

    def test_chenge_constants(self):
        self.M.chenge_constants()
        self.assertEqual(
            self.M.list_form, [
                '2.718281828459045', '+', '(', '-inf', ')', '+', 'nan', '+',
                '(', '-3.141592653589793', ')', '+', '6.283185307179586'
            ]
        )


class Test_Calculator_is_number(unittest.TestCase):
    def setUp(self):
        self.C = calculator.Calculator(C)

    def test_is_number(self):
        self.assertTrue(self.C.is_number('-123.123'))
        self.assertFalse(self.C.is_number('-1r3.123'))


class Test_Calculator_logical_computation_1(unittest.TestCase):
    def setUp(self):
        self.F = calculator.Calculator(F)

    def test_logical_computation(self):
        self.F.logical_computation()
        self.assertEqual(self.F.list_form, ['True'])


class Test_Calculator_logical_computation_2(unittest.TestCase):
    def setUp(self):
        self.F = calculator.Calculator('False==True')

    def test_logical_computation(self):
        self.F.logical_computation()
        self.assertEqual(self.F.list_form, ['False'])


class Test_Calculator_logical_computation_3(unittest.TestCase):
    def setUp(self):
        self.F = calculator.Calculator('5==False')

    def test_logical_computation(self):
        self.F.logical_computation()
        self.assertEqual(self.F.list_form, ['False'])


class Test_Calculator_search_brackets(unittest.TestCase):
    def setUp(self):
        self.C = calculator.Calculator(C)

    def test_search_brackets(self):
        start, finish = self.C.search_brackets()
        self.assertEqual([start, finish], [2, 5])


class Test_Calculator_errors(unittest.TestCase):
    def setUp(self):
        self.D = calculator.Calculator(D)
        self.E = calculator.Calculator(E)
        self.G = calculator.Calculator(F)
        self.N = calculator.Calculator(N)
        self.P = calculator.Calculator(P)

    def test_errors(self):
        with self.assertRaises(calculator.OperatorError) as context:
            self.N.checking()
        self.assertEqual(
            'ERROR: brackets are not balanced', str(context.exception)
        )
        with self.assertRaises(calculator.OperatorError) as context:
            self.P.checking()
        self.assertEqual(
            'ERROR: unknown function \'foo\'', str(context.exception)
        )
        with self.assertRaises(calculator.OperatorError) as context:
            self.E.mul_div_add_sub('//')
        self.assertEqual(
            'ERROR: division by zero \'2 // 0\'', str(context.exception)
        )
        with self.assertRaises(calculator.OperatorError) as context:
            self.G.list_form = ['log', '-3']
            self.G.func_calc('log')
        self.assertEqual(
            'ERROR: a negative number under the \'log\' function: -3',
            str(context.exception)
        )
        self.assertEqual(
            self.D.start(), 'ERROR: incorrect expression \'2 3 , -0.5\''
        )


class Test_Calculator_mul_div_add_sub(unittest.TestCase):
    def setUp(self):
        self.B = calculator.Calculator(B)

    def test_mul_div_add_sub(self):
        self.B.mul_div_add_sub('/')
        self.assertEqual(
            self.B.list_form,
            ['7.706666666666666666666666667', '-', '12', '+', '8.56', '*', '2']
        )
        self.B.mul_div_add_sub('*')
        self.assertEqual(
            self.B.list_form,
            ['7.706666666666666666666666667', '-', '12', '+', '17.12']
        )
        self.B.mul_div_add_sub('-')
        self.assertEqual(
            self.B.list_form,
            ['-4.293333333333333333333333333', '+', '17.12']
        )
        self.B.mul_div_add_sub('+')
        self.assertEqual(self.B.list_form, ['12.82666666666666666666666667'])


class Test_Calculator_func_calc(unittest.TestCase):
    def setUp(self):
        self.J = calculator.Calculator(J)
        self.J.list_form = [a for a in self.J.list_form if a not in {'(', ')'}]
        self.J.chenge_constants()

    def test_func_calc(self):
        self.J.list_form[1].attr = 7
        self.J.func_calc('hypot')
        self.assertEqual(
            self.J.list_form,
            ['round', '28.646216319107296', '+', 'hypot', '4', ',', '3']
        )
        self.J.list_form[3].attr = 1
        self.J.func_calc('hypot')
        self.assertEqual(
            self.J.list_form,
            ['round', '28.646216319107296', '+', '4.0', ',', '3']
        )
        self.J.mul_div_add_sub('+')
        self.assertEqual(
            self.J.list_form, ['round', '32.646216319107296', ',', '3']
        )
        self.J.list_form[0].attr = 3
        self.J.func_calc('round')
        self.assertEqual(self.J.list_form, ['32.646'])


class Test_Import_module_init(unittest.TestCase):
    def setUp(self):
        self.mod = calculator.Import_module(['time'])

    def test_type_of_attribute(self):
        self.assertIsInstance(self.mod.modules, list)


class Test_Import_module_add_standard_module(unittest.TestCase):
    def setUp(self):
        self.mod = calculator
        self.Import = self.mod.Import_module(['time'])

    def test_import_standard_module(self):
        self.Import.import_module()
        self.assertIn('time', self.mod.__dict__)


class Test_Import_module_add_standard_modules(unittest.TestCase):
    def setUp(self):
        self.mod = calculator
        self.Import = self.mod.Import_module(['time', 'decimal'])

    def test_import_standard_module_time(self):
        self.Import.import_module()
        self.assertIn('time', self.mod.__dict__)

    def test_import_standard_module_decimal(self):
        self.Import.import_module()
        self.assertIn('Decimal', self.mod.__dict__)


class Test_Import_module_add_own_module(unittest.TestCase):
    def setUp(self):

        @contextmanager
        def mock_file(filepath, content=''):
            with open(filepath, 'w') as f:
                f.write(content)
            yield filepath
            try:
                import os
                os.remove(filepath)
            except Exception:
                pass

        self.mock_file = mock_file
        self.content = (
            '#!/usr/bin/env python\n\n'
            'def sin(item):\n'
            '    return 42\n'
        )
        self.mod = calculator
        self.Import = self.mod.Import_module(['./my_mod.py'])

    def test_import_standard_module(self):
        with self.mock_file('./my_mod.py', self.content):
            self.Import.import_module()
            self.assertEqual(self.mod.__dict__['sin'](12), 42)


class Test_Import_module_add_own_modules(unittest.TestCase):
    def setUp(self):

        @contextmanager
        def mock_file(filepath, content=''):
            with open(filepath, 'w') as f:
                f.write(content)
            yield filepath
            try:
                import os
                os.remove(filepath)
            except Exception:
                pass

        self.mock_file = mock_file
        self.content_sin = (
            '#!/usr/bin/env python\n\n'
            'def sin(item):\n'
            '    return 42\n'
        )
        self.content_cos = (
            '#!/usr/bin/env python\n\n'
            'def cos(item):\n'
            '    return 62\n'
        )
        self.mod = calculator
        self.Import = self.mod.Import_module(
            ['./my_mod_sin.py ./my_mod_cos.py']
        )

    def test_import_standard_modules(self):
        with self.mock_file('./my_mod_sin.py', self.content_sin), \
                self.mock_file('./my_mod_cos.py', self.content_cos):
            self.Import.import_module()
            self.assertEqual(self.mod.__dict__['sin'](12), 42)
            self.assertEqual(self.mod.__dict__['cos'](12), 62)


if __name__ == '__main__':
    description = 'Test of programm.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', action='store_true',
                        help=('start tests whith cPofile'))
    args = parser.parse_args()

    if args.c:
        def profile(func):
            """Decorator for run function profile"""
            def wrapper(*args, **kwargs):
                profiler = cProfile.Profile()
                result = profiler.runcall(func, *args, **kwargs)
                profiler.print_stats('tottime')
                return result
            return wrapper

        @profile
        def test_calculating_1():
            test = calculator.Calculator(K)
            test.start()

        @profile
        def test_calculating_2():
            test = calculator.Calculator(L)
            test.start()

        test_calculating_1()
        test_calculating_2()

    unittest.main()

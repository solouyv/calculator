#!/usr/bin/env python

import unittest
import calculator
import cProfile


def profile(func):
    """Decorator for run function profile"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.print_stats('tottime')
        return result
    return wrapper


A = '-23-12'
B = '+23.12/3-12+8.56*2'
C = '-9*(-8)'
D = '2.(-0.5)'
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


class Test_Parser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.A = calculator.Parser(A)
        cls.B = calculator.Parser(B)
        cls.C = calculator.Parser(C)
        cls.L = calculator.Parser(L)

    def test_1_pars(self):
        self.A.pars()
        self.assertEqual(self.A.form, ['-', '23', '-', '12'])
        self.B.pars()
        self.assertEqual(
            self.B.form,
            ['+', '23.12', '/', '3', '-', '12', '+', '8.56', '*', '2']
        )
        self.C.pars()
        self.assertEqual(self.C.form, ['-', '9', '*', '(', '-', '8', ')'])
        self.L.pars()
        self.assertEqual(
            self.L.form, [
                'round', '(', 'round', '(', 'pi', ')', '^', '(', 'log', '(',
                'hypot', '(', '12.32', ',', '-', '65.12', ')', '//', '12', ',',
                '10', ')', ')', '+', 'round', '(', 'pi', ',', '4', ')', ',',
                '6', ')'
            ]
        )

    def test_2_hendling(self):
        self.A.hendling()
        self.assertEqual(self.A.form, ['-23', '-', '12'])
        self.B.hendling()
        self.assertEqual(
            self.B.form,
            ['23.12', '/', '3', '-', '12', '+', '8.56', '*', '2']
        )
        self.C.hendling()
        self.assertEqual(self.C.form, ['-9', '*', '(', '-8', ')'])
        self.L.hendling()
        self.assertEqual(
            self.L.form, [
                'round', '(', 'round', '(', 'pi', ')', '^', '(', 'log', '(',
                'hypot', '(', '12.32', ',', '-65.12', ')', '//', '12', ',',
                '10', ')', ')', '+', 'round', '(', 'pi', ',', '4', ')', ',',
                '6', ')'
            ]
        )


class Test_Calculator(unittest.TestCase):
    def setUp(self):
        self.B = calculator.Calculator(B)
        self.C = calculator.Calculator(C)
        self.D = calculator.Calculator(D)
        self.E = calculator.Calculator(E)
        self.F = calculator.Calculator(F)
        self.J = calculator.Calculator(J)
        self.G = calculator.Calculator(F)
        self.K = calculator.Calculator(K)
        self.L = calculator.Calculator(L)
        self.M = calculator.Calculator(M)
        self.N = calculator.Calculator(N)
        self.P = calculator.Calculator(P)

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

    def test_chenge_constants(self):
        self.M.chenge_constants()
        self.assertEqual(
            self.M.list_form, [
                '2.718281828459045', '+', '(', '-inf', ')', '+', 'nan', '+',
                '(', '-3.141592653589793', ')', '+', '6.283185307179586'
            ]
        )

    def test_is_number(self):
        self.assertTrue(self.C.is_number('-123.123'))
        self.assertFalse(self.C.is_number('-1r3.123'))

    def test_logical_computation(self):
        self.F.logical_computation()
        self.assertEqual(self.F.list_form, ['True'])

    def test_search_brackets(self):
        start, finish = self.C.search_brackets()
        self.assertEqual([start, finish], [2, 5])

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
            self.D.start(), 'ERROR: incorrect expression \'2 -0.5\''
        )

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

    def test_func_calc(self):
        self.J.list_form = [a for a in self.J.list_form if a not in {'(', ')'}]
        self.J.chenge_constants()
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

    @profile
    def test_calculating_1(self):
        self.assertEqual(self.K.start(), 'True')

    @profile
    def test_calculating_2(self):
        self.assertEqual(self.L.start(), '5.296829')


if __name__ == '__main__':
    unittest.main()

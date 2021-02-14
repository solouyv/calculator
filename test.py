#!/usr/bin/env python

import unittest
import calculator


class Test_Calculator(unittest.TestCase):
    def setUp(self):
        self.A = calculator.Calculator('-23-12')
        self.B = calculator.Calculator('+23.12-12+8.56')
        self.C = calculator.Calculator('-9*(-8)')
        self.D = calculator.Calculator('2.(-0.5)')
        self.E = calculator.Calculator('2//0')
        self.F = calculator.Calculator('5>=5<3==1')
        self.G = calculator.Calculator('log(-3)')
        self.H = calculator.Calculator('sqrt(-5)')
        self.J = calculator.Calculator('log(4,7)')
        self.K = calculator.Calculator('round(3+1/(pi + 1),5)')
        self.L = calculator.Calculator('round(pi)+round(pi,4)')
        self.M = calculator.Calculator(
            'round(hypot(pi,12.456,15.987,20)+hypot(4),3)'
        )
        # self.M = calculator.Calculator(
        #     'round(pi-3,3)==4//log((5%abs(-3))//(0.5)//1,5)<=3+6'
        # )

    def test_pars(self):
        self.assertEqual(self.A.list_form, ['-23', '-', '12'])
        self.assertEqual(self.B.list_form, ['23.12', '-', '12', '+', '8.56'])
        self.assertEqual(self.C.list_form, ['-9', '*', '(', '-8', ')'])
        self.assertEqual(self.D.list_form, ['2', '(', '-0.5', ')'])
        self.assertEqual(self.E.list_form, ['2', '//', '0'])
        self.assertEqual(
            self.F.list_form, ['5', '>=', '5', '<', '3', '==', '1'])
        self.assertEqual(self.G.list_form, ['log', '(', '-3', ')'])
        self.assertEqual(self.H.list_form, ['sqrt', '(', '-5', ')'])
        self.assertEqual(self.J.list_form, ['log', '(', '4', ',', '7', ')'])
        self.assertEqual(
            self.K.list_form,
            ['round', '(', '3', '+', '1', '/', '(', 'pi', '+', '1', ')', ',',
             '5', ')']
        )
        self.assertEqual(
            self.L.list_form,
            ['round', '(', 'pi', ')', '+', 'round', '(', 'pi', ',', '4', ')'])
        self.assertEqual(self.M.list_form, [
            'round', '(', 'hypot', '(', 'pi', ',', '12.456', ',', '15.987',
            ',', '20', ')', '+', 'hypot', '(', '4', ')', ',', '3', ')'
        ])
        # self.assertEqual(
        #     self.M.list_form,
        #     ['round', '(', 'pi', '-', '3', ',', '3', ')', '==', '4', '//',
        #      'log', '(', '(', '5', '%', 'abs', '(', '-3', ')', ')', '//', '(',
        #      '0.5', ')', '//', '1', ',', '5', ')', '<=', '3', '+', '6']
        # )

    def test_calculating(self):
        self.assertEqual(self.A.answer(), '-35')
        self.assertEqual(self.B.answer(), '19.68')
        self.assertEqual(self.C.answer(), '72')
        self.assertEqual(
            self.D.answer(), 'ERROR: incorrect expression \'2 ( -0.5 )\'')
        self.assertEqual(
            self.E.answer(), 'ERROR: division by zero \'2 // 0\'')
        self.assertEqual(self.G.answer(
        ), 'ERROR: a negative number under the \'log\' function: -3')
        self.assertEqual(self.H.answer(
        ), 'ERROR: a negative number under the \'sqrt\' function: -5')
        self.assertEqual(self.J.answer(), '0.7124143742160444')
        self.assertEqual(self.L.answer(), '6.1416')
        self.assertEqual(self.K.answer(), '3.31831')
        self.assertEqual(self.M.answer(), '31.90824')
        # self.assertEqual(self.M.answer(), 'True')

    def test_bool(self):
        self.F.logical_computation()
        self.assertEqual(self.F.list_form, ['True'])

    # def test_search_brackets(self):
    #     self.


if __name__ == '__main__':
    unittest.main()

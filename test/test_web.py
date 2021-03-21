#!/usr/bin/env python3

import os
import unittest
import tempfile
import sqlite3
from web import create_app
from web.db import get_db, init_db
from flask import g, session
from unittest.mock import Mock


class Test_web_case(unittest.TestCase):
    class AuthActions(object):
        def __init__(self, client):
            self._client = client

        def login(self, username='test', password='test'):
            return self._client.post(
                '/auth/login',
                data={'username': username, 'password': password}
            )

        def logout(self):
            return self._client.get('/auth/logout')

    def setUp(self):
        with open(
            os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb'
        ) as f:
            _data_sql = f.read().decode('utf8')
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
        })
        with self.app.app_context():
            init_db()
            get_db().executescript(_data_sql)
        self.app_client = self.app.test_client()
        self.auth = Test_web_case.AuthActions(self.app_client)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)


class Test_app_exist(Test_web_case):
    def test_app_exist(self):
        self.assertTrue(self.app)
        rv = self.app_client.get('/')
        self.assertIn(b'Calculator', rv.data)


class Test_get_close_db(Test_web_case):
    def test_get_close_db(self):
        with self.app.app_context():
            db = get_db()
            self.assertIs(db, get_db())

        with self.assertRaises(sqlite3.ProgrammingError) as e:
            db.execute('SELECT 1')
            self.assertIn('closed', str(e.exception))


class Test_Auth_Actions(Test_web_case):
    def test_auth_actions(self):
        self.assertEqual(
            self.app_client.get('/auth/register').status_code,
            200
        )
        rv = self.app_client.post(
            '/auth/register',
            data={'username': 'a', 'password': 'a'}
        )
        self.assertEqual(
            'http://localhost/auth/login', rv.headers['Location']
        )
        with self.app.app_context():
            self.assertIsNotNone(
                get_db().execute(
                    "select * from user where username = 'a'",
                ).fetchone()
            )


class Test_register_validate_input(Test_web_case):
    args = Mock()
    args.side_effect = [
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
    ]

    def validate_input(self, username, password, message):
        rv = self.app_client.post(
            '/auth/register',
            data={'username': username, 'password': password}
        )
        self.assertIn(message, rv.data)

    def test_register_validate_input_1(self):
        self.validate_input(*Test_register_validate_input.args())

    def test_register_validate_input_2(self):
        self.validate_input(*Test_register_validate_input.args())

    def test_register_validate_input_3(self):
        self.validate_input(*Test_register_validate_input.args())


class Test_login(Test_web_case):

    def test_login(self):
        self.assertEqual(self.app_client.get('/auth/login').status_code, 200)
        rv = self.auth.login()
        self.assertEqual(rv.headers['Location'], 'http://localhost/')

        with self.app_client:
            self.app_client.get('/')
            self.assertEqual(session['user_id'], 1)
            self.assertEqual(g.user['username'], 'test')

    args = Mock()
    args.side_effect = [
        ('a', 'test', b'Incorrect username.'),
        ('test', 'a', b'Incorrect password.'),
    ]

    def validate_input(self, username, password, message):
        rv = self.auth.login(username, password)
        self.assertIn(message, rv.data)

    def test_register_validate_input_1(self):
        self.validate_input(*Test_login.args())

    def test_register_validate_input_2(self):
        self.validate_input(*Test_login.args())

    def test_logout(self):
        self.auth.login()
        with self.app_client:
            self.auth.logout()
            self.assertNotIn('user_id', session)


class Test_index(Test_web_case):
    def test_index(self):
        rv = self.app_client.get('/')
        self.assertIn(b'Log In', rv.data)
        self.assertIn(b'Register', rv.data)
        self.assertIn(b'Quit', rv.data)
        self.assertIn(b'About', rv.data)
        self.assertNotIn(b'test', rv.data)

        self.auth.login()
        with self.app_client:
            rv = self.app_client.get('/')
            self.assertIn(b'Log Out', rv.data)
            self.assertIn(b'test', rv.data)
            self.assertIn(b'Quit', rv.data)
            self.assertIn(b'About', rv.data)


class Test_about(Test_web_case):
    def test_about(self):
        rv = self.app_client.get('/about')
        self.assertTrue(rv)


class Test_history(Test_web_case):
    def test_history_login_required(self):
        rv = self.app_client.get('/history')
        self.assertEqual(rv.headers['Location'], 'http://localhost/auth/login')
        rv = self.app_client.post('/history')
        self.assertEqual(rv.headers['Location'], 'http://localhost/auth/login')

        self.auth.login()
        with self.app_client:
            rv = self.app_client.get('/history')
            self.assertIn(b'test expression', rv.data)
            rv = self.app_client.post('/history')
            self.assertNotIn(b'test expression', rv.data)


class Test_calculator(Test_web_case):
    def test_calculator_without_login(self):
        self.app_client.post('/', data={'expression': '9-2-3', 'modules': ''})

        with self.app.app_context():
            db = get_db()
            count = db.execute(
                'SELECT COUNT(id) FROM solving_expression').fetchone()[0]
            self.assertEqual(count, 1)

    def test_calculator_with_login(self):
        self.auth.login()
        rv = self.app_client.post(
            '/',
            data={'expression': '9-2-3', 'modules': ''},
            follow_redirects=True
        )
        self.assertIn(b'4', rv.data, )
        with self.app.app_context():
            db = get_db()
            count = db.execute(
                'SELECT COUNT(id) FROM solving_expression').fetchone()[0]
            self.assertEqual(count, 2)

    def test_calculator_without_expression(self):
        self.auth.login()
        rv = self.app_client.post('/', data={'expression': '', 'modules': ''})
        self.assertIn(b'Expression is required.', rv.data)

    def test_calculator_with_module_error(self):
        self.auth.login()
        rv = self.app_client.post(
            '/', data={'expression': '9-2-3', 'modules': 'foo'}
        )
        self.assertIn(b'No module named', rv.data)


class Test_answer(Test_web_case):

    def test_answer(self):
        rv = self.app_client.post('/answer')
        self.assertEqual(rv.headers['Location'], 'http://localhost/')


if __name__ == '__main__':
    unittest.main()

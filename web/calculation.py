#!/usr/bin/env python3
'''
The module for creating a calculator flask Blueprint
'''
import calculator
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
)

from .db import get_db
from .auth import login_required

bp = Blueprint('calculation', __name__)


def calculate(string):
    '''
    The method for evaluating an expression
    '''
    item = calculator.Calculator(string)
    item.start()
    return item.answer


@bp.route('/', methods=('GET', 'POST'))
def index():
    '''
    The method to return the index html page with a request for the expression,
    to produce the calculation and call the answer page
    '''
    if request.method == 'POST':
        error = None
        expression = request.form['expression']
        modules = request.form['modules'].split(',')
        try:
            if modules[0]:
                calculator.Import_module(modules).import_module()
        except ModuleNotFoundError as err:
            error = err

        global solving

        if not expression:
            error = 'Expression is required.'

        if error is not None:
            flash(error)
        else:
            solving = calculate(expression)
            if g.user and not solving.startswith('ERROR'):
                db = get_db()
                db.execute(
                    'INSERT INTO solving_expression (expression,'
                    ' solving, author_id)'
                    ' VALUES (?, ?, ?)',
                    (expression, solving, g.user['id'])
                )
                db.commit()
            return redirect(url_for('calculation.answer'))

    return render_template('calculation/index.html')


@bp.route('/answer', methods=('POST', 'GET'))
def answer():
    '''
    The method to return the answer html page with a result of calculations
    '''
    if request.method == 'POST':
        return redirect(url_for('calculation.index'))
    return render_template('calculation/answer.html', answer=solving)


@bp.route('/history', methods=('GET', 'POST'))
@login_required
def history():
    '''
    The method for returning a page with the history of calculations
    '''
    db = get_db()
    if request.method == 'POST':
        db.execute(
            'DELETE FROM solving_expression'
            ' WHERE author_id = ?',
            (g.user['id'],)
        )
        db.commit()
        return redirect(url_for('calculation.index'))
    answers = db.execute(
        'SELECT  expression, solving, author_id'
        ' FROM solving_expression p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('calculation/history.html', answers=answers)


@bp.route('/about', methods=('GET', 'POST'))
def about():
    '''
    The method for returning the page with the description of the program
    '''
    return render_template('calculation/about.html')


@bp.route('/quit')
def quit():
    '''
    The method for returning the page with goodbye
    and stopping the flask server
    '''
    shutdown_hook = request.environ.get('werkzeug.server.shutdown')
    if shutdown_hook is not None:
        shutdown_hook()
    return render_template('calculation/quit.html')

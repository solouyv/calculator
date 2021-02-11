#!/usr/bin/env python3

import calculator
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .db import get_db
from .auth import login_required

bp = Blueprint('calculation', __name__)


def calculate(string):
    item = calculator.Calculator(string)
    item.start()
    return item.answer


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        expression = request.form['expression']
        error = None
        global solving
        solving = calculate(expression)

        if not expression:
            error = 'expression is required.'

        if error is not None:
            flash(error)
        else:
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
    if request.method == 'POST':
        return redirect(url_for('calculation.index'))
    return render_template('calculation/answer.html', answer=solving)


@bp.route('/history', methods=('GET', 'POST'))
@login_required
def history():
    db = get_db()
    answers = db.execute(
        'SELECT  expression, solving, author_id'
        ' FROM solving_expression p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('calculation/history.html', answers=answers)


@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    return render_template('calculation/index.html')

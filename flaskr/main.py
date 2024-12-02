from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    db = get_db()
    commands = db.execute(
        'SELECT p.id, title, commandline, created, author_id, username'
        ' FROM command p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('main/index.html', commands=commands)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        commandline = request.form['commandline']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO command (title, commandline, author_id)'
                ' VALUES (?, ?, ?)',
                (title, commandline, g.user['id'])
            )
            db.commit()
            return redirect(url_for('main.index'))

    return render_template('main/index.html')


def get_command(id, check_author=True):
    command = get_db().execute(
        'SELECT p.id, title, commandline, created, author_id, username'
        ' FROM command p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if command is None:
        abort(404, f"Command id {id} doesn't exist.")

    if check_author and command['author_id'] != g.user['id']:
        abort(403)

    return command


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    command = get_command(id)

    if request.method == 'POST':
        title = request.form['title']
        commandline = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE command SET title = ?, commandline = ?'
                ' WHERE id = ?',
                (title, commandline, id)
            )
            db.commit()
            return redirect(url_for('main.index'))

    return render_template('main/index.html', command=command)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_command(id)
    db = get_db()
    db.execute('DELETE FROM command WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('main.index'))

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from Doer.auth import login_required
from Doer.db import get_db

import datetime

bp = Blueprint('goals', __name__)

@bp.route('/')
def index():
    db = get_db()
    goals = db.execute(
        'SELECT goal.id, body, created, author_id, username, complete'
        ' FROM goals goal JOIN user u ON goal.author_id = u.id'
        ' ORDER BY created',
    ).fetchall()

    tasks = db.execute(
        'SELECT task.id, task.body, task.created, goal_id, task.complete'
        ' FROM tasks task JOIN goals goal ON task.goal_id = goal.id'
        ' ORDER BY task.created'
    ).fetchall()
    return render_template('goals/index.html', goals=goals, tasks=tasks)


#Resolution backend
@bp.route('/setResoltuion', methods=('GET', 'POST'))
@login_required
def setResolution():
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'YOU NEED A RESOLUTION!!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET resolution = ?'
                ' WHERE id = ?',
                (body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('goals.index'))

    return render_template('goals/setResolution.html')


#Goal backend
@bp.route('/createGoal', methods=('GET', 'POST'))
@login_required
def createGoal():
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'A goal is required!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO goals (body, author_id)'
                ' VALUES (?, ?)',
                (body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('goals.index'))

    return render_template('goals/createGoals.html')

def get_goal(id, check_author=True):
    goal = get_db().execute(
        'SELECT goal.id, body, created, author_id, username, complete'
        ' FROM goals goal JOIN user u ON goal.author_id = u.id'
        ' WHERE goal.id = ?',
        (id,)
    ).fetchone()

    if goal is None:
        abort(404, "Goal id {0} doesn't exist.".format(id))

    if check_author and goal['author_id'] != g.user['id']:
        abort(403)

    return goal

@bp.route('/<int:id>/updateGoal', methods=('GET', 'POST'))
@login_required
def updateGoal(id):
    goal = get_goal(id)

    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'You need a goal!'

        if error is not None:
            flash(error)
        else:
            if(body != goal['body']):
                db = get_db()
                db.execute(
                    'UPDATE goals SET body = ?, created = ?'
                    ' WHERE id = ?',
                    (body, datetime.datetime.now(),id)
                )
                db.commit()
            return redirect(url_for('goals.index'))

    return render_template('goals/updateGoal.html', goal=goal)

@bp.route('/<int:id>/deleteGoal', methods=('POST',))
@login_required
def deleteGoal(id):
    get_goal(id)
    db = get_db()
    db.execute('DELETE FROM tasks WHERE goal_id = ?',(id,))
    db.execute('DELETE FROM goals WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('goals.index'))




#Task backend
@bp.route('/<int:id>/createTask', methods=('GET', 'POST'))
@login_required
def createTask(id):
    goal = get_goal(id)
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'A task is required!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tasks (body, goal_id, author_id)'
                ' VALUES (?, ?, ?)',
                (body, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('goals.index'))

    return render_template('tasks/createTask.html', goal=goal)

def get_task(id):
    task = get_db().execute(
        'SELECT task.id, task.body, task.created, goal_id, task.complete'
        ' FROM tasks task JOIN goals goal ON task.goal_id = goal.id'
        ' WHERE task.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, "Task id {0} doesn't exist.".format(id))

    return task

@bp.route('/<int:id>/updateTask', methods=('GET', 'POST'))
@login_required
def updateTask(id, check_author=True):
    task = get_task(id)

    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'You need a task!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tasks SET body = ?'
                ' WHERE id = ?',
                (body, id)
            )
            db.commit()
            return redirect(url_for('goals.index'))

    return render_template('tasks/updateTask.html', task=task)

@bp.route('/<int:id>/deleteTask', methods=('POST',))
@login_required
def deleteTask(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('goals.index'))

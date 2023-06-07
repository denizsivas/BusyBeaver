from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_BINDS'] = {'bookmark': 'sqlite:///bookmarks.db', 'reminder': 'sqlite:///reminders.db'}
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<Task %r>' % self.id


class Bookmarks(db.Model):
    __bind_key__ = 'bookmark'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    comment = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Bookmark %r>' % self.id


class Reminders(db.Model):
    __bind_key__ = 'reminder'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_target = db.Column(db.DateTime)

    def __repr__(self):
        return '<Reminder %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content, date_created=datetime.now())
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task.'
    else:
        tasks = Todo.query.filter_by(completed=0).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task.'


@app.route('/delete_bookmark/<int:id>')
def delete_bookmark(id):
    bookmark_to_delete = Bookmarks.query.get_or_404(id)
    try:
        db.session.delete(bookmark_to_delete)
        db.session.commit()
        return redirect('/bookmarks_view')
    except:
        return 'There was a problem deleting that bookmark.'


@app.route('/update/<int:id>',methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task.'
    else:
        return render_template('update.html', task=task)


@app.route('/update_bookmark/<int:id>', methods=['GET', 'POST'])
def update_bookmark(id):
    bookmark = Bookmarks.query.get_or_404(id)
    if request.method == 'POST':
        bookmark.content = request.form['content']
        bookmark.comment = request.form['comment']
        try:
            db.session.commit()
            return redirect('/bookmarks_view')
        except:
            return 'There was an issue updating your bookmark.'
    else:
        return render_template('bookmarks_update.html', bookmark=bookmark)


@app.route('/done/<int:id>')
def done(id):
    task_to_done = Todo.query.get_or_404(id)
    try:
        task_to_done.completed = 1
        db.session.add(task_to_done)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem during status change of that task.'


@app.route('/undone/<int:id>')
def undone(id):
    task_to_undone = Todo.query.get_or_404(id)
    try:
        task_to_undone.completed = 0
        db.session.add(task_to_undone)
        db.session.commit()
        return redirect('/done_view')
    except:
        return 'There was a problem during status change of that task.'


@app.route('/done_view')
def done_view():
    tasks = Todo.query.filter_by(completed=1).all()
    return render_template('done_view.html', tasks=tasks)


@app.route('/reminders_view')
def reminders_view():
    return render_template('under_construction.html')


@app.route('/bookmarks_view', methods=['POST', 'GET'])
def bookmarks_view():
    if request.method == 'POST':
        bookmark_content = request.form['content']
        bookmark_comment = request.form['comment']
        new_bookmark = Bookmarks(content=bookmark_content, comment=bookmark_comment, date_created=datetime.now())
        try:
            db.session.add(new_bookmark)
            db.session.commit()
            return redirect('/bookmarks_view')
        except:
            return 'There was an issue adding your bookmark'
    else:
        bookmarks = Bookmarks.query.order_by(Bookmarks.date_created).all()
        return render_template('bookmarks.html', bookmarks=bookmarks)


@app.route('/notes_view')
def notes_view():
    return render_template('under_construction.html')


@app.route('/stats_view')
def stats_view():
    return render_template('under_construction.html')


@app.context_processor
def my_utility_processor():

    def elapsed_time(then, now=datetime.now(), interval="default"):
        duration = now - then
        duration_in_s = duration.total_seconds()
        elapsed_hours = divmod(duration_in_s, 3600)
        elapsed_minutes = divmod(elapsed_hours[1], 60)
        constructed = str(round(elapsed_hours[0])) + ' hr ' + str(round(elapsed_minutes[0])) + ' min'
        return constructed

    def date_now():
        return datetime.now()

    return dict(date_now=date_now, elapsed_time=elapsed_time)


if __name__ == "__main__":
    app.run(debug=True)

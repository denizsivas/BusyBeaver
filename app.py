from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta, date
from dateutil.relativedelta import relativedelta


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
    cycle = db.Column(db.String)
    type = db.Column(db.String)
    date_target = db.Column(db.String)

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
            error_message = 'There was an issue adding your task.'
            return render_template('not_found.html', error_message=error_message)
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
        error_message = 'There was a problem deleting that task.'
        return render_template('not_found.html', error_message=error_message)


@app.route('/delete_bookmark/<int:id>')
def delete_bookmark(id):
    bookmark_to_delete = Bookmarks.query.get_or_404(id)
    try:
        db.session.delete(bookmark_to_delete)
        db.session.commit()
        return redirect('/bookmarks_view')
    except:
        error_message = 'There was a problem deleting that bookmark.'
        return render_template('not_found.html', error_message=error_message)


@app.route('/update/<int:id>',methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            error_message = 'There was an issue updating your task.'
            return render_template('not_found.html', error_message=error_message)
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
            error_message = 'There was an issue updating your bookmark.'
            return render_template('not_found.html', error_message=error_message)
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
        error_message = 'There was a problem during status change of that task.'
        return render_template('not_found.html', error_message=error_message)


@app.route('/undone/<int:id>')
def undone(id):
    task_to_undone = Todo.query.get_or_404(id)
    try:
        task_to_undone.completed = 0
        db.session.add(task_to_undone)
        db.session.commit()
        return redirect('/done_view')
    except:
        error_message = 'There was a problem during status change of that task.'
        return render_template('not_found.html', error_message=error_message)



@app.route('/done_view')
def done_view():
    tasks = Todo.query.filter_by(completed=1).all()
    return render_template('done_view.html', tasks=tasks)


@app.route('/reminders_view', methods=['POST', 'GET'])
def reminders_view():
    if request.method == 'POST':
        reminder_content = request.form['content']
        reminder_type = request.form['type']
        reminder_cycle = request.form['cycle']
        reminder_target_date = request.form['target_date']
        new_reminder = Reminders(content=reminder_content, type=reminder_type, date_created=datetime.now(), cycle=reminder_cycle, date_target=reminder_target_date)
        try:
            db.session.add(new_reminder)
            db.session.commit()
        except:
            error_message = 'There was a problem adding your reminder.'
            return render_template('not_found.html', error_message=error_message)
        return redirect('/reminders_view')
    else:
        reminders = Reminders.query.order_by(Reminders.date_created).all()
        # sort the reminders based on their deadline
        reminders_ext = []
        for reminder in reminders:
            target = date.fromisoformat(reminder.date_target)
            now = datetime.now().date()
            remaining_days = (target - now).days
            combo = (reminder, remaining_days)
            reminders_ext.append(combo)
        reminders_ext.sort(key=lambda a: a[1], reverse=False)
        reminders = list(zip(*reminders_ext))[0]
        return render_template('reminders.html', reminders=reminders)


@app.route('/update_reminder/<int:id>', methods=['GET', 'POST'])
def update_reminder(id):
    reminder = Reminders.query.get_or_404(id)
    if request.method == 'POST':
        reminder.content = request.form['content']
        reminder.type = request.form['type']
        reminder.cycle = request.form['cycle']
        reminder.date_target = request.form['target_date']
        try:
            db.session.commit()
            return redirect('/reminders_view')
        except:
            error_message = 'There was an issue updating your reminder.'
            return render_template('not_found.html', error_message=error_message)
    else:
        return render_template('reminders_update.html', reminder=reminder)


@app.route('/next_reminder/<int:id>')
def next_reminder(id):
    reminder = Reminders.query.get_or_404(id)
    target_date_to_iterate = date.fromisoformat(reminder.date_target)
    if reminder.cycle == 'once':
        error_message = 'This task is not recurrent. Update the type first.'
        return render_template('not_found.html', error_message=error_message)
    elif reminder.cycle == 'daily':
        delta = timedelta(days=1)
        reminder.date_target = target_date_to_iterate + delta
    elif reminder.cycle == 'weekly':
        delta = timedelta(weeks=1)
        reminder.date_target = target_date_to_iterate + delta
    elif reminder.cycle == 'monthly':
        delta = relativedelta(months=1)
        reminder.date_target = target_date_to_iterate + delta
    elif reminder.cycle == 'yearly':
        delta = relativedelta(years=1)
        reminder.date_target = target_date_to_iterate + delta
    try:
        db.session.commit()
        return redirect('/reminders_view')
    except:
        error_message = 'There was an issue iterating your reminder.'
        return render_template('not_found.html', error_message=error_message)


@app.route('/delete_reminder/<int:id>')
def delete_reminder(id):
    reminder_to_delete = Reminders.query.get_or_404(id)
    try:
        db.session.delete(reminder_to_delete)
        db.session.commit()
        return redirect('/reminders_view')
    except:
        error_message = 'There was a problem deleting that reminder.'
        return render_template('not_found.html', error_message=error_message)


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
            error_message = 'There was an issue adding your bookmark'
            return render_template('not_found.html', error_message=error_message)
    else:
        bookmarks = Bookmarks.query.order_by(Bookmarks.date_created).all()
        return render_template('bookmarks.html', bookmarks=bookmarks)


@app.route('/notes_view')
def notes_view():
    return render_template('under_construction.html')


@app.route('/stats_view')
def stats_view():
    tasks_count = Todo.query.filter_by(completed=0).count()
    tasks_completed = Todo.query.filter_by(completed=1).count()
    task_completion = '% ' + str(round((tasks_completed / (tasks_count + tasks_completed))*100, 2))
    reminders_count = Reminders.query.order_by(Reminders.date_created).count()
    bookmarks_count = Bookmarks.query.order_by(Bookmarks.date_created).count()
    reminders_all = Reminders.query.all()
    close_reminders = []
    for reminder in reminders_all:
        target = date.fromisoformat(reminder.date_target)
        now = datetime.now().date()
        remaining_days = (target - now).days
        if remaining_days <= 2:
            close_reminders.append(reminder)

    return render_template('stats.html', tasks_count=tasks_count, reminders_count=reminders_count, bookmarks_count=bookmarks_count, task_completion=task_completion, close_reminders=close_reminders)


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

    def cw_now():
        return datetime.utcnow().isocalendar()[1]

    def time_remaining(target_date):
        target = date.fromisoformat(target_date)
        now = datetime.now().date()
        remaining_days = (target - now).days
        return remaining_days

    return dict(date_now=date_now, elapsed_time=elapsed_time, time_remaining=time_remaining, cw_now=cw_now)


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
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


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(400), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<Note %r' % self.id


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
        if request.form['content'] == '':
            error_message = 'One of the fields is missing.'
            return render_template('not_found.html', error_message=error_message)
        else:
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


@app.route('/update/<int:id>', methods=['GET', 'POST'])
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


@app.route('/reminders_view', methods=['POST', 'GET'])
def reminders_view():
    if request.method == 'POST':
        if request.form['content'] == '' or request.form['type'] == '' or request.form['cycle'] == '' or \
                request.form['target_date'] == '':
            error_message = 'One of the fields is missing.'
            flash(error_message, 'error')
            return redirect('/reminders_view')
        else:
            reminder_content = request.form['content']
            reminder_type = request.form['type']
            reminder_cycle = request.form['cycle']
            reminder_target_date = request.form['target_date']
            new_reminder = Reminders(content=reminder_content, type=reminder_type, date_created=datetime.now(),
                                     cycle=reminder_cycle, date_target=reminder_target_date)
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
        if request.form['content'] == '' or request.form['type'] == '' or request.form['cycle'] == '' or \
                request.form['target_date'] == '':
            error_message = 'One of the fields is missing.'
            flash(error_message, 'error')
            return redirect('/reminders_view')
        else:
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


@app.route('/notes_view', methods=['POST', 'GET'])
def notes_view():
    if request.method == 'POST':
        if request.form['content'] == '':
            error_message = 'Note content cannot be empty.'
            flash(error_message, category='error')
            return redirect('/notes_view')
        else:
            note_content = request.form['content']
            new_note = Notes(content=note_content, date_created=datetime.now())
            try:
                db.session.add(new_note)
                db.session.commit()
            except:
                error_message = 'There was a problem adding your note.'
                return render_template('not_found.html', error_message=error_message)
            return redirect('/notes_view')
    else:
        notes = Notes.query.order_by(Notes.date_created).all()
        return render_template('notes.html', notes=notes)


@app.route('/update_note/<int:id>', methods=['GET', 'POST'])
def update_note(id):
    note = Notes.query.get_or_404(id)
    if request.method == 'POST':
        if request.form['content'] == '':
            error_message = 'One of the fields is missing.'
            flash(error_message, 'error')
            return redirect('/notes_view')
        else:
            note.content = request.form['content']
            try:
                db.session.commit()
                return redirect('/notes_view')
            except:
                error_message = 'There was an issue updating your note.'
                return render_template('not_found.html', error_message=error_message)
    else:
        return render_template('notes_update.html', note=note)


@app.route('/delete_note/<int:id>')
def delete_note(id):
    note_to_delete = Notes.query.get_or_404(id)
    try:
        db.session.delete(note_to_delete)
        db.session.commit()
        return redirect('/notes_view')
    except:
        error_message = 'There was a problem deleting that note.'
        return render_template('not_found.html', error_message=error_message)


@app.route('/purchasing_view')
def purchasing_view():
    return render_template('under_construction.html')


@app.route('/stats_view')
def stats_view():
    tasks_count = Todo.query.filter_by(completed=0).count()
    tasks_completed = Todo.query.filter_by(completed=1).count()
    task_completion = '% ' + str(round((tasks_completed / (tasks_count + tasks_completed)) * 100, 2))
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

    return render_template('stats.html', tasks_count=tasks_count, reminders_count=reminders_count,
                           bookmarks_count=bookmarks_count, task_completion=task_completion,
                           close_reminders=close_reminders)


@app.route('/weather_view')
def weather_view():
    weather_url = os.getenv("WEATHERAPI")
    lat_home = os.getenv("LAT_HOME")
    lon_home = os.getenv("LON_HOME")
    lat_work = os.getenv("LAT_WORK")
    lon_work = os.getenv("LON_WORK")
    api_key = os.getenv("API_KEY")
    payload_home = {"lat": lat_home, "lon": lon_home, "units": 'metric', "appid": api_key}
    # Calling the weather api for home
    response_home = requests.get(weather_url, params=payload_home)
    data_home = response_home.json()
    weather_info = data_home.get('weather')
    description = weather_info[0]['description']
    main_info = data_home.get('main')
    temp = main_info['temp']
    temp_min = main_info['temp_min']
    temp_max = main_info['temp_max']
    humidity = main_info['humidity']
    wind = data_home.get('wind')
    speed = wind['speed']
    degree = wind['deg']
    sys = data_home.get('sys')
    sunrise = sys['sunrise']
    sunset = sys['sunset']
    date_conv_sunrise = (datetime.utcfromtimestamp(sunrise) + timedelta(hours=3)).strftime('%H:%M:%S')
    date_conv_sunset = (datetime.utcfromtimestamp(sunset) + timedelta(hours=3)).strftime('%H:%M:%S')
    home_weather_data = {'description': description, 'temperature': temp, 'temp_min': temp_min, 'temp_max': temp_max,
                         'humidity': humidity, 'wind_speed': speed, 'wind_degree': degree,
                         'converted_sunrise': date_conv_sunrise, 'converted_sunset': date_conv_sunset}
    # Calling the weather api for work
    payload_work = {"lat": lat_work, "lon": lon_work, "units": 'metric', "appid": api_key}
    response_work = requests.get(weather_url, params=payload_work)
    data_work = response_work.json()
    weather_info = data_work.get('weather')
    description = weather_info[0]['description']
    main_info = data_work.get('main')
    temp = main_info['temp']
    temp_min = main_info['temp_min']
    temp_max = main_info['temp_max']
    humidity = main_info['humidity']
    wind = data_work.get('wind')
    speed = wind['speed']
    degree = wind['deg']
    sys = data_work.get('sys')
    sunrise = sys['sunrise']
    sunset = sys['sunset']

    date_conv_sunrise = (datetime.utcfromtimestamp(sunrise) + timedelta(hours=3)).strftime('%H:%M:%S')
    date_conv_sunset = (datetime.utcfromtimestamp(sunset) + timedelta(hours=3)).strftime('%H:%M:%S')
    work_weather_data = {'description': description, 'temperature': temp, 'temp_min': temp_min, 'temp_max': temp_max,
                         'humidity': humidity, 'wind_speed': speed, 'wind_degree': degree,
                         'converted_sunrise': date_conv_sunrise, 'converted_sunset': date_conv_sunset}

    return render_template('weatherinfo.html', weather_at_home=home_weather_data, weather_at_work=work_weather_data)


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

    def numberofday_now():
        dt = datetime.utcnow()
        day = dt.strftime('%A')
        return dt.weekday() + 1, day

    def time_remaining(target_date):
        target = date.fromisoformat(target_date)
        now = datetime.now().date()
        remaining_days = (target - now).days
        return remaining_days

    return dict(date_now=date_now, elapsed_time=elapsed_time, time_remaining=time_remaining, cw_now=cw_now,
                numberofday_now=numberofday_now)


if __name__ == "__main__":
    app.run(debug=True)

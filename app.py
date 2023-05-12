from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(app)

timezone_offset = +3.0  # (UTC+03:00)
tzinfo = timezone(timedelta(hours=timezone_offset))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now(tzinfo))

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        # calculate the elapsed time here
        #for task in tasks:
        #    task.elapsed = getDuration(task.date_created)
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

@app.route('/done/<int:id>', methods = ['GET', 'POST'])
def done(id):
    task = Todo.query.get_or_404(id)
    return render_template('trial.html', task=task)

@app.context_processor
def my_utility_processor():

    def elapsed_time(then, now=datetime.now(), interval="default"):
        print('verilen tarih ' + str(then))
        print('şuanki tarih ' + str(now))
        duration = now - then
        duration_in_s = duration.total_seconds()
        print('aradaki fark ' + str(duration_in_s))
        elapsed_hours = divmod(duration_in_s, 3600)
        elapsed_minutes = divmod(elapsed_hours[1], 60)
        constructed = str(elapsed_hours[0]) + ' hr ' +  str(elapsed_minutes[0]) + ' min'
        return constructed

    # TODO: Complete the missing portion of the timing

    return dict(elapsed_time=elapsed_time)


if __name__ == "__main__":
    app.run(debug=True)

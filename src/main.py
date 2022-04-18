import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime, timedelta
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
socketio = SocketIO(app)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_event(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    conn.close()
    return event


def send_message(title, content):
    package = {}
    package["title"] = title
    package["data"] = content
    send(package, json=True)


def error404():
    return render_template('error.html')


@app.route('/')
def main():
    return render_template('week_view.html')


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['summary']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO events (summary, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('main'))
    return render_template('create.html')


@app.route('/calendars')
def calendars():
    conn = get_db_connection()
    request = "SELECT * FROM calendars"
    cal_elts = conn.execute(request).fetchall()
    conn.close()
    return render_template('calendars.html', cal_elts=cal_elts)


@app.route('/<int:event_id>')
def event(event_id):
    event = get_event(event_id)
    if event is None:
        return error404()
    return render_template('event.html', event=event)


def select_to_dict_list(selection):
    list_ = []
    if len(selection) == 0:
        return list_
    keys = selection[0].keys()
    for row in selection:
        list_.append({key: row[key] for key in keys})
    return list_


@socketio.on('get_events')
def get_events(data):
    start_day = datetime.fromtimestamp(int(data.split(" ")[0].replace(",", ""))/1000.0)
    conn = get_db_connection()
    day_start = start_day.strftime('%Y-%m-%d 00:00:00')
    day_end = (start_day+timedelta(days=int(data.split(" ")[1]))).strftime('%Y-%m-%d 00:00:00')
    request = f"SELECT * FROM events WHERE dt_start > '{day_start}' AND dt_start < '{day_end}'  ORDER BY dt_start"
    events = conn.execute(request).fetchall()
    conn.close()
    events = select_to_dict_list(events)
    send_message("events", events)


@socketio.on('get_calendars')
def get_calendars(data):
    conn = get_db_connection()
    request = "SELECT * FROM calendars ORDER BY id"
    calendars = conn.execute(request).fetchall()
    conn.close()
    calendars = select_to_dict_list(calendars)
    send_message("calendars", calendars)


@socketio.on('set_cal_color')
def set_cal_color(data):
    cal_id = data.split(" ")[0]
    color = "".join(data.split(" ")[1:])
    conn = get_db_connection()
    request = f"UPDATE calendars SET color = '{color}' WHERE id = {cal_id}"
    conn.execute(request).fetchall()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    socketio.run(app)

import random
import sqlite3
import string
from flask import Flask, redirect, render_template
from datetime import datetime, timedelta
from flask_socketio import SocketIO, Namespace
from external_services.google import google_auth, google_calendar
from external_services.strava import strava_auth, strava_activities
from utils import select_to_dict_list
from utils.calendar import get_recurring_events

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

app.register_blueprint(google_auth.app)
app.register_blueprint(strava_auth.app)
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
    socketio.send(package, json=True)


@app.route('/')
def main():
    return redirect("/calendar")


@app.route('/calendar')
def calendar():
    return render_template('week_view.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


def get_events(data):
    start_day = datetime.fromtimestamp(int(data.split(" ")[0].replace(",", ""))/1000.0)
    day_nb = int(data.split(" ")[1])
    conn = get_db_connection()
    day_start = start_day.timestamp()
    day_end = (start_day+timedelta(days=day_nb)).timestamp()
    request = '''SELECT *, strava_activities.id AS strava_id FROM events
                 LEFT JOIN strava_activities ON strava_activities.id=events.strava_act_id
                 WHERE deleted != 1 '''
    request_ = f"AND ((dt_start >= '{day_start}' AND dt_start < '{day_end}')"
    request_ += f" OR (dt_end > '{day_start}' AND dt_start < '{day_start}')) ORDER BY dt_start"
    non_recursive_events = conn.execute(request + request_).fetchall()
    request_ = "AND (recurrence IS NOT NULL AND recurrence != '') ORDER BY dt_start"
    recursive_events = conn.execute(request + request_).fetchall()
    conn.close()
    recursive_events = get_recurring_events(select_to_dict_list(recursive_events),
                                            start_day,
                                            (start_day+timedelta(days=day_nb)))
    events = sorted(select_to_dict_list(non_recursive_events+recursive_events), key=lambda d: d['dt_start'])
    send_message("events", events)


def get_cal_list():
    conn = get_db_connection()
    request = "SELECT * FROM calendars ORDER BY id"
    calendars = conn.execute(request).fetchall()
    conn.close()
    calendars = select_to_dict_list(calendars)
    send_message("calendars", calendars)


def set_cal_color(cal_id, color):
    conn = get_db_connection()
    request = f"UPDATE calendars SET color = '{color}' WHERE id = {cal_id}"
    conn.execute(request).fetchall()
    conn.commit()
    conn.close()


def set_cal_shown(cal_id, shown):
    visibility = "1" if shown == "true" else "0"
    conn = get_db_connection()
    request = f"UPDATE calendars SET shown = '{visibility}' WHERE id = {cal_id}"
    conn.execute(request).fetchall()
    conn.commit()
    conn.close()


def set_cal_activated(cal_id, activation):
    activated = "1" if activation == "true" else "0"
    conn = get_db_connection()
    request = f"UPDATE calendars SET activated = '{activated}' WHERE id = {cal_id}"
    conn.execute(request).fetchall()
    conn.commit()
    conn.close()


def set_cal_title(cal_id, title):
    conn = get_db_connection()
    request = f"UPDATE calendars SET title = '{title}' WHERE id = {cal_id}"
    conn.execute(request).fetchall()
    conn.commit()
    conn.close()


def refresh_calendars():
    if google_auth.is_logged_in():
        google_calendar.store_calendars()
    if strava_auth.is_logged_in():
        strava_activities.store_activities_in_calendars()


class SocketIONameSpace(Namespace):
    def trigger_event(self, event_name, *args):
        if len(args) != 2:
            return
        data = args[1]
        if event_name == "get_events":
            get_events(data)
        elif event_name.startswith("set_cal_"):
            prop = event_name.replace("set_cal_", "")
            cal_id = data.split(" ")[0]
            data = " ".join(data.split(" ")[1:])
            if prop == "activated":
                set_cal_activated(cal_id, data)
            elif prop == "shown":
                set_cal_shown(cal_id, data)
            elif prop == "title":
                set_cal_title(cal_id, data)
            elif prop == "color":
                set_cal_color(cal_id, data)
        elif event_name.startswith("get_cal_"):
            if event_name == "get_cal_list":
                get_cal_list()
        elif event_name == "refresh_calendars":
            refresh_calendars()


socketio.on_namespace(SocketIONameSpace())

if __name__ == '__main__':
    socketio.run(app)

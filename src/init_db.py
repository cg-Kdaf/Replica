import sqlite3
from ics_importer import get_event_from_text

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()


events1 = get_event_from_text("../cache/calendars/calendar0.ics")
events2 = get_event_from_text("../cache/calendars/calendar1.ics")
for id, events in enumerate([events1, events2]):
    cur.execute("INSERT INTO calendars (title) VALUES (?)", str(id))
    for event in events:
        tuple = (event['DTSTART'].strftime('%Y-%m-%d %H:%M:%S'),
                 event['DTEND'].strftime('%Y-%m-%d %H:%M:%S'),
                 "".join(event['SUMMARY']),
                 event['DESCRIPTION'] if 'DESCRIPTION' in event.keys() else "",
                 id)
        print(tuple)
        cur.execute("INSERT INTO events (dt_start, dt_end, summary, content, cal_id) VALUES (?, ?, ?, ?, ?)",
                    tuple)

connection.commit()
connection.close()

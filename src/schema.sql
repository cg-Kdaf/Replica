DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS calendars;


CREATE TABLE calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    color TEXT NOT NULL DEFAULT "rgb(200, 200, 200)",
    external_id TEXT,
    updated TIMESTAMP,
    title TEXT NOT NULL,
    original_title TEXT,
    activated BOOLEAN NOT NULL DEFAULT 1,
    shown BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER UNIQUE, -- index used to refresh calendar. It's the service's event index
    cal_id INTEGER NOT NULL, -- index corresponding to the calendar containing the event
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_start TIMESTAMP NOT NULL,
    dt_end TIMESTAMP,
    summary TEXT,
    content TEXT,
    recurrence TEXT,
    deleted BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY(cal_id) REFERENCES calendars(id) ON DELETE CASCADE
);

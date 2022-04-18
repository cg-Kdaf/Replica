DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS calendars;


CREATE TABLE calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    color TEXT,
    title TEXT NOT NULL
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cal_id INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_start TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_end TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary TEXT NOT NULL,
    content TEXT,
    FOREIGN KEY(cal_id) REFERENCES calendars(id)
);

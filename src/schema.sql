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
CREATE TABLE event_types(id INTEGER PRIMARY KEY AUTOINCREMENT, logo_url TEXT, title TEXT, parent_type INTEGER, FOREIGN KEY(parent_type) REFERENCES event_types(id));
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
    _type INTEGER,
    FOREIGN KEY(_type) REFERENCES event_types(id),
    FOREIGN KEY(cal_id) REFERENCES calendars(id) ON DELETE CASCADE
);
CREATE TABLE strava_activities (
    id INTEGER PRIMARY KEY,
    external_id TEXT,
    upload_id INTEGER,
    updated TIMESTAMP,
    athlete_id TEXT,
    _name TEXT,
    distance FLOAT,
    moving_time INTEGER,
    total_elevation_gain FLOAT,
    elev_high FLOAT,
    elev_low FLOAT,
    _type TEXT,
    _start_date TIMESTAMP,
    _end_date TIMESTAMP,
    achievement_count INTEGER,
    start_latlng TEXT,
    end_latlng TEXT,
    kudos_count INTEGER,
    comment_count INTEGER,
    athlete_count INTEGER,
    photo_count INTEGER,
    map_id TEXT,
    map_polyline TEXT,
    map_summary_polyline TEXT,
    trainer BOOLEAN,
    workout_type INTEGER,
    upload_id_str TEXT,
    average_speed FLOAT,
    max_speed FLOAT,
    gear_id TEXT,
    kilojoules FLOAT,
    average_watts FLOAT
);

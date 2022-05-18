CREATE TABLE calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    color TEXT NOT NULL DEFAULT "rgb(200, 200, 200)",
    external_id TEXT,
    updated INTEGER, -- Timestamp in seconds
    title TEXT NOT NULL,
    original_title TEXT,
    activated BOOLEAN NOT NULL DEFAULT 1,
    shown BOOLEAN NOT NULL DEFAULT 1
);
CREATE TABLE event_types(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logo_url TEXT,
    title TEXT,
    parent_type INTEGER,
    FOREIGN KEY(parent_type) REFERENCES event_types(id)
);
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER UNIQUE, -- index used to refresh calendar. It's the service's event index
    cal_id INTEGER NOT NULL, -- index corresponding to the calendar containing the event
    created INTEGER NOT NULL, -- Timestamp in seconds
    updated INTEGER NOT NULL, -- Timestamp in seconds
    dt_start INTEGER NOT NULL, -- Timestamp in seconds
    dt_end INTEGER, -- Timestamp in seconds,
    name TEXT,
    description TEXT,
    recurrence TEXT,
    deleted BOOLEAN NOT NULL DEFAULT 0,
    type INTEGER,
    strava_act_id INTEGER DEFAULT NULL,
    FOREIGN KEY(type) REFERENCES event_types(id),
    FOREIGN KEY(strava_act_id) REFERENCES strava_activities(id) ON DELETE CASCADE
    FOREIGN KEY(cal_id) REFERENCES calendars(id) ON DELETE CASCADE
);
CREATE TABLE strava_activities (
    id INTEGER PRIMARY KEY,
    external_id TEXT,
    upload_id INTEGER,
    updated INTEGER, -- Timestamp in seconds
    athlete_id TEXT,
    name TEXT,
    description TEXT,
    distance FLOAT,
    moving_time INTEGER,
    elapsed_time INTEGER,
    total_elevation_gain FLOAT,
    elev_high FLOAT,
    elev_low FLOAT,
    type TEXT,
    start_date INTEGER, -- Timestamp in seconds
    end_date INTEGER, -- Timestamp in seconds
    achievement_count INTEGER,
    pr_count INTEGER,
    start_latlng TEXT,
    end_latlng TEXT,
    kudos_count INTEGER,
    comment_count INTEGER,
    athlete_count INTEGER,
    photo_count INTEGER,
    total_photo_count INTEGER,
    map_id TEXT,
    map_polyline TEXT,
    map_summary_polyline TEXT,
    trainer BOOLEAN,
    gear_id INTEGER,
    workout_type INTEGER,
    upload_id_str TEXT,
    average_speed FLOAT,
    max_speed FLOAT,
    average_cadence FLOAT,
    average_heartrate INTEGER,
    max_heartrate INTEGER,
    average_watts FLOAT,
    max_watts FLOAT,
    kilojoules FLOAT,
    calories FLOAT,
    laps_distances TEXT,
    laps_times TEXT,
    laps_speeds TEXT,
    detailed BOOLEAN DEFAULT 0
);
CREATE TABLE strava_segments_effots (
  id INTEGER PRIMARY KEY,
  activity_id INTEGER,
  segment_id INTEGER,
  elapsed_time FLOAT,
  moving_time FLOAT,
  kom_rank INTEGER,
  pr_rank INTEGER,
  FOREIGN KEY(activity_id) REFERENCES strava_activities(id),
  FOREIGN KEY(segment_id) REFERENCES strava_segments(id)
);
CREATE TABLE strava_segments (
  id INTEGER PRIMARY KEY,
  name TEXT,
  activity_type TEXT,
  distance FLOAT,
  average_grade FLOAT,
  maximum_grade FLOAT,
  elevation_high FLOAT,
  elevation_low FLOAT,
  start_latlng TEXT,
  end_latlng TEXT
);
CREATE TABLE strava_athletes (
  id INTEGER PRIMARY KEY,
  human_id INTEGER,
  firstname TEXT,
  lastname TEXT,
  sex BOOLEAN, -- 1 for woman, 0 for man
  city TEXT,
  picture_medium TEXT, -- url to profile pic
  picture TEXT, -- url to profile pic
  follower_count INTEGER,
  following_me BOOLEAN, -- follows logged athlete
  i_follow BOOLEAN -- logged athlete follows
);
CREATE TABLE strava_gears (
  id INTEGER PRIMARY KEY,
  athlete_id INTEGER,
  name TEXT,
  description TEXT,
  distance FLOAT,
  FOREIGN KEY(athlete_id) REFERENCES strava_athletes(id)
);
CREATE TABLE strava_comments (
  id INTEGER PRIMARY KEY,
  athlete_id INTEGER,
  activity_id INTEGER,
  description TEXT,
  FOREIGN KEY(athlete_id) REFERENCES strava_athletes(id),
  FOREIGN KEY(activity_id) REFERENCES strava_activities(id)
);
CREATE TABLE strava_activities_athletes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  athlete_id INTEGER,
  activity_id INTEGER,
  FOREIGN KEY(athlete_id) REFERENCES strava_athletes(id),
  FOREIGN KEY(activity_id) REFERENCES strava_activities(id),
  UNIQUE (athlete_id, activity_id)
);

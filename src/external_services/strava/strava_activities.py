import pytz
import requests
from .strava_auth import build_credentials
from ..common import get_database_connection, poll_calendar
from datetime import datetime, timedelta
from utils import generate_sql_datafields, get_key, sql_select

API_URL = "https://www.strava.com/api/v3/"
STRAVA_CAL_NAME = "Strava Calendar"


def request_api(path, **args):
    creds = build_credentials()
    params = {**creds, **dict(args)}
    return requests.get(API_URL + path, params=params).json()


def get_all_activities():
    page_index = 1
    activities = request_api("athlete/activities",
                             before=datetime.now().timestamp(),
                             after=0,
                             page=page_index,
                             per_page=200)
    # Per page max is 200
    while True:
        page_index += 1
        activities_buffer = request_api("athlete/activities",
                                        before=datetime.now().timestamp(),
                                        after=0,
                                        page=page_index,
                                        per_page=200)
        if activities_buffer == []:
            break
        activities = activities + activities_buffer
    return activities


def calc_end(start, duration_seconds):
    start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
    start += timedelta(seconds=duration_seconds)
    return start.strftime("%Y-%m-%dT%H:%M:%S")


def store_activities_in_calendars():
    store_activities()
    conn = get_database_connection()
    cur = conn.cursor()

    if not poll_calendar(cur, STRAVA_CAL_NAME):
        datas = {
            "title": STRAVA_CAL_NAME,
            "original_title": STRAVA_CAL_NAME
        }
        values, raw_datas = generate_sql_datafields(datas)
        cur.execute("INSERT INTO calendars " + values, raw_datas)

    id_in_db = poll_calendar(cur, STRAVA_CAL_NAME)
    command = f"SELECT updated from calendars WHERE id = {id_in_db}"
    updated_last = sql_select(cur, command)[0]["updated"]
    command = f"SELECT * FROM strava_activities WHERE updated > '{updated_last}'"
    activities_after_updated = sql_select(cur, command)
    for activity in activities_after_updated:
        datas = {
            "cal_id": id_in_db,
            "original_id": activity["id"],
            "dt_start": activity["_start_date"],
            "dt_end": activity["_end_date"],
            "created": activity["_end_date"],
            "updated": activity["updated"],
            "summary": get_key(activity, "_name"),
            "strava_act_id": activity["id"]
        }
        values, raw_datas = generate_sql_datafields(datas)
        cur.execute("INSERT OR REPLACE INTO events " + values, raw_datas)
    request = f"UPDATE calendars SET updated = '{datetime.now().isoformat()}' WHERE id = {id_in_db}"
    conn.execute(request).fetchall()
    conn.commit()
    conn.close()


def store_activities():
    conn = get_database_connection()
    cur = conn.cursor()
    now = datetime.now()

    for activity in get_all_activities():
        utc_offset = datetime.now(pytz.timezone(activity["timezone"][12:])).isoformat()[-6:]
        datas = {
            "id": activity["id"],
            "external_id": activity["external_id"],
            "upload_id": activity["upload_id"],
            "athlete_id": activity["athlete"]["id"],
            "moving_time": get_key(activity, "moving_time", 0),
            "total_elevation_gain": get_key(activity, "total_elevation_gain", 0.0),
            "elev_high": get_key(activity, "elev_high", 0.0),
            "elev_low": get_key(activity, "elev_low", 0.0),
            "_start_date": activity["start_date_local"][:-1] + utc_offset,
            "_end_date": calc_end(activity["start_date_local"], activity["elapsed_time"]) + utc_offset,
            "start_latlng": ", ".join(list(map(str, get_key(activity, "start_latlng", [])))),
            "end_latlng": ", ".join(list(map(str, get_key(activity, "end_latlng", [])))),
            "map_id": get_key(get_key(activity, "map"), "id"),
            "map_polyline": get_key(get_key(activity, "map"), "polyline"),
            "map_summary_polyline": get_key(get_key(activity, "map"), "summary_polyline"),
            "upload_id_str": get_key(activity, "upload_id_str"),
            "average_speed": get_key(activity, "average_speed", 0.0),
            "max_speed": get_key(activity, "max_speed", 0.0),
            "kilojoules": get_key(activity, "kilojoules", 0.0),
            "average_watts": get_key(activity, "average_watts", 0.0)
        }
        changing_datas = {
            "updated": now.isoformat(),  # Keep it first for updating stages
            "_name": activity["name"],
            "distance": get_key(activity, "distance", 0.0),
            "_type": get_key(activity, "type"),
            "achievement_count": get_key(activity, "achievement_count", 0),
            "kudos_count": get_key(activity, "kudos_count", 0),
            "comment_count": get_key(activity, "comment_count", 0),
            "athlete_count": get_key(activity, "athlete_count", 0),
            "photo_count": get_key(activity, "photo_count", 0),
            "trainer": 0 if get_key(activity, "trainer", 0) else 1,
            "workout_type": get_key(activity, "workout_type", 0),
            "gear_id": get_key(activity, "gear_id")
        }
        values, raw_datas = generate_sql_datafields({**datas, **changing_datas})
        cur.execute("INSERT OR IGNORE INTO strava_activities " + values, raw_datas)
        if cur.lastrowid != activity["id"]:
            actual_values = sql_select(cur, f'''SELECT {', '.join(changing_datas.keys())}
                                                FROM strava_activities
                                                WHERE id = {activity['id']}''')
            if list(actual_values[0].values())[1:] != list(changing_datas.values())[1:]:
                set_keys = " = ? , ".join(list(changing_datas.keys())) + " = ?"
                set_values = list(changing_datas.values())
                cur.execute(f"UPDATE strava_activities SET {set_keys} WHERE id = {activity['id']}",
                            set_values)
    conn.commit()
    conn.close()

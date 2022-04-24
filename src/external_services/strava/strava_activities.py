import requests
from .strava_auth import build_credentials
from ..common import get_database_connection
from datetime import datetime, timedelta
from utils import select_to_dict_list, generate_sql_datafields, get_key

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
    return start


def store_activities_in_calendars():
    conn = get_database_connection()
    cur = conn.cursor()

    cur.execute(f"DELETE FROM calendars WHERE original_title = '{STRAVA_CAL_NAME}'")
    existing_cals = select_to_dict_list(cur.execute("SELECT * FROM calendars").fetchall())
    if not any(cal["original_title"] == STRAVA_CAL_NAME for cal in existing_cals):
        datas = {
            "title": STRAVA_CAL_NAME,
            "original_title": STRAVA_CAL_NAME
        }
        values, raw_datas = generate_sql_datafields(datas)
        cur.execute("INSERT INTO calendars " + values, raw_datas)
        existing_cals = select_to_dict_list(cur.execute("SELECT * FROM calendars").fetchall())
        id_in_db = list(filter(lambda cal: cal["original_title"] == STRAVA_CAL_NAME, existing_cals))
        id_in_db = id_in_db[0]["id"]
        for activity in get_all_activities():
            datas = {
                "cal_id": id_in_db,
                "dt_start": get_key(activity, "start_date_local"),
                "dt_end": calc_end(activity["start_date_local"], activity["elapsed_time"]),
                "summary": get_key(activity, "name"),
                "content": f"Distance : {get_key(activity, 'distance')}"
            }
            values, raw_datas = generate_sql_datafields(datas)
            cur.execute("INSERT INTO events " + values, raw_datas)
    conn.commit()
    conn.close()

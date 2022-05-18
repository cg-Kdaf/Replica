import requests
from .strava_auth import build_credentials, get_cookie_valid
from ..common import get_database_connection, poll_calendar
from datetime import datetime
from utils import generate_sql_datafields, generate_sql_datafields_multiple, get_key, sql_select

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


def get_activity_detailed(id):
    activity = request_api("activities/"+str(id))
    return activity


def get_activity_athletes(id):
    cookies = get_cookie_valid()
    json = requests.get(f"https://www.strava.com/feed/activity/{id}/group_athletes",
                        cookies=cookies).json()
    return json["athletes"]


def store_athlete_activity(cur, activity_id):
    athletes = get_activity_athletes(activity_id)
    if athletes == []:
        return
    datas = []
    for athlete in athletes:
        data = {
            "id": athlete["id"],
            "firstname": get_key(athlete, "firstname"),
            "lastname": get_key(athlete, "name").replace(get_key(athlete, "firstname"), ""),
            "picture_medium": get_key(athlete, "avatar_url"),
            "picture": get_key(athlete, "avatar_url").replace("medium", "large"),
            "city": get_key(athlete, "location"),
            "following_me": get_key(athlete, "is_following")
        }
        datas.append(data)
    values, raw_datas = generate_sql_datafields_multiple(datas)
    cur.executemany("INSERT OR REPLACE INTO strava_athletes " + values, raw_datas)
    act_athletes = [{"athlete_id": ath["id"], "activity_id": activity_id} for ath in athletes]
    values, raw_datas = generate_sql_datafields_multiple(act_athletes)
    cur.executemany("INSERT OR IGNORE INTO strava_activities_athletes " + values, raw_datas)


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
            "dt_start": activity["start_date"],
            "dt_end": activity["end_date"],
            "created": activity["end_date"],
            "updated": activity["updated"],
            "name": get_key(activity, "name"),
            "strava_act_id": activity["id"]
        }
        values, raw_datas = generate_sql_datafields(datas)
        cur.execute("INSERT OR REPLACE INTO events " + values, raw_datas)
    request = f"UPDATE calendars SET updated = '{datetime.now().timestamp()}' WHERE id = {id_in_db}"
    cur.execute(request)
    conn.commit()
    conn.close()


def store_activities():
    conn = get_database_connection()
    cur = conn.cursor()
    now = datetime.now()

    for activity in get_all_activities():
        start = int(datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%S%z").timestamp())
        datas = {
            "id": activity["id"],
            "external_id": activity["external_id"],
            "upload_id": activity["upload_id"],
            "athlete_id": activity["athlete"]["id"],
            "moving_time": get_key(activity, "moving_time", 0),
            "total_elevation_gain": get_key(activity, "total_elevation_gain", 0.0),
            "elev_high": get_key(activity, "elev_high", 0.0),
            "elev_low": get_key(activity, "elev_low", 0.0),
            "start_date": start,
            "end_date": start + int(activity["elapsed_time"]),
            "start_latlng": ", ".join(list(map(str, get_key(activity, "start_latlng", [])))),
            "end_latlng": ", ".join(list(map(str, get_key(activity, "end_latlng", [])))),
            "map_id": get_key(get_key(activity, "map"), "id"),
            "map_polyline": get_key(get_key(activity, "map"), "polyline"),
            "map_summary_polyline": get_key(get_key(activity, "map"), "summary_polyline"),
            "upload_id_str": get_key(activity, "upload_id_str"),
            "average_speed": get_key(activity, "average_speed", 0.0),
            "max_speed": get_key(activity, "max_speed", 0.0),
            "kilojoules": get_key(activity, "kilojoules", 0.0),
            "average_watts": get_key(activity, "average_watts", 0.0),
            "detailed": 0
        }
        changing_datas = {
            "updated": int(now.timestamp()),  # Keep it first for updating stages
            "name": activity["name"],
            "distance": get_key(activity, "distance", 0.0),
            "type": get_key(activity, "type"),
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
                # Need to update
                set_keys = " = ? , ".join(list(changing_datas.keys())) + " = ?"
                set_values = list(changing_datas.values())
                cur.execute(f"UPDATE strava_activities SET {set_keys} WHERE id = {activity['id']}",
                            set_values)
                if actual_values[0]["athlete_count"] != changing_datas["athlete_count"]:
                    store_athlete_activity(cur, activity["id"])

    detailed_act_needed = sql_select(cur, '''SELECT id
                                             FROM strava_activities
                                             WHERE detailed = 0''')
    for activity in detailed_act_needed[:80]:
        store_activity_detailed(cur, activity["id"])
        store_athlete_activity(cur, activity["id"])

    conn.commit()
    conn.close()


def store_activity_detailed(cur, activity_id):

    activity = get_activity_detailed(activity_id)
    if 'id' not in activity.keys():
        return
    # TODO #8 too slow here. Is it the requests or the db storing ?
    laps = get_key(activity, "laps", [])
    laps_dist = []
    laps_times = []
    laps_spds = []
    for lap in laps:
        laps_dist.append(str(lap["distance"]))
        laps_times.append(str(lap["elapsed_time"]))
        laps_spds.append(str(lap["average_speed"]))
    now = datetime.now()
    start = datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%S%z").timestamp()
    datas = {
        "id": activity["id"],
        "external_id": activity["external_id"],
        "upload_id": activity["upload_id"],
        "athlete_id": activity["athlete"]["id"],
        "updated": now.timestamp(),  # Keep it first for updating stages
        "name": activity["name"],
        "description": get_key(activity, "description"),
        "moving_time": get_key(activity, "moving_time", 0),
        "elapsed_time": get_key(activity, "elapsed_time", 0),
        "total_elevation_gain": get_key(activity, "total_elevation_gain", 0.0),
        "elev_high": get_key(activity, "elev_high", 0.0),
        "elev_low": get_key(activity, "elev_low", 0.0),
        "start_date": start,
        "end_date": start + int(activity["elapsed_time"]),
        "start_latlng": ", ".join(list(map(str, get_key(activity, "start_latlng", [])))),
        "end_latlng": ", ".join(list(map(str, get_key(activity, "end_latlng", [])))),
        "map_id": get_key(get_key(activity, "map"), "id"),
        "map_polyline": get_key(get_key(activity, "map"), "polyline"),
        "map_summary_polyline": get_key(get_key(activity, "map"), "summary_polyline"),
        "upload_id_str": get_key(activity, "upload_id_str"),
        "average_speed": get_key(activity, "average_speed", 0.0),
        "max_speed": get_key(activity, "max_speed", 0.0),
        "kilojoules": get_key(activity, "kilojoules", 0.0),
        "calories": get_key(activity, "calories", 0.0),
        "average_watts": get_key(activity, "average_watts", 0.0),
        "max_watts": get_key(activity, "max_watts", 0.0),
        "average_cadence": get_key(activity, "average_cadence", 0.0),
        "average_heartrate": get_key(activity, "average_heartrate", 0),
        "max_heartrate": get_key(activity, "max_heartrate", 0),
        "distance": get_key(activity, "distance", 0.0),
        "type": get_key(activity, "type"),
        "achievement_count": get_key(activity, "achievement_count", 0),
        "pr_count": get_key(activity, "pr_count", 0),
        "kudos_count": get_key(activity, "kudos_count", 0),
        "comment_count": get_key(activity, "comment_count", 0),
        "athlete_count": get_key(activity, "athlete_count", 0),
        "photo_count": get_key(activity, "photo_count", 0),
        "total_photo_count": get_key(activity, "total_photo_count", 0),
        "trainer": 0 if get_key(activity, "trainer", 0) else 1,
        "workout_type": get_key(activity, "workout_type", 0),
        "gear_id": get_key(activity, "gear_id"),
        "laps_distances": " ".join(laps_dist),
        "laps_times": " ".join(laps_times),
        "laps_speeds": " ".join(laps_spds),
        "detailed": 1
    }
    values, raw_datas = generate_sql_datafields(datas)
    cur.execute("INSERT OR REPLACE INTO strava_activities " + values, raw_datas)

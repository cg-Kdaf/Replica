import googleapiclient.discovery
from .google_auth import build_credentials
from ..common import get_database_connection
from utils import select_to_dict_list, generate_sql_datafields, get_key


def get_calendar(calendar_id):
    cal_api = googleapiclient.discovery.build('calendar', 'v3', credentials=build_credentials())
    calendar_content = cal_api.events().list(calendarId=calendar_id,
                                             singleEvents=True,
                                             maxResults=9999).execute()
    events = calendar_content["items"]
    while "nextPageToken" in calendar_content.keys():
        calendar_content = cal_api.events().list(calendarId=calendar_id,
                                                 pageToken=calendar_content["nextPageToken"],
                                                 singleEvents=True,
                                                 maxResults=9999).execute()
        events = events + calendar_content["items"]

    return events


def google_startend_datetime(date_time_dict):
    whole_datetime = ""
    if "date" in date_time_dict.keys():
        whole_datetime = whole_datetime + date_time_dict["date"] + " "
    if "dateTime" in date_time_dict.keys():
        whole_datetime = whole_datetime + date_time_dict["dateTime"]
    return whole_datetime


def store_calendars():
    conn = get_database_connection()
    cur = conn.cursor()

    existing_cals = select_to_dict_list(cur.execute("SELECT * FROM calendars").fetchall())
    existing_ids = [cal["external_id"] for cal in existing_cals]
    cal_api = googleapiclient.discovery.build('calendar', 'v3', credentials=build_credentials())
    calendar_list = cal_api.calendarList().list().execute()
    for calendar in calendar_list["items"]:
        if calendar["id"] not in existing_ids:
            cur.execute("INSERT INTO calendars (external_id, title) VALUES (?, ?)", (calendar["id"], calendar["summary"]))
            existing_cals = select_to_dict_list(cur.execute("SELECT * FROM calendars").fetchall())
            id_in_db = list(filter(lambda cal: cal["external_id"] == calendar["id"], existing_cals))
            id_in_db = id_in_db[0]["id"]
            events = get_calendar(calendar["id"])
            for event in events:
                if "recurringEventId" in event.keys():
                    continue
                datas = {
                    "cal_id": id_in_db,
                    "created": get_key(event, 'created'),
                    "updated": get_key(event, 'updated'),
                    "dt_start": google_startend_datetime(get_key(event, 'start', {})),
                    "dt_end": google_startend_datetime(get_key(event, 'end', {})),
                    "summary": get_key(event, 'summary'),
                    "content": get_key(event, 'description')
                }
                values, raw_datas = generate_sql_datafields(datas)
                cur.execute("INSERT INTO events " + values, raw_datas)
    conn.commit()
    conn.close()

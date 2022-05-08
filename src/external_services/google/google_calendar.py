from datetime import datetime, timedelta, timezone
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from .google_auth import build_credentials
from ..common import get_database_connection
from utils import list_to_dict, select_to_dict_list, generate_sql_datafields, get_key


def get_calendar(cal_api, calendar_id, updated_min=None):
    if updated_min:
        arg = {"updatedMin": updated_min}
    else:
        arg = {}
    events = []
    page_token = None
    while True:
        calendar_content = cal_api.events().list(calendarId=calendar_id,
                                                 pageToken=page_token,
                                                 maxResults=9999,
                                                 showDeleted=True,
                                                 **arg).execute()
        events += calendar_content["items"]
        page_token = get_key(calendar_content, "nextPageToken", None)
        if not page_token:
            break

    return events


def google_startend_datetime(date_time_dict):
    whole_datetime = ""
    if "date" in date_time_dict.keys():
        whole_datetime = whole_datetime + date_time_dict["date"] + " "
    if "dateTime" in date_time_dict.keys():
        whole_datetime = whole_datetime + date_time_dict["dateTime"]
    return whole_datetime


def store_event(db_conn, event, cal_id):
    datas = {
        "cal_id": cal_id,
        "original_id": get_key(event, "iCalUID", "NULL"),
        "created": get_key(event, 'created'),
        "updated": get_key(event, 'updated'),
        "dt_start": google_startend_datetime(get_key(event, 'start', {})),
        "dt_end": google_startend_datetime(get_key(event, 'end', {})),
        "summary": get_key(event, 'summary'),
        "content": get_key(event, 'description'),
        "recurrence": "\n".join(get_key(event, 'recurrence')),
        "deleted": "1" if get_key(event, 'status', "") == "cancelled" else "0"
    }
    values, raw_datas = generate_sql_datafields(datas)
    db_conn.execute("REPLACE INTO events " + values, raw_datas)


def store_calendars():
    conn = get_database_connection()
    cur = conn.cursor()

    now_iso = datetime.now(timezone.utc).isoformat()
    existing_cals = select_to_dict_list(cur.execute("SELECT * FROM calendars").fetchall())
    cals_by_id = list_to_dict(existing_cals, "external_id")
    cal_api = googleapiclient.discovery.build('calendar', 'v3', credentials=build_credentials())
    calendar_list = cal_api.calendarList().list(showHidden=True).execute()
    for calendar in calendar_list["items"]:
        id_in_db = None
        if calendar["id"] not in cals_by_id.keys():
            cur.execute("INSERT INTO calendars (external_id, title) VALUES (?, ?)", (calendar["id"], calendar["summary"]))
            existing_cals = select_to_dict_list(cur.execute("SELECT * FROM calendars").fetchall())
            cals_by_id = list_to_dict(existing_cals, "external_id")
            id_in_db = cals_by_id[calendar["id"]]["id"]
            events = get_calendar(cal_api, calendar["id"])
            for event in events:
                if "recurringEventId" in event.keys():
                    continue
                store_event(cur, event, id_in_db)
        else:
            id_in_db = cals_by_id[calendar["id"]]["id"]
            last_time_updated = get_key(cals_by_id[calendar["id"]], "updated", None)
            last_time_updated = datetime.fromisoformat(last_time_updated) - timedelta(minutes=30)
            last_time_updated = last_time_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                events = get_calendar(cal_api, calendar["id"], updated_min=last_time_updated)
                for event in events:
                    if "recurringEventId" in event.keys():
                        continue
                    store_event(cur, event, id_in_db)
            except HttpError as err:
                if err.resp.status == 410:
                    events = get_calendar(cal_api, calendar["id"])
                    for event in events:
                        if "recurringEventId" in event.keys():
                            continue
                        store_event(cur, event, id_in_db)
                else:
                    raise
        cur.execute(f"UPDATE calendars SET updated = '{now_iso}' WHERE id = {id_in_db}").fetchall()
    conn.commit()
    conn.close()

from datetime import date, datetime
from icalendar import Calendar, Event
import recurring_ical_events
import re
import pytz
from copy import deepcopy

"""
Refere to https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html
for more advanced details about how ics rules works.
"""


def str_date_or_datetime(time_str):
    datetime_elt = time_str.replace(" ", "")
    if len(datetime_elt) > 10:
        if "-" not in time_str:
            datetime_elt = datetime.strptime(time_str.replace("Z", ""), "%Y%m%dT%H%M%S")
        else:
            datetime_elt = datetime.fromisoformat(datetime_elt)
    else:
        if "-" not in time_str:
            datetime_elt = datetime.strptime(time_str, "%Y%m%d")
        else:
            datetime_elt = datetime.combine(date.fromisoformat(datetime_elt), datetime.min.time())
    datetime_elt = datetime_elt.replace(tzinfo=pytz.UTC)
    return datetime_elt


def get_recurring_events(initiator_events, period_start, period_end):
    events_by_id = {event["id"]: event for event in initiator_events}
    calendar = Calendar()
    instanced_events = []
    for event in initiator_events:
        event_obj = Event()
        for line in event["recurrence"].split("\n"):
            parts = re.split(";|:", line)
            props = {}
            for prop in parts[1:]:
                if "=" in prop:
                    value = prop.split("=")[1]
                    if "," in value:
                        value = value.split(",")
                    props[prop.split("=")[0]] = value
                else:
                    props = [str_date_or_datetime(date) for date in prop.split(",")]
                if prop.split("=")[0] == 'UNTIL':
                    props[prop.split("=")[0]] = str_date_or_datetime(prop.split("=")[1])
            event_obj.add(parts[0], props)

        event_obj["ID"] = event["id"]
        event_obj.add('dtstart', str_date_or_datetime(event["dt_start"]))
        event_obj.add('dtend', str_date_or_datetime(event["dt_end"]))
        calendar.add_component(event_obj)
    events_in_period = recurring_ical_events.of(calendar).between(period_start, period_end)
    for event in events_in_period:
        start = event["dtstart"].dt
        end = event["dtend"].dt
        id = event["ID"]
        new_event = deepcopy(events_by_id[id])
        new_event["dt_start"] = start.isoformat()
        new_event["dt_end"] = end.isoformat()
        instanced_events.append(new_event)
    return instanced_events

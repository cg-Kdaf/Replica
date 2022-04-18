from datetime import datetime, timedelta

wanted_params = ["DTSTART",
                 "DTEND",
                 "SUMMARY",
                 "RRULE",
                 "EXDATE",
                 "BEGIN:VEVENT",
                 "END:VEVENT"]
dates_lines = ["DTSTART",
               "DTEND",
               "EXDATE"]
needed_params = ["DTSTART",
                 "DTEND",
                 "SUMMARY"]


def get_event_from_text(file_path):
    '''Get events upcomming from a ics textfile'''

    events = []
    in_event = False
    event_index = -1
    calendar_file = open(file_path, "r").readlines()

    def str_to_datetime(date_str):
        datetime_time = None
        if len(date_str) > 10:  # parsing datetime like 20191031T225959(Z)
            datetime_time = datetime(int(date_str[:4]),  # Year
                                     int(date_str[4:6]),  # Month
                                     int(date_str[6:8]),  # Day
                                     int(date_str[9:11]),  # Hour
                                     int(date_str[11:13]),  # Minute
                                     int(date_str[13:15]))  # Second
            if "Z" in date_str:
                datetime_time += timedelta(hours=2)
        else:  # parsing datetime like 20191031
            datetime_time = datetime(int(date_str[:4]),  # Year
                                     int(date_str[4:6]),  # Month
                                     int(date_str[6:8]),  # Day
                                     0,
                                     0,
                                     0)
        return(datetime_time)

    # ||| Parsing Calendar and create all events, no matter if they're from past ||||
    for line in calendar_file:
        if "BEGIN:VEVENT" in line:  # Create new event when begin detected
            events.append({})  # Create the new event
            event_index += 1  # Increse index for each event
            in_event = True  # Used to know if the line is part of the event
            continue

        if not in_event:  # Go next line if not in event
            continue

        # If line is not valid, or start with a space, go next line
        line = line.replace("\n", '')
        if ":" not in line:
            continue

        if not any(x in line for x in wanted_params):
            # Go next line if word detected, used to hide unwanted props
            continue

        # Split line with attribute name and attribute value
        terms = line.split(":")
        is_summary = terms[0] == 'SUMMARY'

        if terms[1] in [' ', '']:
            if is_summary:
                events.pop()
                event_index -= 1
                in_event = False
            continue

        if ";" in terms[0]:
            terms[0] = terms[0].split(";")[0]

        if "=" in terms[1] and not is_summary:
            value_new = {}
            for elt in terms[1].split(';'):
                key, value = elt.split('=')
                if len(value) in [8, 15, 16]:
                    value = str_to_datetime(value)
                value_new[key] = value
            terms[1] = value_new

        if "END:VEVENT" in line:  # Finalize event when end reached
            if any(x not in events[event_index].keys() for x in needed_params):
                events.pop()
                event_index -= 1
            in_event = False
            continue

        if any(x in terms[0] for x in dates_lines):
            terms[1] = str_to_datetime(terms[1])

        if terms[0] in events[event_index].keys():
            if not isinstance(events[event_index][terms[0]], list):
                content = events[event_index][terms[0]]
                events[event_index][terms[0]] = []
                events[event_index][terms[0]].append(content)
            events[event_index][terms[0]].append(terms[1])
        else:
            events[event_index][terms[0]] = terms[1]
    return events

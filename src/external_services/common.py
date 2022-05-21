from os import path
import json

from utils import select_to_dict_list

CREDENTIAL_DIR = "credentials"
SERVICES_DIR = "service_keys"

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

__credential_path = path.join(path.curdir, "../"+CREDENTIAL_DIR)
__service_key_path = path.join(path.curdir, "../"+SERVICES_DIR)


def get_credentials(service_name):
    if path.exists(path.join(__credential_path, service_name+".json")):
        with open(path.join(__credential_path, service_name+".json"), "r") as file:
            return json.load(file)
    return {}


def store_credentials(service_name, data):
    credentials = get_credentials(service_name)
    data = {**credentials, **data}
    with open(path.join(__credential_path, service_name+".json"), "w") as file:
        json.dump(data, file)


def get_service_keys(service_name):
    if path.exists(path.join(__service_key_path, service_name+".json")):
        with open(path.join(__service_key_path, service_name+".json"), "r") as file:
            return json.load(file)
    return {}


def poll_calendar(cur, cal_name):
    command = f"SELECT id from calendars WHERE original_title = '{cal_name}'"
    rows = select_to_dict_list(cur.execute(command).fetchall())
    if rows == []:
        return False
    else:
        return rows[0]["id"]

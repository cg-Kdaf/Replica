from os import path
import json
import sqlite3

CREDENTIAL_DIR = "credentials"
SERVICES_DIR = "service_keys"
DATABASE_FILE = "database.db"

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
    with open(path.join(__credential_path, service_name+".json"), "w") as file:
        json.dump(data, file)


def get_service_keys(service_name):
    if path.exists(path.join(__service_key_path, service_name+".json")):
        with open(path.join(__service_key_path, service_name+".json"), "r") as file:
            return json.load(file)
    return {}


def get_database_connection():
    conn = sqlite3.connect(path.join(path.curdir, DATABASE_FILE))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

from os import path
import sqlite3
from utils import select_to_dict_list

DATABASE_FILE = "database.db"


def get_database_connection():
    conn = sqlite3.connect(path.join(path.curdir, DATABASE_FILE))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def sql_select(conn, request):
    """Get the result of the request as a list of dicts

    Args:
        conn (Object): Sql connection/cursor object
        request (str): Request string

    Returns:
        list: list of selected rows
    """
    return select_to_dict_list(conn.execute(request).fetchall())


def generate_sql_datafields(data_dict):
    """Return a string for the sql command and a tuple for the sql datas

    Args:
        data_dict (dict)

    Returns:
        tuple: ("(datakey1, datakey2, ...) VALUES (?, ?, ...)", (data1, data2, ...))
    """
    key_names = "(" + "".join([key + "," for key in data_dict.keys()])[:-1] + ")"
    values = "(" + ("?,"*len(data_dict.keys()))[:-1] + ")"
    return "".join(key_names + " VALUES " + values), tuple(data_dict[key] for key in data_dict.keys())


def generate_sql_datafields_multiple(data_list):
    """Return a string for the sql command and a tuple of tuples for the sql datas

    Args:
        data_list (list of dict)

    Returns:
        tuple: ( "(datakey1, datakey2, ...) VALUES (?, ?, ...)",
                    ((data1, data2, ...), (data1, data2, ...), ...) )
    """
    key_names = "(" + "".join([key + "," for key in data_list[0].keys()])[:-1] + ")"
    values = "(" + ("?,"*len(data_list[0].keys()))[:-1] + ")"
    return "".join(key_names + " VALUES " + values), tuple(tuple(data.values()) for data in data_list)

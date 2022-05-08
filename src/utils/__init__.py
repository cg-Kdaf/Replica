

def select_to_dict_list(selection):
    """Get the content returned by a sql request and transform it to a list of dicts

    Args:
        selection (sql3lite rows) : selected rows

    Returns:
        list: list of selected rows
    """
    list_ = []
    if len(selection) == 0:
        return list_
    keys = selection[0].keys()
    for row in selection:
        list_.append({key: row[key] for key in keys})
    return list_


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


def get_key(dict_, key, default=""):
    if key in dict_.keys():
        return dict_[key]
    else:
        return default


def list_to_dict(list_of_dict, key):
    return {dict_[key]: dict_ for dict_ in list_of_dict}

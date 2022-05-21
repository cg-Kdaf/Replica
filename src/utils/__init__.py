

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


def get_key(dict_, key, default=""):
    if key in dict_.keys():
        return dict_[key]
    else:
        return default


def list_to_dict(list_of_dict, key):
    return {dict_[key]: dict_ for dict_ in list_of_dict}

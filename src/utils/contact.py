from utils.database import generate_sql_datafields


def store_contact(conn, **args):
    cur = conn.cursor()
    datas = args
    values, raw_datas = generate_sql_datafields(datas)
    cur.execute("INSERT INTO contacts " + values, raw_datas)
    return cur.lastrowid

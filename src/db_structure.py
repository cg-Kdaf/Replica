import sqlite3

connection = sqlite3.connect('database.db')
schema = connection.execute("SELECT * FROM sqlite_master;").fetchall()
if schema != []:
    schema_str = [sc[-1] for sc in schema if sc[-1] != None]
    schema_str = "".join([sc+";\n" if "sqlite_sequence" not in sc else "" for sc in schema_str])
    with open('schema.sql', "w") as f:
        f.write(schema_str)
else:
    with open('schema.sql', "r") as f:
        connection.executescript(f.read())


connection.commit()
connection.close()

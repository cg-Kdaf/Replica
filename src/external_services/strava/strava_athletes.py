from utils.database import sql_select
from utils.contact import store_contact


def people_contact_from_athlete(conn, id):
    athlete = sql_select(conn, f"SELECT * FROM strava_athletes WHERE id={id}")[0]
    contact_id = store_contact(
        conn,
        first_name=athlete["firstname"].title(),
        last_name=athlete["lastname"].title(),
        picture=athlete["picture_medium"]
    )
    conn.execute(f"UPDATE strava_athletes SET contact_id = '{contact_id}' WHERE id = {id}")
    conn.commit()

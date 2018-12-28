import database
import sqlite3
def add_pikapoints(user_id, points):
    conn = sqlite3.connect('pikapoints.db')
    if(conn is not None):
        database.add_pikapoints_query(conn, user_id, points)
        conn.close()

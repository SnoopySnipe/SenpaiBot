import database
import sqlite3
db = 'foo.db'
def initialize(server_name):
    db = server_name + '.db'
    conn = sqlite3.connect(db)
    database.initialize(conn)
    conn.close()
def add_pikapoints(user_id, points):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.add_pikapoints_query(conn, user_id, points)
        conn.close()

def get_pikapoints(user_id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_pikapoints_query(conn, user_id)
        if(result is not None):
            result = result[0]
        conn.close()
        return result

def get_pikalogue():
    conn = sqlite3.connect(db)
    if(conn is not None):
        result = database.get_pikalogue(conn)
        conn.close()
        return result

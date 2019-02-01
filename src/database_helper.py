import database
import sqlite3
def initialize(server_name):
    global db
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

def get_pity(user_id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_pity(conn, user_id)
        conn.close()
        return result

def get_focus():
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_focus(conn)
        conn.close()
        return result

def get_user_details(user_id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_user_details(conn, user_id)
        conn.close()
        return result

def get_roll(roll):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_roll(conn, roll)
        conn.close()
        return result

def adjust_pity(user_id, got_five=None):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.adjust_pikapity(conn, user_id, got_five)
        conn.close()

def adjust_points(user_id):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.adjust_points(conn, user_id)
        conn.close()

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

def get_focus(region):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_focus(conn, region)
        conn.close()
        return result

def get_user_details(user_id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_user_details(conn, user_id)
        conn.close()
        return result

def get_roll(roll, region=None):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_roll(conn, roll, region)
        conn.close()
        return result

def get_units(region):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_units(conn, region)
        conn.close()
        return result

def adjust_pity(user_id, got_five=None):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.adjust_pikapity(conn, user_id, got_five)
        conn.close()

def adjust_points(user_id, points):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.adjust_points(conn, user_id, points)
        conn.close()

def get_inventory(user_id, region=None):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_inventory(conn, user_id, region)
        conn.close()
        return result

def get_from_inventory(user_id, poke_id):
    conn = sqlite3.connect(db)
    result = False
    if(conn is not None):
        if len(database.get_from_inventory(conn, user_id, poke_id)) > 0:
            result = True
        conn.close()
    return result

def add_inventory(user_id, poke_id):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.add_inventory(conn, user_id, poke_id)
        conn.close()

def get_pokemon(name):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_pokemon(conn, name)
        conn.close()
        return result

def remove_inventory(user_id, poke_id):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.remove_inventory(conn, user_id, poke_id)
        conn.close()

def change_focus(*args):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.change_focus(conn, *args)
        conn.close()

def run_sql(query):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.run_sql(conn, query)
        conn.close()

def full_remove_inventory(user_id, rarity, region=None):
    conn = sqlite3.connect(db)
    if (conn is not None):
        return database.full_remove_inventory(conn, user_id, rarity, region)
        conn.close()

def remove_dupes(user_id, rarity, region=None):
    conn = sqlite3.connect(db)
    if (conn is not None):
        return database.remove_dupes(conn, user_id, rarity, region)
        conn.close()

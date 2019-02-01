import sqlite3
from sqlite3 import Error
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def add_pikapoints_query(conn, user_id, points):
    try:
        c = conn.cursor()
        sql_insert_new_balance="""INSERT OR IGNORE INTO pikapoints VALUES ($user_id, $points);"""
        sql_update_balance="""UPDATE pikapoints SET points = points + $points WHERE id=$user_id;"""
        placeholders = {"user_id":user_id, "points": points}
        c.execute(sql_insert_new_balance, placeholders)
        c.execute(sql_update_balance, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_pikapoints_query(conn, user_id):
    try:
        c = conn.cursor()
        sql_select_balance = """SELECT points FROM pikapoints WHERE id=$user_id"""
        placeholders = {"user_id":user_id}
        c.execute(sql_select_balance, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def adjust_pikapity(conn, user_id, got_five=None):
    try:
        c = conn.cursor()
        if got_five is None:
            sql_setup_pikapity = """INSERT OR IGNORE INTO pikapity(id, three, four, five, focus) VALUES($user_id, 400, 500, 40, 60);"""
            placeholders = {"user_id": user_id}
            c.execute(sql_setup_pikapity, placeholders)
        elif (got_five == True):
            sql_update_pikapity = """UPDATE pikapity SET focus = 60, five = 40, four = 500, three = 400 WHERE id=$user_id;"""
            placeholders = {"user_id": user_id}
            c.execute(sql_update_pikapity, placeholders)
        else:
            sql_update_pikapity = """UPDATE pikapity SET focus = focus + 10, five = five + 5, four = four - 5, three = three - 10 WHERE id=$user_id;"""
            placeholders = {"user_id": user_id}
            c.execute(sql_update_pikapity, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def setup_pikagacha(conn, id, name, rarity, focus):
    try:
        c = conn.cursor()
        sql_setup_pikagacha = """REPLACE INTO pikagacha(id, name, rarity, focus) VALUES($id, $name, $rarity, $focus)"""
        placeholders = {"id": id, "name": name, "rarity": rarity, "focus": focus}
        c.execute(sql_setup_pikagacha, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_pity(conn, user_id):
    try:
        c = conn.cursor()
        sql_get_pity = """SELECT three, four, five, focus FROM pikapity WHERE id=$user_id"""
        placeholders = {"user_id": user_id}
        c.execute(sql_get_pity, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def get_focus(conn):
    try:
        c = conn.cursor()
        sql_get_focus = """SELECT name FROM pikagacha WHERE focus=1"""
        c.execute(sql_get_focus)
        return c.fetchall()
    except Error as e:
        print(e)

def get_user_details(conn, user_id):
    try:
        c = conn.cursor()
        sql_get_user_details = """SELECT points, three, four, five, focus FROM pikapoints INNER JOIN pikapity ON pikapoints.id = pikapity.id WHERE pikapoints.id = $user_id"""
        placeholders = {"user_id": user_id}
        c.execute(sql_get_user_details, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def adjust_points(conn, user_id):
    try:
        c = conn.cursor()
        sql_update_points = """UPDATE pikapoints SET points = points - 1 WHERE id = $user_id"""
        placeholders = {"user_id": user_id}
        c.execute(sql_update_points, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_roll(conn, roll):
    try:
        c = conn.cursor()
        if roll == 1:
            sql = """SELECT name FROM pikagacha WHERE focus = 1"""
        else:
            sql = """SELECT name FROM pikagacha WHERE rarity = $roll"""
        placeholders = {"roll": roll}
        c.execute(sql, placeholders)
        return c.fetchall()
    except Error as e:
        print(e)

sql_create_pikapoints_table = """CREATE TABLE IF NOT EXISTS pikapoints (
                                    id integer PRIMARY KEY,
                                    points integer DEFAULT 0)"""
sql_create_pikagacha_table = """CREATE TABLE IF NOT EXISTS pikagacha (id integer PRIMARY KEY, name text NOT NULL UNIQUE, rarity integer NOT NULL, focus integer NOT NULL)"""
sql_create_pikapity_table = """CREATE TABLE IF NOT EXISTS pikapity (id integer PRIMARY KEY, three integer NOT NULL, four integer NOT NULL, five integer NOT NULL, focus integer NOT NULL)"""

def initialize(conn):
    create_table(conn, sql_create_pikapoints_table)
    create_table(conn, sql_create_pikagacha_table)
    create_table(conn, sql_create_pikapity_table)

    pokemon = {
        0: ("Magikarp", 3, 0),
        1: ("Eevee", 4, 0),
        2: ("Pikachu", 5, 1),
        3: ("Dragonite", 5, 1),
        4: ("Charizard", 5, 0)
    }
    for key in pokemon:
        setup_pikagacha(conn, key, pokemon[key][0], pokemon[key][1], pokemon[key][2])

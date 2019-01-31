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

def setup_pikalogue(conn, id, name, description, price):
    try:
        c = conn.cursor()
        sql_setup_pikalogue = """REPLACE INTO pikalogue(id, name, description, price) VALUES($id, $name, $description, $price)"""
        placeholders = {"id": id, "name": name, "description": description, "price": price}
        c.execute(sql_setup_pikalogue, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_pikalogue(conn):
    try:
        c = conn.cursor()
        sql_get_pikalogue = """SELECT * FROM pikalogue"""
        c.execute(sql_get_pikalogue)
        return c.fetchall()
    except Error as e:
        print(e)

sql_create_pikapoints_table = """CREATE TABLE IF NOT EXISTS pikapoints (
                                    id integer PRIMARY KEY,
                                    points integer DEFAULT 0)"""
sql_create_pikalogue_table = """CREATE TABLE IF NOT EXISTS pikalogue (id integer PRIMARY KEY, name text NOT NULL UNIQUE, description text NOT NULL, price integer NOT NULL)"""

def initialize(conn):
    create_table(conn, sql_create_pikapoints_table)
    create_table(conn, sql_create_pikalogue_table)

    pikalogue = {
        0: ("Pikakicket", "You're going to use this on Wesley aren't you?", 500000)
        }
    for key in pikalogue:
        setup_pikalogue(conn, key, pikalogue[key][0], pikalogue[key][1], pikalogue[key][2])

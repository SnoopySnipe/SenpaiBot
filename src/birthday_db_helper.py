import sqlite3
from sqlite3 import Error

def initialize():
    global bdb
    bdb = 'birthdays.db'
    conn = sqlite3.connect(bdb)
    try:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS birthdays (
                                            id CHAR(50) PRIMARY KEY,
                                            mm integer DEFAULT 0,
                                            dd integer DEFAULT 0)""")
    except Error as e:
        print(e)
    conn.close()

def add(id, mm, dd):
    conn = sqlite3.connect(bdb)
    if(conn is not None):
        try:
            c = conn.cursor()
            sql_insert_new_birthday="""INSERT OR IGNORE INTO birthdays (id, mm, dd) VALUES ($id, $mm, $dd);"""
            placeholders = {"id":id, "mm": mm, "dd": dd}
            c.execute(sql_insert_new_birthday, placeholders)
            conn.commit()
        except Error as e:
            print(e)
        conn.close()

def delete(id):
    conn = sqlite3.connect(bdb)
    if(conn is not None):
        try:
            c = conn.cursor()
            sql_del_birthday="""DELETE FROM birthdays WHERE id=$id;"""
            placeholders = {"id":id}
            c.execute(sql_del_birthday, placeholders)
            conn.commit()
        except Error as e:
            print(e)
        conn.close()

def list():
    conn = sqlite3.connect(bdb)
    if(conn is not None):
        try:
            c = conn.cursor()
            sql_all_birthday="""SELECT * FROM birthdays ORDER BY mm, dd;"""
            c.execute(sql_all_birthday)
            return c.fetchall()
        except Error as e:
            print(e)
        conn.close()

def get_today_birthdays(mm,dd):
    conn = sqlite3.connect(bdb)
    if(conn is not None):
        try:
            c = conn.cursor()
            sql_today_birthday="""SELECT * FROM birthdays WHERE mm=$mm AND dd=$dd;"""
            placeholders = {"mm":mm, "dd":dd}
            c.execute(sql_today_birthday, placeholders)
            return c.fetchall()
        except Error as e:
            print(e)
        conn.close()

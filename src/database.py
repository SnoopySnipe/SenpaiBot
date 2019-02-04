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
            sql_setup_pikapity = """INSERT OR IGNORE INTO pikapity(id, three, four, five, focus) VALUES($user_id, 540, 420, 10, 30);"""
            placeholders = {"user_id": user_id}
            c.execute(sql_setup_pikapity, placeholders)
        elif (got_five == True):
            sql_update_pikapity = """UPDATE pikapity SET focus = 30, five = 10, four = 420, three = 540 WHERE id=$user_id;"""
            placeholders = {"user_id": user_id}
            c.execute(sql_update_pikapity, placeholders)
        else:
            sql_update_pikapity = """UPDATE pikapity SET focus = focus + 5, five = five + 5, four = four - 5, three = three - 5 WHERE id=$user_id;"""
            placeholders = {"user_id": user_id}
            c.execute(sql_update_pikapity, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def setup_pikagacha(conn, id, name, rarity, focus):
    try:
        c = conn.cursor()
        sql_setup_pikagacha = """INSERT OR IGNORE INTO pikagacha(id, name, rarity, focus) VALUES($id, $name, $rarity, $focus)"""
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

def get_focus(conn, region):
    try:
        c = conn.cursor()
        sql_get_focus = """SELECT name FROM pikagacha WHERE focus = 1 AND id BETWEEN $low AND $high"""
        placeholders = {"low": region[1], "high": region[2]}
        c.execute(sql_get_focus, placeholders)
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

def adjust_points(conn, user_id, points):
    try:
        c = conn.cursor()
        sql_update_points = """UPDATE pikapoints SET points = points + $points WHERE id = $user_id"""
        placeholders = {"user_id": user_id, "points": points}
        c.execute(sql_update_points, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_roll(conn, roll, region=None):
    try:
        c = conn.cursor()
        if region is None:
            if roll == 1:
                sql = """SELECT name, id, rarity FROM pikagacha WHERE focus = 1"""
            else:
                sql = """SELECT name, id, rarity FROM pikagacha WHERE rarity = $roll AND focus = 0"""
            placeholders = {"roll": roll}
        else:
            if roll == 1:
                sql = """SELECT name, id, rarity FROM pikagacha WHERE focus = 1 AND id BETWEEN $low AND $high"""
            else:
                sql = """SELECT name, id, rarity FROM pikagacha WHERE rarity = $roll AND focus = 0 AND id BETWEEN $low AND $high"""
            placeholders = {"roll": roll, "low": region[1], "high": region[2]}
        c.execute(sql, placeholders)
        return c.fetchall()
    except Error as e:
        print(e)

def get_units(conn, region):
    try:
        c = conn.cursor()
        sql = """SELECT name, rarity, focus FROM pikagacha WHERE id BETWEEN $low AND $high"""
        placeholders = {"low": region[1], "high": region[2]}
        c.execute(sql, placeholders)
        return c.fetchall()
    except Error as e:
        print(e)

def get_inventory(conn, user_id, region=None):
    try:
        c = conn.cursor()
        if region is not None:
            sql = """SELECT DISTINCT * FROM (SELECT user_id, poke_id, name, rarity, count(*) FROM inventory INNER JOIN pikagacha ON inventory.poke_id = pikagacha.id WHERE inventory.user_id = $user_id AND pikagacha.id BETWEEN $low AND $high GROUP BY user_id, poke_id, name, rarity ORDER BY rarity DESC, poke_id ASC)"""
            placeholders = {"user_id": user_id, "low": region[1], "high": region[2]}
            c.execute(sql, placeholders)
        else:
            sql = """SELECT DISTINCT * FROM (SELECT user_id, poke_id, name, rarity, count(*) FROM inventory INNER JOIN pikagacha ON inventory.poke_id = pikagacha.id WHERE inventory.user_id = $user_id GROUP BY user_id, poke_id, name, rarity ORDER BY rarity DESC, poke_id ASC)"""
            placeholders = {"user_id": user_id}
            c.execute(sql, placeholders)
        return c.fetchall()
    except Error as e:
        print(e)

def add_inventory(conn, user_id, poke_id):
    try:
        c = conn.cursor()
        sql = """INSERT INTO inventory(user_id, poke_id) VALUES($user_id, $poke_id)"""
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_pokemon(conn, name):
    try:
        c = conn.cursor()
        sql = """SELECT id, rarity FROM pikagacha WHERE name = $name"""
        placeholders = {"name": name}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def remove_inventory(conn, user_id, poke_id):
    try:
        c = conn.cursor()
        sql = """DELETE FROM inventory WHERE user_id = $user_id AND poke_id = $poke_id LIMIT 1"""
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_from_inventory(conn, user_id, poke_id):
    try:
        c = conn.cursor()
        sql = """SELECT * FROM inventory WHERE user_id = $user_id AND poke_id = $poke_id"""
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        c.execute(sql, placeholders)
        return c.fetchall()
    except Error as e:
        print(e)

def change_focus(conn, *args):
    try:
        c = conn.cursor()
        sql1 = """UPDATE pikagacha SET focus = 0;"""
        c.execute(sql1)
        for poke in args:
            sql2 = """UPDATE pikagacha SET focus = 1 WHERE name = $poke"""
            placeholders = {"poke": poke}
            c.execute(sql2, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def run_sql(conn, query):
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)


sql_create_pikapoints_table = """CREATE TABLE IF NOT EXISTS pikapoints (
                                    id integer PRIMARY KEY,
                                    points integer DEFAULT 0)"""
sql_create_pikagacha_table = """CREATE TABLE IF NOT EXISTS pikagacha (id integer PRIMARY KEY, name text NOT NULL UNIQUE, rarity integer NOT NULL, focus integer NOT NULL)"""
sql_create_pikapity_table = """CREATE TABLE IF NOT EXISTS pikapity (id integer PRIMARY KEY, three integer NOT NULL, four integer NOT NULL, five integer NOT NULL, focus integer NOT NULL)"""
sql_create_inventory = """CREATE TABLE IF NOT EXISTS inventory (user_id integer NOT NULL, poke_id integer NOT NULL, inventory_id integer PRIMARY KEY)"""

def load_pikadata(path):
    data = {}
    with open(path, mode='r') as file:
        for line in file:
            line_data = line.split("\t")
            data[int(line_data[0])] = (line_data[1], int(line_data[2]), int(line_data[3]))
    return data

def initialize(conn):
    create_table(conn, sql_create_pikapoints_table)
    create_table(conn, sql_create_pikagacha_table)
    create_table(conn, sql_create_pikapity_table)
    create_table(conn, sql_create_inventory)

    #c = conn.cursor()
    #c.execute("UPDATE pikapoints SET points = 150")
    #c.execute("UPDATE pikapity SET focus = 30, five = 10, four = 420, three = 540")
    #c.execute("DELETE FROM inventory")
    #conn.commit()

    pokemon = load_pikadata('pokedata.csv')
    for key in pokemon:
        setup_pikagacha(conn, key, pokemon[key][0], pokemon[key][1], pokemon[key][2])

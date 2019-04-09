import sqlite3
from sqlite3 import Error
import math
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def add_pikapoints_query(conn, user_id, points):
    try:
        c = conn.cursor()
        sql_insert_new_balance="""INSERT OR IGNORE INTO pikapoints (id, points) VALUES ($user_id, $points);"""
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

def get_savings(conn, user_id):
    try:
        c = conn.cursor()
        sql_select_balance = """SELECT points FROM bank WHERE id=$user_id"""
        placeholders = {"user_id":user_id}
        c.execute(sql_select_balance, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def adjust_pikapity(conn, user_id, got_five=None):
    try:
        c = conn.cursor()
        if got_five is None:
            sql_setup_pikapity = """INSERT OR IGNORE INTO pikapity(id, three, four, five, focus) VALUES($user_id, 540, 420, 30, 10);"""
            placeholders = {"user_id": user_id}
            c.execute(sql_setup_pikapity, placeholders)
        elif (got_five == True):
            sql_update_pikapity = """UPDATE pikapity SET focus = 10, five = 30, four = 420, three = 540 WHERE id=$user_id;"""
            placeholders = {"user_id": user_id}
            c.execute(sql_update_pikapity, placeholders)
        else:
            sql_update_pikapity = """UPDATE pikapity SET focus = focus + 5, five = five + 5, four = four - 5, three = three - 5 WHERE id=$user_id;"""
            placeholders = {"user_id": user_id}
            c.execute(sql_update_pikapity, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def setup_pikagacha(conn, id, name, rarity, focus, bst):
    try:
        c = conn.cursor()
        sql_setup_pikagacha = """INSERT OR IGNORE INTO pikagacha(id, name, rarity, focus, bst) VALUES($id, $name, $rarity, $focus, $bst)"""
        placeholders = {"id": id, "name": name, "rarity": rarity, "focus": focus, "bst": bst}
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

def adjust_savings(conn, user_id, points):
    try:
        c = conn.cursor()
        sql_insert_new_balance = """INSERT OR IGNORE INTO bank (id) VALUES ($user_id)"""
        sql_update_points = """UPDATE bank SET points = points + $points WHERE id = $user_id"""
        placeholders = {"user_id": user_id, "points": points}
        c.execute(sql_insert_new_balance, placeholders)
        c.execute(sql_update_points, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_roll(conn, roll, region=None):
    try:
        c = conn.cursor()
        if roll == 8:
            sql = """SELECT name, id, rarity FROM pikagacha WHERE rarity = $roll AND active = 1"""
            placeholders = {"roll": roll}
        elif region is None:
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
        sql = """SELECT name, rarity, focus, active FROM pikagacha WHERE id BETWEEN $low AND $high"""
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

def get_box(conn, user_id):
    try:
        c = conn.cursor()
        sql = """SELECT inventory.poke_id, pikagacha.rarity FROM inventory INNER JOIN pikagacha ON inventory.poke_id = pikagacha.id WHERE inventory.user_id = $user_id ORDER BY pikagacha.rarity DESC, inventory.poke_id ASC"""
        placeholders = {"user_id": user_id}
        c.execute(sql, placeholders)
        return c.fetchall()
    except Error as e:
        print(e)

def get_poke_count(conn, user_id, poke_id):
    try:
        c = conn.cursor()
        sql = """SELECT count(*) FROM inventory WHERE user_id = $user_id AND poke_id = $poke_id"""
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def get_bag(conn, user_id):
    try:
        c = conn.cursor()
        sql = """SELECT DISTINCT ball, count(ball) FROM bag WHERE user_id = $user_id GROUP BY ball ORDER BY ball ASC"""
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

def add_item(conn, user_id, item_id):
    try:
        c = conn.cursor()
        sql = """INSERT INTO bag(user_id, ball) VALUES($user_id, $item_id)"""
        placeholders = {"user_id": user_id, "item_id": item_id}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_pokemon(conn, name):
    try:
        c = conn.cursor()
        sql = """SELECT id, rarity, bst FROM pikagacha WHERE name = $name"""
        placeholders = {"name": name}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def get_pokemon_name(conn, id):
    try:
        c = conn.cursor()
        sql = """SELECT name, bst FROM pikagacha WHERE id = $id"""
        placeholders = {"id": id}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def add_fav(conn, user_id, poke_id):
    try:
        c = conn.cursor()
        sql = """INSERT INTO favs (user_id, poke_id) VALUES ($user_id, $poke_id)"""
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def del_fav(conn, user_id, poke_id):
    try:
        c = conn.cursor()
        sql = """DELETE FROM favs WHERE user_id = $user_id AND poke_id = $poke_id"""
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def del_all_favs(conn, user_id):
    try:
        c = conn.cursor()
        sql = """DELETE FROM favs WHERE user_id = $user_id"""
        placeholders = {"user_id": user_id}
        c.execute(sql, placeholders)
        conn.commit()
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

def full_remove_inventory(conn, user_id, rarity, region=None):
    try:
        c = conn.cursor()
        if region is None:
            sql = """DELETE FROM inventory WHERE user_id = $user_id AND poke_id IN (SELECT id FROM pikagacha WHERE rarity = $rarity) AND poke_id NOT IN (SELECT poke_id FROM favs WHERE user_id = $user_id)"""
            placeholders = {"user_id": user_id, "rarity": rarity}
        else:
            sql = """DELETE FROM inventory WHERE user_id = $user_id AND poke_id IN (SELECT id FROM pikagacha WHERE rarity = $rarity AND id BETWEEN $low AND $high) AND poke_id NOT IN (SELECT poke_id FROM favs WHERE user_id = $user_id)"""
            placeholders = {"user_id": user_id, "rarity": rarity, "low": region[1], "high": region[2]}
        rows = c.execute(sql, placeholders).rowcount
        conn.commit()
        return rows
    except Error as e:
        print(e)

def fullrelease_pokemon(conn, user_id, poke_id):
    try:
        c = conn.cursor()
        sql = """DELETE FROM inventory WHERE user_id = $user_id AND poke_id = $poke_id"""
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        rows = c.execute(sql, placeholders).rowcount
        conn.commit()
        return rows
    except Error as e:
        print(e)

def limitrelease_pokemon(conn, user_id, poke_id, limit):
    try:
        limit = str(limit)
        c = conn.cursor()
        sql = """DELETE FROM inventory WHERE user_id = $user_id AND poke_id = $poke_id LIMIT """ + limit
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        rows = c.execute(sql, placeholders).rowcount
        conn.commit()
        return rows
    except Error as e:
        print(e)

def releasedupes_pokemon(conn, user_id, poke_id):
    try:
        c = conn.cursor()
        sql = """DELETE FROM inventory WHERE inventory_id IN (SELECT inventory_id FROM inventory LEFT JOIN (SELECT MIN(inventory_id) as inv_id, user_id, poke_id FROM inventory GROUP BY user_id, poke_id) as KeepRows ON inventory.inventory_id = KeepRows.inv_id WHERE KeepRows.inv_id IS NULL AND inventory.user_id = $user_id AND inventory.poke_id = $poke_id)"""
        placeholders = {"user_id": user_id, "poke_id": poke_id}
        rows = c.execute(sql, placeholders).rowcount
        conn.commit()
        return rows
    except Error as e:
        print(e)

def remove_dupes(conn, user_id, rarity, region=None):
    try:
        c = conn.cursor()
        if region is None:
            sql = """DELETE FROM inventory WHERE inventory_id IN (SELECT inventory_id FROM inventory LEFT JOIN (SELECT MIN(inventory_id) as inv_id, user_id, poke_id FROM inventory GROUP BY user_id, poke_id) as KeepRows ON inventory.inventory_id = KeepRows.inv_id WHERE KeepRows.inv_id IS NULL AND inventory.user_id = $user_id AND inventory.poke_id IN (SELECT id FROM pikagacha WHERE rarity = $rarity) AND inventory.poke_id NOT IN (SELECT poke_id FROM favs WHERE user_id = $user_id))"""
            placeholders = {"user_id": user_id, "rarity": rarity}
        else:
            sql = """DELETE FROM inventory WHERE inventory_id IN (SELECT inventory_id FROM inventory LEFT JOIN (SELECT MIN(inventory_id) as inv_id, user_id, poke_id FROM inventory GROUP BY user_id, poke_id) as KeepRows ON inventory.inventory_id = KeepRows.inv_id WHERE KeepRows.inv_id IS NULL AND inventory.user_id = $user_id AND inventory.poke_id IN (SELECT id FROM pikagacha WHERE rarity = $rarity AND id BETWEEN $low AND $high) AND inventory.poke_id NOT IN (SELECT poke_id FROM favs WHERE user_id = $user_id))"""
            placeholders = {"user_id": user_id, "rarity": rarity, "low": region[1], "high": region[2]}
        rows = c.execute(sql, placeholders).rowcount
        conn.commit()
        return rows
    except Error as e:
        print(e)

def get_favs(conn, user_id):
    try:
        c = conn.cursor()
        sql = """SELECT poke_id FROM favs WHERE user_id = $user_id"""
        placeholders = {"user_id": user_id}
        c.execute(sql, placeholders)
        return c.fetchall()
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

def get_high_streak(conn):
    try:
        c = conn.cursor()
        sql = """SELECT id, streak FROM pikapoints WHERE streak >= 5"""
        c.execute(sql)
        return c.fetchone()
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

def change_special(conn, *args):
    try:
        c = conn.cursor()
        sql = """UPDATE pikagacha SET active = 0"""
        c.execute(sql)
        for arg in args:
            sql = """UPDATE pikagacha SET active = 1 WHERE name = $name"""
            placeholders = {"name": arg}
            c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_special(conn):
    try:
        c = conn.cursor()
        sql = """SELECT id, name FROM pikagacha WHERE rarity = 8 AND active = 1"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)

def run_sql(conn, query):
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)

def get_sql(conn, query):
    try:
        c = conn.cursor()
        c.execute(query)
        return c.fetchall()
    except Error as e:
        print(e)

def get_streak(conn, user_id):
    try:
        c = conn.cursor()
        sql = """SELECT streak FROM pikapoints WHERE id = $user_id"""
        placeholders = {"user_id": user_id}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def get_streaker(conn):
    try:
        c = conn.cursor()
        sql = """SELECT id, streak FROM pikapoints WHERE streak != 0"""
        c.execute(sql)
        return c.fetchone()
    except Error as e:
        print(e)

def update_streak(conn, user_id):
    try:
        c = conn.cursor()
        sql1 = """UPDATE pikapoints SET streak = 0 WHERE id != $user_id"""
        sql2 = """UPDATE pikapoints SET streak = streak + 1 WHERE id = $user_id"""
        placeholders = {"user_id": user_id}
        c.execute(sql1, placeholders)
        c.execute(sql2, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def perform_trade(conn, id1, id2, pokemonid1, pokemonid2):
    try:
        c = conn.cursor()
        sql1 = """UPDATE inventory SET user_id = $id2 WHERE user_id = $id1 AND poke_id = $pokemonid1 LIMIT 1"""
        sql2 = """UPDATE inventory SET user_id = $id1 WHERE user_id = $id2 AND poke_id = $pokemonid2 LIMIT 1"""
        placeholders1 = {"id2": id2, "id1": id1, "pokemonid1": pokemonid1}
        placeholders2 = {"id1": id1, "id2": id2, "pokemonid2": pokemonid2}
        c.execute(sql1, placeholders1)
        c.execute(sql2, placeholders2)
        conn.commit()
    except Error as e:
        print(e)

def get_from_jackpot(conn, id):
    try:
        c = conn.cursor()
        sql = """SELECT id FROM jackpot where id = $id"""
        placeholders = {"id": id}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def get_contribution(conn, id):
    try:
        c = conn.cursor()
        sql = """SELECT contribution FROM jackpot where id = $id"""
        placeholders = {"id": id}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def update_jackpot(conn, id, reset, new=False):
    try:
        c = conn.cursor()
        placeholders = {"id": id}
        if new:
            sql1 = """INSERT INTO jackpot (id) VALUES ($id)"""
            c.execute(sql1, placeholders)
            conn.commit()
        if reset:
            sql2 = """UPDATE jackpot SET contribution = 0"""
            c.execute(sql2)
        else:
            sql2 = """UPDATE jackpot SET contribution = contribution + 1 WHERE id = $id"""
            c.execute(sql2, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_jackpot(conn, sum):
    try:
        c = conn.cursor()
        if sum:
            sql = """SELECT sum(contribution) FROM jackpot"""
            c.execute(sql)
            return c.fetchone()
        else:
            sql = """SELECT * FROM jackpot WHERE contribution > 0 ORDER BY contribution DESC"""
            c.execute(sql)
            return c.fetchall()
    except Error as e:
        print(e)

def get_jackpot_rewards(conn):
    try:
        c = conn.cursor()
        sql = """SELECT * FROM jackpot WHERE contribution >= 3 ORDER BY contribution DESC"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)

def check_bag(conn, user_id, ball_id):
    try:
        c = conn.cursor()
        sql = """SELECT * FROM bag WHERE user_id = $user_id AND ball = $ball_id"""
        placeholders = {"user_id": user_id, "ball_id": ball_id}
        c.execute(sql, placeholders)
        return c.fetchall()
    except Error as e:
        print(e)

def use_item(conn, user_id, ball_id):
    try:
        c = conn.cursor()
        sql = """DELETE FROM bag WHERE user_id = $user_id AND ball = $ball_id LIMIT 1"""
        placeholders = {"user_id": user_id, "ball_id": ball_id}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_stadium(conn):
    try:
        c = conn.cursor()
        sql = """SELECT * FROM stadium"""
        c.execute(sql)
        return c.fetchone()
    except Error as e:
        print(e)

def update_stadiun(conn, insert):
    try:
        c = conn.cursor()
        if insert:
            sql = """INSERT INTO stadium (battle) VALUES (1)"""
        else:
            sql = """DELETE FROM stadium"""
        c.execute(sql)
        conn.commit()
    except Error as e:
        print(e)

def register(conn, id, name):
    try:
        c = conn.cursor()
        sql = """SELECT * FROM trainer WHERE name = $name"""
        placeholders = {"name": name}
        c.execute(sql, placeholders)
        result = c.fetchone()
        if result is None:
            sql = """SELECT * FROM trainer WHERE id = $id"""
            placeholders = {"id": id}
            c.execute(sql, placeholders)
            result = c.fetchone()
            if result is None:
                sql = """INSERT INTO trainer (id, name) VALUES ($id, $name)"""
                placeholders = {"id": id, "name": name}
                c.execute(sql, placeholders)
                conn.commit()
                return 0
            else:
                sql = """UPDATE trainer SET name = $name WHERE id = $id"""
                placeholders = {"id": id, "name": name}
                c.execute(sql, placeholders)
                conn.commit()
                return 1
        else:
            if result[0] != id:
                return 3
            else:
                return 2
    except Error as e:
        print(e)
        return 4

def get_trainer(conn, name):
    try:
        c = conn.cursor()
        sql = """SELECT * FROM trainer WHERE name = $name"""
        placeholders = {"name": name}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def get_trainers(conn):
    try:
        c = conn.cursor()
        sql = """SELECT id, name, rank, team FROM trainer ORDER BY name ASC"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)

def increment_stat(conn, id, stat):
    try:
        c = conn.cursor()
        if stat == 'rolls':
            sql = """UPDATE trainer SET rolls = rolls + 1 WHERE id = $id"""
        elif stat == 'bricks':
            sql = """UPDATE trainer SET bricks = bricks + 1 WHERE id = $id"""
        elif stat == 'jackpots':
            sql = """UPDATE trainer SET jackpots = jackpots + 1 WHERE id = $id"""
        elif stat == 'opens':
            sql = """UPDATE trainer SET opens = opens + 1 WHERE id = $id"""
        elif stat == 'releases':
            sql = """UPDATE trainer SET releases = releases + 1 WHERE id = $id"""
        elif stat == 'trades':
            sql = """UPDATE trainer SET trades = trades + 1 WHERE id = $id"""
        elif stat == 'quizzes':
            sql = """UPDATE trainer SET quizzes = quizzes + 1 WHERE id = $id"""
        elif stat == 'streaks':
            sql = """UPDATE trainer SET streaks = streaks + 1 WHERE id = $id"""
        elif stat == 'shutdowns':
            sql = """UPDATE trainer SET shutdowns = shutdowns + 1 WHERE id = $id"""
        elif stat == 'battles':
            sql = """UPDATE trainer SET battles = battles + 1 WHERE id = $id"""
        elif stat == 'wins':
            sql = """UPDATE trainer SET wins = wins + 1 WHERE id = $id"""
        elif stat == 'underdogs':
            sql = """UPDATE trainer SET underdogs = underdogs + 1 WHERE id = $id"""
        elif stat == 'highstakewins':
            sql = """UPDATE trainer SET highstakewins = highstakewins + 1 WHERE id = $id"""
        elif stat == 'losses':
            sql = """UPDATE trainer SET losses = losses + 1 WHERE id = $id"""
        elif stat == 'neverlucky':
            sql = """UPDATE trainer SET neverlucky = neverlucky + 1 WHERE id = $id"""
        elif stat == 'highstakeloss':
            sql = """UPDATE trainer SET highstakeloss = highstakeloss + 1 WHERE id = $id"""
        placeholders = {"id": id}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_team(conn, team):
    try:
        c = conn.cursor()
        sql = """SELECT trainer.name, trainer.rank, trainer.id FROM trainer INNER JOIN rank ON trainer.rank = rank.rank WHERE trainer.team = $team ORDER BY rank.id DESC, trainer.name ASC"""
        placeholders = {"team": team}
        c.execute(sql, placeholders)
        return c.fetchall()
    except Error as e:
        print(e)

def get_trainer_team(conn, id):
    try:
        c = conn.cursor()
        sql = """SELECT team, name, rank, prestige, currxp, highstreak FROM trainer WHERE id = $id"""
        placeholders = {"id": id}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def update_high_streak(conn, id, streak):
    try:
        c = conn.cursor()
        sql = """UPDATE trainer SET highstreak = $streak WHERE id = $id"""
        placeholders = {"streak": streak, "id": id}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def update_team(conn, id, team):
    try:
        c = conn.cursor()
        sql = """UPDATE trainer SET team = $team WHERE id = $id"""
        placeholders = {"id": id, "team": team}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def update_rank(conn, id, rank):
    try:
        c = conn.cursor()
        sql = """UPDATE trainer SET rank = $rank WHERE id = $id"""
        placeholders = {"id": id, "rank": rank}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def update_exp(conn, id, inc, reset):
    try:
        c = conn.cursor()
        if reset:
            sql = """UPDATE trainer SET totalxp = 0, currxp = 0 WHERE id = $id"""
            placeholders = {"id": id}
        else:
            sql = """UPDATE trainer SET totalxp = totalxp + $inc, currxp = currxp + $inc WHERE id = $id"""
            placeholders = {"id": id, "inc": inc}
        c.execute(sql, placeholders)
        conn.commit()
    except Error as e:
        print(e)

def get_next_rank(conn, rank):
    try:
        c = conn.cursor()
        sql = """SELECT rank, xp FROM rank WHERE id = (SELECT id FROM rank WHERE rank = $rank) + 1"""
        placeholders = {"rank": rank}
        c.execute(sql, placeholders)
        return c.fetchone()
    except Error as e:
        print(e)

def prestige(conn, id, reset):
    try:
        c = conn.cursor()
        if reset:
            sql = """UPDATE trainer SET prestige = 0 WHERE id = $id"""
            placeholders = {"id": id}
            c.execute(sql, placeholders)
            conn.commit()
        else:
            sql = """UPDATE trainer SET prestige = prestige + 1, currxp = 0, rank = 'Recruit' WHERE id = $id"""
            placeholders = {"id": id}
            c.execute(sql, placeholders)
            conn.commit()
    except Error as e:
        print(e)

def promote(conn, id):
    try:
        trainer = get_trainer_team(conn, id)
        if trainer is None:
            return None
        name = trainer[1]
        team = trainer[0]
        rank = trainer[2]
        if rank in ('Pokémon Trainer', 'Boss'):
            return None
        next_rank = get_next_rank(conn, rank)
        next_rank_name = next_rank[0]
        next_rank_xp = next_rank[1]
        curr_xp = trainer[4]
        if curr_xp < next_rank_xp:
            return None

        c = conn.cursor()
        sql = """UPDATE trainer SET rank = $new_rank, currxp = currxp - $next_rank_xp WHERE id = $id"""
        placeholders = {"new_rank": next_rank_name, "next_rank_xp": next_rank_xp, "id": id}
        c.execute(sql, placeholders)
        conn.commit()
        if next_rank_name in ('Crook', 'Grunt', 'Thug', 'Associate', 'Hitman'):
            ball = 'Poké Ball'
            add_item(conn, id, 1)
        elif next_rank_name in ('Officer', 'Sergeant', 'Captain', 'Lieutenant'):
            ball = 'Great Ball'
            add_item(conn, id, 2)
        elif next_rank_name in ('Admin', 'Commander', 'Boss'):
            ball = 'Ultra Ball'
            add_item(conn, id, 3)
        return "{} has been promoted from {} {} to {} {} and received a {}!".format(name, team, rank, team, next_rank_name, ball)
    except Error as e:
        print(e)

def team_split(conn, id1, id2, shutdown, gain):
    try:
        c = conn.cursor()
        sql = """SELECT team FROM trainer WHERE id = $id"""
        ph = {"id": id1}
        c.execute(sql, ph)
        p1_team = c.fetchone()
        if p1_team is None:
            return None
        elif p1_team[0] == '':
            return None
        else:
            p1_team = p1_team[0]

        ph = {"id": id2}
        c.execute(sql, ph)
        p2_team = c.fetchone()

        sql = """SELECT count(*) FROM trainer WHERE team = $team"""
        ph = {"team": p1_team}
        c.execute(sql, ph)
        team1_size = c.fetchone()
        team1_size = team1_size[0]

        if p2_team is None:
            team_multiplier = 1
        elif p2_team[0] == '':
            team_multiplier = 1
        else:
            p2_team = p2_team[0]
            if p1_team == p2_team:
                shutdown = 1

            ph = {"team": p2_team}
            c.execute(sql, ph)
            team2_size = c.fetchone()
            team2_size = team2_size[0]

            if shutdown <= 1:
                team_multiplier = 1
            else:
                team_multiplier = team2_size/team1_size

        sql = """SELECT rank.id, trainer.prestige FROM rank INNER JOIN trainer ON rank.rank = trainer.rank WHERE trainer.id = $id"""
        ph = {"id": id1}
        c.execute(sql, ph)
        trainer_details = c.fetchone()
        trainer_rank = trainer_details[0]
        trainer_prestige = trainer_details[1]

        return min(math.ceil((((max(10, trainer_rank - 1 + 12 * trainer_prestige)) * team_multiplier) + (5 * (shutdown - 1))) / (team1_size - 1)), gain)

    except Error as e:
        print(e)


sql_create_pikapoints_table = """CREATE TABLE IF NOT EXISTS pikapoints (
                                    id integer PRIMARY KEY,
                                    points integer DEFAULT 0,
                                    streak integer DEFAULT 0)"""
sql_create_pikagacha_table = """CREATE TABLE IF NOT EXISTS pikagacha (id integer PRIMARY KEY, name text NOT NULL UNIQUE, rarity integer NOT NULL, focus integer NOT NULL, bst integer NOT NULL, active integer DEFAULT 0)"""
sql_create_pikapity_table = """CREATE TABLE IF NOT EXISTS pikapity (id integer PRIMARY KEY, three integer NOT NULL, four integer NOT NULL, five integer NOT NULL, focus integer NOT NULL)"""
sql_create_inventory = """CREATE TABLE IF NOT EXISTS inventory (user_id integer NOT NULL, poke_id integer NOT NULL, inventory_id integer PRIMARY KEY)"""
sql_create_jackpot = """CREATE TABLE IF NOT EXISTS jackpot (id integer NOT NULL, contribution integer DEFAULT 0)"""
sql_create_bag = """CREATE TABLE IF NOT EXISTS bag (user_id integer NOT NULL, ball integer NOT NULL, bag_id integer PRIMARY KEY)"""
sql_create_bank = """CREATE TABLE IF NOT EXISTS bank (id integer PRIMARY KEY, points integer DEFAULT 0)"""
sql_create_fav = """CREATE TABLE IF NOT EXISTS favs (user_id integer NOT NULL, poke_id integer NOT NULL, fav_id integer PRIMARY KEY) """
sql_create_stadium = """CREATE TABLE IF NOT EXISTS stadium (battle integer PRIMARY KEY DEFAULT 0)"""
sql_create_trainer = """CREATE TABLE IF NOT EXISTS trainer (id integer PRIMARY KEY, name text NOT NULL UNIQUE, rank text DEFAULT 'Pokémon Trainer', rolls integer DEFAULT 0, bricks integer DEFAULT 0, jackpots integer DEFAULT 0, opens integer DEFAULT 0, releases integer DEFAULT 0, trades integer DEFAULT 0, quizzes integer DEFAULT 0, streaks integer DEFAULT 0, shutdowns integer DEFAULT 0, battles integer DEFAULT 0, wins integer DEFAULT 0, underdogs integer DEFAULT 0, highstakewins integer DEFAULT 0, losses integer DEFAULT 0, neverlucky integer DEFAULT 0, highstakeloss integer DEFAULT 0, team text NOT NULL DEFAULT '', totalxp integer DEFAULT 0, currxp integer DEFAULT 0, prestige integer DEFAULT 0, highstreak integer DEFAULT 0)"""
sql_create_ranks = """CREATE TABLE IF NOT EXISTS rank (id integer PRIMARY KEY, rank text NOT NULL UNIQUE, xp integer NOT NULL)"""
sql_create_team = """CREATE TABLE IF NOT EXISTS team (id integer PRIMARY KEY, name text NOT NULL UNIQUE)"""

def load_pikadata(path):
    data = {}
    with open(path, mode='r') as file:
        for line in file:
            line_data = line.split("\t")
            data[int(line_data[0])] = (line_data[1], int(line_data[2]), int(line_data[3]), int(line_data[4]))
    return data

def initialize_teams(conn, team_names):
    try:
        c = conn.cursor()
        for name in team_names:
            sql = """INSERT OR IGNORE INTO team (name) VALUES ($name)"""
            placeholders = {"name": name}
            c.execute(sql, placeholders)
            conn.commit()
    except Error as e:
        print(e)

def initialize_ranks(conn, ranks):
    try:
        c = conn.cursor()
        for rank in ranks:
            sql = """INSERT OR IGNORE INTO rank (rank, xp) VALUES ($rank, $xp)"""
            placeholders = {"rank": rank[0], "xp": rank[1]}
            c.execute(sql, placeholders)
            conn.commit()
    except Error as e:
        print(e)

def initialize(conn):
    create_table(conn, sql_create_pikapoints_table)
    create_table(conn, sql_create_pikagacha_table)
    create_table(conn, sql_create_pikapity_table)
    create_table(conn, sql_create_inventory)
    create_table(conn, sql_create_jackpot)
    create_table(conn, sql_create_bag)
    create_table(conn, sql_create_bank)
    create_table(conn, sql_create_fav)
    create_table(conn, sql_create_stadium)
    create_table(conn, sql_create_trainer)
    create_table(conn, sql_create_ranks)
    create_table(conn, sql_create_team)

    pokemon = load_pikadata('pokedata.csv')
    for key in pokemon:
        setup_pikagacha(conn, key, pokemon[key][0], pokemon[key][1], pokemon[key][2], pokemon[key][3])

    teams = ['Team Electrocution', 'Team Lensflare', 'Team Hyperjoy']
    initialize_teams(conn, teams)

    ranks = [('Recruit', 0), ('Crook', 250), ('Grunt', 500), ('Thug', 750), ('Associate', 1000), ('Hitman', 1250),
             ('Officer', 1500), ('Sergeant', 1750), ('Captain', 2000), ('Lieutenant', 2250), ('Admin', 2500),
             ('Commander', 2750), ('Boss', 3500)]
    initialize_ranks(conn, ranks)

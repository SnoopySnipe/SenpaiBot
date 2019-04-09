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

def get_savings(user_id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_savings(conn, user_id)
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

def adjust_savings(user_id, points):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.adjust_savings(conn, user_id, points)
        conn.close()

def get_inventory(user_id, region=None):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_inventory(conn, user_id, region)
        conn.close()
        return result

def get_poke_count(user_id, poke_id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_poke_count(conn, user_id, poke_id)
        conn.close()
        return result

def get_stadium():
    conn = sqlite3.connect(db)
    result = False
    if(conn is not None):
        if database.get_stadium(conn) is not None:
            result = True
        conn.close()
    return result

def update_stadium(insert):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.update_stadiun(conn, insert)
        conn.close()

def get_bag(user_id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_bag(conn, user_id)
        conn.close()
        return result

def check_bag(user_id, ball_id):
    conn = sqlite3.connect(db)
    result = False
    if(conn is not None):
        if len(database.check_bag(conn, user_id, ball_id)) > 0:
            result = True
        conn.close()
    return result

def use_item(user_id, ball_id):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.use_item(conn, user_id, ball_id)
        conn.close()

def get_from_inventory(user_id, poke_id):
    conn = sqlite3.connect(db)
    result = False
    if(conn is not None):
        if len(database.get_from_inventory(conn, user_id, poke_id)) > 0:
            result = True
        conn.close()
    return result

def get_high_streak():
    conn = sqlite3.connect(db)
    result = None
    if (conn is not None):
        if database.get_high_streak(conn) is not None:
            result = database.get_high_streak(conn)
        conn.close()
    return result

def add_inventory(user_id, poke_id):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.add_inventory(conn, user_id, poke_id)
        conn.close()

def add_item(user_id, item_id):
    conn = sqlite3.connect(db)
    if(conn is not None):
        database.add_item(conn, user_id, item_id)
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

def change_special(*args):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.change_special(conn, *args)
        conn.close()

def run_sql(query):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.run_sql(conn, query)
        conn.close()

def get_sql(query):
    conn = sqlite3.connect(db)
    result = []
    if (conn is not None):
        result = database.get_sql(conn, query)
        conn.close()
    return result

def full_remove_inventory(user_id, rarity, region=None):
    conn = sqlite3.connect(db)
    if (conn is not None):
        return database.full_remove_inventory(conn, user_id, rarity, region)
        conn.close()

def fullrelease_pokemon(user_id, poke_id):
    conn = sqlite3.connect(db)
    if (conn is not None):
        return database.fullrelease_pokemon(conn, user_id, poke_id)
        conn.close()

def releasedupes_pokemon(user_id, poke_id):
    conn = sqlite3.connect(db)
    if (conn is not None):
        return database.releasedupes_pokemon(conn, user_id, poke_id)
        conn.close()

def remove_dupes(user_id, rarity, region=None):
    conn = sqlite3.connect(db)
    if (conn is not None):
        return database.remove_dupes(conn, user_id, rarity, region)
        conn.close()

def add_fav(user_id, poke_id):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.add_fav(conn, user_id, poke_id)
        conn.close()

def del_fav(user_id, poke_id):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.del_fav(conn, user_id, poke_id)
        conn.close()

def del_all_favs(user_id):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.del_all_favs(conn, user_id)
        conn.close()

def get_favs(user_id):
    conn = sqlite3.connect(db)
    result = None
    if (conn is not None):
        result = database.get_favs(conn, user_id)
        conn.close()
        return result

def get_pokemon_name(id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_pokemon_name(conn, id)
        conn.close()
        return result

def get_streak(user_id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_streak(conn, user_id)
        conn.close()
        return result

def update_streak(user_id):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.update_streak(conn, user_id)
        conn.close()

def get_streaker():
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_streaker(conn)
        conn.close()
        return result

def perform_trade(id1, id2, pokemonid1, pokemonid2):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.perform_trade(conn, id1, id2, pokemonid1, pokemonid2)
        conn.close()

def update_jackpot(id, reset):
    conn = sqlite3.connect(db)
    if (conn is not None):
        new = False
        if database.get_from_jackpot(conn, id) is None:
            new = True
        database.update_jackpot(conn, id, reset, new=new)
        conn.close()

def get_jackpot(sum):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_jackpot(conn, sum)
        conn.close()
        return result

def get_contribution(id):
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_contribution(conn, id)
        conn.close()
        return result

def get_jackpot_rewards():
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_jackpot_rewards(conn)
        conn.close()
        return result

def register(id, name):
    conn = sqlite3.connect(db)
    if(conn is not None):
        return database.register(conn, id, name)
        conn.close()

def get_trainer(name):
    conn = sqlite3.connect(db)
    result = None
    if (conn is not None):
        result = database.get_trainer(conn, name)
        conn.close()
    return result

def get_trainers():
    conn = sqlite3.connect(db)
    result = []
    if (conn is not None):
        result = database.get_trainers(conn)
        conn.close()
    return result

def increment_stat(id, stat):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.increment_stat(conn, id, stat)
        conn.close()

def get_team(team):
    conn = sqlite3.connect(db)
    result = []
    if (conn is not None):
        result = database.get_team(conn, team)
        conn.close()
    return result

def get_trainer_team(id):
    conn = sqlite3.connect(db)
    result = None
    if (conn is not None):
        result = database.get_trainer_team(conn, id)
        conn.close()
    return result

def update_team(id, team):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.update_team(conn, id, team)
        conn.close()

def update_rank(id, rank):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.update_rank(conn, id, rank)
        conn.close()

def update_exp(id, inc, reset=False):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.update_exp(conn, id, inc, reset)
        conn.close()

def get_next_rank(rank):
    conn = sqlite3.connect(db)
    result = None
    if (conn is not None):
        result = database.get_next_rank(conn, rank)
        conn.close()
    return result

def prestige(id, reset=False):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.prestige(conn, id, reset)
        conn.close()

def promote(id):
    conn = sqlite3.connect(db)
    result = None
    if (conn is not None):
        result = database.promote(conn, id)
        conn.close()
    return result

def team_split(id1, id2, shutdown, gain):
    conn = sqlite3.connect(db)
    result = None
    if (conn is not None):
        result = database.team_split(conn, id1, id2, shutdown, gain)
        conn.close()
    return result

def update_high_streak(id, streak):
    conn = sqlite3.connect(db)
    if (conn is not None):
        database.update_high_streak(conn, id, streak)
        conn.close()

def get_special():
    conn = sqlite3.connect(db)
    result = None
    if(conn is not None):
        result = database.get_special(conn)
        conn.close()
    return result

def get_box(user_id):
    conn = sqlite3.connect(db)
    result = []
    if (conn is not None):
        result = database.get_box(conn, user_id)
        conn.close()
    return result

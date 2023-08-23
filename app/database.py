# import aiosqlite as sq
import json
import sqlite3 as sq
from game_logic import json_imports


async def db_start():
    global db, cur
    db = sq.connect('tg.db')
    # db = sq.connect('../tg.db')  # debug

    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS players("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER, "
                "location INTEGER, "
                "max_health INTEGER, "
                "current_health INTEGER, "
                "current_energy INTEGER, "
                "max_energy INTEGER, "
                "inventory TEXT, "
                "credits INTEGER, "
                "experience INTEGER, "
                "level INTEGER, "
                "main_quest INTEGER, "
                "side_quest TEXT, "
                "tutorial_quest INTEGER, "
                "cargo TEXT, "
                # ship type is  dict with ship details (max weapon slots, max armor slots, max_hp etc.)
                "ship_type TEXT, "
                "ship_weapon_slots TEXT, "
                "attributes TEXT, "
                "stats TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS items("
                "i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "it_name TEXT,"
                "it_shortname TEXT,"
                "desc TEXT, "
                "type TEXT, "
                "effects TEXT, "
                "craft TEXT, "
                "price INTEGER, "
                "attributes TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS enemies("
                "en_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "en_name TEXT,"
                "en_shortname TEXT,"
                "desc TEXT, "
                "type TEXT, "
                "attributes TEXT, "
                "stats TEXT, "
                "en_drop TEXT)")  # because name drop conflicts with db :)
    cur.execute("CREATE TABLE IF NOT EXISTS materials("
                "mt_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "mt_name TEXT, "
                "mt_shortname TEXT, "
                "type TEXT, "
                "price INTEGER, "
                "conver TEXT)"),
    db.commit()


async def cmd_start_db(user_id):  # initialize new player
    user = cur.execute(
        "SELECT * FROM players WHERE tg_id = ?", (user_id,)).fetchone()
    if not user:
        # hardcoded new user parameters
        cur.execute(
            "INSERT INTO players (tg_id, location, current_energy, max_energy, inventory, credits, experience, level, main_quest, side_quest, tutorial_quest, cargo, ship_type, ship_weapon_slots, stats, attributes, max_health, current_health) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, 0, 5, 5, "{}", 100, 0, 1, 0, "None", 0, "{}", "starter_ship", "[2]", json_imports.player_stats(), json_imports.player_attributes(), 100, 100))  # defaults are location=0 current_energy=0, max_energy=0
        db.commit()
        await db_write_items_json()
        await db_write_enemies_json()


async def new_user_check(user_id) -> bool:
    '''
    Check if user is new
    True if new, False if old
    '''
    user = cur.execute(
        "SELECT * FROM players WHERE tg_id = ?", (user_id,)).fetchone()
    if user:
        return False
    else:
        return True


async def db_read_int(table, user_id, column):  # custom db_access
    '''
    access db: read int from table

    args:
        table == Table name in sqlite
        user_id == tg_id from players Table
        column == column
    '''
    value = cur.execute(
        f"SELECT {column} FROM {table} WHERE tg_id = ?", (user_id,))
    return value.fetchone()[0]


async def db_energy_parser():
    '''parse whole db'''
    value = cur.execute(
        "SELECT tg_id, current_energy, max_energy FROM players")
    return value.fetchall()


async def db_read_dict(table, user_id, column):  # custom db_access
    value = cur.execute(
        f"SELECT {column} FROM {table} WHERE tg_id = ?", (user_id,))
    value = json.loads(value.fetchone()[0])
    return value


async def db_write_int(table, user_id, column, value) -> None:  # custom db_access
    '''access db: write or write mode of attributes for a single user'''
    cur.execute(
        f"UPDATE {table} SET {column} = ? WHERE tg_id = ?", (value, user_id))
    db.commit()


async def db_write_dict(table, user_id, column, key, value) -> None:  # custom db_access
    '''write data to dict'''
    data = await db_read_dict(table, user_id, column)
    data[key] = value
    json_data = json.dumps(data)
    cur.execute(
        f"UPDATE {table} SET {column} = ? WHERE tg_id = ?", (json_data, user_id))
    db.commit()


# async def add_items(state):
#     async with state.proxy() as data:
#         cur.execute("INSERT INTO items (name, desc, price, photo, brand) VALUES (?, ?, ?, ?, ?)",
#                     (data['name'], data['desc'], data['price'], data['photo'], data['type']))
#         db.commit()


async def db_write_enemies_json():
    enemies = json_imports.read_enemies()
    for row in enemies:
        output = enemies[row]
        name = json.dumps(output.get("name"))
        description = json.dumps(output.get("description"))
        stats = json.dumps(output.get("stats"))
        attributes = json.dumps(output.get("attributes"))
        drop = json.dumps(output.get("drop"))
        shortname = json.dumps(output.get("shortname"))
        item_exists = cur.execute(
            "SELECT * FROM enemies WHERE en_name = ?", (name,)).fetchone()
        if not item_exists:
            cur.execute(
                "INSERT INTO enemies (en_name, desc, stats, attributes, en_drop, en_shortname) VALUES (?, ?, ?, ?, ?, ?)", (name, description, stats, attributes, drop, shortname))
            db.commit()


async def db_write_items_json():
    items = json_imports.read_items()
    for row in items:
        output = items[row]
        name = json.dumps(output.get("name"))
        description = json.dumps(output.get("description"))
        item_type = json.dumps(output.get("type"))
        effects = json.dumps(output.get("effects"))
        craft = json.dumps(output.get("craft"))
        price = json.dumps(output.get("price"))
        attributes = json.dumps(output.get("attributes"))
        shortname = json.dumps(output.get("shortname"))
        item_exists = cur.execute(
            "SELECT * FROM items WHERE it_name = ?", (name,)).fetchone()
        if not item_exists:
            cur.execute(
                "INSERT INTO items (it_name, desc, type, effects, craft, price, attributes, it_shortname) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, description, item_type, effects, craft, price, attributes, shortname))
            db.commit()

#
# -----need functions to read jsons from db
# -----and also to add materials from admin
#
# cur.execute("CREATE TABLE IF NOT EXISTS materials("
#             "mt_id INTEGER PRIMARY KEY AUTOINCREMENT, "
#             "mt_name TEXT, "
#             "type TEXT, "
#             "price INTEGER)"
#             "conver TEXT)")


# read what enemies can spawn at loc
async def db_read_enemies_attributes(gps):
    data = cur.execute(
        "SELECT en_shortname, attributes FROM enemies").fetchall()
    output = []
    for line in data:
        shortname = line[0]
        # description = line[1]
        # stats = line[2]
        attributes = json.loads(line[1])
        min_loc = int(attributes.get("min_loc"))
        max_loc = int(attributes.get("max_loc"))
        # drop = line[4]
        if gps >= min_loc and gps <= max_loc:
            output.append(shortname)
            # print(f"appending en_shortname {shortname}")
    return output


async def db_read_details(table, value, column, search_col):  # custom db_access
    value = cur.execute(
        f"SELECT {column} FROM {table} WHERE {search_col} = ?", (value,))
    value = json.loads(value.fetchone()[0])
    return value

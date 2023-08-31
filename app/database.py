# import aiosqlite as sq
import json
import sqlite3 as sq
from game_logic import json_imports


async def db_start_pl():
    global db_pl, cur_pl
    db_pl = sq.connect('players.db')

    cur_pl = db_pl.cursor()
    cur_pl.execute("CREATE TABLE IF NOT EXISTS players("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER, "
                "tg_name TEXT, "
                "location INTEGER, "
                "max_health INTEGER, "
                "current_health INTEGER, "
                "current_energy INTEGER, "
                "max_energy INTEGER, "
                "pl_items TEXT, "
                "pl_materials TEXT, "
                "credits INTEGER, "
                "experience INTEGER, "
                "level INTEGER, "
                "main_quest INTEGER, "
                "side_quest TEXT, "
                "tutorial_quest INTEGER, "
                "cargo TEXT, "
                # ship type is  dict with ship details (max weapon slots, max armor slots, max_hp etc.)
                "ship_type TEXT, "
                "ship_slots TEXT, "
                "attributes TEXT, "
                "abilities TEXT)")
    db_pl.commit()


async def db_start_gm():
    global db_gm, cur_gm
    db_gm = sq.connect('game.db')

    cur_gm = db_gm.cursor()
    cur_gm.execute("CREATE TABLE IF NOT EXISTS items("
                "i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "it_name TEXT,"
                "it_shortname TEXT,"
                "desc TEXT, "
                "type TEXT, "
                "effects TEXT, "
                "craft TEXT, "
                "price INTEGER, "
                "attributes TEXT)")
    cur_gm.execute("CREATE TABLE IF NOT EXISTS enemies("
                "en_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "en_name TEXT,"
                "en_shortname TEXT,"
                "desc TEXT, "
                "type TEXT, "
                "attributes TEXT, "
                "stats TEXT, "
                "en_drop TEXT)")  # because name drop conflicts with db :)
    cur_gm.execute("CREATE TABLE IF NOT EXISTS materials("
                "mt_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "mt_name TEXT, "
                "mt_shortname TEXT, "
                "type TEXT, "
                "price INTEGER, "
                "mt_drop TEXT)"),
    db_gm.commit()    


async def cmd_start_db(user_id):  # initialize new player
    user = cur_pl.execute(
        "SELECT * FROM players WHERE tg_id = ?", (user_id,)).fetchone()
    if not user:
        # hardcoded new user parameters
        ship_slots = json_imports.player_ship_slots()
        pl_items = json_imports.player_pl_items()
        pl_materials = json_imports.player_pl_materials()
        cur_pl.execute(
            "INSERT INTO players (tg_id, location, current_energy, max_energy, pl_items, credits, experience, level, main_quest, side_quest, tutorial_quest, cargo, ship_type, ship_slots, abilities, attributes, max_health, current_health, pl_materials) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, 0, 5, 5, pl_items, 100, 0, 1, 0, "None", 0, "{}", "starter_ship", ship_slots, json_imports.player_abilities(), json_imports.player_attributes(), 100, 100, pl_materials))  # defaults are location=0 current_energy=0, max_energy=0
        db_pl.commit()
        await db_write_items_json()
        await db_write_enemies_json()
        await db_write_materials_json()


async def new_user_check(user_id) -> bool:
    '''
    Check if user is new
    True if new, False if old
    '''
    user = cur_pl.execute(
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
    if table == "players":
        value = cur_pl.execute(
        f"SELECT {column} FROM {table} WHERE tg_id = ?", (user_id,))
    else:
        value = cur_gm.execute(
        f"SELECT {column} FROM {table} WHERE tg_id = ?", (user_id,))        
    return value.fetchone()[0]


async def db_energy_parser():
    '''parse whole db'''
    value = cur_pl.execute(
        "SELECT tg_id, current_energy, max_energy FROM players")
    return value.fetchall()


async def db_read_dict(table, user_id, column):  # custom db_access
    if table == "players":
        value = cur_pl.execute(
            f"SELECT {column} FROM {table} WHERE tg_id = ?", (user_id,))
    else:
        value = cur_gm.execute(
        f"SELECT {column} FROM {table} WHERE tg_id = ?", (user_id,))
    value = json.loads(value.fetchone()[0])
    return value


async def db_write_int(table, user_id, column, value) -> None:  # custom db_access
    '''access db: write or write mode of attributes for a single user'''
    if table == "players":
        cur_pl.execute(
            f"UPDATE {table} SET {column} = ? WHERE tg_id = ?", (value, user_id))
        db_pl.commit()
    else:
        cur_gm.execute(
            f"UPDATE {table} SET {column} = ? WHERE tg_id = ?", (value, user_id))
        db_gm.commit()

#    will not bu used ????
# async def db_write_dict(table, user_id, column, key, value) -> None:  # custom db_access
#     '''write data to dict'''
#     data = await db_read_dict(table, user_id, column)
#     data[key] = value
#     json_data = json.dumps(data)
#     if table == "players":
#         cur_pl.execute(
#             f"UPDATE {table} SET {column} = ? WHERE tg_id = ?", (json_data, user_id))
#         db_pl.commit()
#     else:
#         cur_gm.execute(
#         f"UPDATE {table} SET {column} = ? WHERE tg_id = ?", (json_data, user_id))
#         db_gm.commit()
    

# custom db_access
async def db_write_dict_full(table: str, user_id: int, column: str, new_dict: dict) -> None:
    '''write data to dict'''
    json_data = json.dumps(new_dict)
    if table == "players":
        cur_pl.execute(
            f"UPDATE {table} SET {column} = ? WHERE tg_id = ?", (json_data, user_id))
        db_pl.commit()
    else:
        cur_gm.execute(
        f"UPDATE {table} SET {column} = ? WHERE tg_id = ?", (json_data, user_id))
        db_gm.commit()


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
        en_type = json.dumps(output.get("type"))
        item_exists = cur_gm.execute(
            "SELECT * FROM enemies WHERE en_shortname = ?", (shortname,)).fetchone()
        if not item_exists:
            cur_gm.execute(
                "INSERT INTO enemies (en_name, desc, stats, attributes, en_drop, en_shortname, type) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, description, stats, attributes, drop, shortname, en_type))
            db_gm.commit()


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
        item_exists = cur_gm.execute(
            "SELECT * FROM items WHERE it_name = ?", (name,)).fetchone()
        if not item_exists:
            cur_gm.execute(
                "INSERT INTO items (it_name, desc, type, effects, craft, price, attributes, it_shortname) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, description, item_type, effects, craft, price, attributes, shortname))
            db_gm.commit()


async def db_write_materials_json():
    items = json_imports.read_materials()
    for row in items:
        output = items[row]
        name = json.dumps(output.get("name"))
        shortname = json.dumps(output.get("shortname"))
        mat_type = json.dumps(output.get("type"))
        price = json.dumps(output.get("price"))
        drop = json.dumps(output.get("drop"))
        item_exists = cur_gm.execute(
            "SELECT * FROM materials WHERE mt_name = ?", (name,)).fetchone()
        if not item_exists:
            cur_gm.execute(
                "INSERT INTO materials (mt_name, mt_shortname, type, price, mt_drop) VALUES (?, ?, ?, ?, ?)", (name, shortname, mat_type, price, drop))
            db_gm.commit()


# read what enemies can spawn at loc
async def db_read_enemies_attributes(gps):
    data = cur_gm.execute(
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
    
    value = cur_gm.execute(
        f"SELECT {column} FROM {table} WHERE {search_col} = ?", (value,))
    value = json.loads(value.fetchone()[0])
    return value


async def db_read_full_name(table, value, column, search_col) -> str:
    try:
        value = cur_gm.execute(
        f"SELECT {column} FROM {table} WHERE {search_col} = ?", (value,))
        result = value.fetchone()
        if result:
            return result[0]
        else:
            return "No matching value found."
    except Exception as e:
        return f"Error: {e}"


async def db_parse_all_ores(gps):
    name = f"\"ore\""
    cur_pl.execute(
        "SELECT mt_name, mt_shortname, mt_drop FROM materials WHERE type = ?", (name,))
    materials = cur_pl.fetchall()
    return materials

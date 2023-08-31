from app.database import db_read_dict, db_write_dict_full, db_write_int, db_read_int, db_read_details, db_read_full_name
from game_logic import space_map
from game_logic import mechanics as m
from emojis import *


async def add_pl_exp(user_id, exp):
    old_exp = await db_read_int("players", user_id, "experience")
    await db_write_int("players", user_id, "experience", old_exp + exp)


async def add_pl_credits(user_id, got_credits):
    old_credits = await db_read_int("players", user_id, "credits")
    await db_write_int("players", user_id, "credits", old_credits + got_credits)


async def add_pl_items(user_id, it_shortname, count):
    pl_items = await db_read_dict("players", user_id, "pl_items")
    # print("before IF in add_pl_items", pl_items)
    if pl_items.get(it_shortname, False):  # if item is already in inventory
        count_old = pl_items.get(it_shortname)
        pl_items.update({it_shortname: count+count_old})
        # print("inside 1 IF in add_pl_items", pl_items)
        print(
            f"adding item {it_shortname}, player owned count =", count, " + ", count_old)
    else:
        count_old = pl_items.get(it_shortname)
        pl_items.update({it_shortname: count})
        print(
            f"inventory was empty ({count_old}), adding {it_shortname} (x{count})")
        # print("inside 2 IF in add_pl_items", pl_items)
    # new function to update value in dictionary
    await db_write_dict_full("players", user_id, "pl_items", pl_items)


async def add_pl_materials(user_id, mt_shortname, count):
    pl_materials = await db_read_dict("players", user_id, "pl_materials")
    # print("before IF in add_pl_materials", pl_materials)
    if pl_materials.get(mt_shortname, False):  # if item is already in inventory
        count_old = pl_materials.get(mt_shortname)
        pl_materials.update({mt_shortname: count+count_old})
        # print("inside 1 IF in add_pl_materials", pl_materials)
        print(
            f"adding item {mt_shortname}, player owned count =", count, " + ", count_old)
    else:
        count_old = pl_materials.get(mt_shortname)
        pl_materials.update({mt_shortname: count})
        print(
            f"inventory was empty ({count_old}), adding {mt_shortname} (x{count})")
        # print("inside 2 IF in add_pl_materials", pl_materials)
    # new function to update value in dictionary
    await db_write_dict_full("players", user_id, "pl_materials", pl_materials)


async def add_pl_ores(user_id, mt_shortname, count):
    pl_ores = await db_read_dict("players", user_id, "pl_materials")
    # print("before IF in add_pl_ores", pl_ores)
    if pl_ores.get(mt_shortname, False):  # if item is already in inventory
        count_old = pl_ores.get(mt_shortname)
        pl_ores.update({mt_shortname: count+count_old})
        # print("inside 1 IF in add_pl_ores", pl_ores)
        print(
            f"adding item {mt_shortname}, player owned count =", count, " + ", count_old)
    else:
        count_old = pl_ores.get(mt_shortname)
        pl_ores.update({mt_shortname: count})
        print(
            f"inventory was empty ({count_old}), adding {mt_shortname} (x{count})")
        # print("inside 2 IF in add_pl_ores", pl_ores)
    # new function to update value in dictionary
    await db_write_dict_full("players", user_id, "pl_materials", pl_ores)


async def apply_item(user_id, i_id, state):
    '''apply only 1 item at a time'''
    # get item quantity by user_id
    # get details to item
    # apply item with conditions
    # reduce used quantity from user_id

    current_state = await state.get_state()
    gps = await m.get_location(user_id)  # remake to state
    loc_features = await space_map.features(gps)
    it_type = await db_read_full_name("items", i_id, "type", "i_id")
    # it_shorname = await db_read_full_name("items", i_id, "it_shortname", "i_id")
    # it_shorname = it_shorname[1:-1]

    # player_quantity = await db_read_dict("players", user_id, "pl_items")
    # player_quantity = player_quantity[it_shorname]


    it_shortname, player_quantity = await get_item_quantity_from_inv(i_id, user_id)
    it_name = await db_read_full_name("items", it_shortname, "it_name", "it_shortname")

    if player_quantity < 1:
        return "Your quantity is < 1"
    print("it_type", it_type)
    if "consumable" in it_type:
        healed_result = await m.restore_hp(user_id, 50) # hardcoded heal            # apply effect_choice function() here
        if healed_result:
            await add_pl_items(user_id, it_shortname, -1) # -1 from inventory
            text = f"used 1 {it_name}, feeling goooood"
        else:
            text = f"already at full hp"
    elif current_state == "State:docked" and "shipyard" in loc_features:
        # can use upgrades
        if "weapons" in it_type:
            text = await equip_weapon(user_id, it_shortname, it_name)
        elif "shields" in it_type:
            text = await equip_item(user_id, it_shortname, it_name, "shields")
        elif "armor" in it_type:
            text = await equip_item(user_id, it_shortname, it_name, "armor")
        elif "scanner" in it_type:
            text = await equip_item(user_id, it_shortname, it_name, "scanner")
        elif "None" in it_type:
            # ERROR
            print("ERROR IN NONE TYPE OF applicable item")
            text = "ERRORRRRRR"
            pass
        else:
            # EXCEPTION
            print("EXCEPTION TYPE OF applicable item")
    else:
        # can not use upgrades, go to shipyard
        text = "Dock for a shipyard to do it for you..."
    return text


async def equip_weapon(user_id, it_shortname, it_name):
    pl_ship_slots = await db_read_dict("players", user_id, "ship_slots")
    pl_weapon_slots = {key:value for key, value in pl_ship_slots.items() if key.startswith("weapons_")} # {'weapons_1': 'rusty_machine_gun', 'weapons_2': ''}
    print("pl_weapon_slots", pl_weapon_slots) 
    slots_count = len(pl_weapon_slots)
    
    old_weapon = pl_weapon_slots.get("weapons_" + str(slots_count))
    await add_pl_items(user_id, old_weapon, 1)

    for i in reversed(range(1,slots_count)):
        print(i)
        pl_weapon_slots.update({"weapons_"+str(i+1) : pl_weapon_slots.get("weapons_"+str(i), "")})
        print("pl_weapon_slots", pl_weapon_slots) 

    pl_weapon_slots.update({"weapons_1":it_shortname})
    pl_ship_slots.update(pl_weapon_slots)

    await add_pl_items(user_id, it_shortname, -1) # -1 from inventory
    await db_write_dict_full("players", user_id, "ship_slots", pl_ship_slots) # write new slots to db
    return "You equipped {it_name} to slot 1. other items changed slots to the right. Last item is in your Inventory".format(it_name=it_name)


async def equip_item(user_id, it_shortname, it_name, it_type):
    pl_ship_slots = await db_read_dict("players", user_id, "ship_slots")
    old_item = pl_ship_slots.get(it_type)
    await add_pl_items(user_id, old_item, 1)
    await add_pl_items(user_id, it_shortname, -1) # -1 from inventory
    pl_ship_slots.update(it_shortname)
    return "You equipped {it_name}. Find your previous {it_type} in {emoji}Inventory".format(it_name=it_name, it_type=it_type, emoji=paperbox)

async def unequip_all_items(user_id):
    pl_ship_slots = await db_read_dict("players", user_id, "ship_slots")
    for key,value in pl_ship_slots.items():
        await add_pl_items(user_id, value, 1) # add 1 item to inventory
        pl_ship_slots.update({key:""})
    return "Unequipped all items."



async def get_item_quantity_from_inv(i_id, user_id):
    it_shortname = await db_read_full_name("items", i_id, "it_shortname", "i_id")
    it_shortname = it_shortname[1:-1]
    player_quantity = await db_read_dict("players", user_id, "pl_items")
    player_quantity = player_quantity[it_shortname]
    return it_shortname, player_quantity


async def sell_item():
    # get item quantity by user_id
    # get details to item
    # reduce used quantity from user_id
    ...


async def sell_material():
    ...

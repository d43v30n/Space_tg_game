from app.database import db_read_dict, db_write_dict_full, db_write_int, db_read_int, db_read_details, db_read_full_name
from game_logic import space_map
from game_logic import mechanics as m


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
    # it_name = await db_read_full_name("items", i_id, "it_name", "i_id")

    # player_quantity = await db_read_dict("players", user_id, "pl_items")
    # player_quantity = player_quantity[it_shorname]


    it_shortname, player_quantity = await get_item_quantity_from_inv(i_id, user_id)

    if player_quantity < 1:
        return "Your quantity is < 1"
    
    if (current_state == "State:docked" or current_state == "State:job") and "shipyard" in loc_features:
        # can use upgrades
        if "consumable" == it_type[1:1]:
            await add_pl_items(user_id, it_shortname, -1) # -1 from inventory
            await m.restore_hp(user_id, 50) # hardcoded heal            # apply effect_choice function() here
        elif "weapons" in it_type:
            # use if in shipyard / docked to station
            pass
        elif "shields" in it_type:
            # use if in shipyard / docked to station
            pass
        elif "armor" in it_type:
            # use if in shipyard / docked to station
            pass
        elif "scanner" in it_type:
            # use if in shipyard / docked to station
            pass
        elif "None" in it_type:
            # ERROR
            print("ERROR IN NONE TYPE OF applicable item")
            pass
        else:
            # EXCEPTION
            print("EXCEPTION TYPE OF applicable item")

    else:
        # can not use upgrades, go to shipyard
        pass


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

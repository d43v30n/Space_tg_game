from app.database import db_read_dict, db_write_dict_full, db_write_int, db_read_int, db_read_details, db_read_full_name
from game_logic import space_map
from game_logic import mechanics as m
from game_logic.states import State

from emojis import *


async def add_pl_exp(user_id, exp):
    old_exp = await db_read_int("players", user_id, "experience")
    await db_write_int("players", user_id, "experience", old_exp + exp)


async def change_pl_credits(user_id, delta_credits):
    old_credits = await db_read_int("players", user_id, "credits")
    new_credits = old_credits + delta_credits
    if new_credits < 0:
        return False, "Not enough {money_bag}Credits".format(money_bag=money_bag)
    else:
        await db_write_int("players", user_id, "credits", new_credits)
        return True, "{money_bag}Credits: {delta_credits}".format(money_bag=money_bag, delta_credits=delta_credits)


async def add_pl_items(user_id, it_shortname, count):
    pl_items = await db_read_dict("players", user_id, "pl_items")
    # print("before IF in add_pl_items", pl_items)
    if pl_items.get(it_shortname, False):  # if item is already in inventory
        count_old = pl_items.get(it_shortname)
        new_count = count+count_old
        if new_count <= 0:
            del pl_items[it_shortname]
            await db_write_dict_full("players", user_id, "pl_items", pl_items)
            return
        pl_items.update({it_shortname: count+count_old})
        # print("inside 1 IF in add_pl_items", pl_items)
        print(
            f"adding item {it_shortname}, player new count =", new_count)
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
        new_count = count+count_old
        if new_count <= 0:
            del pl_materials[mt_shortname]
            await db_write_dict_full("players", user_id, "pl_materials", pl_materials)
            return
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
    current_state = await state.get_state()
    gps = await m.get_location(user_id)  # remake to state
    loc_features = await space_map.features(gps)
    try:
        it_type = await db_read_full_name("items", i_id, "type", "i_id")
        it_shortname, player_quantity = await get_item_quantity_from_inv(i_id, user_id)
    except:
        return "You do not have this item"
    # it_shortname = f"\"{it_shortname}\""
    it_name = await db_read_full_name("items", f"\"{it_shortname}\"", "it_name", "it_shortname")

    if player_quantity < 1:
        return "Your quantity is < 1"
    if "consumable" in it_type:
        # hardcoded heal            # apply effect_choice function() here
        it_effect = await db_read_full_name("items", f"\"{it_shortname}\"", "effects", "it_shortname")
        it_effect = eval(it_effect)
        print("it_effect", it_effect)
        heal_amount = it_effect.get("restore_hp")
        if "restore_hp" in it_effect:
            print("--heal_amount", heal_amount)
            healed_result = await m.restore_hp(user_id, heal_amount, with_cd=False)
            if healed_result:
                # -1 from inventory
                await add_pl_items(user_id, it_shortname, -1)
                text = f"used 1 {it_name}, feeling goooood"
            else:
                text = f"already at full hp"
    elif current_state == "State:docked" and "shipyard" in loc_features:
        # can use upgrades
        if "weapon" in it_type:
            text = await equip_weapon(user_id, it_shortname, it_name)
        elif "shield" in it_type:
            text = await equip_item(user_id, it_shortname, it_name, "shield")
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
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    job_text = "applyied item with i_id={i_id}".format(i_id=i_id)
    await state.clear()
    await state.set_state(State.gps_state)
    await state.update_data(gps_state=gps)
    await state.set_state(State.job)
    await state.update_data(job=job_text)
    await state.set_state(State.docked)
    return text


async def equip_weapon(user_id, it_shortname, it_name):
    pl_ship_slots = await db_read_dict("players", user_id, "ship_slots")
    pl_weapon_slots = {key: value for key, value in pl_ship_slots.items(
    ) if key.startswith("weapon_")}  # {'weapon_1': 'rusty_machine_gun', 'weapon_2': ''}
    print("pl_weapon_slots", pl_weapon_slots)
    slots_count = len(pl_weapon_slots)
    old_weapon = pl_weapon_slots.get("weapon_" + str(slots_count))
    if old_weapon != "":  # skip empty slots
        await add_pl_items(user_id, old_weapon, 1)

    for i in reversed(range(1, slots_count)):
        print(i)
        pl_weapon_slots.update(
            {"weapon_"+str(i+1): pl_weapon_slots.get("weapon_"+str(i), "")})
        print("pl_weapon_slots", pl_weapon_slots)

    pl_weapon_slots.update({"weapon_1": it_shortname})
    pl_ship_slots.update(pl_weapon_slots)

    await add_pl_items(user_id, it_shortname, -1)  # -1 from inventory
    # write new slots to db
    await db_write_dict_full("players", user_id, "ship_slots", pl_ship_slots)
    return "You equipped {it_name} to slot 1. other items changed slots to the right. Your previous weapon form {slots_count} in {emoji}Inventory".format(it_name=it_name, emoji=paperbox, slots_count=slots_count)


async def equip_item(user_id, it_shortname, it_name, it_type):
    pl_ship_slots = await db_read_dict("players", user_id, "ship_slots")
    old_item = pl_ship_slots.get(it_type)
    print("old_item", old_item)
    print("new it_shortname", it_shortname)
    if old_item != "":  # skip empty slots
        await add_pl_items(user_id, old_item[1:-1], 1)
    await add_pl_items(user_id, it_shortname, -1)  # -1 from inventory
    pl_ship_slots.update({it_type: it_shortname})
    # write new slots to db
    await db_write_dict_full("players", user_id, "ship_slots", pl_ship_slots)
    return "You equipped {it_name}. Find your previous {it_type} in {emoji}Inventory".format(it_name=it_name, it_type=it_type, emoji=paperbox)


async def unequip_all_items(user_id, state):
    current_state = await state.get_state()
    gps = await m.get_location(user_id)  # remake to state
    loc_features = await space_map.features(gps)

    if current_state == "State:docked" and "shipyard" in loc_features:

        pl_ship_slots = await db_read_dict("players", user_id, "ship_slots")
        for key, value in pl_ship_slots.items():
            if value == "":  # skip empty slots
                continue
            # value = f"\"{value}\""
            await add_pl_items(user_id, value, 1)  # add 1 item to inventory
            pl_ship_slots.update({key: ""})
        print("FINAL ITEMS ARE:", pl_ship_slots)
        # write new slots to db
        await db_write_dict_full("players", user_id, "ship_slots", pl_ship_slots)
        return "Unequipped all items."
    else:
        text = "Dock for a shipyard to do it for you..."
    return text


async def get_item_quantity_from_inv(i_id, user_id):
    it_shortname = await db_read_full_name("items", i_id, "it_shortname", "i_id")
    it_shortname = it_shortname[1:-1]
    try:
        player_quantity = await db_read_dict("players", user_id, "pl_items")
        player_quantity = player_quantity[it_shortname]
    except:
        return "You do not have this item"
    return it_shortname, player_quantity


async def sell_item():
    # get item quantity by user_id
    # get details to item
    # reduce used quantity from user_id
    ...


async def sell_material():
    ...


async def craft_item(user_id, i_id) -> bool:
    recepie = await db_read_details("items", i_id, "craft", "i_id")
    it_shortname = await db_read_full_name("items", i_id, "it_shortname", "i_id")
    # it_shortname = it_shortname[1:-1]

    pl_items, pl_materials = await m.get_player_information(user_id, "pl_items", "pl_materials")
    print("sdfdsf ", pl_items, pl_materials)
    pl_items = eval(pl_items)
    pl_materials = eval(pl_materials)
    old_credits = await db_read_int("players", user_id, "credits")
    igredients_str = []
    if recepie is None:
        return False, "This item is not craftable! Your cheating will be reported!!"
    for item, count in recepie.items():
        # print(f"need {count} of {item}")
        ingredient_name = await db_read_full_name("items", item, "it_shortname", "it_shortname")
        if int(pl_items.get(item, 0)) >= count:
            await add_pl_items(user_id, item, -count)
            igredients_str.append(f"{count}x of {ingredient_name}")
            pass
        elif int(pl_materials.get(item, 0)) >= count:
            igredients_str.append(f"{count}x of {ingredient_name}")
            await add_pl_materials(user_id, item, -count)
            #     # craft_materials_dict.update({count: count})
            pass
        elif item == "credits" and old_credits >= count:
            await change_pl_credits(user_id, -count)
            igredients_str.append("{emoji}Credits: -{count}".format(
                emoji=money_bag, count=count))
        else:
            # print(
            # f"{count} of {ingredient_name} is not enough. {pl_materials.get(item, 0)}/{pl_items.get(item, 0)} is needed")
            # max() is to filter 0 out
            return False, f"You need: {count} of {ingredient_name}\nYou have only {max(pl_materials.get(item, 0), pl_items.get(item, 0))}."
    await add_pl_items(user_id, it_shortname[1:-1], 1)
    return True, "\n".join(igredients_str)

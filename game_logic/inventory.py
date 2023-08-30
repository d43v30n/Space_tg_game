from app.database import db_read_dict, db_write_dict_full, db_write_int, db_read_int, db_read_details, db_read_full_name


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


async def apply_item(user_id, item_id):
    # get item quantity by user_id
    # get details to item
    # apply item with conditions
    # reduce used quantity from user_id
    item_data = db_read_details()
    item_name = db_read_full_name


async def sell_item():
    # get item quantity by user_id
    # get details to item
    # reduce used quantity from user_id
    ...


async def sell_material():
    ...

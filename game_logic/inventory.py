from app.database import db_read_dict, db_write_dict_full

async def add_pl_items(user_id, it_shortname, count):
    pl_items = await db_read_dict("players", user_id, "pl_items")
    print("before IF in add_pl_items", pl_items)
    if pl_items.get(it_shortname, False):  # if item is already in inventory
        count_old = pl_items.get(it_shortname)
        pl_items.update({it_shortname: count+count_old})
        print("inside 1 IF in add_pl_items", pl_items)
        print(
            f"adding item {it_shortname}, player owned count =", count, " + ", count_old)
    else:
        count_old = pl_items.get(it_shortname)
        pl_items.update({it_shortname: count})
        print(
            f"inventory was empty ({count_old}), adding {it_shortname} (x{count})")
        print("inside 2 IF in add_pl_items", pl_items)
    # new function to update value in dictionary
    await db_write_dict_full("players", user_id, "pl_items", pl_items)


async def add_pl_materials(user_id, mt_shortname, count):
    pl_materials = await db_read_dict("players", user_id, "pl_materials")
    print("before IF in add_pl_materials", pl_materials)
    if pl_materials.get(mt_shortname, False):  # if item is already in inventory
        count_old = pl_materials.get(mt_shortname)
        pl_materials.update({mt_shortname: count+count_old})
        print("inside 1 IF in add_pl_materials", pl_materials)
        print(
            f"adding item {mt_shortname}, player owned count =", count, " + ", count_old)
    else:
        count_old = pl_materials.get(mt_shortname)
        pl_materials.update({mt_shortname: count})
        print(
            f"inventory was empty ({count_old}), adding {mt_shortname} (x{count})")
        print("inside 2 IF in add_pl_materials", pl_materials)
    # new function to update value in dictionary
    await db_write_dict_full("players", user_id, "pl_materials", pl_materials)
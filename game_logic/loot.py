from aiogram.types import Message
from app.database import db_parse_mt_drop_locations
from random import randint
import game_logic.inventory as invent
import game_logic.mechanics as m
from game_logic.space_map import *
from game_logic.states import State
import keyboards.main_kb as kb



async def init_loot_at_loc(user_id, gps: int) -> dict:
    all_loot = await db_parse_mt_drop_locations(gps)
    drop_text = []

    for material in all_loot:
        mt_name, mt_shortname, mt_drop = material
        mt_drop_dict = eval(mt_drop)  # Convert mt_drop string to a dictionary
        count = mt_drop_dict.get("count", 1)
        chance = mt_drop_dict.get("chance", 1)
        min_loc = mt_drop_dict.get("min_loc", 0)
        max_loc = mt_drop_dict.get("max_loc", 0)
        
        if min_loc <= gps <= max_loc:
            flag = await m.roll_chance(chance)
            if flag:
                await invent.add_pl_materials(user_id, mt_shortname, count)
                drop_text.append(f"You found {mt_name} (x{count}) with chance {chance} ")
                print("LOOOOOOT", drop_text)
    return "\n".join(drop_text)
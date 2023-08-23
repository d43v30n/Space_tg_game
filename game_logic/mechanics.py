from app.database import *
from asyncio import sleep  # create_task, gather
from game_logic import space_map
from random import randint
import keyboards.main_kb as kb


COOLDOWN = 10


async def move_forward(user_id):
    location = await db_read_int("players", user_id, "location")
    location = location + 1
    if await space_map.read_map(location):
        await sleep(COOLDOWN)
        await db_write_int("players", user_id, "location", location)
        return location
    else:
        return None


async def jump_home(user_id):
    home = 0
    await sleep(COOLDOWN)
    await db_write_int("players", user_id, "location", home)


async def get_location(user_id):
    return await db_read_int("players", user_id, "location")


async def get_max_energy(user_id):
    return await db_read_int("players", user_id, "max_energy")


async def get_current_energy(user_id):
    return await db_read_int("players", user_id, "current_energy")


async def get_player_information(user_id, info_type, *args: str) -> tuple:
    if args:
        items = []
        if info_type == "attributes":
            for item in args:
                attributes = await db_read_dict("players", user_id, "attributes")
                items.append(attributes.get(item))
        elif info_type == "stats":
            for item in args:
                stats = await db_read_dict("players", user_id, "stats")
                items.append(stats.get(item))
        return items


async def get_energy(user_id) -> tuple:
    '''("current_energy", "max_energy")'''
    energy = await get_current_energy(user_id), await get_max_energy(user_id)
    return energy


# async def add_task_scheduler(function, offset, *args) -> None:
#     '''schedule Task to global var tasks
#     offset is schedule to run after.. seconds'''
#     global task_scheduler
#     task_scheduler = sched.scheduler(time.time, time.sleep)
#     task_scheduler.enter(offset, 1, create_task, (function(*args),))

async def roll_chance(chance: float) -> bool:
    '''chance is float, min 0.00001 max 1'''
    val = randint(1, 100000)/100000
    if val <= float(chance):
        print(f"Chance of {chance} rolled for True with {val}")
        return True
    else:
        print(f"Chance of {chance} rolled for False with {val}")
        return False


async def rand_event(gps) -> str:
    loc_features = await space_map.features(gps)
    variants = ["randevent"]
    possible_enemies = await db_read_enemies_attributes(gps)
    variants += possible_enemies
    print("variants", variants)
    for en_id in possible_enemies:
        chance = await db_read_details("enemies", en_id, "attributes", "en_id")
        chance = chance.get("chance")
        if await roll_chance(chance):
            enemy_name = await db_read_details("enemies", en_id, "en_name", "en_id")
            return enemy_name
        else:
            return None
    else:
        return None
    # loc_name = await space_map.name(gps)
    # keyboard = await kb.keyboard_selector(state)

    # if "enemy" in loc_features:
    #     if roll_chance(0.1):
    #         await message.answer(f"You arrived to {loc_name}", reply_markup=keyboard)

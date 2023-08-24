from app.database import *
from asyncio import sleep  # create_task, gather
from game_logic import space_map
from random import randint, choice
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


async def get_player_information(user_id, *args: str) -> list:
    '''returns list of strings'''
    items = []
    for item in args:
        if item == "inventory":
            inventory = await db_read_dict("players", user_id, "inventory")
            items.append(inventory)
        elif item == "cargo":
            cargo = await db_read_dict("players", user_id, "cargo")
            items.append(cargo)
        elif item == "ship_slots":
            ship_slots = await db_read_dict("players", user_id, "ship_slots")
            items.append(ship_slots)
        elif item == "attributes":
            attributes = await db_read_dict("players", user_id, "attributes")
            items.append(attributes)
        elif item == "abilities":
            abilities = await db_read_dict("players", user_id, "abilities")
            items.append(abilities)
        else:
            column = await db_read_int("players", user_id, item)
            items.append(column)
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
        # print(f"Chance of {chance} rolled for True with {val}")
        return True
    else:
        # print(f"Chance of {chance} rolled for False with {val}")
        return False


async def rand_event(gps) -> str:
    events = await space_map.event(gps)
    event = choice(events)
    # event = None
    if event == "enemies":
        # print("rolled for enemie...")
        possible_enemies = await db_read_enemies_attributes(gps)
        for en_shortname in possible_enemies:
            chance = await db_read_details("enemies", en_shortname, "attributes", "en_shortname")
            # print(F"trying to spawn {en_shortname} with chance={chance}")
            chance = chance.get("chance")
            if await roll_chance(chance):
                enemy_name = await db_read_details("enemies", en_shortname, "en_name", "en_shortname")
                return enemy_name
            else:
                return None
        else:
            return None
    elif event == "drop":
        chance = 0
        if await roll_chance(chance):
            drop_name = None
            return drop_name
        else:
            return None
    elif event == "":  # other events
        pass

from app.database import *
from asyncio import sleep  # create_task, gather
from game_logic import space_map, energy_manager
from random import randint, choice
import keyboards.main_kb as kb
from handlers import errors
from emojis import *


COOLDOWN = 10
COOLDOWN_HEAL = 20


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


async def mine_here(user_id):
    await energy_manager.use_one_energy(user_id)
    await sleep(COOLDOWN)


async def scan_area(user_id):
    await energy_manager.use_one_energy(user_id)
    await sleep(COOLDOWN)


async def teleport_home(user_id):
    home = 0
    await db_write_int("players", user_id, "location", home)


async def get_location(user_id):
    return await db_read_int("players", user_id, "location")


async def get_max_energy(user_id):
    return await db_read_int("players", user_id, "max_energy")


async def get_current_energy(user_id):
    return await db_read_int("players", user_id, "current_energy")


async def get_main_text_row(user_id):
    attributes = await get_player_information(user_id, "attributes")
    information = await get_player_information(user_id, "current_health", "max_health", "credits", "experience", "level", "main_quest", "side_quest", "ship_type", "abilities")
    faction = attributes[0].get("faction")
    gps = await get_location(user_id)
    loc_name = await space_map.name(gps)
    energy = await get_energy(user_id)
    current_energy, max_energy = energy  # Unpack the energy tuple
    current_health, max_health, player_credits, experience, level, main_quest, side_quest, ship_type, abilities = information

    # Use .format() for string formatting with custom emojis
    row1= "{loc_name}\n".format(loc_name=loc_name)
    row2 = "{gps_emj}{gps} {heart}{current_health}/{max_health} {energy_smiley}{current_energy}/{max_energy}".format(
        gps_emj=gps_emj, gps=gps, heart=heart, current_health=current_health, max_health=max_health, current_energy=current_energy, max_energy=max_energy, energy_smiley=energy_smiley
    )
    row3 = f"Faction: {faction}\n\nShip Stats:\nHP: {current_health}/{max_health},\nmain_quest: {main_quest}\nside_quest: {side_quest}\n\nCredits: {player_credits}\nExperience: {experience}\nLevel: {level}"
    return row1, row2, row3


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


async def restore_hp(user_id):
    current_hp = await db_read_int("players", user_id, "current_health")
    max_hp = await db_read_int("players", user_id, "max_health")
    if current_hp < max_hp:
        await sleep(COOLDOWN_HEAL)
        await db_write_int("players", user_id, "current_health", max_hp)
        return True
    else:
        return False

async def player_dead(user_id):
    await db_write_int("players", user_id, "current_health", 1) # set 1 hp 
    await jump_home(user_id)


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
    val = randint(1, 100000) / 100000
    if val <= float(chance):
        print(f"Chance of {chance} rolled for True with {val}")
        return True
    else:
        print(f"Chance of {chance} rolled for False with {val}")
        return False


async def rand_event(gps) -> str:
    events = await space_map.event(gps)
    # event = f"\"{choice(events)}\""
    event = choice(events)
    if event == "enemies":
        # print("rolled for enemie...")
        possible_enemies = await db_read_enemies_attributes(gps)
        print("possible_enemies ", possible_enemies)
        for en_shortname in possible_enemies:
            chance = await db_read_details("enemies", en_shortname, "attributes", "en_shortname")
            chance = chance.get("chance")
            # print(F"trying to spawn {en_shortname} with chance={chance}")
            if await roll_chance(chance):
                print("spawning ", en_shortname)
                return "enemies", en_shortname
    elif event == "drop":
        # possible_materials = 
        chance = 0
        if await roll_chance(chance):

            drop_name = None
            return "drop", drop_name
        else:
            print("no drop")
            return None, None
    elif event == "":  # other events
        print("event == ''   this should not happen!!")
        pass
    return None, None


async def show_items(user_id) -> str:
    invent_items = await db_read_dict("players", user_id, "pl_items")
    text = ""
    for it_shortname, count in invent_items.items():
        it_shortname = f"\"{it_shortname}\""
        it_name = await db_read_full_name("items", it_shortname, "it_name", "it_shortname")
        it_id = await db_read_full_name("items", it_shortname, "i_id", "it_shortname")
        text += f"- {it_name} (x{count}) /item_{it_id}\n"
    return text


async def show_materials(user_id) -> str:
    invent_materials = await db_read_dict("players", user_id, "pl_materials")
    text = ""
    for mt_shortname, count in invent_materials.items():
        mt_shortname = f"\"{mt_shortname}\""
        mt_name = await db_read_full_name("materials", mt_shortname, "mt_name", "mt_shortname")
        text += f"- {mt_name} (x{count})\n"
    return text



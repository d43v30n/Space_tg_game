from app.database import *
from asyncio import sleep  # create_task, gather
from game_logic import space_map
from random import randint, choices
from app import database as db
from game_logic import energy_manager
from game_logic.states import State
import game_logic.inventory as invent
import keyboards.main_kb as kb
from handlers import errors
from emojis import *


COOLDOWN = 45
COOLDOWN_HEAL = 55


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
    row1 = "<i><b>{loc_name}\n</b></i>".format(loc_name=loc_name)
    row2 = "{gps_emj}{gps} {heart}{current_health}/{max_health} {energy_smiley}{current_energy}/{max_energy}".format(
        gps_emj=gps_emj, gps=gps, heart=heart, current_health=current_health, max_health=max_health, current_energy=current_energy, max_energy=max_energy, energy_smiley=energy_smiley
    )
    row3 = "Faction: {faction}\nmain_quest: {main_quest}\nside_quest: {side_quest}\n\n{money_bag}Credits: {player_credits}\n{bar_chart}Exploration Data: {experience}\nShip AI Level : {level}".format(
        faction=faction, main_quest=main_quest, side_quest=side_quest, money_bag=money_bag,  player_credits=player_credits, bar_chart=bar_chart,
        experience=experience, level=level)
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


async def restore_hp(user_id, count=0, with_cd=True, repair_speed=1):
    current_hp = await db_read_int("players", user_id, "current_health")
    max_hp = await db_read_int("players", user_id, "max_health")
    diff = abs(current_hp - max_hp)
    if current_hp >= max_hp:
        return False
    else:
        if with_cd:
            await sleep(diff * repair_speed)
        if not count:
            new_hp = max_hp
        else:
            new_hp = min(count+current_hp, max_hp)
    await db_write_int("players", user_id, "current_health", new_hp)
    return True


async def player_dead(user_id):
    await db_write_int("players", user_id, "current_health", 1)  # set 1 hp
    await sleep(90)
    await db_write_int("players", user_id, "location", 0)


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
    '''chance is float, in 0.001 max 1'''
    val = randint(1, 1000) / 1000
    if val <= float(chance):
        print(f"Chance of {chance} rolled for True with {val}")
        return True
    else:
        print(f"Chance of {chance} rolled for False with {val}")
        return False


async def rand_event(gps) -> str:
    events = await space_map.events(gps)
    # event = f"\"{choice(events)}\""
    events_list = [key for key in events.keys()]
    event_weights = [value for value in events.values()]
    event = choices(events_list, weights=event_weights)[0]
    print("event of choice is :", event)

    if event == "enemies":
        print("rolled for enemie...")
        possible_enemies = await db_read_enemies_attributes(gps)
        print("possible_enemies ", possible_enemies)
        for en_shortname in possible_enemies:
            chance = await db_read_details("enemies", en_shortname, "attributes", "en_shortname")
            chance = chance.get("chance")
            print(F"trying to spawn {en_shortname} with chance={chance}")
            if await roll_chance(chance):
                print("spawning ", en_shortname)
                return "enemies", en_shortname

    elif event == "mining_event":
        event_details = await space_map.mine_event_details(gps)
        chance = event_details["chance"]
        if await roll_chance(chance):
            print("mining_event ", event_details)
            return "mining_event", event_details
        else:
            print("nothing mined")
            return None, None

    elif event == "scanning_event":
        event_details = await space_map.scan_event_details(gps)
        chance = event_details["chance"]
        # if level ok
        if await roll_chance(chance):
            print("scanning_event ", event_details)
            return f"scanning_event", event_details
        else:
            print("nothing scanned")
            return "map_event", None

    elif event == "encounter":
        event_details = await space_map.encounter_event_details(gps)
        chance = event_details["chance"]
        if await roll_chance(chance):
            print("encounter ", event_details)
            return "encounter", event_details
        else:
            print("nothing scanned")
            return "encounter", None

    elif event == "None":
        return None
    else:  # other events
        print("event exception ''   this should not happen!! [mechanics.py]")
        return None


async def show_items(user_id) -> str:
    invent_items = await db_read_dict("players", user_id, "pl_items")
    text = ""
    for it_shortname, count in invent_items.items():
        it_shortname = f"\"{it_shortname}\""
        it_name = await db_read_full_name("items", it_shortname, "it_name", "it_shortname")
        it_id = await db_read_full_name("items", it_shortname, "i_id", "it_shortname")
        text += f"- {it_name} (x{count}) /use_{it_id}\n"
    return text


async def show_materials(user_id) -> str:
    invent_materials = await db_read_dict("players", user_id, "pl_materials")
    text = ""
    for mt_shortname, count in invent_materials.items():
        mt_shortname = f"\"{mt_shortname}\""
        mt_name = await db_read_full_name("materials", mt_shortname, "mt_name", "mt_shortname")
        text += f"- {mt_name} (x{count})\n"
    return text


async def mine_here(user_id, gps: int, message, state) -> dict:
    possible_ores = await db_parse_all_ores(gps)
    # print("possible_ores are ",possible_ores)
    state_data = await state.get_data()
    text_job = state_data["job"]
    drop_text = []
    for ore in possible_ores:
        mt_name, mt_shortname, mt_drop = ore
        mt_drop_dict = eval(mt_drop)  # Convert mt_drop string to a dictionary
        count = mt_drop_dict.get("count", 1)
        chance = mt_drop_dict.get("chance", 1)
        if not text_job.startswith("after scanning at"):
            chance = chance / 10
        min_loc = mt_drop_dict.get("min_loc", 0)
        max_loc = mt_drop_dict.get("max_loc", 0)

        if min_loc <= gps <= max_loc:
            flag = await roll_chance(chance)
            if flag:
                await invent.add_pl_ores(user_id, mt_shortname[1:-1], count)
                drop_text.append(
                    f"You found {mt_name} (x{count})")  # with chance {chance} ")
                exp = 50
                drop_text.append("{bar_chart}Exploration Data gathered: {exp}.".format(
                    exp=exp, bar_chart=bar_chart))

        state_data = await state.get_data()

    loc_name = await space_map.name(gps)
    await state.set_state(State.mining)
    await state.update_data(job="mining in progress at {loc_name}".format(loc_name=loc_name), mining="mining at {loc_name}...".format(loc_name=loc_name))
    await energy_manager.use_one_energy(message.from_user.id)
    keyboard = await kb.keyboard_selector(state)

    await message.answer("Mining at {loc_name}".format(loc_name=loc_name), reply_markup=keyboard)

    await sleep(COOLDOWN)
    if drop_text == []:
        exp = 30
        drop_text.append(
            "You got no ore this time, maybe you should try somewhere else?\n")
        drop_text.append("{bar_chart}Exploration Data gathered: {exp}.".format(
            exp=exp, bar_chart=bar_chart))
    await invent.add_pl_exp(message.from_user.id, exp)
    return "\n".join(drop_text)


async def scan_area(message, state):
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    text_job = state_data["job"]
    loc_features = await space_map.features(gps)
    loc_name = await space_map.name(gps)
    current_energy = await get_current_energy(message.from_user.id)
    keyboard = await kb.keyboard_selector(state)

    if current_energy >= 1:
        await energy_manager.use_one_energy(message.from_user.id)


# scan event fork

        if text_job.endswith("scanning_event_5"):
            await sleep(COOLDOWN)
            jobtext = "just arrived to {loc_name} and encountered scanning_event_4".format(
                loc_name=loc_name)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)
            return "You should try to scan once more!"

        if text_job.endswith("scanning_event_4"):
            await sleep(COOLDOWN)
            jobtext = "just arrived to {loc_name} and encountered scanning_event_3".format(
                loc_name=loc_name)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)
            return "You should try to scan once more!"

        if text_job.endswith("scanning_event_3"):
            await sleep(COOLDOWN)
            jobtext = "just arrived to {loc_name} and encountered scanning_event_2".format(
                loc_name=loc_name)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)
            return "You should try to scan once more!"

        elif text_job.endswith("scanning_event_2"):
            await sleep(COOLDOWN)
            jobtext = "just arrived to {loc_name} and encountered scanning_event_1".format(
                loc_name=loc_name)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)
            return "You should try to scan once more!"

        elif text_job.endswith("scanning_event_1"):
            await sleep(COOLDOWN)
            jobtext = "after scanning at {loc_name}".format(
                loc_name=loc_name)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)

            result = await trigger_scan_event(message, state)
            # if result[0]:
            #     await message.answer("Sucsessfully mined event.\n{text}".format(text=result[1]), reply_markup=keyboard)
            # else:
            #     await message.answer("Mining event unsecsessful.\n{text}".format(text=result[1]), reply_markup=keyboard)
            result = result[1]
        else:
            if "mining" in loc_features:
                exp = 70
                result = "ore presence"
                jobtext = "after scanning at {loc_name}, found ore".format(
                    loc_name=loc_name)
            elif text_job.endswith("and encountered mining_event"):
                exp = 200
                result = "Presence of suspicious ground fraction is detected. We should try our luck mining it now."
                jobtext = "after scanning at {loc_name}, mining_event".format(
                    loc_name=loc_name)
            else:
                exp = 40
                result = "nothing"
                jobtext = "after scanning at {loc_name}, found nothing.".format(
                    loc_name=loc_name)
            await state.set_state(State.scanning)
            await state.update_data(job="scanning in progress", scanning="scanning at {loc_name}...".format(loc_name=loc_name))
            await message.answer("Scanning at {loc_name}".format(loc_name=loc_name), reply_markup=keyboard)
            await sleep(COOLDOWN)
            await invent.add_pl_exp(message.from_user.id, exp)


# / scan event fork
        await state.clear()
        await state.set_state(State.gps_state)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)
        await state.update_data(job=jobtext)
    else:
        result = None
        await message.answer("Your ship is out of energy! Charge it on Station or with Energy Cell", reply_markup=keyboard)
    return result


async def trigger_scan_event(message, state):
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    # text_job = state_data["job"]
    # loc_features = await space_map.features(gps)
    # loc_name = await space_map.name(gps)
    pl_level = await get_player_information(message.from_user.id, "level")
    event_details = await space_map.scan_event_details(gps)
    if int(event_details["level"]) > pl_level[0]:
        return False, "Your scanner is too small >)"
    # keyboard = await kb.keyboard_selector(state)

    drop_text = []

    only_materials = {key: value for key,
                      value in event_details.items() if key.startswith("material_")}
    print("only_materials", only_materials)
    for mt in only_materials.values():
        count = mt["count"]
        mt_shortname = mt["mt_shortname"]
        mt_shortname = f"\"{mt_shortname}\""
        mt_name = await db_read_full_name("materials", mt_shortname, "mt_name", "mt_shortname")
        text = f"Dropped {mt_name} (x{count})"  # with drop chance {droprate}."
        await invent.add_pl_materials(message.from_user.id, mt_shortname[1:-1], count)
        drop_text.append(text)

    exp = event_details["experience"]
    await invent.add_pl_exp(message.from_user.id, exp)
    exp_text = "Received:\n{bar_chart}Exploration Data: {exp}".format(
        exp=exp, bar_chart=bar_chart)
    drop_text.append(exp_text)
    return True, "\n".join(drop_text)


async def trigger_minings_event(message, state):
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    # text_job = state_data["job"]
    # loc_features = await space_map.features(gps)
    # loc_name = await space_map.name(gps)
    # keyboard = await kb.keyboard_selector(state)
    event_details = await space_map.mine_event_details(gps)
    print("event_details", event_details)
    drop_text = []
    await energy_manager.use_one_energy(message.from_user.id)
    await energy_manager.use_one_energy(message.from_user.id)

    only_materials = {key: value for key,
                      value in event_details.items() if key.startswith("material_")}
    print("only_materials", only_materials)
    for mt in only_materials.values():
        count = mt["count"]
        mt_shortname = mt["mt_shortname"]
        mt_shortname = f"\"{mt_shortname}\""
        mt_name = await db_read_full_name("materials", mt_shortname, "mt_name", "mt_shortname")
        text = f"Dropped {mt_name} (x{count})"  # with drop chance {droprate}."
        await invent.add_pl_materials(message.from_user.id, mt_shortname[1:-1], count)
        drop_text.append(text)

    exp = event_details["experience"]
    await invent.add_pl_exp(message.from_user.id, exp)
    exp_text = "Received:\n{bar_chart}Exploration Data: {exp}".format(
        exp=exp, bar_chart=bar_chart)
    drop_text.append(exp_text)
    return "\n".join(drop_text)


async def buy_item(user_id, item_id):
    price = await db.db_read_int("items", item_id, "price", "i_id")
    it_shortname = await db.db_read_details("items", item_id, "it_shortname", "i_id")
    it_name = await db.db_read_full_name("items", item_id, "it_name", "i_id")
    credits_ok = await invent.change_pl_credits(user_id, -price)
    if credits_ok[0]:
        await invent.add_pl_items(user_id, it_shortname, 1)
        return "Buying {it_name} with /info_{item_id} for {money_bag}{price}".format(it_name=it_name, item_id=item_id, price=price, money_bag=money_bag)
    else:
        return credits_ok[1]


async def craftable_item_list(user_id):
    pl_items, pl_materials = await get_player_information(user_id, "pl_items", "pl_materials")
    search_list = []
    pl_items = eval(pl_items)
    pl_materials = eval(pl_materials)
    search_list.append(pl_items)
    search_list.append(pl_materials)
    print("search_list is ", search_list)
    can_craft_items = []

    craftable_items = await db.db_parse_craftable_items(search_list)
    for item in craftable_items:
        craft_it_shortname, recepie = item
        recepie = eval(recepie)
        recepie.pop("credits", None)
        # check if player has enough materials
        for key, value in recepie.items():
            if int(pl_items.get(key, 0)) >= value:
                # craft_items_dict.update({key: value})
                pass
            elif int(pl_materials.get(key, 0)) >= value:
                # craft_materials_dict.update({key: value})
                pass
            else:
                return "You have not enough materials"
        it_name = await db.db_read_full_name("items", item[0], "it_name", "it_shortname")
        it_id = await db.db_read_full_name("items", item[0], "i_id", "it_shortname")
        can_craft_items.append(it_name + " /craft_" + str(it_id))

    if can_craft_items != []:
        out = "\n".join(can_craft_items)
        return "You can craft:\n{out}".format(out=out)
    else:
        return "You can not craft anything"

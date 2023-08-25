from aiogram.types import Message
from app.database import db_read_details, db_write_int, db_read_int
import asyncio
from random import randint
import game_logic.mechanics as m
from game_logic.space_map import *
from game_logic.states import State
import keyboards.main_kb as kb


async def init_fight(message: Message, enemy_id, state: State):
    user_id = message.from_user.id
    state_data = await state.get_data()
    keyboard = await kb.keyboard_selector(state)
    await state.set_state(State.fighting)
    stats = await m.get_player_information(user_id, "location", "max_health", "current_health", "level", "ship_slots")
    location = int(stats[0])  # to use in possible location debuffs
    max_health = int(stats[1])
    current_health = int(stats[2])
    level = int(stats[3])  # for escaping calc
    ship_slots = {key: value for key, value in stats[4].items() if value != ""}

    player_dmg = await get_player_dmg(ship_slots)
    player_shield = await get_player_shield(ship_slots)
    player_armor = await get_player_armor(ship_slots)

    # dmg calculation
    enemy_stats = await get_enemy_fight_stats(enemy_id)
    en_name = await db_read_details("enemies", enemy_id, "en_name", "en_shortname")
    en_hp = enemy_stats.get("health")
    en_dmg = enemy_stats.get("damage")
    en_arm = enemy_stats.get("armor")
    en_shld = enemy_stats.get("shields")

    await message.answer(f"You are fighting against {en_name}. Yor enemy has HP:{en_hp}, DMG:{en_dmg}", reply_markup=keyboard)

    while current_health > 0 and en_hp > 0:
        # player hit enemy
        eff_player_dmg = max(player_dmg - en_shld, 0)
        en_hp = max(0, en_hp - eff_player_dmg)

        if en_hp <= 0:  # player win
            await get_fight_drop(user_id, enemy_id)
            print("en_hp = ", en_hp)
            print("current_health = ", current_health)
            await state.clear()
            await state.set_state(State.gps_state)
            gps = await m.get_location(message.from_user.id)
            await state.update_data(gps_state=gps)
            await state.set_state(State.job)
            await state.update_data(job=f"Won after fight with {enemy_id}")
            return "win"

        # enemy hit player
        eff_en_dmg = max(en_dmg - player_shield, 0)
        current_health = max(0, current_health - eff_en_dmg)

        if current_health <= 0:  # enemy win
            jump_home_task = await m.player_dead(user_id)
            await message.answer(f"Yo are dead now. Yor enemy had {en_hp}HP left. You will now respawn at home", reply_markup=keyboard)
            await state.clear()
            await state.set_state(State.gps_state)
            gps = await m.get_location(message.from_user.id)
            await state.update_data(gps_state=gps)
            await state.set_state(State.job)
            await state.update_data(job=f"Loose after fight with {enemy_id}")
            return "loose"
        await db_write_int("players", user_id, "current_health", current_health)
    print("en_hp = ", en_hp)
    print("current_health = ", current_health)


async def get_player_dmg(ship_slots) -> int:
    weapons = {key: value for key, value in ship_slots.items()
               if key.startswith("weapons")}
    player_dmg = 0
    if not weapons is None:
        for weapon in weapons.values():
            it_shortname = f"\"{weapon}\""
            it_effects = await db_read_details("items", it_shortname, "effects", "it_shortname")

            crit_multiplier = 1.5
            player_dmg += int(randint(it_effects.get("damage_min"),
                              it_effects.get("damage_max"))*crit_multiplier)
    return player_dmg


async def get_player_shield(ship_slots) -> int:
    shields = {key: value for key, value in ship_slots.items() if key.startswith(
        "shield")}  # possible to have ship with multiple shield slots
    # print("shld", shields)
    player_shield = 0
    if not shields is None:
        for shield in shields.values():
            it_shortname = f"\"{shield}\""
            it_effects = await db_read_details("items", it_shortname, "effects", "it_shortname")
            player_shield += int((it_effects.get("shield")))
    return player_shield


async def get_player_armor(ship_slots) -> int:
    armors = {key: value for key, value in ship_slots.items() if key.startswith(
        "armor")}  # possible to have ship with multiple armor slots
    # print("arm", armors)
    player_armor = 0
    if not armors is None:
        for armor in armors.values():
            it_shortname = f"\"{armor}\""
            it_effects = await db_read_details("items", it_shortname, "effects", "it_shortname")
            player_armor += int((it_effects.get("armor")))
    return player_armor


async def get_enemy_fight_stats(en_shortname):
    # enemy = f"\"{en_shortname}\""
    enemy = en_shortname
    stats = await db_read_details("enemies", enemy, "stats", "en_shortname")
    return stats


async def get_fight_drop(user_id, en_shortname):
    # en_shortname = f"\"{en_shortname}\""
    drop = []
    en_drop = await db_read_details("enemies", en_shortname, "en_drop", "en_shortname")
    
    
    # credits
    got_credits = en_drop.get("credits")
    drop.append(f"Credits: {got_credits}")
    old_credits = await db_read_int("players", user_id, "credits")
    await db_write_int("players", user_id, "credits", old_credits + got_credits)

    # exp
    exp = en_drop.get("exp")
    drop.append(f"Experience : {exp}")
    old_exp = await db_read_int("players", user_id, "experience")
    await db_write_int("players", user_id, "experience", old_exp + exp)

    #items
    en_drop_items = {key: value for key, value in en_drop.items() if key.startswith(
        "it_name_")}
    print("en_drop_items", en_drop_items)
    # {'it_name_1': {'droprate': 0.5, 'scrap_metal': 1}}
    for drop_only_items in en_drop_items.values():
        try:
            droprate = drop_only_items.get("droprate")
        except:
            droprate = 1  # defauld drop rate ist 100%
        print()
        only_items = {key: value for key,
                      value in drop_only_items.items() if key != "droprate"}
        # for item, count in only_items:
        #     it_shortname = item
        #     text = f"Dropped {it_shortname} (x{count}) with drop chance {droprate}."
        #     drop.append(text)
    print("drop", drop)
    old_items = await db_read_int("players", user_id, "pl_items")


    
    
    #materials
    old_materials = await db_read_int("players", user_id, "pl_materials")
    en_drop_materials = {key: value for key, value in en_drop.items() if key.startswith(
        "mt_name_")}
    print("en_drop_materials", en_drop_materials)
    


    print(old_items)
    print(old_materials)

    return "\n".join(drop)


async def timer():
    print("awaiting timer")
    await asyncio.sleep(60)
    print("timer ended")

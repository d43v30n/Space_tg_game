from aiogram.types import Message
from app.database import db_read_details
import asyncio
from random import randint
from game_logic.space_map import *
from game_logic.mechanics import get_player_information, jump_home


async def init_fight(message: Message, enemy_id):
    user_id = message.from_user.id
    stats = await get_player_information(user_id, "location", "max_health", "current_health", "level", "ship_slots")
    # print(stats)
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
    en_hp = enemy_stats.get("health")
    en_dmg = enemy_stats.get("damage")
    en_arm = enemy_stats.get("armor")
    en_shld = enemy_stats.get("shields")

    while current_health > 0 and en_hp > 0:
        # player hit enemy
        eff_player_dmg = max(player_dmg - en_shld, 0)
        en_hp = max(0, en_hp - eff_player_dmg)

        if en_hp <= 0:  # player win
            loot = await get_fight_drop(user_id, enemy_id)

            return "win"

        # enemy hit player
        eff_en_dmg = max(en_dmg - player_shield, 0)
        current_health = max(0, current_health - eff_en_dmg)

        if current_health <= 0:  # enemy win
            jump_home_task = await jump_home(user_id)
            return "loose"
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
    drop_items = await db_read_details("enemies", en_shortname, "en_drop", "en_shortname")
    exp = drop_items.get("exp")
    credits = drop_items.get("credits")
    drop.append(exp)
    drop.append(credits)
    items = {key: value for key, value in drop_items.items() if key.startswith(
        "it_name")}
    for item in items.values():
        drop.append(item)
    print("drop", drop)
    return drop  # [exp, credits, loot]


async def timer():
    print("awaiting timer")
    await asyncio.sleep(60)
    print("timer ended")

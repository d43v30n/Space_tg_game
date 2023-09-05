from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

from dotenv import load_dotenv
from os import getenv

from app import database as db
from game_logic import energy_manager, space_map, fight
from game_logic import mechanics as m
from game_logic import inventory as invent
from game_logic.states import State
from handlers import errors

import keyboards.main_kb as kb

# debug:
from game_logic import fight

load_dotenv()
router = Router()
ADMIN_ID = getenv("ADMIN_ID")


@router.message(State.admin, Command("get_image_id"))
async def adm_test_handler(message: Message, state: FSMContext) -> None:
    # await message.answer_photo("AgACAgIAAxkDAAI03WTvhfh9byTLKl1_AAF9C6nG4wO4HwACUskxG2EPgUs4-mQ4o3GyRQEAAwIAA3kAAzAE")
    file_ids = []
    image_from_pc = FSInputFile("images/ringworld.png")
    result = await message.answer_photo(
        image_from_pc,
        caption="Изображение из файла на компьютере"
    )
    file_ids.append(result.photo[-1].file_id)

    await message.answer("Отправленные файлы:\n"+"\n".join(file_ids))


@router.message(Command("admin"))
async def adm_login_handler(message: Message, state: FSMContext) -> None:
    global ADMIN_ID
    if message.from_user.id == int(ADMIN_ID):
        print("Admin logged in id=", message.from_user.id)
        await state.clear()
        await state.set_state(State.admin)
        await message.answer(f"Hi Admin!", reply_markup=kb.admin_kb())
    else:
        await errors.unknown_input_handler(message, state)


@router.message(State.admin, Command("logout"))
async def adm_logout_handler(message: Message, state: FSMContext) -> None:
    global ADMIN_ID
    if message.from_user.id == int(ADMIN_ID):
        print("Admin logged out id=", message.from_user.id)
        await errors.reset_handler(message, state)
        await message.answer(f"Bye Admin!", reply_markup=kb.main_kb())
    else:
        await errors.reset_handler(message, state)


@router.message(State.admin, Command("help"))
async def adm_help_handler(message: Message, state: FSMContext) -> None:
    await message.answer(f"/admin\n/logout\n/list_all_users\n\nDatabase commands:\n/load_enemies\n/load_items\n/load_materials\n\nBalancing info:\n/list_materials_drop\n/list_all_enemies\n\n/get_image_id\n/test_fight\n\nUnder dev:\n/add_materials", reply_markup=kb.admin_kb())


@router.message(State.admin, Command("load_enemies"))
async def adm_load_enemies_handler(message: Message, state: FSMContext) -> None:
    await message.answer(f"Loading enemies from json to db", reply_markup=kb.admin_kb())
    await db.db_write_enemies_json()


@router.message(State.admin, Command("load_items"))
async def adm_load_items_handler(message: Message, state: FSMContext) -> None:
    await message.answer(f"Loading items from json to db", reply_markup=kb.admin_kb())
    await db.db_write_items_json()


@router.message(State.admin, Command("load_materials"))
async def adm_load_materials_handler(message: Message, state: FSMContext) -> None:
    await message.answer(f"Loading materials from json to db", reply_markup=kb.admin_kb())
    await db.db_write_materials_json()


# @router.message(State.admin, Command("add_materials"))
# async def adm_load_materials_handler(message: Message, state: FSMContext) -> None:
#     current_state = await state.get_state()


@router.message(State.admin, Command("list_all_users"))
async def adm_list_all_users_handler(message: Message, state: FSMContext) -> None:
    users = await db.list_all_users()
    user_list = []
    for user in users:
        tg_id, tg_name, experience, credits, pl_items, pl_materials = user
        tg_id = str(tg_id)
        experience = str(experience)
        credits = str(credits)
        tg_name = "@" + tg_name
        user_text = [tg_id, tg_name, experience,
                     credits, pl_items, pl_materials]
        text = " ".join(user_text)
        user_list.append(text)
    await message.answer("\n".join(user_list), reply_markup=kb.admin_kb())


@router.message(State.admin, Command("list_all_enemies"))
async def adm_list_all_enemies_handler(message: Message, state: FSMContext) -> None:
    enemies = await db.list_all_enemies()
    enemy_list = []
    for enemy in enemies:
        en_id, en_name, en_shortname, desc, type, attributes, stats,  en_drop = enemy
        text = str(en_id) + " " + en_name + " " + stats
        enemy_list.append(text)
    await message.answer("\n".join(enemy_list), reply_markup=kb.admin_kb())


@router.message(State.admin, Command("list_materials_drop"))
async def adm_list_materials_drop_handler(message: Message, state: FSMContext) -> None:
    out = []
    for i in range(18+1):
        gps = i
        ores_data = await db.db_parse_all_ores(gps)
        for data in ores_data:
            name = data[0]
            data_dict = eval(data[2])
            min_loc = int(data_dict.get("min_loc"))
            max_loc = int(data_dict.get("max_loc"))
            features = await space_map.features(i)
            mining = False
            if "mining" in features:
                mining = True
            if min_loc <= i <= max_loc:
                # print(f"DROP at {gps}: Ore: {name},")
                out.append(f"DROP at GPS{str(i).ljust(2)}[{mining}]: {name}")
    await message.answer(f"Here is list of materials drop:", reply_markup=kb.admin_kb())
    await message.answer("\n".join(out), reply_markup=kb.admin_kb())


@router.message(State.admin, Command("test_fight"))
async def echo_image_id(message: Message, state: FSMContext) -> None:
    await fight.get_fight_drop(message.from_user.id, "\"ironclad_ivan\"")


@router.message(State.admin, Command("test"))
async def echo_image_id(message: Message, state: FSMContext) -> None:
    out = await fight.engaging_enemy_choice(message.from_user.id, "\"elon_musk\"")
    if out:
        await message.answer("True", reply_markup=kb.admin_kb())
    else:
        await message.answer("False", reply_markup=kb.admin_kb())

    print("out", out)

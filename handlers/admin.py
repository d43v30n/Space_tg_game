from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from dotenv import load_dotenv
from os import getenv

from app import database as db
from game_logic import loot
from game_logic import mechanics as m
from game_logic.states import State
from handlers import errors

import keyboards.main_kb as kb

# debug:
from game_logic import fight

load_dotenv()
router = Router()
ADMIN_ID = getenv("ADMIN_ID")


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
    await message.answer(f"/admin\n/logout\n/load_enemies\n/load_items\n/load_materials\n/add_materials", reply_markup=kb.admin_kb())


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


@router.message(State.admin, Command("test"))
async def adm_test_handler(message: Message, state: FSMContext) -> None:
    out = await loot.init_loot_at_loc(2)
    print("out", out)
    # for i in range(18):
    #     gps=i
    #     result = await db.db_parse_mt_drop_locations(gps)
    #     print(f"DROP at {gps} = ", result)


@router.message(State.admin, Command("add_materials"))
async def adm_load_materials_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

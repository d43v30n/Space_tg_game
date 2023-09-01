from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from emojis import *

from game_logic import mechanics as m
from game_logic import space_map
from game_logic import inventory as invent
from app.database import db_read_full_name
from handlers import errors

import keyboards.main_kb as kb

router = Router()


@router.message(F.text == "Ship info")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    keyboard = await kb.keyboard_selector(state)

    info = await m.get_player_information(message.from_user.id, "ship_slots")
    # print(info)

    wep_header = "Weapons"
    shl_header = "Shields"
    arm_header = "Armor"
    sca_header = "Scanner"
    empty_slot = "[empty-slot]"
    damage = None
    defence = None
    weapons = []
    shields = []
    armor = []
    scanners = []
    table = []
    for slot_type, eq_item in info[0].items():
        if eq_item == "":
            eq_item_name = empty_slot
        else:
            eq_item = f"\"{eq_item}\""
            eq_item_name = await db_read_full_name("items", eq_item, "it_name", "it_shortname")
        eq_item_name = "<b>" + eq_item_name[1:-1].ljust(26, " ") + "</b>"

        if slot_type.startswith("weapon"):
            weapons.append("|> " + eq_item_name + "|")
        elif slot_type.startswith("shield"):
            shields.append("|> " + eq_item_name + "|")
        elif slot_type.startswith("armor"):
            armor.append("|> " + eq_item_name + "|")
        elif slot_type.startswith("scanner"):
            scanners.append("|> " + eq_item_name + "|")
    table.append("|" + wep_header.center(28, "=") + "|")
    for _ in weapons:
        table.append(_)
    table.append("\n|" + shl_header.center(28, "=") + "|")
    for _ in shields:
        table.append(_)
    table.append("\n|" + arm_header.center(28, "=") + "|")
    for _ in armor:
        table.append(_)
    table.append("\n|" + sca_header.center(28, "=") + "|")
    for _ in scanners:
        table.append(_)


    await message.answer("Damage: {damage}\nDefence: {defence}\nShields: {shields}\n\n\n<code>{table}</code>\n\nYou can unequip all items with\n/unequip_all_items".format(
        damage=damage, defence=defence, shields=shields, table="\n".join(table)), reply_markup=keyboard)


@router.message(F.text == "Guild")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        gps = state_data["gps_state"]
        keyboard = await kb.keyboard_selector(state)
        await message.answer(f"Here is your Guild info", reply_markup=keyboard)
    except:
        await errors.unknown_input_handler(message, state)


@router.message(Command("unequip_all_items"))
async def echo_image_id(message: Message, state: FSMContext) -> None:
    text = await invent.unequip_all_items(message.from_user.id, state)
    keyboard = await kb.keyboard_selector(state)
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "{emoji}Cargo".format(emoji=barrel))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    # try:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    keyboard = await kb.keyboard_selector(state)
    cargo = await m.show_materials(message.from_user.id)
    await message.answer(f"Here is your Cargo:\n{cargo}", reply_markup=keyboard)
    # except:
    #    await errors.unknown_input_handler(message, state)


@router.message(F.text == "{emoji}Inventory".format(emoji=paperbox))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    # try:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    keyboard = await kb.keyboard_selector(state)
    inv = await m.show_items(message.from_user.id)
    await message.answer(f"Here is your Inventory:\n{inv}", reply_markup=keyboard)
    # except:
    #    await errors.unknown_input_handler(message, state)


@router.message(F.text.startswith("/item_"))
async def item_selector_handler(message: Message, state: FSMContext) -> None:
    text = message.text
    keyboard = await kb.keyboard_selector(state)
    current_state = await state.get_state()
    if current_state != "State:job" and current_state != "State:docked":
        await message.answer(f"You can not do this right now", reply_markup=keyboard)
        return
    if text.startswith("/item_"):
        # try:
        id = str(message.text)
        flag = id.split("_")[0][1:]
        id = int(id.split("_")[1])
        print(f"applying {flag} with id {id}")
        await message.answer(f"Using {text} 1x".format(text=text), reply_markup=keyboard)
        out = await invent.apply_item(message.from_user.id, id, state)
        await message.answer(out, reply_markup=keyboard)

        # except:
        #     print("ERROR")

    else:
        print(f"wrong_command_exception: ", message.text)
        await errors.unknown_input_handler(message, state)

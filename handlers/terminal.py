from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from emojis import *

from game_logic.states import State
from game_logic import mechanics as m
# from game_logic import enregy_manager as em

from handlers import errors

import keyboards.main_kb as kb

router = Router()


@router.message(F.text == "Ship info")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    keyboard = await kb.keyboard_selector(state)
    # gps = state_data["gps_state"]
    # attributes = await m.get_player_information(message.from_user.id, "attributes")
    # faction = attributes[0].get("faction")
    # energy = await m.get_energy(message.from_user.id)
    # current_energy = energy[0]
    # max_energy = energy[1]
    # information = await m.get_player_information(message.from_user.id, "current_health", "max_health", "credits", "experience", "level", "main_quest", "side_quest", "ship_type", "abilities")
    # current_health = information[0]
    # max_health = information[1]
    # player_credits = information[2]
    # experience = information[3]
    # level = information[4]
    # main_quest = information[5]
    # side_quest = information[6]
    # ship_type = information[7]
    # abilities = information[8]
    info = await m.get_player_information(message.from_user.id, "ship_slots")
    shields = f"".center(11, "-")
    wep_header = "|--------Weapons---------|"
    shl_header = "|--------Shields---------|"
    arm_header = "|---------Armor----------|"
    sca_header = "|--------Scanner---------|"
    emp_header = "|------------------------|"
    headers = {"weapons":"|--Weapons--|", "shields":"|--Shields--|", "armor":"|---Armor---|", "scanner":"|--Scanner--|"}
    damage = None
    defence = None
    weapons = []
    shields = []
    armor = []
    scanners = []
    table = []
    print(info)
    for slot_type, eq_item in info[0].items():
        if slot_type.startswith("weapons"):
            weapons.append("|" + eq_item + "|")
        elif slot_type.startswith("shields"):
            shields.append("|" + eq_item + "|")
        elif slot_type.startswith("armor"):
            armor.append("|" + eq_item + "|")
        elif slot_type.startswith("scanners"):
            scanners.append("|" + eq_item + "|")
    table.append(wep_header)
    for _ in weapons:
        _.ljust(26, "-")
        table.append(_)
    table.append(shl_header)
    for _ in shields:
        _.ljust(26, "-")
        table.append(_)
    table.append(arm_header)
    for _ in armor:
        _.ljust(26, "-")
        table.append(_)
    table.append(sca_header)
    for _ in scanners:
        _.ljust(26, "-")
        table.append(_)


    armor = f"".center(11, "-")
        


    await message.answer("Damage: {damage}\nDefence: {defence}\nShields: {shields}\n\n\n<code>{table}</code>".format(damage=damage, defence=defence, shields=shields, table="\n".join(table)), reply_markup=keyboard)


@router.message(F.text == "Guild")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        gps = state_data["gps_state"]
        keyboard = await kb.keyboard_selector(state)
        await message.answer(f"Here is your Guild info", reply_markup=keyboard)
    except:
        await errors.unknown_input_handler(message, state)


@router.message(F.text == "{emoji}Cargo".format(emoji=barrel))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    #try:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    keyboard = await kb.keyboard_selector(state)
    cargo = await m.show_materials(message.from_user.id)
    await message.answer(f"Here is your Cargo:\n{cargo}", reply_markup=keyboard)
    #except:
    #    await errors.unknown_input_handler(message, state)


@router.message(F.text == "{emoji}Inventory".format(emoji=paperbox))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    #try:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    keyboard = await kb.keyboard_selector(state)
    inv = await m.show_items(message.from_user.id)
    await message.answer(f"Here is your Inventory:\n{inv}", reply_markup=keyboard)
    #except:
    #    await errors.unknown_input_handler(message, state)


@router.message(F.text.startswith("/item_"))
async def item_selector_handler(message: Message, state: FSMContext) -> None:
    text = message.text
    current_state = await state.get_state()
    if current_state != "State:job":
        keyboard = await kb.keyboard_selector(state)
        await message.answer(f"You can not do this right now", reply_markup=keyboard)
        return
    if text.startswith("/item_"):
        try:
            id = str(message.text)
            flag = id.split("_")[0][1:]
            id = int(id.split("_")[1])
            print(f"applying {flag} with id {id}")
            await ()
        except:
            print("ERROR")

        state_data = await state.get_data()
        gps = state_data["gps_state"]
        job_text = f"applying {flag} with id {id}"
        await state.clear()
        await state.set_state(State.gps_state)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)
        await state.update_data(job=job_text)
    else:
        print(f"wrong_command_exception: ", message.text)
        await errors.unknown_input_handler(message, state)
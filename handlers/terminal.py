from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from game_logic import mechanics as m
# from game_logic import enregy_manager as em

from handlers import errors

import keyboards.main_kb as kb

router = Router()


@router.message(F.text == "Ship info")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    # try:
    state_data = await state.get_data()
    keyboard = await kb.keyboard_selector(state)
    gps = state_data["gps_state"]
    information = await m.get_player_information(message.from_user.id, "stats", "health", "current_energy", "damage", "defence", "shields", "max_energy")
    energy = await m.get_energy(message.from_user.id)
    faction = await m.get_player_information(message.from_user.id, "attributes", "faction")
    faction = faction[0]
    health = information[0]
    current_energy = energy[0]
    damage = information[2]
    defence = information[3]
    shields = information[4]
    max_energy = energy[1]
    await message.answer(f"Faction: {faction}\n\nShip Stats:\nHP: {health},\nDamage: {damage}\nDefence: {defence}\nShields: {shields}\nEnergy: {current_energy}/{max_energy}", reply_markup=keyboard)
    # except:
    # await errors.unknown_input_handler(message, state)


@router.message(F.text == "Guild")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        gps = state_data["gps_state"]
        keyboard = await kb.keyboard_selector(state)
        await message.answer(f"Here is your Guild info", reply_markup=keyboard)
    except:
        await errors.unknown_input_handler(message, state)


@router.message(F.text == "Cargo")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        gps = state_data["gps_state"]
        keyboard = await kb.keyboard_selector(state)
        await message.answer(f"Here is your Cargo info", reply_markup=keyboard)
    except:
        await errors.unknown_input_handler(message, state)


@router.message(F.text == "Inventory")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        gps = state_data["gps_state"]
        keyboard = await kb.keyboard_selector(state)
        await message.answer(f"Here is your Inventory", reply_markup=keyboard)
    except:
        await errors.unknown_input_handler(message, state)

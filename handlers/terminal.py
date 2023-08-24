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
    faction = await m.get_player_information(message.from_user.id, "attributes")
    faction = faction[0].get("faction")
    energy = await m.get_energy(message.from_user.id)
    current_energy = energy[0]
    max_energy = energy[1]
    information = await m.get_player_information(message.from_user.id, "current_health", "max_health", "credits", "experience", "level", "main_quest", "side_quest", "ship_type", "abilities")
    current_health = information[0]
    max_health = information[1]
    player_credits = information[2]
    experience = information[3]
    level = information[4]
    main_quest = information[5]
    side_quest = information[6]
    ship_type = information[7]
    abilities = information[8]
    damage = None
    defence = None
    shields = None
    await message.answer(f"Faction: {faction}\n\nShip Stats:\nHP: {current_health}/{max_health},\nDamage: {damage}\nDefence: {defence}\nShields: {shields}\nEnergy: {current_energy}/{max_energy}\n\nCredits: {player_credits}\nExperience: {experience}\nLevel: {level}", reply_markup=keyboard)
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

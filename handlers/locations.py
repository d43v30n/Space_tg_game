from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from emojis import *
from game_logic import space_map
from game_logic import mechanics as m
from game_logic.states import State, is_busy

from handlers import errors

import keyboards.main_kb as kb


router = Router()


@router.message(State.docked, F.text == "Back")
async def back_button_docked_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    text = state_data["job"]
    energy = await m.get_energy(message.from_user.id)
    keyboard = await kb.keyboard_selector(state)
    if await is_busy(state_data):
        await message.answer(f"You are {text}.", reply_markup=keyboard)
    else:
        await message.answer(f"Your ship and crew awaits your orders! Currently we have {energy[0]}/{energy[1]} energy to do some stuff.", reply_markup=keyboard)


@router.message(State.docked, F.text == "Undock")
async def undock_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    jobtext_str = f"Undocked in {await space_map.name(gps)}"
    await errors.reset_handler(message, state, gps=gps, jobtext=jobtext_str)
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"You are undocked and free to go", reply_markup=keyboard)


@router.message(State.docked, F.text == "{emoji}Shipyard".format(emoji=flying_saucer))
async def jump_home_handler(message: Message, state: FSMContext) -> None:
    max_health, current_health = await m.get_player_information(message.from_user.id, "max_health", "current_health")
    if current_health <= max_health:
        keyboard = await kb.keyboard_selector(state)
        state_data = await state.get_data()
        gps = state_data["gps_state"]
        loc_name = await space_map.name(gps)
        repairing_text = "Parked at shipyard at {loc_name}".format(
            loc_name=loc_name)
        await message.answer(f"You leaved your vessel for repair. Wait until it is ready", reply_markup=keyboard)
        await state.set_state(State.repairing)
        await state.update_data(job="started repairing at {loc_name}".format(loc_name=loc_name), docked="docked to {loc_name}".format(loc_name=loc_name), repairing=repairing_text)
        await m.restore_hp(message.from_user.id)
        await message.answer("Your Ship has been repaired", reply_markup=keyboard)
        jobtext_str = "Parked at shipyard at {loc_name}".format(
            loc_name=loc_name)
        await errors.reset_handler(message, state, gps=gps, jobtext=jobtext_str)
        await state.set_state(State.docked)
        await state.update_data(job="docked to {loc_name}".format(loc_name=loc_name), docked="to Ringworld station")
    else:
        await message.answer(f"Your Ship is already fully repaired", reply_markup=keyboard)

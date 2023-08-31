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


@router.message(State.repairing, F.text == "Back")
async def back_button_docked_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    text = state_data["job"]
    energy = await m.get_energy(message.from_user.id)
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"You are back to RW now.", reply_markup=keyboard)
    # if await is_busy(state_data):
    #     await message.answer(f"You are {text}.", reply_markup=keyboard)
    # else:
    #     await message.answer(f"Your ship and crew awaits your orders! Currently we have {energy[0]}/{energy[1]} energy to do some stuff.", reply_markup=keyboard)


@router.message(State.docked, F.text == "Undock")
async def undock_rw_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    jobtext_str = f"Undocked in {await space_map.name(gps)}"
    await errors.reset_handler(message, state, gps=gps, jobtext=jobtext_str)
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"You are undocked and free to go", reply_markup=keyboard)


@router.message(State.docked, F.text == "{emoji}Parts trader".format(emoji=parts_trader_emoji))
async def back_button_docked_handler(message: Message, state: FSMContext) -> None:
    keyboard = await kb.keyboard_selector(state)
    await message.answer("You are talking to Parts trader", reply_markup=kb.ringworld_shipyard_kb())


@router.message(State.docked, F.text == "Back to city")
async def back_button_docked_handler(message: Message, state: FSMContext) -> None:
    keyboard = await kb.keyboard_selector(state)
    await message.answer("You are back to centeral city", reply_markup=keyboard)


@router.message(State.docked, F.text == "{emoji}Shipyard".format(emoji=flying_saucer))
async def shipyard_rw_handler(message: Message, state: FSMContext) -> None:
    await message.answer("You entered shipyard. Your ship stats are: ...", reply_markup=kb.ringworld_shipyard_kb())


@router.message(State.docked, F.text == "{emoji}Repair".format(emoji=repair_emoji))
async def repair_rw_handler(message: Message, state: FSMContext) -> None:
    max_health, current_health = await m.get_player_information(message.from_user.id, "max_health", "current_health")
    if current_health <= max_health:
        keyboard = await kb.keyboard_selector(state)
        state_data = await state.get_data()
        gps = state_data["gps_state"]
        loc_name = await space_map.name(gps)
        repairing_text = "Parked at shipyard at {loc_name}".format(
            loc_name=loc_name)
        await message.answer(f"You leaved your vessel for repair. Wait until it is ready, you will be able to only access your terminal during this procedure.", reply_markup=keyboard)
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

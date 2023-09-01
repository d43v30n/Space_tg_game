from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from emojis import *
from game_logic import space_map
from game_logic import mechanics as m
from game_logic.states import State

from handlers import errors

import keyboards.main_kb as kb

router = Router()



@router.message(State.job, Command("settings"))
async def settings_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(State.settings_state)
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"You entered settings", reply_markup=keyboard)

@router.message(State.docked, Command("settings"))
async def settings_handler_docked(message: Message, state: FSMContext) -> None:
    await settings_handler(message, state)





@router.message(State.settings_state, Command("change_nickname"))
async def change_nickname_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(State.settings_nickname)
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"Now, enter your new nickname", reply_markup=keyboard)







@router.message(State.settings_state, Command("exit_settings"))
async def settings_handler(message: Message, state: FSMContext) -> None:
    gps = await m.get_location(message.from_user.id)
    await errors.reset_handler(message, state) 
    await message.answer(f"You exited settings", reply_markup=kb.main_kb())

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from game_logic import mechanics as m
from game_logic.states import State
import keyboards.main_kb as kb


router = Router()


async def reset_handler(message: Message, state=None, gps=None, jobtext=None) -> None:
    if state is not None and jobtext is not None:
        state_data = await state.get_data()
        gps = state_data["gps_state"]
    if state is not None and jobtext is None:
        jobtext = f"floating at {gps}"
    elif state is None and jobtext is None:
        jobtext = f"floating somewhere.."
    else:  # state is None and jobtext is not None
        gps = await m.get_location(message.from_user.id)
    await state.clear()
    await state.set_state(State.gps_state)
    await state.update_data(gps_state=gps)
    await state.set_state(State.job)
    await state.update_data(job=jobtext)

# debugging commans /state


@router.message(Command("state"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    state_data = await state.get_data()
    print(f"current_state = {current_state}")
    print(f"state_data = {state_data}")


@router.message(State.job)
async def wrong_input_handler(message: Message, state: FSMContext) -> None:
    gps = await m.get_location(message.from_user.id)
    await message.answer(f"Wrong input, try again", reply_markup=kb.main_kb(gps))


@router.message()  # should be last in this file in order to handle all unknown messages
async def unknown_input_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    print("unknown_input_handler; state is:", current_state)
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(f"Unknown error, try /start to debug", reply_markup=ReplyKeyboardRemove())
    else:
        # , reply_markup=ReplyKeyboardRemove())
        await message.answer(f"Unknown error.")

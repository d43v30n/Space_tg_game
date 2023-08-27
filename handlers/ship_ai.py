from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from game_logic import space_map, fight
from game_logic import mechanics as m
from game_logic.states import State

from handlers import errors

import keyboards.main_kb as kb


router = Router()


@router.message(State.job, F.text == "Jump Home")
async def jump_home_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    if gps != 0:
        await state.set_state(State.confirmation)
        await state.update_data(confirmation="jumping home confirmation")
        await message.answer(f"Are you sure? Press Jump Home again to confirm.", reply_markup=kb.ship_ai_kb())
    else:
        keyboard = await kb.keyboard_selector(state)
        await message.answer(f"You already here", reply_markup=keyboard)


@router.message(State.confirmation, F.text == "Jump Home")
async def jump_home_confirm_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    loc_name = await space_map.name(gps)  # old loc
    keyboard = await kb.keyboard_selector(state)
    await state.set_state(State.travelling)
    await state.update_data(job=f"jumped home from {loc_name}")
    await state.update_data(travelling="Jumping Home")
    await message.answer(f"3.. 2.. 1.. Jump!", reply_markup=keyboard)
    await m.jump_home(message.from_user.id)
    await state.clear()
    await state.set_state(State.gps_state)
    gps = await m.get_location(message.from_user.id)
    await state.update_data(gps_state=gps)
    await state.set_state(State.job)
    await state.update_data(job=f"after Home Jump")
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"Finally, Home!", reply_markup=kb.main_kb())


@router.message(State.confirmation, F.text != "Jump Home")
async def jump_home_confirm_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(State.gps_state)
    gps = await m.get_location(message.from_user.id)
    await state.update_data(gps_state=gps)
    await state.set_state(State.job)
    await state.update_data(job=f"aborted Home Jump")
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"aborted home jump!", reply_markup=keyboard)


@router.message(State.job, F.text == "Travel forward")
async def travel_forward_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    loc_name = await space_map.name(gps)  # old loc
    keyboard = await kb.keyboard_selector(state)
    await state.set_state(State.travelling)
    await state.update_data(job=f"jumped forward from {loc_name}")
    await state.update_data(travelling="Travelling Forward")
    await message.answer(f"Engines starting, space exploration proceeding..", reply_markup=keyboard)
    if await space_map.read_map(gps+1):
        new_loc_gps = await m.move_forward(message.from_user.id)
        gps = new_loc_gps
        loc_features = await space_map.features(gps)
        loc_name = await space_map.name(gps)
        await state.clear()
        await state.set_state(State.gps_state)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)

        event = await m.rand_event(gps)
        print(event[0])

        # event check
        if event[0] is None:

            print("entered 1")
            await state.update_data(job=f"just arrived to {loc_name}")
            #
            #
            #       loc features function
            #
            #
            if "mining" in loc_features:
                await message.answer(f"You arrived to {loc_name}, Try to scan here.", reply_markup=keyboard)
            else:
                await message.answer(f"You arrived to {loc_name}", reply_markup=keyboard)
        elif event[0] == "enemies":
            print("entered 2")
            enemy_shorname = event[1]
            # await message.answer(f"Triggered event {event}. Spawning {enemy_shorname}", reply_markup=keyboard)
            await state.update_data(job=f"just arrived to {loc_name} and encountered {event}")
            # fight_result -> "win" of "loose" str
            fight_result = await fight.init_fight(message, enemy_shorname, state)
            print(f"fight_result, {fight_result}")
            if fight_result == "win":
                await message.answer(f"(WON) Figth result is : {fight_result}.", reply_markup=keyboard)
            else:
                await message.answer(f"(LOST) Figth result is : {fight_result}.", reply_markup=keyboard)
        elif event[0] == "drop":
            print("entered 3")
            await state.update_data(job=f"just arrived to {loc_name}")
            #
            #
            #       loc features function
            #
            #
            if "mining" in loc_features:
                await message.answer(f"You arrived to {loc_name}, Try to scan here.", reply_markup=keyboard)
            else:
                await message.answer(f"You arrived to {loc_name}", reply_markup=keyboard)
        elif event[0] == "shipyard":
            print("entered 4")
            await state.update_data(job=f"just arrived to {loc_name}")
            #
            #
            #       loc features function
            #
            #
            if "mining" in loc_features:
                await message.answer(f"You arrived to {loc_name}, Try to scan here.", reply_markup=keyboard)
            else:
                await message.answer(f"You arrived to {loc_name}", reply_markup=keyboard)
        else:
            await state.update_data(job=f"just arrived to {loc_name}")
            await message.answer(f"You arrived to {loc_name}", reply_markup=keyboard)
            print("should not happen. unknown event in location")

    else:
        print("reached end of map")
        await state.clear()
        await state.set_state(State.gps_state)
        gps = 0
        await m.jump_home(message.from_user.id)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)
        await state.update_data(job=f"Reached map end, returning")
        keyboard = await kb.keyboard_selector(state)
        await message.answer(f"I was travelling too long, and lost my disres. I should rest now..", reply_markup=keyboard)


# busy traveling forward or home
@router.message(F.text.in_({"Travel forward", "Jump Home"}))
async def busy_travel_handler(message: Message, state: FSMContext) -> None:
    state_name = await state.get_state()
    if state_name is not None:
        try:
            state_data = await state.get_data()
            gps = state_data["gps_state"]
            text_job = state_data["job"]
            keyboard = await kb.keyboard_selector(state)
            try:
                text_travelling = state_data["travelling"]
                await message.answer(f"You just {text_job} and {text_travelling}.", reply_markup=keyboard)
            except:
                await message.answer(f"You just {text_job}. This usually takes some time, you know.", reply_markup=keyboard)
        except:
            await errors.unknown_input_handler(message, state)
    else:
        await errors.unknown_input_handler(message, state)


@router.message(State.job, F.text == "Mine here")
async def mining_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    loc_name = await space_map.name(gps)
    loc_features = await space_map.features(gps)
    keyboard = await kb.keyboard_selector(state)
    if "mining" in loc_features:
        await state.update_data(job=f"mining in progress")
        await message.answer(f"Mining at {loc_name}", reply_markup=keyboard)
    else:
        await message.answer(f"No ore around", reply_markup=keyboard)


@router.message(State.job, F.text == "Scan area")
async def scanning_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    loc_features = await space_map.features(gps)
    loc_name = await space_map.name(gps)
    keyboard = await kb.keyboard_selector(state)
    if "mining" in loc_features:
        await state.update_data(job=f"found ore, mining is possible")
        await message.answer(f"Scanning {loc_name}, found ore", reply_markup=keyboard)
    else:
        await message.answer(f"Scanning {loc_name}, found nothing", reply_markup=keyboard)

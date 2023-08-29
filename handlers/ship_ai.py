from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from game_logic import energy_manager, space_map, fight
from game_logic import mechanics as m
from game_logic.states import State
from emojis import *

from handlers import errors

import keyboards.main_kb as kb


router = Router()


@router.message(State.job, F.text == "{emoji}Jump Home".format(emoji=refresh_symbol))
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


@router.message(State.confirmation, F.text == "{emoji}Jump Home".format(emoji=refresh_symbol))
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
    await message.answer(f"Finally, Home!", reply_markup=kb.main_kb(gps))


@router.message(State.confirmation, F.text != "{emoji}Jump Home".format(emoji=refresh_symbol))
async def jump_home_confirm_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(State.gps_state)
    gps = await m.get_location(message.from_user.id)
    await state.update_data(gps_state=gps)
    await state.set_state(State.job)
    await state.update_data(job=f"aborted Home Jump")
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"aborted home jump!", reply_markup=keyboard)


@router.message(State.job, F.text == "{emoji}Travel Forward".format(emoji=play_button))
async def travel_forward_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    if gps is None:
        gps = await m.get_location(message.from_user.id)
    loc_name = await space_map.name(gps)  # old loc
    keyboard = await kb.keyboard_selector(state)
    await state.set_state(State.travelling)
    await state.update_data(job=f"jumped forward from {loc_name}")
    await state.update_data(travelling="Travelling Forward")
    if await space_map.read_map(gps+1):
        await message.answer("Engines starting, space exploration proceeding..", reply_markup=kb.main_kb(gps+1))
        # new_loc_gps = await m.move_forward(message.from_user.id)
        # gps = new_loc_gps
        loc_features = await space_map.features(gps)
        loc_name = await space_map.name(gps)
        await state.clear()
        await state.set_state(State.gps_state)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)
        await state.update_data(job=f"rolling for event")

        event = await m.rand_event(gps)
        # print(event[0])
        if not event:
            await state.update_data(job=f"just arrived to {loc_name}")
            keyboard = await kb.keyboard_selector(state)
            await message.answer(f"You arrived to {loc_name}", reply_markup=keyboard)
            return
        # event check
        if event[0] is None:
            print("entered 1")
            keyboard = await kb.keyboard_selector(state)
            await state.update_data(job=f"just arrived to {loc_name}")
            if "mining" in loc_features:
                await message.answer(f"You arrived to {loc_name}, Try to scan here.", reply_markup=keyboard)
            else:
                await message.answer(f"You arrived to {loc_name}.", reply_markup=keyboard)

        elif event[0] == "enemies":
            print("entered 2")
            keyboard = await kb.keyboard_selector(state)
            enemy_shorname = event[1]
            # await message.answer(f"Triggered event {event}. Spawning {enemy_shorname}", reply_markup=keyboard)
            await state.update_data(job=f"just arrived to {loc_name} and encountered {event[0]}")
            # fight_result -> "win" of "loose" str
            fight_result = await fight.init_fight(message, enemy_shorname, state)
            if fight_result[0] == "win":
                await message.answer(f"Figth result is : {fight_result[0]}.\n\nReceived:\n{fight_result[1]}", reply_markup=keyboard)

        elif event[0] == "mining_event":
            print("entered 3")
            keyboard = await kb.keyboard_selector(state)
            await state.update_data(job=f"just arrived to {loc_name} and encountered {event[0]}")
            if "mining" in loc_features:
                await message.answer(f"You arrived to {loc_name}, Try to mine here (mine event).", reply_markup=keyboard)
            else:
                await message.answer(f"You arrived to {loc_name} (mine event).", reply_markup=keyboard)

        elif event[0] == "scanning_event":
            print("entered 4")
            keyboard = await kb.keyboard_selector(state)
            scans = event[1]["scans_required"]
            await state.update_data(job=f"just arrived to {loc_name} and encountered {event[0]}_{scans}")
            if "mining" in loc_features:
                await message.answer(f"You arrived to {loc_name}, Try to scan here (scan event).", reply_markup=keyboard)
            else:
                await message.answer(f"You arrived to {loc_name} (scan event).", reply_markup=keyboard)

        else:
            await state.update_data(job=f"just arrived to {loc_name}")
            keyboard = await kb.keyboard_selector(state)
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
@router.message(F.text.in_({"{emoji}Travel Forward".format(emoji=play_button), "{emoji}Jump Home".format(emoji=refresh_symbol)}))
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


@router.message(State.job, F.text == "{emoji}Mine here".format(emoji=pickaxe))
async def mining_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    text_job = state_data["job"]
    loc_name = await space_map.name(gps)
    loc_features = await space_map.features(gps)
    current_energy = await m.get_current_energy(message.from_user.id)
    keyboard = await kb.keyboard_selector(state)
    if "mining" in loc_features and not text_job.startswith("after mining at"):
        if current_energy >= 1:
            await state.set_state(State.mining)
            await state.update_data(job="mining in progress at {loc_name}".format(loc_name=loc_name), mining="mining in progress...")
            await energy_manager.use_one_energy(message.from_user.id)
            await message.answer("Mining at {loc_name}".format(loc_name=loc_name), reply_markup=keyboard)
            result = await m.mine_here(message.from_user.id, gps)
            await message.answer("Found:\n{result}".format(result=result), reply_markup=keyboard)
            jobtext = "after mining at {loc_name}".format(loc_name=loc_name)
            await state.clear()
            await state.set_state(State.gps_state)
            await state.update_data(gps_state=gps)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)
        else:
            await message.answer("Your ship is out of energy! Charge it on Station or with Energy Cell", reply_markup=keyboard)
    elif text_job.startswith("after scanning at") and text_job.endswith(""):
        pass
    else:
        await message.answer("No ore around", reply_markup=keyboard)


@router.message(State.mining)
async def busy_mining_handler(message: Message, state: FSMContext) -> None:
    keyboard = await kb.keyboard_selector(state)
    await message.answer("You are busy mining", reply_markup=keyboard)


@router.message(State.job, F.text == "{emoji}Scan area".format(emoji=magnifying_glass))
async def scanning_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    text_job = state_data["job"]
    loc_features = await space_map.features(gps)
    loc_name = await space_map.name(gps)
    keyboard = await kb.keyboard_selector(state)

    if text_job.endswith("scanning_event_3"):
        await m.scan_area(message, state)
        jobtext = "just arrived to {loc_name} and encountered scanning_event_2".format(
            loc_name=loc_name)
        await state.set_state(State.job)
        await state.update_data(job=jobtext)
        return
    elif text_job.endswith("scanning_event_2"):
        await m.scan_area(message, state)
        jobtext = "just arrived to {loc_name} and encountered scanning_event_1".format(
            loc_name=loc_name)
        await state.set_state(State.job)
        await state.update_data(job=jobtext)
        return
    elif text_job.endswith("scanning_event_1"):
        jobtext = "after scanning at {loc_name}".format(
            loc_name=loc_name)
        await state.set_state(State.job)
        await state.update_data(job=jobtext)
        # TRIGGER EVENT HERE
        print("TRIGGER EVENT HERE")
        return

    if "mining" in loc_features and not text_job.startswith("scanning."):
        await m.scan_area(message, state)
    else:
        await message.answer(f"Scanning {loc_name}, found nothing", reply_markup=keyboard)

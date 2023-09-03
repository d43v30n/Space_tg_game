from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from game_logic import energy_manager, space_map, fight
from game_logic import mechanics as m
from game_logic.states import State
from app.database import db_read_details
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
    # await message.answer_photo("AgACAgIAAxkDAAI03WTvhfh9byTLKl1_AAF9C6nG4wO4HwACUskxG2EPgUs4-mQ4o3GyRQEAAwIAA3kAAzAE")
    await message.answer(f"Finally, Ringworld!", reply_markup=kb.main_kb(gps))


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
        new_loc_gps = await m.move_forward(message.from_user.id)
        gps = new_loc_gps
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
            await message.answer("<code>{rocket}Ship AI</code> wakes you up from cryogenic sleep.\nOn the display: <b>{loc_name}</b> {gps_emj}{gps}.".format(rocket=rocket, loc_name=loc_name, gps_emj=gps_emj, gps=gps), reply_markup=keyboard)
            return

        if "mining" in loc_features:
            mining_text = ", mining is possible"
        else:
            mining_text = ""

        # event check
        if event[0] is None:
            print("entered 1 None")
            keyboard = await kb.keyboard_selector(state)
            await state.update_data(job=f"just arrived to {loc_name}{mining_text}.")
            await message.answer("<code>{rocket}Ship AI</code> wakes you up from cryogenic sleep.\nOn the display: <b>{loc_name}</b> {gps_emj}{gps}.".format(rocket=rocket, loc_name=loc_name, gps_emj=gps_emj, gps=gps), reply_markup=keyboard)

        elif event[0] == "enemies":
            print("entered 2 enemies")
            enemy_shorname = event[1]
            enemy_faction = await db_read_details(
                "enemies", enemy_shorname, "attributes", "en_shortname")
            print("enemy_faction", enemy_faction["faction"])
            await state.set_state(State.fighting_choice)
            await state.update_data(fighting=f"new fight")
            keyboard = await kb.keyboard_selector(state)
            await state.update_data(job=f"just arrived to {loc_name}{mining_text} and encountered {event[0]}", fighting=f" event {event} spawning {enemy_shorname}")
            await message.answer("<code>{rocket}Ship AI</code> wakes you up from cryogenic sleep.\n\nEnemies are engaging! Your decision, cap?\n\nSignature match found, faction: <b>{enemy_faction}</b>.".format(rocket=rocket, enemy_faction=enemy_faction["faction"]), reply_markup=keyboard)

        elif event[0] == "mining_event":
            print("entered 3 mining_event")
            keyboard = await kb.keyboard_selector(state)
            await state.update_data(job=f"just arrived to {loc_name}{mining_text} and encountered {event[0]}")
            await message.answer("<code>{rocket}Ship AI</code> wakes you up from cryogenic sleep.\nOn the display: <b>{loc_name}</b>. MINING_EVENT_TRIGGERED (in dev)".format(rocket=rocket, loc_name=loc_name), reply_markup=keyboard)

        elif event[0] == "scanning_event":
            print("entered 4 scanning_event")
            keyboard = await kb.keyboard_selector(state)
            scans = event[1]["scans_required"]
            await state.update_data(job=f"just arrived to {loc_name}{mining_text} and encountered {event[0]}_{scans}")
            await message.answer("<code>{rocket}Ship AI</code> wakes you up from cryogenic sleep.\nOn the display: <b>{loc_name}</b>.\n\nOur scanners have detected some <b>unusal</b> behavior, we should investigate it! Use your scanner.".format(rocket=rocket, loc_name=loc_name), reply_markup=keyboard)
        elif event[0] == "encounter":
            print("entered 5 encounter")
            await state.update_data(job=f"just arrived to {loc_name}{mining_text}...")
            keyboard = await kb.keyboard_selector(state)
            await message.answer("<code>{rocket}Ship AI</code> wakes you up from cryogenic sleep.\nOn the display: <b>{loc_name}</b> ENCOUNTER_EVENT_TRIGGERED (in dev)".format(rocket=rocket, loc_name=loc_name), reply_markup=keyboard)
        else:
            print(
                "should not happen. unknown event in location, event[0] = ", event[0])
            await state.update_data(job=f"just arrived to {loc_name}{mining_text}...")
            keyboard = await kb.keyboard_selector(state)
            await message.answer("<code>{rocket}Ship AI</code> wakes you up from cryogenic sleep.\nOn the display: <b>{loc_name}</b>.".format(rocket=rocket, loc_name=loc_name), reply_markup=keyboard)

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


@router.message(State.fighting_choice, F.text == "{emoji}Engage enemy".format(emoji=swords_emoji))
async def fighting_chioce_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    fighting_data = state_data["fighting"]
    en_shortname = fighting_data.split(" ")[-1]
    en_name = await db_read_details("enemies", en_shortname, "en_name", "en_shortname")
    await state.set_state(State.fighting)
    keyboard = await kb.keyboard_selector(state)
    await message.answer(f"When you approach, you see that you are facing {en_name}. Space guns are shooting...".format(en_name=en_name), reply_markup=keyboard)
    fight_result = await fight.init_fight(message, en_shortname, state)
    row1, row2, row3 = await m.get_main_text_row(message.from_user.id)
    header_txt = "{row1}{row2}".format(row1=row1, row2=row2)
    keyboard = await kb.keyboard_selector(state)
    if fight_result[0] == "win":
        await message.answer(header_txt + fight_result[1], reply_markup=keyboard)
    else:
        await state.clear()
        await state.set_state(State.gps_state)
        gps = await m.get_location(message.from_user.id)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)
        await state.update_data(job=f"Dead after fighht with {en_shortname}")
        await message.answer(header_txt + fight_result[1], reply_markup=keyboard)


@router.message(State.fighting_choice, F.text == "{emoji}Try to escape".format(emoji=running_emoji))
async def fleeing_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    fighting_data = state_data["fighting"]
    en_shortname = fighting_data.split(" ")[-1]
    en_name = await db_read_details("enemies", en_shortname, "en_name", "en_shortname")
    flee_available = await fight.engaging_enemy_choice(message.from_user.id, en_shortname)
    flee_chance = await m.roll_chance(0.3)  # flee chance is hardcoded 20%
    if flee_available and flee_chance:
        await errors.reset_handler(message, state, jobtext="fleeing from enemy successfull")
        keyboard = await kb.keyboard_selector(state)
        await message.answer("You were lucky to get some cover in Asteroids belt and hide your ass.", reply_markup=keyboard)
    else:
        await state.set_state(State.fighting)
        keyboard = await kb.keyboard_selector(state)
        await message.answer("You were unlucky and now you can only FIGHT. Your enemy is {en_name}".format(en_name=en_name), reply_markup=keyboard)
        fight_result = await fight.init_fight(message, en_shortname, state)
        row1, row2, row3 = await m.get_main_text_row(message.from_user.id)
        header_txt = "{row1}{row2}".format(row1=row1, row2=row2)
        if fight_result[0] == "win":
            await message.answer(header_txt + fight_result[1], reply_markup=keyboard)
        else:
            await state.clear()
            await state.set_state(State.gps_state)
            gps = await m.get_location(message.from_user.id)
            await state.update_data(gps_state=gps)
            await state.set_state(State.job)
            await state.update_data(job=f"Dead after fight with {en_shortname}")
            await message.answer(header_txt + fight_result[1], reply_markup=keyboard)


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
    if current_energy >= 1:
        # after scanning at {loc_name}, nothing found
        if text_job.endswith("and encountered mining_event"):
            if current_energy >= 2:
                await message.answer("Yo begin to mine event roid. For this yo should have at least 2 energy".format(), reply_markup=keyboard)
                result = await m.trigger_minings_event(message, state)
                await message.answer("You found while mining at event:\n{result}".format(result=result), reply_markup=keyboard)
            else:
                await message.answer("<i>{rocket}Ship AI reporting.</i>\n\n\"We can't mine as you have less than 2{energy_smiley}Energy\"".format(energy_smiley=energy_smiley, rocket=rocket), reply_markup=keyboard)
        elif "mining" in loc_features and not text_job.startswith("after mining at") and "mined ore" not in text_job:
            result = await m.mine_here(message.from_user.id, gps, message, state)
            print("mining ore result", result)
            if not result.startswith("You found no ore."):
                jobtext = "mined ore at {loc_name}".format(loc_name=loc_name)
            else:
                jobtext = "mined nothing at {loc_name}".format(
                    loc_name=loc_name)
            await message.answer("<i>{rocket}Ship AI reporting.</i>\n\n{result}".format(result=result, rocket=rocket), reply_markup=keyboard)
            await state.clear()
            await state.set_state(State.gps_state)
            await state.update_data(gps_state=gps)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)
        elif text_job.startswith("after scanning at") and text_job.endswith(""):
            pass
        else:
            await message.answer("Nothing to mine. Did scanners noticed something?", reply_markup=keyboard)
    else:
        await message.answer("Your ship is out of energy! Charge it on Station or with Energy Cell", reply_markup=keyboard)


@router.message(State.mining)
async def busy_mining_handler(message: Message, state: FSMContext) -> None:
    if message.text.startswith("/state"):
        await errors.command_state_handler(message, state)
    else:
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


# unscanned and unmined location that can be mined
    if "encountered scanning_event_" in text_job:
        result = await m.scan_area(message, state)
        if result:
            print("entered if not if ")
            await message.answer("<i>{rocket}Ship AI reporting.</i>\nScanning complete, we have some <b>results</b>.\n\n{result}.".format(result=result, rocket=rocket), reply_markup=keyboard)

    elif "mining" in loc_features and not text_job.startswith("after scanning at ") and not text_job.startswith("mined"):
        scan_result = await m.scan_area(message, state)
        if scan_result:
            jobtext = "after scanning at {loc_name}, found ore".format(
                loc_name=loc_name)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)
        else:
            jobtext = "after scanning at {loc_name}, scanners found nothing".format(
                loc_name=loc_name)
            await state.set_state(State.job)
            await state.update_data(job=jobtext)
    else:
        await message.answer(f"Nothing to scan at {loc_name}.", reply_markup=keyboard)

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app import database as db
from emojis import *
from game_logic import inventory as invent
from game_logic import mechanics as m
from game_logic import space_map
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


@router.message(State.repairing)
async def repairing_state_handler(message: Message, state: FSMContext) -> None:
    keyboard = await kb.keyboard_selector(state)
    await message.answer("While your ship is under repair, you can only access {emoji}Terminal".format(emoji=computer), reply_markup=keyboard)


@router.message(State.docked, F.text == "{emoji}Undock".format(emoji=undock_emoji))
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
        await message.answer("You leaved your vessel for repair. Wait until it is ready, you will be able to only access your {emoji}Terminal during this procedure.".format(emoji=computer), reply_markup=keyboard)
        await state.set_state(State.repairing)
        await state.update_data(job="started repairing at {loc_name}".format(loc_name=loc_name), docked="docked to {loc_name}".format(loc_name=loc_name), repairing=repairing_text)
        await m.restore_hp(message.from_user.id)
        await message.answer("Your Ship has been repaired", reply_markup=keyboard)
        jobtext_str = "Parked at shipyard at {loc_name}".format(
            loc_name=loc_name)
        await errors.reset_handler(message, state, gps=gps, jobtext=jobtext_str)
        await state.set_state(State.docked)
        await state.update_data(job="docked to {loc_name}".format(loc_name=loc_name), docked="to {loc_name}".format(loc_name=loc_name))
    else:
        keyboard = await kb.keyboard_selector(state)
        await message.answer("Your Ship is already fully repaired", reply_markup=keyboard)


@router.message(State.docked, F.text == "{emoji}Night Club".format(emoji=night_club_emoji))
async def night_club_handler(message: Message, state: FSMContext) -> None:
    beer_id = await db.db_read_int("items", "\"craft_beer\"", "i_id", "it_shortname")
    beer_price = await db.db_read_int("items", "\"craft_beer\"", "price", "it_shortname")
    await message.answer("Hello, Cap! My name is Alicia, local bartender of the {emoji}Night Club here on the Ringworld.\n\nhere you can meet different people or have some really good craft beer.\n\n<code>to buy some stuff:</code>\n/buy_{beer_id} - {beer_price}{money_bag}".format(emoji=night_club_emoji, beer_id=beer_id, money_bag=money_bag, beer_price=beer_price), reply_markup=kb.night_club_kb())


@router.message(F.text.startswith("/buy_"))
async def item_selector_handler(message: Message, state: FSMContext) -> None:
    text = message.text
    keyboard = await kb.keyboard_selector(state)
    current_state = await state.get_state()
    if current_state != "State:job" and current_state != "State:docked":
        await message.answer(f"You can not do this right now", reply_markup=keyboard)
        return
    if text.startswith("/buy_"):
        id = str(message.text)
        flag = id.split("_")[0][1:]
        id = int(id.split("_")[1])
        out = await m.buy_item(message.from_user.id, id)
        await message.answer(out, reply_markup=keyboard)

        # await message.answer(f"Using {text} 1x".format(text=text), reply_markup=keyboard)
        # out = await invent.apply_item(message.from_user.id, id, state)
        # await message.answer(out, reply_markup=keyboard)
    else:
        print(f"wrong_command_exception: ", message.text)
        await errors.unknown_input_handler(message, state)


@router.message(F.text.startswith("/id_"))
async def item_info_handler(message: Message, state: FSMContext) -> None:
    id = str(message.text)
    id = int(id.split("_")[1])
    keyboard = await kb.keyboard_selector(state)
    it_name = await db.db_read_details("items", id, "it_name", "i_id")
    it_desc = await db.db_read_details("items", id, "desc", "i_id")
    it_effects = await db.db_read_details("items", id, "effects", "i_id")
    await message.answer(f"{it_name}\n{it_desc}\n{it_effects}", reply_markup=keyboard)

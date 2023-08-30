from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ParseMode

from app import database as db
from emojis import *
from game_logic import energy_manager, mechanics as m
from game_logic import space_map
from game_logic.states import *

from handlers import errors

import keyboards.main_kb as kb

# All handlers should be attached to the Router (or Dispatcher)
router = Router()


@router.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    current_state = await state.get_state()
    is_new_user = await db.new_user_check(message.from_user.id)
    if current_state is None and is_new_user:
        print(
            f"New user registered: id={message.from_user.id}, username=@{message.from_user.username}")
        await db.cmd_start_db(message.from_user.id)
        # await message.answer("{void_emj}}Void greets you commander!\n\n@{message.from_user.username}, you are in trouble, but you should figure it out on your own.\nDont forget to /help if you need more information!\nTry to asking your 🚀Ship AI for help.", reply_markup=kb.main_kb(0))
        await message.answer(
            "{void_emj}Void greets you, commander!\n\n@{u_id}, you find yourself in a precarious situation, but fear not, for your resourcefulness shall light the way.\nDon't hesitate to seek guidance with /help if you require more insights!\nYour trusty {rocket}Ship AI stands ready to assist you.".format(
                u_id=message.from_user.username, void_emj=void_emj, rocket=rocket),
            reply_markup=kb.main_kb(0)
)

        gps = await m.get_location(message.from_user.id)
        # lore messages for new player guidance
        await state.set_state(State.gps_state)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)
        await state.update_data(job="new user")
    elif current_state is None:
        gps = await m.get_location(message.from_user.id)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)
        await state.update_data(job="entering state")
        print(
            f"User logged in: id={message.from_user.id}, username=@{message.from_user.username}")
        keyboard = await kb.keyboard_selector(state)
        # await message.answer(f"Welcome back, @{message.from_user.username}, my old friend!\nGame server has been updated. ", reply_markup=keyboard)
        await message.answer(
            "Welcome back, @{u_id}\nGame server has been updated.\n\nDon't hesitate to seek guidance with /help if you require more insights!\nYour trusty {rocket}Ship AI stands ready to assist you.".format(u_id=message.from_user.username, void_emj=void_emj, rocket=rocket), reply_markup=keyboard)
    elif current_state == "State:admin":
        await errors.command_reset_handler(message, state)
    else:
        await errors.unknown_input_handler(message, state)


@ router.message(Command("help"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await message.answer("""<b>Welcome to Conquerors of the Void Bot - Your Galactic Journey Begins! 🚀</b>

<i>Embark on an Epic Space Exploration Adventure! 🌌</i>

<b>Commander</b>, get ready to dive into the cosmos and experience the thrill of interstellar travel, resource management, and intense turn-based battles. In Conquerors of the Void, you'll navigate uncharted galaxies, discover alien civilizations, and test your strategic prowess in a mix of <b>RPG</b> and <i>survival</i> gameplay.

<b>Getting Started:</b>
To start your cosmic adventure, simply type <code>/start</code>. You'll receive a sturdy starship, a handful of resources, and a loyal AI to begin your journey.

<b>Gameplay Basics:</b>
- <b>Exploration:</b> Navigate through star systems by using your Ship AI. Unveil new planets, anomalies, and celestial wonders. Keep an eye on your ship's HP and Energy!
- <b>Upgrades:</b> Enhance your starship, crew skills, and weaponry using resources you collect during your travels. Access the upgrade menu with  /upgrades.
- <b>Trading:</b> Visit space stations to trade resources, buy equipment, and sell rare discoveries. Engage in commerce to bolster your resources and fund your adventure.
- <b>Turn-Based Battles:</b> Encounter hostile space creatures and rival explorers.
- <b>Strategy:</b> Every decision matters. Choose your path wisely, manage your resources efficiently, and strategize during battles to emerge victorious.

<b>RPG Elements:</b>
- <b>Crew Development:</b> Your crew members have distinct skills and backgrounds. Train them to improve their abilities and unlock new talents for a variety of strategic advantages.
- <b>Character Progression:</b> As you explore and conquer challenges, your commander's skills will grow. Tailor your character's development to match your preferred playstyle.
- <b>Alliances and Factions:</b> Form alliances with alien civilizations, gain their trust, and unlock unique quests, technologies, and storylines.

<b>Survival Challenges:</b>
- <b>Resource Management:</b> Keep an eye on your ship's energy, food supplies, and life support systems. Scarcity of resources adds a layer of survival challenge.
- <b>Quests and Objectives:</b> Engage in story-driven quests that will test your decision-making abilities and determine the fate of your spacefaring journey.

<b>Join the Community:</b>
Connect with fellow spacefarers, share tips, and participate in discussions in our official Conquerors of the Void Telegram group <a href='http://www.example.com/'>here</a>.

<b>Get Help:</b>
For a list of available commands, type <code>/commands</code>. If you need assistance at any point, type <code>/help</code> to display this message again.

<i>May the stars guide you, Commander! Your legacy among the galaxies awaits. 🌌</i>

""", reply_markup=kb.main_kb(0), parse_mode=ParseMode.HTML)


@ router.message(State.job, F.text == "{emoji}Ship AI".format(emoji=rocket))
async def ship_ai_menu(message: Message, state: FSMContext) -> None:
    state_data=await state.get_data()
    gps=state_data["gps_state"]
    if gps is None:
        gps=await m.get_location(message.from_user.id)
    
    # keyboard = await kb.keyboard_selector(state, "{emoji}Ship AI".format(emoji=rocket))
    row1, row2, row3 = await m.get_main_text_row(message.from_user.id)
    jobtext = state_data["job"]
    if jobtext.endswith("found ore"):
        found_ore_text = "Our scanners detected ore here! We can try to mine."
    else:
        found_ore_text = ""
    await message.answer("{row1}{row2}\nShip AI: \"We are currently free to go.\" \n\nAny further orders, cap?\n{found_ore_text}".format(row1=row1, row2=row2, found_ore_text=found_ore_text), reply_markup=kb.ship_ai_kb())


@ router.message(F.text == "{emoji}Ship AI".format(emoji=rocket))
async def ship_ai_busy(message: Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        gps = state_data["gps_state"]
        travelling = state_data["travelling"]
        keyboard = await kb.keyboard_selector(state, "{emoji}Ship AI".format(emoji=rocket))
        await message.answer(f"Your Ship AI is busy ({travelling})", reply_markup=keyboard)
    except:
        await errors.unknown_input_handler(message, state)


# Terminal should be always accessable
@ router.message(F.text == "{emoji}Terminal".format(emoji=computer))
async def terminal_menu(message: Message, state: FSMContext) -> None:
    row1, row2, row3=await m.get_main_text_row(message.from_user.id)
    try:
        await message.answer("{row1}{row2}\n{row3}".format(row1=row1, row2=row2, row3=row3), reply_markup=kb.terminal_kb())
    except:
        await errors.unknown_input_handler(message, state)


@ router.message(F.text == "Back")
async def back_button_handler(message: Message, state: FSMContext) -> None:
    current_state=await state.get_state()
    if current_state == "State:confirmation":
        print("entered confirmation reset")
        gps=await m.get_location(message.from_user.id)
        energy=await m.get_energy(message.from_user.id)
        keyboard=await kb.keyboard_selector(state)
        job_text="Exiting confirmation"
        await state.clear()
        await state.set_state(State.gps_state)
        await state.update_data(gps_state=gps)
        await state.set_state(State.job)
        await state.update_data(job=job_text)
        await message.answer(f"Your ship and crew awaits your orders! Currently we have {energy[0]}/{energy[1]} energy to do some stuff.", reply_markup=keyboard)
    else:
        try:
            energy=await m.get_energy(message.from_user.id)
            state_data=await state.get_data()
            gps=state_data["gps_state"]
            text=state_data["job"]
            keyboard=await kb.keyboard_selector(state)
            if await is_busy(state_data):
                await message.answer(f"You are {text}.", reply_markup=kb.main_kb(gps))
            else:
                await message.answer(f"Your ship and crew awaits your orders! Currently we have {energy[0]}/{energy[1]} energy to do some stuff.", reply_markup=keyboard)
        except:
            await errors.unknown_input_handler(message, state)


@ router.message(State.job, F.text == "Dock to Ringworld station")
async def jump_home_handler(message: Message, state: FSMContext) -> None:
    state_data=await state.get_data()
    gps=state_data["gps_state"]
    if gps == 0:
        text_job=state_data["job"]
        loc_name=await space_map.name(gps)
        await state.set_state(State.docked)
        await state.update_data(job="docked to {loc_name}".format(loc_name=loc_name), docked="to Ringworld station")
        keyboard=await kb.keyboard_selector(state)
        await message.answer(f"Yes, my beloved home. How long has it bee. {loc_name}, i Love YOU!\n\nYou approach this colossal space station and dock to it at international space port.\n\nWhile docked your ship will be charged for free!", reply_markup=keyboard)
        await energy_manager.restore_all_energy(message.from_user.id)
        # 1 docking timer
        # 2 essage docked with plenty of station information
    else:
        await errors.unknown_input_handler(message, state)


@ router.message(State.docked, F.text == "Dock to Ringworld station")
async def jump_home_handler(message: Message, state: FSMContext) -> None:
    keyboard=await kb.keyboard_selector(state)
    await message.answer(f"Already docked", reply_markup=keyboard)

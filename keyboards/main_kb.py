from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from emojis import *


async def keyboard_selector(state, menu=None):
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    job_name = state_data["job"]
    state_name = await state.get_state()
    if gps == 0 and (state_name == "State:docked" or state_name == "State:repairing") :
        keyboard = ringworld_kb()
    elif job_name.endswith("and encountered mining_event") or job_name.endswith("and encountered scanning_event"):
        keyboard = at_location_kb(gps)
    elif menu == "{emoji}Ship AI".format(emoji=rocket):
        keyboard = ship_ai_kb()
    else:
        keyboard = main_kb(gps)
    return keyboard


def core_kb(gps=None) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="{emoji}Ship AI".format(emoji=rocket))
    kb.button(text="{emoji}Terminal".format(emoji=computer))
    return kb


def main_kb(gps=None) -> ReplyKeyboardMarkup:  # for known locations
    kb = ReplyKeyboardBuilder()
    core = core_kb(gps)
    kb.attach(core)
    if gps == 0:
        kb.button(text="Dock to Ringworld station")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def ship_ai_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="{emoji}Jump Home".format(emoji=refresh_symbol))
    kb.button(text="{emoji}Travel Forward".format(emoji=play_button))
    kb.button(text="{emoji}Mine here".format(emoji=pickaxe))
    kb.button(text="{emoji}Scan area".format(emoji=magnifying_glass))
    kb.button(text="Back")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def terminal_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Ship info")
    kb.button(text="Guild")
    kb.button(text="{emoji}Cargo".format(emoji=barrel))
    kb.button(text="{emoji}Inventory".format(emoji=paperbox))
    kb.button(text="Back")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def at_location_kb(gps) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    core = core_kb(gps)
    kb.attach(core)
    kb.button(text="Interact")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def ringworld_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="{emoji}Shipyard".format(emoji=flying_saucer))
    kb.button(text="Undock")
    kb.button(text="{emoji}Terminal".format(emoji=computer))
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def ringworld_shipyard_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="{emoji}Repair".format(emoji=repair_emoji))
    kb.button(text="{emoji}Parts trader".format(emoji=parts_trader_emoji))
    kb.button(text="Back to city")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def admin_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="/help")
    kb.button(text="/test")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

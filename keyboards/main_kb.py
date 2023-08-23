from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def keyboard_selector(state, menu=None):
    state_data = await state.get_data()
    gps = state_data["gps_state"]
    job_name = state_data["job"]
    state_name = await state.get_state()
    if state_name == "State:docked" and gps == 0:
        keyboard = ringworld_kb()
    elif job_name == "found ore, mining is possible":
        keyboard = at_location_kb(gps)
    elif menu == "Ship AI":
        keyboard = ship_ai_kb()
    else:
        keyboard = main_kb(gps)
    return keyboard


def core_kb(gps=None) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Ship AI")
    kb.button(text="Terminal")
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
    kb.button(text="Jump Home")
    kb.button(text="Travel forward")
    kb.button(text="Mine here")
    kb.button(text="Scan area")
    kb.button(text="Back")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def terminal_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Ship info")
    kb.button(text="Guild")
    kb.button(text="Cargo")
    kb.button(text="Inventory")
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
    kb.button(text="Bar")
    kb.button(text="Undock")
    kb.button(text="Terminal")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def admin_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="/logout")
    kb.button(text="/load_enemies")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

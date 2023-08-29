from aiogram.types import Message
from app.database import db_read_details, db_write_int, db_read_int, db_read_dict, db_write_dict, db_write_dict_full, db_read_full_name
import asyncio
from random import randint
import game_logic.inventory as invent
import game_logic.mechanics as m
from game_logic.space_map import *
from game_logic.states import State
import keyboards.main_kb as kb


async def init_fight(message: Message, state: State):
    pass

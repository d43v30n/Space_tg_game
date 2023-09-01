#!/usr/bin/env python3

import asyncio
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from app import database as db
from handlers import admin, settings, core, ship_ai, terminal, locations, errors
from game_logic import fight as f

# debug

load_dotenv()
TOKEN = getenv("BOT_TOKEN")


async def on_startup(bot: Bot) -> None:
    '''initialize db'''
    await db.db_start_pl()
    await db.db_start_gm()


    print('> BOT has been successfully started')


async def main():
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_routers(admin.router)
    dp.include_routers(core.router)
    dp.include_routers(settings.router)
    dp.include_routers(ship_ai.router)
    dp.include_routers(terminal.router)
    dp.include_routers(locations.router)
    dp.include_routers(errors.router)

    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    pass

import asyncio
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from app import database as db
from handlers import admin, core, ship_ai, terminal, locations, errors

load_dotenv()
TOKEN = getenv("BOT_TOKEN")


async def on_startup(bot: Bot) -> None:
    '''initialize db'''
    await db.db_start()
    # await db.
    print('Бот успешно запущен!')


async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp.include_routers(admin.router)
    dp.include_routers(core.router)
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

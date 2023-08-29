from app.database import db_write_int, db_energy_parser
# , add_task_scheduler
from game_logic.mechanics import get_current_energy, get_max_energy
# from asyncio import sleep, gather, create_task


ENERGY_CD = 5


async def restore_one_energy(user_id):
    current_energy = await get_current_energy(user_id)
    # await sleep(ENERGY_CD)
    await db_write_int("players", user_id, "current_energy", current_energy+1)


async def restore_all_energy(user_id):
    current_energy = await get_max_energy(user_id)
    # await sleep(ENERGY_CD)
    await db_write_int("players", user_id, "current_energy", current_energy)


async def use_one_energy(user_id):
    current_energy = await get_current_energy(user_id)
    # await sleep(ENERGY_CD)
    if current_energy >= 1:
        await db_write_int("players", user_id, "current_energy", current_energy-1)
        return current_energy-1
    else:
        return current_energy


# async def restore_energy_cells():
# data = await db_energy_parser()
# tasks = []
# for line in data:
# user_id = line[0]
# current_energy = line[1]
# max_energy = line[2]
# num_cells = max_energy - current_energy
# for _ in range(num_cells):
# await add_task_scheduler(restore_one_energy, ENERGY_CD, user_id)
# await gather(*tasks)

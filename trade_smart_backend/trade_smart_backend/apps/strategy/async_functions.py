import asyncio
from datetime import datetime

async def indicator_data_populator_bulk(*args):
    coroutines = []
    for indicator_entity in args:
        coroutines.append(indicator_data_populator(indicator_entity))
    asyncio.gather(*coroutines)

async def indicator_data_populator(indicator_entity):
    indicator_entity.populate_data()
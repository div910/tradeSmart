import asyncio
from datetime import datetime

async def measurement_data_populator_bulk(*args):
    coroutines = []
    for measurement_entity in args:
        coroutines.append(measurement_data_populator(measurement_entity))
    asyncio.gather(*coroutines)

async def measurement_data_populator(measurement_entity):
    measurement_entity.populate_data()
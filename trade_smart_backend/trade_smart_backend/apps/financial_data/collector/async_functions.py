import asyncio
from datetime import datetime
from trade_smart_backend.apps.financial_data.collector.financial_data_collector_base import DataCollector

def fetch_security_candlestick_data_bulk(*args):
    # Fetch list of securities to gather financial_data for
    coroutines = []
    all_security_entity = []
    # Call individual financial_data collection function to fetch financial_data from respective
    # source and save into influx.
    for current_security_entity in all_security_entity:
        coroutines.append(fetch_security_candlestick_data(current_security_entity))
    asyncio.gather(*coroutines)

async def fetch_security_candlestick_data(current_security_entity):
    # write a function to fetch candlestick financial_data for input security entity and save it into influx
    DataCollector(current_security_entity)



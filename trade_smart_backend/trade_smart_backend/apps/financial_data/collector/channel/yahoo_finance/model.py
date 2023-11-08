import numpy as np
import pandas as pd
from pathlib import Path
from trade_smart_backend.utils.influx_db_utils import Influx
import asyncio
#Data Source
import yfinance as yf


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


class DataCollector:

    def __init__(self, data_collector_entity=None):
        self.security_entity_obj = data_collector_entity
        self.symbol = config.get("symbol")
        self.msft = yf.Ticker(self.symbol)
        self.influx_obj = Influx()

    """
        This function should bring all the possible details available on the platform, for a particular stock.
        Should process all information and model it for our financial_data storage
        And after that should place the content into respective storages
    """
    def add_stock_to_database(self):
        # Fetch Stock Details from Yahoo Finance
        # process stock details dictionary to store into Database
        # Store Stock Details into MySQL database
        pass


    """
        This function would let you fetch history financial_data from yahoo finance for a particular stock
        This will process that financial_data and fetch relevent details, convert it into dataframes
        Post processing it will store all financial_data into a timeseries dataframe.
    """
    def get_history_data_previous_date(self):
        history_data = self.msft.history(period="1d", interval="1m",
                start=None, end=None, prepost=False, actions=True,
                auto_adjust=True, back_adjust=False, repair=True, keepna=False,
                proxy=None, rounding=False, timeout=10,
                raise_errors=False)

        # Create a new DataFrame with specific columns
        history_data_imp_columns = history_data.loc[:, ['Open', 'High', 'Low', 'Close', 'Volume']].copy()

        # Rename columns of the new DataFrame
        history_data_imp_columns_renamed = history_data_imp_columns.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})

        for i in range(0, len(history_data_imp_columns_renamed), 100):
            chunk = history_data_imp_columns_renamed.iloc[i:i + 100]
            processed_chunk = self.influx_obj.insert_dataframe(measurement='candlestick', tag_dict={'symbol': self.symbol},
                                              fields_dataframe=chunk)
            print(processed_chunk)

        return {"success": True, "info": f"financial_data collected for tasks: {tasks} previous date {processed_result}"}


    """
        This function would let you fetch history financial_data from yahoo finance for a particular stock
        This will process that financial_data and fetch relevent details, convert it into dataframes
        Post processing it will store all financial_data into a timeseries dataframe.
    """
    async def get_history_data_previous_date_async(self):
        history_data = self.msft.history(period="1d", interval="1m",
                start=None, end=None, prepost=False, actions=True,
                auto_adjust=True, back_adjust=False, repair=True, keepna=False,
                proxy=None, rounding=False, timeout=10,
                raise_errors=False)

        # Create a new DataFrame with specific columns
        history_data_imp_columns = history_data.loc[:, ['Open', 'High', 'Low', 'Close', 'Volume']].copy()

        # Rename columns of the new DataFrame
        history_data_imp_columns_renamed = history_data_imp_columns.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
        tasks = []
        for i in range(0, len(history_data_imp_columns_renamed), 100):
            chunk = history_data_imp_columns_renamed.iloc[i:i + 100]
            task = asyncio.create_task(self.influx_obj.insert_dataframe_async(measurement='candlestick', tag_dict={'symbol': self.symbol}, fields_dataframe=chunk))
            tasks.append(task)

        processed_result = await asyncio.gather(*tasks)
        print(processed_result)
        return {"success": True, "info": f"financial_data collected for tasks: {tasks} previous date {processed_result}"}



    """
        Same as get_history_data_previous_date() but capable of fetching financial_data for custom dates
    """

    def get_history_data_custom_dates(self, start=None, end=None):
        history_data = self.msft.history(period=None, interval="1m",
                                         start=start, end=end, prepost=False, actions=True,
                                         auto_adjust=True, back_adjust=False, repair=True, keepna=False,
                                         proxy=None, rounding=False, timeout=10,
                                         raise_errors=False)

        # Create a new DataFrame with specific columns
        history_data_imp_columns = history_data.loc[:, ['Open', 'High', 'Low', 'Close', 'Volume']].copy()

        # Rename columns of the new DataFrame
        history_data_imp_columns_renamed = history_data_imp_columns.rename(
            columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})

        for i in range(0, len(history_data_imp_columns_renamed), 100):
            chunk = history_data_imp_columns_renamed.iloc[i:i + 100]
            processed_chunk = self.influx_obj.insert_dataframe(measurement='candlestick',
                                                               tag_dict={'symbol': self.symbol},
                                                               fields_dataframe=chunk)
            print(processed_chunk)

        return {"success": True, "info": "financial_data colllected for previous date"}

    async def execute_parallel(self):
        tasks = []
        for _ in range(10):
            task = asyncio.create_task(self.influx_obj.my_function())
            tasks.append(task)
        ans = await asyncio.gather(*tasks)
        return ans


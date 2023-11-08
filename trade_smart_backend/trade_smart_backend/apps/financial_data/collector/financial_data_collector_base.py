from abc import ABC, abstractmethod #For abstract Methods
import numpy as np
import pandas as pd
from pathlib import Path
from trade_smart_backend.utils.influx_db_utils import Influx
import asyncio
#Data Source
import yfinance as yf


class DataCollector(ABC):

    def __init__(self, data_collector_entity=None):
        self.security_entity_obj = data_collector_entity
        self.symbol = self.security_entity_obj.symbol
        self.msft = yf.Ticker(self.symbol)


    def add_update_security_to_knowledge(self):
        """
            This function should bring all the possible details available on the platform, for a particular stock.
            Should process all information and model it for our financial_data storage in mysql
            And after that should place the content into respective storages
        """

        # Fetch Stock Details from Yahoo Finance
        knowledge = self.get_latest_security_knowledge()

        # process stock details dictionary to store into Database
        db_save_object = {
            "":""
        }
        # Store Stock Details into MySQL database



    def add_latest_candlestick(self):
        pass

    def add_history_candlestick(self, **kwargs):
        """
            This function would let you fetch history financial_data from yahoo finance for a particular stock
            This will process that financial_data and fetch relevent details, convert it into dataframes
            Post processing it will store all financial_data into a timeseries dataframe.
        """
        history_data = self.msft.history(period=None, interval="1m",
                                         start=kwargs.get('start'), end=kwargs.get('end'), prepost=False, actions=True,
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

        # return {"success": True, "info": "financial_data colllected for previous date"}

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

        return {"success": True, "info": f"financial_data collected for tasks: {'tasks'} previous date {'processed_result'}"}

import asyncio

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
    history_data_imp_columns_renamed = history_data_imp_columns.rename(
        columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
    tasks = []
    for i in range(0, len(history_data_imp_columns_renamed), 100):
        chunk = history_data_imp_columns_renamed.iloc[i:i + 100]
        task = asyncio.create_task(
            self.influx_obj.insert_dataframe_async(measurement='candlestick', tag_dict={'symbol': self.symbol},
                                                   fields_dataframe=chunk))
        tasks.append(task)

    processed_result = await asyncio.gather(*tasks)
    print(processed_result)
    return {"success": True, "info": f"financial_data collected for tasks: {tasks} previous date {processed_result}"}


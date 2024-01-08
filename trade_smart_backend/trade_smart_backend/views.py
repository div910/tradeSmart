import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import HttpResponse
from trade_smart_backend.celery_app.tasks import debug_task
# from trade_smart_backend.celery_app.tasks_data import example_task
import pandas as pd

def health(request):
    # result = example_task.apply_async()
    # print(result)
    result_2 = debug_task.apply_async(queue='ts_queue_1')
    print(result_2)
    print("HELLO")
    return HttpResponse("Health Success.")

def index(request):
    return render(request, "index.html")

def push_task(request):

    return HttpResponse("Push Task Success.")


def get_history_data():
    pass

def get_ticker_data():
    pass

def build_indicator_data():
    pass

def purge_old_data():
    pass


@csrf_exempt
def store_instrument(request):
    body_params = json.loads(request.body.decode("utf-8"))
    data_storage_log_dict = {
        "ins_name": body_params.get("instrument"),
        "ins_source": "API",
        "ins_destination": "Influx",
        "ins_meta": json.dumps({
            "data": {
                "high": body_params.get("high"),
                "open": body_params.get("open"),
                "close": body_params.get("close"),
                "low": body_params.get("low"),
                "volume": body_params.get("volume")
            }
        })
    }
    from trade_smart_backend.models.mysql_models.data_storage_log import DataStorageLog
    db_resp = DataStorageLog().insert(data_storage_log_dict)
    if db_resp.get("success", False) is False:
        print(db_resp)
        return HttpResponse(json.dumps({"success": False, "error": f"Insert Failure in MySQL, {db_resp.get('message')}"}))

    # Send data to Influx
    df_dict = {
        'Open': [body_params.get("open"), body_params.get("open")],
        'High': [body_params.get("high"), body_params.get("high")],
        'Low': [body_params.get("high"), body_params.get("high")],
        'Close': [body_params.get("high"), body_params.get("high")],
        'Volume': [body_params.get("volume"), body_params.get("volume")]
    }
    # df = pd.DataFrame(list(df_dict.items()))
    from trade_smart_backend.utils.influx_db_utils import Influx
    measurement_list = [{
        'Open': body_params.get("open"),
        'High': body_params.get("high"),
        'Low': body_params.get("high"),
        'Close': body_params.get("high"),
        'Volume': body_params.get("volume")
    }]
    influx_resp = Influx().insert_dataframe(measurement = "test", tag_dict = {"instrument": data_storage_log_dict.get("ins_name")}, fields_list=measurement_list)
    print(influx_resp)
    return HttpResponse(json.dumps({"success": True}))

@csrf_exempt
def collect_angel_broking_history_data(request):
    from trade_smart_backend.apps.financial_data.collector.channel.angel_broking.model import DataCollector
    DataCollector().get_history_data_previous_date()
    return HttpResponse(json.dumps({"success": True}))

@csrf_exempt
def end_to_end(request):
    body_params = json.loads(request.body.decode("utf-8"))

    # get data from yahoo finance
    import yfinance as yf
    msft = yf.Ticker("MSFT")
    print(msft.info)

    history_data = msft.history(period="1d", interval="1m",
                                start=None, end=None, prepost=False, actions=True,
                                auto_adjust=True, back_adjust=False, repair=True, keepna=False,
                                proxy=None, rounding=False, timeout=10,
                                raise_errors=False)
    print(type(history_data))

    # Create a new DataFrame with specific columns
    history_data_imp_columns = history_data.loc[:, ['Open', 'High', 'Low', 'Close', 'Volume']].copy()

    # Rename columns of the new DataFrame
    history_data_imp_columns_renamed = history_data_imp_columns.rename(
        columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})

    # Store Data in Influx DB

    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    from datetime import datetime

    url = "http://localhost:8086"
    token = 'yx6JRL0nCzxw5Q67CQ2OPlFdJoVqo4cOHk7gRjfMY43cJlIzRXXNJ0MTB9K-EY7PwGRpq_uRKAAcDYsoagA5gg=='
    org = 'trade_smart'
    bucket = 'trade_smart'

    def insert_dataframe(measurement=None, tag_dict=None, fields_dataframe=None, fields_list=[]):
        if measurement is None or tag_dict is None:
            return {"success": False, "error": "Incorrect input Arguments"}

        # # Convert DataFrame to InfluxDB line protocol format
        points = []
        if fields_dataframe is not None:
            for _, row in fields_dataframe.iterrows():
                point = Point(measurement)
                for tag_key, tag_value in tag_dict.items():
                    point.tag(tag_key, tag_value)
                for column, value in row.items():
                    point.field(column, value)
                point.time(_)
                points.append(point)
        if fields_list is not None or len(fields_list) > 0:
            for field in fields_list:
                point = Point(measurement)
                for tag_key, tag_value in tag_dict.items():
                    point.tag(tag_key, tag_value)
                for key, val in field.items():
                    point.field(key, val)
                points.append(point)

        # [p for p in points]
        line_protocol = "\n".join([p.to_line_protocol() for p in points])

        # Write financial_data to InfluxDB

        client = InfluxDBClient(url=url, token=token)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        writer_resp = write_api.write(bucket=bucket, org=org, record=line_protocol)
        client.close()

        # Write financial_data to InfluxDB
        # with InfluxDBClient(url=self.url, token=self.token) as client:
        #     with client.write_api(write_options=SYNCHRONOUS) as write_api:
        #         write_api.write(bucket=self.bucket, org=self.org, record=line_protocol)

        return

    for i in range(0, len(history_data_imp_columns_renamed), 100):
        chunk = history_data_imp_columns_renamed.iloc[i:i + 100]
        processed_chunk = insert_dataframe(measurement='candlestick', tag_dict={'symbol': "MSFT"},
                                           fields_dataframe=chunk)
        print(processed_chunk)

    # Fetch data from Influx DB and draw indicators
    import pandas as pd
    url = "http://localhost:8086"
    token = 'yx6JRL0nCzxw5Q67CQ2OPlFdJoVqo4cOHk7gRjfMY43cJlIzRXXNJ0MTB9K-EY7PwGRpq_uRKAAcDYsoagA5gg=='
    org = 'trade_smart'
    bucket = 'trade_smart'

    def fetch_records(measurement):
        # Need to implement a query builder method
        client = InfluxDBClient(url=url, token=token)
        query = f'from(bucket: "{bucket}") |> range(start: 0) |> filter(fn: (r) => r._measurement == "{measurement}")'
        query = """
            from(bucket: "trade_smart")
              |> range(start: -24h)
              |> filter(fn: (r) => r["_measurement"] == "candlestick")
              |> filter(fn: (r) => r["symbol"] == "MSFT")
              |> yield(name: "mean")
        """
        print(query)
        tables = client.query_api().query(query, org=org)
        client.close()
        return tables

    influx_resp = fetch_records("MSFT")
    print(influx_resp)
    data_frames = [pd.DataFrame(table.records) for table in influx_resp]
    # Print the DataFrame(s)

    for i, df in enumerate(data_frames):
        print(f"\nDataFrame {i + 1}:\n{df}")

    # Store Indicator in Influx DB
    # Trade
    return HttpResponse(json.dumps({"success": True}))


from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from django.conf import settings
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import time
import asyncio

class Influx():

    def __init__(self, database='nse_stocks'):
        self.url = settings.INFLUX_DATABASE.get('CONNECT', {}).get('url', 'http://localhost:8086')
        self.token = settings.INFLUX_DATABASE.get('CONNECT', {}).get('token', '')
        self.org = settings.INFLUX_DATABASE.get('CONNECT', {}).get('org', '')
        self.bucket = settings.INFLUX_DATABASE.get('CONNECT', {}).get('bucket', '')

    def insert_dataframe(self, measurement=None, tag_dict=None, fields_dataframe=None, fields_list=[]):
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

        if fields_list is not None:
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
        client = InfluxDBClient(url=self.url, token=self.token)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        writer_resp = write_api.write(bucket=self.bucket, org=self.org, record=line_protocol)
        client.close()

        # Write financial_data to InfluxDB
        # with InfluxDBClient(url=self.url, token=self.token) as client:
        #     with client.write_api(write_options=SYNCHRONOUS) as write_api:
        #         write_api.write(bucket=self.bucket, org=self.org, record=line_protocol)

        return

    async def insert_dataframe_async(self, measurement=None, tag_dict=None, fields_dataframe=None, num = 0):
        print(f'HERE~{num}')
        if measurement is None or tag_dict is None or fields_dataframe is None:
            return {"success": False, "error": "Incorrect input arguments"}

        # Convert DataFrame to InfluxDB line protocol format
        points = []
        for _, row in fields_dataframe.iterrows():
            point = Point(measurement)
            for tag_key, tag_value in tag_dict.items():
                point.tag(tag_key, tag_value)
            for column, value in row.items():
                point.field(column, value)
            point.time(_)
            points.append(point)

        line_protocol = "\n".join([p.to_line_protocol() for p in points])

        async with InfluxDBClientAsync(url=self.url, token=self.token, org=self.org) as client:
            await client.write_api().write(bucket=self.bucket, record=line_protocol)

        return {"success": True}

    def fetch_records(self, measurement):
        # Need to implement a query builder method
        client = InfluxDBClient(url=self.url, token=self.token)
        query = f'from(bucket: "{self.bucket}") |> range(start: 0) |> filter(fn: (r) => r._measurement == "{measurement}")'
        tables = client.query_api().query(query, org=self.org)
        client.close()
        return tables

    def execute_custom_query(self, query=None):
        # Need to implement a query builder method
        if query is None:
            return
        tables = None
        try:
            with InfluxDBClient(url=self.url, token=self.token) as client:
                tables = client.query_api().query(query, org=self.org)
        except Exception as ex:
            raise

        return tables

    def delete_records(self, measurement=None, start=None, end=None, tag=None):
        """

        :param measurement: str | candlestick
        :param start: Datetime
        :param end: Datetime
        :param tag: Dict | {'symbol': 'IDFCBK.NS'}
        :return:
        """
        client = InfluxDBClient(url=self.url, token=self.token)
        delete_query = f'from(bucket: "{self.bucket}") |> range(start: 0) |> filter(fn: (r) => r._measurement == "{measurement}") |> delete()'

        # User start = 0 for delete all Unix epoch start time (1970-01-01 00:00:00 UTC)
        start = datetime.utcfromtimestamp(0)
        end = datetime.utcnow()
        tables = client.delete_api().delete(start=start, stop=end, predicate=f'_measurement="{measurement}"',
                                            bucket=self.bucket, org=self.org)
        client.close()
        return tables

    async def my_function(self):
        # Simulate a function with a runtime of 1 second
        await asyncio.sleep(10)
        print("Function executed.")
        return {"success": True}
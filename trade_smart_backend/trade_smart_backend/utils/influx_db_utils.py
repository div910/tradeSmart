from influxdb_client import InfluxDBClient, Point
from django.conf import settings
from influxdb_client.client.write_api import SYNCHRONOUS

class Influx():

    def __init__(self, database='nse_stocks'):
        self.url = settings.INFLUX_DATABASE.get('CONNECT', {}).get('url', 'http://localhost:8086')
        self.token = settings.INFLUX_DATABASE.get('CONNECT', {}).get('token', '')
        self.org = settings.INFLUX_DATABASE.get('CONNECT', {}).get('org', '')
        self.bucket = settings.INFLUX_DATABASE.get('CONNECT', {}).get('bucket', '')

    def insert_dataframe(self, measurement=None, tag_dict=None, fields_dataframe=None):
        if measurement is None or tag_dict is None or fields_dataframe is None:
            return {"success": False, "error": "Incorrect input Arguments"}

        # # Convert DataFrame to InfluxDB line protocol format
        points = []
        for _, row in fields_dataframe.iterrows():
            point = Point(measurement)
            for tag_key, tag_value in tag_dict.items():
                point.tag(tag_key, tag_value)
            for column, value in row.items():
                point.field(column, value)
            point.time(_)
            points.append(point)

        # [p for p in points]
        line_protocol = "\n".join([p.to_line_protocol() for p in points])

        # Write data to InfluxDB
        client = InfluxDBClient(url=self.url, token=self.token)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        writer_resp = write_api.write(bucket=self.bucket, org=self.org, record=line_protocol)
        client.close()

        return writer_resp
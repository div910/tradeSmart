from influxdb import InfluxDBClient
import datetime
import logging
from trade_smart_backend.apps.app_settings import *
from django.conf import settings

class Influx():

    def __init__(self, database='nse_stocks'):
        self.db = settings.INFLUX_DATABASE.get('DATABASE', {}).get(database, 'nse_stocks')
        self.client = InfluxDBClient(settings.INFLUX_DATABASE.get('CONNECT', {}).get('host'), settings.INFLUX_DATABASE.get('CONNECT', {}).get('port'), settings.INFLUX_DATABASE.get('CONNECT', {}).get('username'), settings.INFLUX_DATABASE.get('CONNECT', {}).get('password'), self.db)
        self.client.create_database(self.db)
        self.client.switch_database(self.db)

    #Setup Payload
    def prepare_history_data(self, measurement, source, history_data):
        json_payload = []
        for i in history_data:
            time = datetime.datetime.strptime(i[0].split('+')[0], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=5, minutes=30)
            data = {
                "measurement": measurement,
                "tags": {
                    "source": source,
                    "ticker": "TSLA"
                },
                "time": time,
                "fields": {
                    'open': i[1],
                    'high': i[2],
                    'low': i[3],
                    'close': i[4],
                    'volume': i[5]
                }
            }
            json_payload.append(data)
        self.insert(json_payload)
        return json_payload

    def validate_data(self, json_payload):
    #     use json schema validator
        return {'success': True}

    def insert(self, json_payload):
        validation_resp = self.validate_data(json_payload)
        if validation_resp.get('success', False) is False:
            logging.info(f'Validation Failed for data to be inserted {json_payload}')
            return {'success': False, 'error': ERROR_RESPONSE_CODES['INPUT_VALIDATION_FAILURE']}
        try:
            self.client.write_points(json_payload)
        except Exception as ex:
            logging.error(f'Influx insert error {ex} for payload {json_payload}')
            return {'success': False, 'error': ERROR_RESPONSE_CODES['DATABASE_FAILURE']}
        return {'success': True}
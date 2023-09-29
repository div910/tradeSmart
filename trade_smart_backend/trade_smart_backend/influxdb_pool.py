# # influxdb_pool.py
#
# from influxdb_client.client import InfluxDBClient
# # from influxdb_client_fork import InfluxDBClientPool
#
# from django.conf import settings
#
# # INFLUXDB_POOL = InfluxDBClientPool(**settings.INFLUXDB_CONNECTION_POOL)
#
# class InfluxDBPoolManager:
#     def __enter__(self):
#         self.client = INFLUXDB_POOL.get_client()
#         return self.client
#
#     def __exit__(self, exc_type, exc_value, traceback):
#         INFLUXDB_POOL.release_client(self.client)

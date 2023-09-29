from trade_smart_backend.utils.influx_db_utils import Influx
class MeasurementEntity:
    def __init__(self, **kwargs):
        "source"
        "bucket"
        "name"
        "start_time"
        "time_delta"

        self.name = kwargs.get('name')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.data = kwargs.get('financial_data')
        self.influx_db_obj = Influx()

    def set_tags(self, tag_dict={}):
        pass

    def populate_data(self):
        query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: {self.start_time})
              |> filter(fn: (r) =>
                  r["_measurement"] == "RSI" and
                  r["NIFTY50"] == "true" and
                  r["Exchange"] == "NSE"
              )
              |> project(columns: ["_time", "A", "B", "C"])
        '''
        db_resp = self.influx_db_obj.execute_custom_query(query)
        # db_resp_df = pd.DataFrame(result)
        self.data = db_resp
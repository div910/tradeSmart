STRATEGY_EXECUTION_CONFIG = {
    "config_1": {
        "measurement_data": [
            {
                "source": "influxdb",
                "bucket": "trade_smart",
                "name": "rsi",
                "start_time": "datetime.datetime.now()", # eval datetime
                "time_delta": "datetime.timedelta(days=5)", # eval timedelta
            },
            {
                "source": "influxdb",
                "bucket": "trade_smart",
                "name": "macd",
                "start_time": "datetime.datetime.now()", # eval datetime
                "time_delta": "datetime.timedelta(days=5)", # eval timedelta
            },
            {
                "source": "influxdb",
                "bucket": "trade_smart",
                "name": "mv20",
                "start_time": "datetime.datetime.now()", # eval datetime
                "time_delta": "datetime.timedelta(days=5)", # eval timedelta
            }
        ]
    }
}
STRATEGY_EXECUTION_CONFIG = {
    "config_1": {
        "indicator_data": [
            {
                "name": "rsi",
                "start_time": "current",
                "time_delta": "60 days",
                "interval": "minutes"
            },
            {
                "name": "macd",
                "start_time": "current",
                "time_delta": "40 days",
                "interval": "minutes"
            },
            {
                "name": "mv20",
                "start_time": "current",
                "time_delta": "20 days",
                "interval": "seconds"
            }
        ]
    }
}
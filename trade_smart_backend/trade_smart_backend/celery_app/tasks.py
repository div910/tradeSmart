from trade_smart_backend.celery_app.apps import app
from celery.schedules import crontab
import asyncio
from trade_smart_backend.apps.financial_data.channel.yahoo_finance.data_collector import \
    fetch_security_candlestick_data_bulk


@app.task()
def debug_task(*args, **kwargs):
    print("DEBUG_TASK")


# @periodic_task(run_every=crontab(minute='*/5'))  # Run every 5 minutes
# def scheduled_example_task():
#     print("This is a scheduled example task.")
#     # Your task logic goes
#     here

def collect_latest_candlestick():
    asyncio.run(fetch_security_candlestick_data_bulk())

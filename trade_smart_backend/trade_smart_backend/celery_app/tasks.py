from trade_smart_backend.celery_app.apps import app
from celery.schedules import crontab

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# @periodic_task(run_every=crontab(minute='*/5'))  # Run every 5 minutes
# def scheduled_example_task():
#     print("This is a scheduled example task.")
#     # Your task logic goes here
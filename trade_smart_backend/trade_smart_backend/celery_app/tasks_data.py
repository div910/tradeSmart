from celery import shared_task
from trade_smart_backend.celery_app.apps import app

# @shared_task
# def example_task():
#     print("This is an example Celery task.")
#     # Your task logic goes here

@app.task(bind=True)
def example_task(self):
    print('Request: {0!r}'.format(self.request))

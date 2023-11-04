from trade_smart_backend.celery_app.apps import app


# @shared_task
# def example_task():
#     print("This is an example Celery task.")

@app.task()
def example_task(*args, **kwargs):
    print("EXAMPLE_TASK")

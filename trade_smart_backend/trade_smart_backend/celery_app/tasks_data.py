from celery import shared_task

@shared_task
def example_task():
    print("This is an example Celery task.")
    # Your task logic goes here
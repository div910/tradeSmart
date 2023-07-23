from django.shortcuts import render
from django.shortcuts import HttpResponse
from trade_smart_backend.celery_app.tasks import debug_task
# from trade_smart_backend.celery_app.tasks_data import example_task


def health(request):
    # result = example_task.apply_async()
    # print(result)
    result_2 = debug_task.apply_async()
    print(result_2)
    print("HELLO")
    return HttpResponse("Health Success.")

def index(request):
    return render(request, "index.html")

def get_history_data():
    pass

def get_ticker_data():
    pass

def build_indicator_data():
    pass

def purge_old_data():
    pass

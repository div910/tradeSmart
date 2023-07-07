from django.shortcuts import render
from django.shortcuts import HttpResponse


def health(request):
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

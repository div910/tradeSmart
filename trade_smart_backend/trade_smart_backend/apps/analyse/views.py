from django.shortcuts import render
from django.shortcuts import HttpResponse

def collect_history_data(request):
    return HttpResponse("collect_history_data Success.")
from django.shortcuts import render
from django.shortcuts import HttpResponse
# Create your views here.
from trade_smart_backend.apps.data.services.web_socket import WebSocketConsumer

def collect_data(request):
    return HttpResponse("collect_history_data Success.")
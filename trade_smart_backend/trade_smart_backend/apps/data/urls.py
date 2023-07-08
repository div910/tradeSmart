from django.urls import path
from django.urls import re_path
from trade_smart_backend.apps.data.services.web_socket import WebSocketConsumer
from .views import *

urlpatterns = [
    re_path(r'ws/websocket/$', WebSocketConsumer.as_asgi()),
    path('collect_data/', collect_data),
]
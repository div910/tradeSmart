from django.urls import path
from .views import *

urlpatterns = [
    path('collect_history_data/', collect_history_data),
]
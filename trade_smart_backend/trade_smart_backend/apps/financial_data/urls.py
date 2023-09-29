from django.urls import path
from django.urls import re_path
from .views import *

urlpatterns = [
    path('collect_data/', collect_history_data_from_yahoo),
]
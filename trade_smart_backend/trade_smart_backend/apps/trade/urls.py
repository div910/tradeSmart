from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('buy/', buy),
    path('sell/', sell)
]
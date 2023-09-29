"""
URL configuration for trade_smart_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *
from trade_smart_backend.apps.trade import urls as trade_urls
from trade_smart_backend.apps.financial_data import urls as data_urls
from trade_smart_backend.apps.analyse import urls as analyse_urls

urlpatterns = [
    path('', index),
    path('health/', health),
    path('admin/', admin.site.urls),
    path('trade/', include(trade_urls)),
    path('financial_data/', include(data_urls)),
    path('analyse/', include(analyse_urls))
]
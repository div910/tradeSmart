from django.shortcuts import render
from django.shortcuts import HttpResponse

def sell(request):
    return HttpResponse("Sell Success.")

def buy(request):
    return HttpResponse("Buy Success.")
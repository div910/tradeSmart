from django.shortcuts import HttpResponse, render
# Create your views here.
import json
from trade_smart_backend.apps.financial_data.collector.channel.yahoo_finance.model import DataCollector

async def collect_history_data_from_yahoo(request):
    config = {
        "symbol": request.GET.get('symbol')
    }
    obj = DataCollector(config)
    # resp = await obj.execute_parallel()
    resp = await obj.get_history_data_previous_date_async()
    return HttpResponse(f"collect_history_data Success. {resp}")

def view_financial_data(request):
    body = request.GET
    # create data collector entity
    # create object of financial data projector class
    # call prepare response function
    # return rendered response
    return render(request, "financial_data/view_candlestick.html")

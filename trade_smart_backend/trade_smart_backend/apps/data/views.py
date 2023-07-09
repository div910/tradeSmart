from django.shortcuts import HttpResponse
# Create your views here.
from trade_smart_backend.apps.data.channel.yahoo_finance.data_collector import DataCollector

def collect_history_data_from_yahoo(request):
    config = {
        "symbol": request.GET.get('symbol')
    }
    resp = DataCollector(config).get_history_data_previous_date()
    return HttpResponse(f"collect_history_data Success. {resp}")
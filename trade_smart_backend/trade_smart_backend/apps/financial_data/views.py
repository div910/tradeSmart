from django.shortcuts import HttpResponse
# Create your views here.
from trade_smart_backend.apps.financial_data.channel.yahoo_finance.data_collector import DataCollector

async def collect_history_data_from_yahoo(request):
    config = {
        "symbol": request.GET.get('symbol')
    }
    obj = DataCollector(config)
    # resp = await obj.execute_parallel()
    resp = await obj.get_history_data_previous_date_async()
    return HttpResponse(f"collect_history_data Success. {resp}")
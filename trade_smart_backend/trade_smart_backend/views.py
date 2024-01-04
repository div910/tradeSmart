import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import HttpResponse
from trade_smart_backend.celery_app.tasks import debug_task
# from trade_smart_backend.celery_app.tasks_data import example_task
import pandas as pd

def health(request):
    # result = example_task.apply_async()
    # print(result)
    result_2 = debug_task.apply_async(queue='ts_queue_1')
    print(result_2)
    print("HELLO")
    return HttpResponse("Health Success.")

def index(request):
    return render(request, "index.html")

def push_task(request):

    return HttpResponse("Push Task Success.")


def get_history_data():
    pass

def get_ticker_data():
    pass

def build_indicator_data():
    pass

def purge_old_data():
    pass


@csrf_exempt
def store_instrument(request):
    body_params = json.loads(request.body.decode("utf-8"))
    data_storage_log_dict = {
        "ins_name": body_params.get("instrument"),
        "ins_source": "API",
        "ins_destination": "Influx",
        "ins_meta": json.dumps({
            "data": {
                "high": body_params.get("high"),
                "open": body_params.get("open"),
                "close": body_params.get("close"),
                "low": body_params.get("low"),
                "volume": body_params.get("volume")
            }
        })
    }
    from trade_smart_backend.models.mysql_models.data_storage_log import DataStorageLog
    db_resp = DataStorageLog().insert(data_storage_log_dict)
    if db_resp.get("success", False) is False:
        print(db_resp)
        return HttpResponse(json.dumps({"success": False, "error": f"Insert Failure in MySQL, {db_resp.get('message')}"}))

    # Send data to Influx
    df_dict = {
        'Open': [body_params.get("open"), body_params.get("open")],
        'High': [body_params.get("high"), body_params.get("high")],
        'Low': [body_params.get("high"), body_params.get("high")],
        'Close': [body_params.get("high"), body_params.get("high")],
        'Volume': [body_params.get("volume"), body_params.get("volume")]
    }
    # df = pd.DataFrame(list(df_dict.items()))
    from trade_smart_backend.utils.influx_db_utils import Influx
    measurement_list = [{
        'Open': body_params.get("open"),
        'High': body_params.get("high"),
        'Low': body_params.get("high"),
        'Close': body_params.get("high"),
        'Volume': body_params.get("volume")
    }]
    influx_resp = Influx().insert_dataframe(measurement = "test", tag_dict = {"instrument": data_storage_log_dict.get("ins_name")}, fields_list=measurement_list)
    print(influx_resp)
    return HttpResponse(json.dumps({"succss": True}))


# from trade_smart_backend.apps.financial_data.services.smart_web_socket import SmartConnect
from .smart_web_socket import SmartConnect
import pyotp

class HistoricalDataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.obj = None

    def login(self, client_id, password):
        self.obj = SmartConnect(api_key=self.api_key)
        data = self.obj.generateSession(client_id, password)
        self.obj.set_access_token(data["financial_data"]["accessToken"])
        refresh_token = data["financial_data"]["refreshToken"]
        self.obj.set_refresh_token(refresh_token)

    def fetch_historical_data(self, exchange, symbol_token, interval, from_date, to_date):
        historic_param = {
            "exchange": exchange,
            "symboltoken": symbol_token,
            "interval": interval,
            "fromdate": from_date,
            "todate": to_date
        }
        try:
            self.obj.getCandleData(historic_param)
        except Exception as e:
            print("Historic API failed: {}".format(str(e)))

# Example usage
if __name__ == "__main__":
    api_key = "YOUR_API_KEY"
    client_id = "YOUR_CLIENT_ID"
    password = "YOUR_PASSWORD"
    totp = pyotp.TOTP(token).now()
    obj = HistoricalDataFetcher(api_key)
    obj.login(client_id, password)

    exchange = "NSE"
    symbol_token = "3045"
    interval = "ONE_MINUTE"
    from_date = "2021-02-08 09:00"
    to_date = "2021-02-08 09:16"

    obj.fetch_historical_data(exchange, symbol_token, interval, from_date, to_date)

# try:
#     historicParam={
#     "exchange": "NSE",
#     "symboltoken": "3045",
#     "interval": "ONE_MINUTE",
#     "fromdate": "2021-02-08 09:00",
#     "todate": "2021-02-08 09:16"
#     }
#     obj.getCandleData(historicParam)
# except Exception as e:
#     print("Historic Api failed: {}".format(e.message))
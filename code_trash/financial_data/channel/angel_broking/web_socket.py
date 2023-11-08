import asyncio
import websockets
# from trade_smart_backend.apps.financial_data.services.smart_web_socket import SmartWebSocket
from django.conf import settings
# from smartapi import SmartWebSocket
# from .smart_web_socket import SmartWebSocket

"""
Created on Fri Apr 23 11:38:36 2021

@author: Sandip.Khairnar
"""

import websocket
import six
import base64
import zlib
import datetime
import time
import json
import threading
import ssl


class SmartWebSocket(object):
    ROOT_URI = 'wss://wsfeeds.angelbroking.com/NestHtml5Mobile/socket/stream'
    HB_INTERVAL = 30
    HB_THREAD_FLAG = False
    WS_RECONNECT_FLAG = False
    feed_token = None
    client_code = None
    ws = None
    task_dict = {}

    def __init__(self, FEED_TOKEN, CLIENT_CODE):
        self.root = self.ROOT_URI
        self.feed_token = FEED_TOKEN
        self.client_code = CLIENT_CODE
        if self.client_code == None or self.feed_token == None:
            return "client_code or feed_token or task is missing"

    def _subscribe_on_open(self):
        request = {"task": "cn", "channel": "NONLM", "token": self.feed_token, "user": self.client_code,
                   "acctid": self.client_code}
        print(request)
        self.ws.send(
            six.b(json.dumps(request))
        )

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # More statements comes here
            if self.HB_THREAD_FLAG:
                break
            print(datetime.datetime.now().__str__() + ' : Start task in the background')

            self.heartBeat()

            time.sleep(self.HB_INTERVAL)

    def subscribe(self, task, token):
        # print(self.task_dict)
        self.task_dict.update([(task, token), ])
        # print(self.task_dict)
        if task in ("mw", "sfi", "dp"):
            strwatchlistscrips = token  # dynamic call

            try:
                request = {"task": task, "channel": strwatchlistscrips, "token": self.feed_token,
                           "user": self.client_code, "acctid": self.client_code}

                self.ws.send(
                    six.b(json.dumps(request))
                )
                return True
            except Exception as e:
                self._close(reason="Error while request sending: {}".format(str(e)))
                raise
        else:
            print("The task entered is invalid, Please enter correct task(mw,sfi,dp) ")

    def resubscribe(self):
        for task, marketwatch in self.task_dict.items():
            print(task, '->', marketwatch)
            try:
                request = {"task": task, "channel": marketwatch, "token": self.feed_token,
                           "user": self.client_code, "acctid": self.client_code}

                self.ws.send(
                    six.b(json.dumps(request))
                )
                return True
            except Exception as e:
                self._close(reason="Error while request sending: {}".format(str(e)))
                raise

    def heartBeat(self):
        try:
            request = {"task": "hb", "channel": "", "token": self.feed_token, "user": self.client_code,
                       "acctid": self.client_code}
            print(request)
            self.ws.send(
                six.b(json.dumps(request))
            )

        except:
            print("HeartBeat Sending Failed")
            # time.sleep(60)

    def _parse_text_message(self, message):
        """Parse text message."""

        data = base64.b64decode(message)

        try:
            data = bytes((zlib.decompress(data)).decode("utf-8"), 'utf-8')
            data = json.loads(data.decode('utf8').replace("'", '"'))
            data = json.loads(json.dumps(data, indent=4, sort_keys=True))
        except ValueError:
            return

        # return financial_data
        if data:
            self._on_message(self.ws, data)

    def connect(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.ROOT_URI,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error)

        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def __on_message(self, ws, message):
        self._parse_text_message(message)
        # print(msg)

    def __on_open(self, ws):
        print("__on_open################")
        self.HB_THREAD_FLAG = False
        self._subscribe_on_open()
        if self.WS_RECONNECT_FLAG:
            self.WS_RECONNECT_FLAG = False
            self.resubscribe()
        else:
            self._on_open(ws)

    def __on_close(self, ws):
        self.HB_THREAD_FLAG = True
        print("__on_close################")
        self._on_close(ws)

    def __on_error(self, ws, error):

        if ("timed" in str(error)) or ("Connection is already closed" in str(error)) or (
                "Connection to remote host was lost" in str(error)):

            self.WS_RECONNECT_FLAG = True
            self.HB_THREAD_FLAG = True

            if (ws is not None):
                ws.close()
                ws.on_message = None
                ws.on_open = None
                ws.close = None
                # print (' deleting ws')
                del ws

            self.connect()
        else:
            print('Error info: %s' % (error))
            self._on_error(ws, error)

    def _on_message(self, ws, message):
        pass

    def _on_open(self, ws):
        pass

    def _on_close(self, ws):
        pass

    def _on_error(self, ws, error):
        pass

ss = None

async def websocket_consumer(websocket, path):
    # Perform any necessary setup tasks
    feed_token = "092017047"
    client_code = settings.CLIENT_ID
    token = "EXCHANGE|TOKEN_SYMBOL"  # SAMPLE: nse_cm|2885&nse_cm|1594&nse_cm|11536&nse_cm|3045
    task = "mw"  # mw|sfi|dp

    ss = SmartWebSocket(feed_token, client_code)

    # Assign the callbacks
    ss._on_open = on_open
    ss._on_message = on_message
    ss._on_error = on_error
    ss._on_close = on_close

    await ss.connect()

    try:
        while True:
            message = await websocket.recv()
            # Handle incoming messages, if needed
    except websockets.exceptions.ConnectionClosed:
        pass

    await ss.close()

def on_open():
    asyncio.get_event_loop().create_task(ss.subscribe(task, token))

def on_message(message):
    print("Ticks: {}".format(message))

def on_error(error):
    print(error)

def on_close():
    print("Close")

# Start the WebSocket server
start_server = websockets.serve(websocket_consumer, "localhost", 8000)

# Run the event loop
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()





# from channels.generic.websocket import AsyncWebsocketConsumer
# # from smartapi import SmartWebSocket
# from trade_smart_backend.apps.financial_data.services.smart_web_socket import SmartWebSocket
# from django.conf import settings
#
# class WebSocketConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Perform any necessary setup tasks
#         self.feed_token = "092017047"
#         self.client_code = settings.CLIENT_ID
#         self.token = "nse_cm|2885&nse_cm|1594&nse_cm|11536&nse_cm|3045"  # SAMPLE: nse_cm|2885&nse_cm|1594&nse_cm|11536&nse_cm|3045
#         self.task = "mw"  # mw|sfi|dp
#
#         self.ss = SmartWebSocket(self.feed_token, self.client_code)
#
#         # Assign the callbacks
#         self.ss._on_open = self.on_open
#         self.ss._on_message = self.on_message
#         self.ss._on_error = self.on_error
#         self.ss._on_close = self.on_close
#
#         await self.ss.connect()
#
#     async def disconnect(self, close_code):
#         # Perform any necessary cleanup tasks
#         await self.ss.close()
#
#     async def on_open(self):
#         await self.ss.subscribe(self.task, self.token)
#
#     async def receive(self, text_data=None, bytes_data=None):
#         """
#         Called with a decoded WebSocket frame.
#         """
#         pass
#
#     async def send(self, text_data=None, bytes_data=None, close=False):
#         """
#         Sends a reply back down the WebSocket
#         """
#         if text_data is not None:
#             await super().send({"type": "websocket.send", "text": text_data})
#         elif bytes_data is not None:
#             await super().send({"type": "websocket.send", "bytes": bytes_data})
#         else:
#             raise ValueError("You must pass one of bytes_data or text_data")
#         if close:
#             await self.close(close)
#
#     async def on_message(self, message):
#         print("Ticks: {}".format(message))
#
#     async def on_error(self, error):
#         print(error)
#
#     async def on_close(self):
#         print("Close")

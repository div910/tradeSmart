import websocket
import six
import base64
import zlib
import datetime
import time
import json
import threading
import ssl
from six.moves.urllib.parse import urljoin
import json
import logging
import SmartApi.smartExceptions as ex
import requests
from requests import get
import re, uuid
import socket
from SmartApi.version import __version__, __title__
log = logging.getLogger(__name__)


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

        # return data
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


class SmartConnect(object):
    # _rootUrl = "https://openapisuat.angelbroking.com"
    _rootUrl = "https://apiconnect.angelbroking.com"  # prod endpoint
    # _login_url ="https://smartapi.angelbroking.com/login"
    _login_url = "https://smartapi.angelbroking.com/publisher-login"  # prod endpoint
    _default_timeout = 7  # In seconds

    _routes = {
        "api.login": "/rest/auth/angelbroking/user/v1/loginByPassword",
        "api.logout": "/rest/secure/angelbroking/user/v1/logout",
        "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.user.profile": "/rest/secure/angelbroking/user/v1/getProfile",

        "api.order.place": "/rest/secure/angelbroking/order/v1/placeOrder",
        "api.order.modify": "/rest/secure/angelbroking/order/v1/modifyOrder",
        "api.order.cancel": "/rest/secure/angelbroking/order/v1/cancelOrder",
        "api.order.book": "/rest/secure/angelbroking/order/v1/getOrderBook",

        "api.ltp.data": "/rest/secure/angelbroking/order/v1/getLtpData",
        "api.trade.book": "/rest/secure/angelbroking/order/v1/getTradeBook",
        "api.rms.limit": "/rest/secure/angelbroking/user/v1/getRMS",
        "api.holding": "/rest/secure/angelbroking/portfolio/v1/getHolding",
        "api.position": "/rest/secure/angelbroking/order/v1/getPosition",
        "api.convert.position": "/rest/secure/angelbroking/order/v1/convertPosition",

        "api.gtt.create": "/gtt-service/rest/secure/angelbroking/gtt/v1/createRule",
        "api.gtt.modify": "/gtt-service/rest/secure/angelbroking/gtt/v1/modifyRule",
        "api.gtt.cancel": "/gtt-service/rest/secure/angelbroking/gtt/v1/cancelRule",
        "api.gtt.details": "/rest/secure/angelbroking/gtt/v1/ruleDetails",
        "api.gtt.list": "/rest/secure/angelbroking/gtt/v1/ruleList",

        "api.candle.data": "/rest/secure/angelbroking/historical/v1/getCandleData"
    }

    try:
        clientPublicIp = " " + get('https://api.ipify.org').text
        if " " in clientPublicIp:
            clientPublicIp = clientPublicIp.replace(" ", "")
        hostname = socket.gethostname()
        clientLocalIp = socket.gethostbyname(hostname)
    except Exception as e:
        print("Exception while retriving IP Address,using local host IP address", e)
    finally:
        clientPublicIp = "106.193.147.98"
        clientLocalIp = "127.0.0.1"
    clientMacAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    accept = "application/json"
    userType = "USER"
    sourceID = "WEB"

    def __init__(self, api_key=None, access_token=None, refresh_token=None, feed_token=None, userId=None, root=None,
                 debug=False, timeout=None, proxies=None, pool=None, disable_ssl=False, accept=None, userType=None,
                 sourceID=None, Authorization=None, clientPublicIP=None, clientMacAddress=None, clientLocalIP=None,
                 privateKey=None):
        self.debug = debug
        self.api_key = api_key
        self.session_expiry_hook = None
        self.disable_ssl = disable_ssl
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.feed_token = feed_token
        self.userId = userId
        self.proxies = proxies if proxies else {}
        self.root = root or self._rootUrl
        self.timeout = timeout or self._default_timeout
        self.Authorization = None
        self.clientLocalIP = self.clientLocalIp
        self.clientPublicIP = self.clientPublicIp
        self.clientMacAddress = self.clientMacAddress
        self.privateKey = api_key
        self.accept = self.accept
        self.userType = self.userType
        self.sourceID = self.sourceID

        if pool:
            self.reqsession = requests.Session()
            reqadapter = requests.adapters.HTTPAdapter(**pool)
            self.reqsession.mount("https://", reqadapter)
            print("in pool")
        else:
            self.reqsession = requests

        # disable requests SSL warning
        requests.packages.urllib3.disable_warnings()

    def requestHeaders(self):
        return {
            "Content-type": self.accept,
            "X-ClientLocalIP": self.clientLocalIp,
            "X-ClientPublicIP": self.clientPublicIp,
            "X-MACAddress": self.clientMacAddress,
            "Accept": self.accept,
            "X-PrivateKey": self.privateKey,
            "X-UserType": self.userType,
            "X-SourceID": self.sourceID
        }

    def setSessionExpiryHook(self, method):
        if not callable(method):
            raise TypeError("Invalid input type. Only functions are accepted.")
        self.session_expiry_hook = method

    def getUserId(self):
        return self.userId

    def setUserId(self, id):
        self.userId = id

    def setAccessToken(self, access_token):

        self.access_token = access_token

    def setRefreshToken(self, refresh_token):

        self.refresh_token = refresh_token

    def setFeedToken(self, feedToken):

        self.feed_token = feedToken

    def getfeedToken(self):
        return self.feed_token

    def login_url(self):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        return "%s?api_key=%s" % (self._login_url, self.api_key)

    def _request(self, route, method, parameters=None):
        """Make an HTTP request."""
        params = parameters.copy() if parameters else {}

        uri = self._routes[route].format(**params)
        url = urljoin(self.root, uri)

        # Custom headers
        headers = self.requestHeaders()

        if self.access_token:
            # set authorization header

            auth_header = self.access_token
            headers["Authorization"] = "Bearer {}".format(auth_header)

        if self.debug:
            log.debug("Request: {method} {url} {params} {headers}".format(method=method, url=url, params=params,
                                                                          headers=headers))

        try:
            r = requests.request(method,
                                 url,
                                 data=json.dumps(params) if method in ["POST", "PUT"] else None,
                                 params=json.dumps(params) if method in ["GET", "DELETE"] else None,
                                 headers=headers,
                                 verify=not self.disable_ssl,
                                 allow_redirects=True,
                                 timeout=self.timeout,
                                 proxies=self.proxies)

        except Exception as e:
            raise e

        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))

        # Validate the content type.
        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))

            except ValueError:
                raise ex.DataException("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))

            # api error
            if data.get("error_type"):
                # Call session hook if its registered and TokenException is raised
                if self.session_expiry_hook and r.status_code == 403 and data["error_type"] == "TokenException":
                    self.session_expiry_hook()

                # native errors
                exp = getattr(ex, data["error_type"], ex.GeneralException)
                raise exp(data["message"], code=r.status_code)

            return data
        elif "csv" in headers["Content-type"]:
            return r.content
        else:
            raise ex.DataException("Unknown Content-type ({content_type}) with response: ({content})".format(
                content_type=headers["Content-type"],
                content=r.content))

    def _deleteRequest(self, route, params=None):
        """Alias for sending a DELETE request."""
        return self._request(route, "DELETE", params)

    def _putRequest(self, route, params=None):
        """Alias for sending a PUT request."""
        return self._request(route, "PUT", params)

    def _postRequest(self, route, params=None):
        """Alias for sending a POST request."""
        return self._request(route, "POST", params)

    def _getRequest(self, route, params=None):
        """Alias for sending a GET request."""
        return self._request(route, "GET", params)

    def generateSession(self, clientCode, password, totp):

        params = {"clientcode": clientCode, "password": password, "totp": totp}
        loginResultObject = self._postRequest("api.login", params)

        if loginResultObject['status'] == True:
            jwtToken = loginResultObject['data']['jwtToken']
            self.setAccessToken(jwtToken)
            refreshToken = loginResultObject['data']['refreshToken']
            feedToken = loginResultObject['data']['feedToken']
            self.setRefreshToken(refreshToken)
            self.setFeedToken(feedToken)
            user = self.getProfile(refreshToken)

            id = user['data']['clientcode']
            # id='D88311'
            self.setUserId(id)
            user['data']['jwtToken'] = "Bearer " + jwtToken
            user['data']['refreshToken'] = refreshToken
            user['data']['feedToken'] = feedToken

            return user
        else:
            return loginResultObject

    def terminateSession(self, clientCode):
        logoutResponseObject = self._postRequest("api.logout", {"clientcode": clientCode})
        return logoutResponseObject

    def generateToken(self, refresh_token):
        response = self._postRequest('api.token', {"refreshToken": refresh_token})
        jwtToken = response['data']['jwtToken']
        feedToken = response['data']['feedToken']
        self.setFeedToken(feedToken)
        self.setAccessToken(jwtToken)

        return response

    def renewAccessToken(self):
        response = self._postRequest('api.refresh', {
            "jwtToken": self.access_token,
            "refreshToken": self.refresh_token,

        })

        tokenSet = {}

        if "jwtToken" in response:
            tokenSet['jwtToken'] = response['data']['jwtToken']
        tokenSet['clientcode'] = self.userId
        tokenSet['refreshToken'] = response['data']["refreshToken"]

        return tokenSet

    def getProfile(self, refreshToken):
        user = self._getRequest("api.user.profile", {"refreshToken": refreshToken})
        return user

    def placeOrder(self, orderparams):

        params = orderparams

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        orderResponse = self._postRequest("api.order.place", params)['data']['orderid']

        return orderResponse

    def modifyOrder(self, orderparams):
        params = orderparams

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        orderResponse = self._postRequest("api.order.modify", params)
        return orderResponse

    def cancelOrder(self, order_id, variety):
        orderResponse = self._postRequest("api.order.cancel", {"variety": variety, "orderid": order_id})
        return orderResponse

    def ltpData(self, exchange, tradingsymbol, symboltoken):
        params = {
            "exchange": exchange,
            "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken
        }
        ltpDataResponse = self._postRequest("api.ltp.data", params)
        return ltpDataResponse

    def orderBook(self):
        orderBookResponse = self._getRequest("api.order.book")
        return orderBookResponse

    def tradeBook(self):
        tradeBookResponse = self._getRequest("api.trade.book")
        return tradeBookResponse

    def rmsLimit(self):
        rmsLimitResponse = self._getRequest("api.rms.limit")
        return rmsLimitResponse

    def position(self):
        positionResponse = self._getRequest("api.position")
        return positionResponse

    def holding(self):
        holdingResponse = self._getRequest("api.holding")
        return holdingResponse

    def convertPosition(self, positionParams):
        params = positionParams
        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])
        convertPositionResponse = self._postRequest("api.convert.position", params)

        return convertPositionResponse

    def gttCreateRule(self, createRuleParams):
        params = createRuleParams
        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        createGttRuleResponse = self._postRequest("api.gtt.create", params)
        # print(createGttRuleResponse)
        return createGttRuleResponse['data']['id']

    def gttModifyRule(self, modifyRuleParams):
        params = modifyRuleParams
        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])
        modifyGttRuleResponse = self._postRequest("api.gtt.modify", params)
        # print(modifyGttRuleResponse)
        return modifyGttRuleResponse['data']['id']

    def gttCancelRule(self, gttCancelParams):
        params = gttCancelParams
        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        # print(params)
        cancelGttRuleResponse = self._postRequest("api.gtt.cancel", params)
        # print(cancelGttRuleResponse)
        return cancelGttRuleResponse

    def gttDetails(self, id):
        params = {
            "id": id
        }
        gttDetailsResponse = self._postRequest("api.gtt.details", params)
        return gttDetailsResponse

    def gttLists(self, status, page, count):
        if type(status) == list:
            params = {
                "status": status,
                "page": page,
                "count": count
            }
            gttListResponse = self._postRequest("api.gtt.list", params)
            # print(gttListResponse)
            return gttListResponse
        else:
            message = "The status param is entered as" + str(
                type(status)) + ". Please enter status param as a list i.e., status=['CANCELLED']"
            return message

    def getCandleData(self, historicDataParams):
        params = historicDataParams
        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])
        getCandleDataResponse = self._postRequest("api.candle.data", historicDataParams)
        return getCandleDataResponse

    def _user_agent(self):
        return (__title__ + "-python/").capitalize() + __version__


class SmartAPIException(Exception):

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(SmartAPIException, self).__init__(message)
        self.code = code


class GeneralException(SmartAPIException):
    """An unclassified, general error. Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(GeneralException, self).__init__(message, code)


class TokenException(SmartAPIException):
    """Represents all token and authentication related errors. Default code is 403."""

    def __init__(self, message, code=403):
        """Initialize the exception."""
        super(TokenException, self).__init__(message, code)


class PermissionException(SmartAPIException):
    """Represents permission denied exceptions for certain calls. Default code is 403."""

    def __init__(self, message, code=403):
        """Initialize the exception."""
        super(PermissionException, self).__init__(message, code)


class OrderException(SmartAPIException):
    """Represents all order placement and manipulation errors. Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(OrderException, self).__init__(message, code)


class InputException(SmartAPIException):
    """Represents user input errors such as missing and invalid parameters. Default code is 400."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(InputException, self).__init__(message, code)


class DataException(SmartAPIException):
    """Represents a bad response from the backend Order Management System (OMS). Default code is 502."""

    def __init__(self, message, code=502):
        """Initialize the exception."""
        super(DataException, self).__init__(message, code)


class NetworkException(SmartAPIException):
    """Represents a network issue between api and the backend Order Management System (OMS). Default code is 503."""

    def __init__(self, message, code=503):
        """Initialize the exception."""
        super(NetworkException, self).__init__(message, code)
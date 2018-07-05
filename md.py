from ctpwrapper import ApiStructure
from ctpwrapper import MdApiPy
from ctpwrapper import TraderApiPy
import asyncio
from copy import copy

Md_PRICE = {}
loop = asyncio.get_event_loop()

def done(requestID, result):
    Md_PRICE[requestID] = result

class Md(MdApiPy):
    def __init__(self, broker_id, investor_id, password, request_id=1):
        self.broker_id = broker_id
        self.investor_id = investor_id
        self.password = password
        self.request_id = request_id
        self.data_available = None

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):

        self.ErrorRspInfo(pRspInfo, nRequestID)

    def ErrorRspInfo(self, info, request_id):
        """
        :param info:
        :return:
        """
        if info.ErrorID != 0:
            print('request_id=%s ErrorID=%d, ErrorMsg=%s',
                  request_id, info.ErrorID, info.ErrorMsg.decode('gbk'))
        return info.ErrorID != 0

    def OnFrontConnected(self):
        """
        :return:
        """

        user_login = ApiStructure.ReqUserLoginField(BrokerID=self.broker_id,
                                                    UserID=self.investor_id,
                                                    Password=self.password)
        self.ReqUserLogin(user_login, self.request_id)

    def OnFrontDisconnected(self, nReason):

        print("Md OnFrontDisconnected %s", nReason)
        sys.exit()

    def OnHeartBeatWarning(self, nTimeLapse):
        """心跳超时警告。当长时间未收到报文时，该方法被调用。
        @param nTimeLapse 距离上次接收报文的时间
        """
        print('Md OnHeartBeatWarning, time = %s', nTimeLapse)

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        """
        用户登录应答
        :param pRspUserLogin:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo.ErrorID != 0:
            print("Md OnRspUserLogin failed error_id=%s msg:%s",
                  pRspInfo.ErrorID, pRspInfo.ErrorMsg.decode('gbk'))
        else:
            print("Md user login successfully")
            self.Join()

    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, blsLast):
        pass

    def OnRtnDepthMarketData(self, pDepthMarketData):
        done(pDepthMarketData.InstrumentID.decode('utf-8').upper(), ApiStructure.DepthMarketDataField.from_dict(pDepthMarketData.to_dict()))
        if self.data_available:
            if not self.data_available.done():
                loop.call_soon_threadsafe(self.data_available.set_result, True)
                self.data_available = None

    def wait_available_data(self):
        self.data_available = asyncio.Future()
        return self.data_available

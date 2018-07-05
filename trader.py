from ctpwrapper import ApiStructure
from ctpwrapper import TraderApiPy
from ctpwrapper import TraderApiPy
import asyncio

Trader_FUTURES = {}
loop = asyncio.get_event_loop()

def done(requestID, result):
    if requestID in Trader_FUTURES:
        future = Trader_FUTURES[requestID]
        loop.call_soon_threadsafe(future.set_result, result)
        del Trader_FUTURES[requestID]

class Trader(TraderApiPy):

    def __init__(self, broker_id, investor_id, password, request_id=1):
        self.request_id = request_id
        self.broker_id = broker_id.encode()
        self.investor_id = investor_id.encode()
        self.password = password.encode()

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

    def OnHeartBeatWarning(self, nTimeLapse):
        """心跳超时警告。当长时间未收到报文时，该方法被调用。
        @param nTimeLapse 距离上次接收报文的时间
        """
        print("on OnHeartBeatWarning time: ", nTimeLapse)

    def OnFrontDisconnected(self, nReason):
        print("on FrontDisConnected disconnected", nReason)

    def OnFrontConnected(self):

        req = ApiStructure.ReqUserLoginField(BrokerID=self.broker_id,
                                             UserID=self.investor_id,
                                             Password=self.password)
        self.ReqUserLogin(req, self.request_id)
        print("Trader on front connection")

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):

        if pRspInfo.ErrorID != 0:
            print("Trader OnRspUserLogin failed error_id=%s msg:%s",
                  pRspInfo.ErrorID, pRspInfo.ErrorMsg.decode('gbk'))
        else:
            print("Trader user login successfully")

            inv = ApiStructure.QryInvestorField(BrokerID=self.broker_id, InvestorID=self.investor_id)

            self.ReqQryInvestor(inv, self.inc_request_id())
            req = ApiStructure.SettlementInfoConfirmField(BrokerID=self.broker_id, InvestorID=self.investor_id)

            self.ReqSettlementInfoConfirm(req, self.inc_request_id())

            self.Join()

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        print(pSettlementInfoConfirm, pRspInfo, pRspInfo.ErrorMsg.decode("GBK"))

    def inc_request_id(self):
        self.request_id += 1
        return self.request_id

    def OnRspQryInvestor(self, pInvestor, pRspInfo, nRequestID, bIsLast):
        print(pInvestor, pRspInfo)

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        done(nRequestID, pInvestorPosition)

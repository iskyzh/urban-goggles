# coding: utf-8

import sys

from ctpwrapper import ApiStructure
from ctpwrapper import MdApiPy
from ctpwrapper import TraderApiPy
from trader import Trader, Trader_FUTURES
from md import Md, Md_PRICE

import time
import CONST
import asyncio

md = Md(CONST.BORDKER_ID, CONST.INVESTOR_ID, CONST.PASSWORD)
trader = Trader(CONST.BORDKER_ID, CONST.INVESTOR_ID, CONST.PASSWORD)
md.Create()
md.RegisterFront(CONST.MD_SERVER)
md.Init()

trader = Trader(CONST.BORDKER_ID, CONST.INVESTOR_ID, CONST.PASSWORD)
trader.Create()
trader.RegisterFront(CONST.TD_SERVER)
trader.SubscribePrivateTopic(2)
trader.Init()

def ctp_handle(result):
    """
    0: 发送成功
    -1: 因网络原因发送失败
    -2: 未处理请求队列总数量超限。
    -3: 每秒发送请求数量超限。
    """
    if result != 0:
        print(result)
    assert(result == 0)

def sub_market_data(codes):
    ctp_handle(md.SubscribeMarketData(codes))

def get_market_data(code):
    return Md_PRICE[code] if code in Md_PRICE else None

async def wait_data_available(code):
    def check_data():
        for i in code:
            if not(i in Md_PRICE):
                return False
        return True

    while not check_data():
        await md.wait_available_data()

def create_trader_future():
    req_id = trader.inc_request_id()
    future = asyncio.Future()
    Trader_FUTURES[req_id] = future
    return req_id, asyncio.futures.wrap_future(future, loop=loop)

def get_investor_position(instrument_id):
    structure = ApiStructure.QryInvestorPositionField(
        BrokerID=CONST.BORDKER_ID,
        InvestorID=CONST.INVESTOR_ID,
        InstrumentID=instrument_id
    )
    req_id, future = create_trader_future()
    ctp_handle(trader.ReqQryInvestorPosition(structure, req_id))
    return future

loop=asyncio.get_event_loop()

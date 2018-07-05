"""
Data Processing Library
Daily Summary: http://www.cffex.com.cn/sj/hqsj/rtj/201807/03/index.xml
Realtime Data:
http://www.cffex.com.cn/quote_IH.txt
All Futures:
http://www.cffex.com.cn/cp/index_6719.xml
"""

import requests as req
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

NOW = datetime.now() - timedelta(days=1)

DATA_SOURCE = {
    "daily_summary": "http://www.cffex.com.cn/sj/hqsj/rtj/%d%02d/%02d/index.xml" % (NOW.year, NOW.month, NOW.day),
    "realtime_data": {
        "IH": "http://www.cffex.com.cn/quote_IH.txt",
        "IC": "http://www.cffex.com.cn/quote_IC.txt",
        "IF": "http://www.cffex.com.cn/quote_IF.txt"
    },
    "futures": "http://www.cffex.com.cn/cp/index_6719.xml",
    "sina":"http://hq.sinajs.cn/rn=00000000&list=CFF_%s"
}

def read_futures():
    """
        Returns:
            instrument, publish, due, start, end, price, date
            代码, 上市日, 到期日, 开始交割日, 最后交割日, 挂牌基准价, 日期
    """
    data = req.get(DATA_SOURCE["futures"]).text
    df = pd.DataFrame([np.array([data.text for data in entry]) for entry in ET.fromstring(data)])
    df.columns = ['instrument', 'publish', 'due', 'start', 'end', 'price', 'date']
    df['price'] = df['price'].astype(np.float64)
    df = df.set_index('instrument')
    return df

def read_realtime_data(code):
    """
        Returns:
            instrument, openprice, highest, lowest, lastprice, updown, bprice, bamount, sprice, samount, volume, position
    """
    df = pd.read_csv(DATA_SOURCE["realtime_data"][code])
    df = df.set_index('instrument')
    for col in ['openprice', 'highest', 'lowest', 'lastprice', 'updown', 'bprice', 'bamount', 'sprice', 'samount', 'volume', 'position']:
        df[col] = df[col].astype(np.float64)
    return df

def read_daily_summary():
    """
        Returns:
            合约代码, 今开盘, 最高价, 最低价, 今收盘, 持仓量, 成交量, 成交金额
    """
    data = req.get(DATA_SOURCE["daily_summary"]).text
    df = pd.DataFrame([np.array([data.text for data in entry]) for entry in ET.fromstring(data)])
    df = df[[0, 2, 3, 4, 5, 6, 10, 11]]
    df.columns = ['instrument', 'openprice', 'highest', 'lowest', 'close', 'position', 'deal', 'deal_price']
    for col in ['openprice', 'highest', 'lowest', 'close', 'position', 'deal', 'deal_price']:
        df[col] = df[col].astype(np.float64)
    df = df.set_index('instrument')
    return df

def read_sina_data(code):
    data = req.get(DATA_SOURCE["sina"] % code).text
    return float(data.split(',')[3])

#!/usr/local/bin/python3
# coding: utf-8

import pandas as pd
import numpy as np
import tushare as ts
from read import read
import process
import CTP
import time
import asyncio

async def main():
    # In[0]: 输入
    ori_df = read()
    # In[1]: 沪深 300
    result = pd.DataFrame([
        await transaction(ori_df, ts.get_hs300s(), 'IF', 300),
        await transaction(ori_df, ts.get_sz50s(), 'IH', 300),
        await transaction(ori_df, ts.get_zz500s(), 'IC', 200)
    ])
    result.columns = ['代码', '现货总市值', '合约市值', '合约数']
    print(result)

async def transaction(ori_df, __index, __code, __multiplier):
    # In[1]: 获取所有期货
    available_futures = pd.Series(process.read_realtime_data(__code).index)
    CTP.sub_market_data(available_futures)
    print('获取期货信息...')
    await CTP.wait_data_available(available_futures)

    # In[2]: 选择买入的期货
    df_futures = pd.DataFrame(list(map(
        lambda data: (data.InstrumentID.decode('utf-8'), data.LastPrice, data.Volume, data.OpenInterest, data.UpdateTime),
        [CTP.get_market_data(code) for code in available_futures])
    ), columns=['code', 'lastPrice', 'volume', 'openInterest', 'updateTime'])
    df_futures = df_futures.set_index('code')
    df_futures['total'] = df_futures['openInterest'] * df_futures['volume']
    _id = df_futures['total'].idxmax()
    future = df_futures.loc[_id]
    current_price = future['lastPrice'] * __multiplier

    # In[3]: 获取现货信息
    indexes = __index.set_index('code')
    print('获取现货信息...')
    df_indexes = ts.get_realtime_quotes(pd.Series(indexes.index))[['code', 'price']]
    df_indexes['price'] = df_indexes['price'].astype(np.float64)
    df_indexes = df_indexes.set_index('code')

    # In[4]: 计算市值
    df_data = ori_df.copy()
    df_data = df_data.join(df_indexes)
    df_data['value'] = df_data['price'] * df_data['position']
    total = df_data['value'].sum()

    # In[5]: 计算合约数
    return _id, total, current_price, total / current_price

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

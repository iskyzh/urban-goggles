#!/usr/local/bin/python3
# coding: utf-8

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import tushare as ts
from read import read
import process

# In[0]: 输入
df = read()
df

# In[1]: 获取实时股票价格
realtime_data = ts.get_realtime_quotes(pd.Series(df.index))
realtime_data = realtime_data[['code', 'price']]
realtime_data

# In[2]: 合并到 DataFrame, 计算市值
for code, price in realtime_data.values:
    df.loc[code, 'price'] = price
df['price'] = df['price'].astype(np.float64)
df['value'] = df['position'] * df['price']
df

# In[3]: 获取指数
hs300 = ts.get_hs300s().set_index('code')
sz50 = ts.get_sz50s().set_index('code')
zz500 = ts.get_zz500s().set_index('code')
hs300

# In[4]: 计算合约数
def transaction(df, future, summary, code, multiplier):
    _id = summary[summary.index.str.startswith(code)]['volXpos'].idxmax()
    buy = summary.loc[_id]['close'] * multiplier
    total = df[df.index.isin(future.index)]['value'].sum()
    return _id, total, buy, total / buy

summary = process.read_daily_summary()
summary['volXpos'] = summary['position'] * summary['deal']
result = pd.DataFrame(np.array((
    transaction(df, sz50, summary, 'IH', 300),
    transaction(df, zz500, summary, 'IC', 200),
    transaction(df, hs300, summary, 'IF', 300)
)))
result.columns = ['代码', '合约数', '合约市值', '现货总市值']
result

# In[5]: 储存
result.to_csv('result.csv')
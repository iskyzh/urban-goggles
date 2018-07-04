# coding: utf-8
import pandas as pd
import numpy as np
import os

columns = ['证券代码', '证券名称', '持仓']

def process_file(filename):

    data = pd.read_excel('./data/%s' % filename)
    instruction = ("\nIn %s\n" % filename) + "".join(map(lambda d: '%d. %s\n' % d, enumerate(data.columns)))
    print(instruction)
    cols = [int(input('In %s, select column for %s -> ' % (filename, col))) for col in columns]
    data = data[data.columns[cols]]
    data.columns = ['code', 'name', 'position']
    return data.dropna()

def convert_number(val):
    new_val = val.replace(',','')
    return float(new_val)

def get_file_list():
    return os.listdir('./data')

def read():
    files = filter(lambda file: (file.endswith('.xls') or file.endswith('.xlsx')), get_file_list())
    data = map(process_file, files)
    df = pd.concat(data)

    df['position'] = df['position'].apply(str).apply(convert_number).astype(np.float64)
    df['code'] = df['code'].astype(object).map(lambda code: '%06d' % code)
    df = df.set_index('code')
    df = df.groupby(df.index).agg({'name': 'first', 'position': 'sum'})
    return df

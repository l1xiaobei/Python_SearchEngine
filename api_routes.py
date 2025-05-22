from flask import Blueprint, jsonify
from jqdatasdk import *
import pandas as pd

api = Blueprint('api', __name__)

auth('13971463828', 'lhysS233')  # 替换为你自己的账号

# 设置显示所有行和列（避免折叠）
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', 1000)  # 设置输出宽度（防止换行）

@api.route('/api/index')
def index_data():
    df = get_price('000001.XSHG', start_date='2025-02-17', end_date='2025-02-17', frequency='daily', fields=['close', 'pre_close'])
    if df.empty:
        return jsonify({'error': '无数据'}), 404
    latest = df.iloc[0]
    change_pct = round((latest['close'] - latest['pre_close']) / latest['pre_close'] * 100, 2)
    return jsonify({
        'index_name': '上证指数',
        'price': latest['close'],
        'change': change_pct
    })

@api.route('/api/all_indices')
def all_indices():
    date = '2025-02-17'

    indices_config = [
        {
            "market": "A股行情",
            "indices": [
                {"code": "000001.XSHG", "name": "上证指数"},
                {"code": "399001.XSHE", "name": "深证成指"},
                {"code": "399006.XSHE", "name": "创业板指"},
                #{"code": "899050.BJ",   "name": "北证50"},
                {"code": "000688.XSHG", "name": "科创50"},
                {"code": "000300.XSHG", "name": "沪深300"},
            ]
        }
    ]
    #     {
    #         "market": "港股行情",
    #         "indices": [
    #             #{"code": "HSI.HI",   "name": "恒生指数"},
    #             {"code": "HSCEI.HI", "name": "国企指数"},
    #             {"code": "HSTECH.HI", "name": "恒生科技"},
    #         ]
    #     },
    #     {
    #         "market": "美股行情",
    #         "indices": [
    #             {"code": "DJI.GI",  "name": "道琼斯"},
    #             {"code": "IXIC.GI", "name": "纳斯达克"},
    #             {"code": "INX.GI",  "name": "标普500"},
    #         ]
    #     },
    #     {
    #         "market": "其他市场",
    #         "indices": [
    #             {"code": "N225.GI",   "name": "日经225"},
    #             {"code": "FTSE.GI",   "name": "富时100"},
    #             {"code": "GDAXI.GI",  "name": "DAX30"},
    #         ]
    #     }
    # ]

    result = []

    for group in indices_config:
        indices = []
        for item in group['indices']:
            df = get_price(item['code'], start_date=date, end_date=date, frequency='daily', fields=['close', 'pre_close'])
            if not df.empty:
                close = float(df['close'].iloc[0])
                pre_close = float(df['pre_close'].iloc[0])
                change = ((close - pre_close) / pre_close) * 100 if pre_close != 0 else 0
                indices.append({
                    'name': item['name'],
                    'price': close,
                    'change': change
                })
        result.append({
            'market': group['market'],
            'indices': indices
        })

    return jsonify({
        'date': date,
        'groups': result
    })
# obtained from jjboi8708/OrderflowChart
# https://github.com/jjboi8708/OrderflowChart/commit/3eee2756c434764acef3dce10d46f6178ea2b367

import json
import random
import string
import requests
import pandas as pd
import websocket
from OrderFlow import OrderFlowChart

SYMBOL = 'btcusdt'
DEPTH_LIMIT = 20
KEEP_CANDLES = 20

orderflow_df = pd.DataFrame(columns=['bid_size', 'price', 'ask_size', 'identifier'])
ohlc_df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'identifier'])


def random_id(length=5):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def fetch_orderbook():
    url = 'https://api.binance.com/api/v3/depth'
    resp = requests.get(url, params={'symbol': SYMBOL.upper(), 'limit': DEPTH_LIMIT})
    data = resp.json()
    bids = {float(p): float(q) for p, q in data.get('bids', [])}
    asks = {float(p): float(q) for p, q in data.get('asks', [])}
    prices = sorted(set(list(bids.keys()) + list(asks.keys())), reverse=True)
    rows = []
    for price in prices:
        rows.append({
            'price': price,
            'bid_size': bids.get(price, 0.0),
            'ask_size': asks.get(price, 0.0),
        })
    return pd.DataFrame(rows)


def on_message(ws, message):
    global orderflow_df, ohlc_df
    data = json.loads(message)
    kline = data.get('k')
    if not kline:
        return
    if kline.get('x'):
        identifier = random_id()
        ts = pd.to_datetime(kline['T'], unit='ms')
        candle = pd.DataFrame({
            'open': [float(kline['o'])],
            'high': [float(kline['h'])],
            'low': [float(kline['l'])],
            'close': [float(kline['c'])],
            'identifier': [identifier]
        }, index=[ts])
        ohlc_df = pd.concat([ohlc_df, candle])

        ob = fetch_orderbook()
        ob['identifier'] = identifier
        ob.index = [ts] * len(ob)
        orderflow_df = pd.concat([orderflow_df, ob])

        if len(ohlc_df) > KEEP_CANDLES:
            keep_ids = ohlc_df.iloc[-KEEP_CANDLES:]['identifier']
            ohlc_df = ohlc_df.iloc[-KEEP_CANDLES:]
            orderflow_df = orderflow_df[orderflow_df['identifier'].isin(keep_ids)]

        chart = OrderFlowChart(orderflow_df, ohlc_df, identifier_col='identifier')
        chart.plot()


def on_error(ws, error):
    print('WebSocket error:', error)


def on_close(ws, close_status_code, close_msg):
    print('WebSocket closed')


def on_open(ws):
    print('WebSocket connection opened')


if __name__ == '__main__':
    print('Starting real-time chart...')
    ws = websocket.WebSocketApp(
        f'wss://stream.binance.com:9443/ws/{SYMBOL}@kline_1m',
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

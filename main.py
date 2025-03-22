import websocket
import json
import requests
import time
import threading
from threading import Thread

from websocket import WebSocketApp
import settings as st
from logger import Logger
from typing import Dict, Any

logger = Logger(__name__, st.APPLICATION_LOG, write_to_stdout=st.DEBUG_MODE).get()

telegram_bot_params: Dict[Any, Any] = st.TELEGRAM_BOT_PARAMS

# alerts = []

SECONDS_IN_20_HOURS = 20*3600

binance_ws_url = 'wss://fstream.binance.com/ws'

symbols = ['BNBUSDT', 'ETHUSDT', 'SOLUSDT']
currencies = {
    'BNBUSDT': 0.0,
    'ETHUSDT': 0.0,
    'SOLUSDT': 0.0
}

def tg_message(text):
    # 'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset=-1'
    try:
        res = requests.get(f'https://api.telegram.org/bot{telegram_bot_params['token']}/sendMessage',
                           params=dict(chat_id = telegram_bot_params['chat_id'], text=text))
        logger.info(f"tg_message(): Telegram message sent: {res}")
    except Exception as e:
        logger.info(f"tg_message(): Failed to send Telegram message: {e}")


def send_message(text):
    logger.info(f"send_message(): Trying to send Telegram message: {text}")
    thread = Thread(target = tg_message, args = (text, ))
    thread.start()
    thread.join()
    logger.info(f"send_message(): Thread finished")


# def alert_down(symbol, price, data):
#     for x in data:
#         if x['s'] == symbol and float(x['c']) <= price and x['s'] not in alerts:
#             logger.info(f"alert_down(): Alert 'down': {x['s']} {x['c']}")
#             alerts.append(f"{x['s']}")
#             send_message(f"{x['s']} {x['c']}")


# def alert_up(symbol, price, data):
#     for x in data:
#         if x['s'] == symbol and float(x['c']) >= price and x['s'] not in alerts:
#             logger.info(f"alert_up(): Alert 'up': {x['s']} {x['c']}")
#             alerts.append(f"{x['s']}")
#             send_message(f"{x['s']} {x['c']}")


def alert_change(percent: float, data):
    for x in data:
        symbol = x['s']
        if symbol in currencies.keys():
            price = float(x['c'])
            old_price = currencies[symbol]
            if abs(price - old_price) >= old_price * (percent / 100):
                currencies[symbol] = price
                if price > old_price:
                    become = 'higher'
                else:
                    become = 'lower'

                mess = f"{symbol} {become} {old_price} {price}"
                logger.info(f"alert_change(): {mess}")
                send_message(mess)


def on_open(ws):
    sub_msg = {"method": "SUBSCRIBE", "params": ["!miniTicker@arr"], "id": 1}
    ws.send(json.dumps(sub_msg))
    mess = f"Connected on {time.ctime()}"
    logger.info(f"on_open(): {mess}")
    send_message(mess)


def on_message(ws, message):
    # logger.info(f"on_message(): New message")
    data = json.loads(message)
    alert_change(1, data)
    # alert_down(' SOLUSDT', 134.00, data)
    # alert_up('SOLUSDT', 124.0, data)


def on_close(ws, close_status_code, close_msg):
    mess = f"Connection closed on {time.ctime()}: close_status_code: {close_status_code}, close_msg: {close_msg}"
    logger.info(f"on_close(): {mess}")
    send_message(mess)

    time.sleep(5)
    connect_to_network(interval=SECONDS_IN_20_HOURS, url=binance_ws_url)


def on_error(ws, e):
    mess = f"on_error: {e}"
    logger.info(f"on_error(): {mess}")
    send_message(mess)


def intentionally_close_socket(ws: WebSocketApp, interval: int):
    mess = f"Intentionally closing after {interval} seconds working"
    logger.info(f"intentionally_close_socket(): {mess}")
    send_message(mess)
    ws.close()


def connect_to_network(interval, url):  #  -> WebSocketApp | None
    logger.info(f"connect_to_network(): Entry point")
    try:
        ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
        threading.Timer(interval, intentionally_close_socket, [ws, interval]).start()
        ws.run_forever()  # ping_interval=2, reconnect=2
        # return ws
    except Exception as e:
        logger.info(f"connect_to_network(): Exception while connecting to url {url}: {e}")
        # raise
        # return None


if __name__ == "__main__":
    connect_to_network(interval=SECONDS_IN_20_HOURS, url=binance_ws_url)

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

IDENT_STR = "BINANCE PRICE CHANGING ALERTER"

logger = Logger(__name__, st.APPLICATION_LOG, write_to_stdout=st.DEBUG_MODE).get()

telegram_bot_params: Dict[Any, Any] = st.TELEGRAM_BOT_PARAMS

symbols_params = st.SYMBOLS_PARAMS

processing_params: Dict[Any, Any] = st.PROCESSING_PARAMS

# alerts = []

SECONDS_IN_20_HOURS = 20*3600

MESSAGES_COUNTER: int = 0

binance_ws_url = 'wss://fstream.binance.com/ws'

symbols_list = symbols_params['symbols_list'].split(',')

currencies: Dict[str, float] = dict()

for item in symbols_list:
    currencies[item] = 0.0


def tg_message(text):
    # 'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset=-1'
    logger.info(f"tg_message(): Trying to send Telegram message: {text}")
    try:
        res = requests.get(f"https://api.telegram.org/bot{telegram_bot_params['token']}/sendMessage",
                           params=dict(chat_id = telegram_bot_params['chat_id'], text=text))
        logger.info(f"tg_message(): Telegram message sent: {res}")
    except Exception as e:
        logger.info(f"tg_message(): Failed to send Telegram message: {e}")


def send_telegram_message(text):
    logger.info(f"send_telegram_message(): Trying to send Telegram message: {text}")
    thread = Thread(target = tg_message, args = (f"{IDENT_STR}:: {text}", ))
    thread.start()
    # thread.join()
    logger.info(f"send_message(): End OF Trying to send Telegram message: {text}")


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
                send_telegram_message(mess)


def on_open(ws):
    sub_msg = {"method": "SUBSCRIBE", "params": ["!miniTicker@arr"], "id": 1}
    ws.send(json.dumps(sub_msg))
    mess = f"Connected on {time.ctime()}"
    logger.info(f"on_open(): {mess}")
    send_telegram_message(mess)


def on_message(ws, message):
    global MESSAGES_COUNTER
    MESSAGES_COUNTER += 1

    change_percent = float(processing_params['change_percent'])

    data = json.loads(message)
    alert_change(percent=change_percent, data=data)
    # alert_down(' SOLUSDT', 134.00, data)
    # alert_up('SOLUSDT', 124.0, data)

    alive_interval = int(processing_params['alive_interval'])

    if MESSAGES_COUNTER % alive_interval == 0:
        mess = f"I am alive. MESSAGES_COUNTER={MESSAGES_COUNTER}"
        logger.info(f"on_message(): {mess}")
        send_telegram_message(mess)


def on_close(ws, close_status_code, close_msg):
    mess = f"Connection closed on {time.ctime()}: close_status_code: {close_status_code}, close_msg: {close_msg}"
    logger.info(f"on_close(): {mess}")
    send_telegram_message(mess)

    time.sleep(5)
    connect_to_network(interval=SECONDS_IN_20_HOURS, url=binance_ws_url)


def on_error(ws, e):
    mess = f"error: {e}"
    logger.info(f"on_error(): {mess}")
    send_telegram_message(mess)


def intentionally_close_socket(ws: WebSocketApp, interval: int):
    mess = f"Intentionally closing after {interval} seconds working"
    logger.info(f"intentionally_close_socket(): {mess}")
    send_telegram_message(mess)
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
    # pass
    connect_to_network(interval=SECONDS_IN_20_HOURS, url=binance_ws_url)

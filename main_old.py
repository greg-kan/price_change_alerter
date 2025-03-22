import websocket
import json
import requests
import time
import threading
from threading import Thread

from websocket import WebSocket, WebSocketApp
import settings as st
from logger import Logger

logger = Logger(__name__, st.APPLICATION_LOG, write_to_stdout=st.DEBUG_MODE).get()


alerts = []

TELEGRAM_TOKEN = ''
TELEGRAM_CHANNEL = ''
TELEGRAM_CHAT_ID = 12345

SECONDS_IN_10_HOURS = 10*3600

binance_ws_url = 'wss://fstream.binance.com/ws'

# logger = logging.getLogger()

# ws: WebSocketApp | None = None
def tg_message(text):
    # 'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset=-1'
    try:
        res = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
                           params=dict(chat_id = TELEGRAM_CHAT_ID, text=text))
        logger.info(f"Telegram message sent: {res}")
    except Exception as e:
        logger.info(f"Failed to send Telegram message: {e}")


def send_message(text):
    logger.info(f"send_message: Trying to send Telegram message: {text}")
    thread = Thread(target = tg_message, args = (text, ))
    thread.start()
    thread.join()
    logger.info(f"send_message: Thread finished")


def alert_down(symbol, price, data):
    for x in data:
        if x['s'] == symbol and float(x['c']) <= price and x['s'] not in alerts:
            logger.info(f"Alert 'down': {x['s']} {x['c']}")
            alerts.append(f"{x['s']}")
            send_message(f"{x['s']} {x['c']}")


def alert_up(symbol, price, data):
    for x in data:
        if x['s'] == symbol and float(x['c']) >= price and x['s'] not in alerts:
            logger.info(f"Alert 'up': {x['s']} {x['c']}")
            alerts.append(f"{x['s']}")
            send_message(f"{x['s']} {x['c']}")


def on_open(ws):
    sub_msg = {"method": "SUBSCRIBE", "params": ["!miniTicker@arr"], "id": 1}
    ws.send(json.dumps(sub_msg))
    mess = f"Connected on {time.ctime()}"
    logger.info(mess)
    send_message(mess)


def on_message(ws, message):
    print("New message")
    data = json.loads(message)
    alert_down(' SOLUSDT', 130.00, data)
    alert_up('SOLUSDT', 120.0, data)


def on_close(ws, close_status_code, close_msg):
    mess = f"Connection closed on {time.ctime()}: close_status_code: {close_status_code}, close_msg: {close_msg}"
    logger.info(mess)
    send_message(mess)

    time.sleep(5)
    ws = retry_connecting(connect_to_network, url=binance_ws_url)


def on_error(ws, e):
    mess = f"on_error: {e}"
    logger.info(mess)
    send_message(mess)


# def check_ws_connected(interval):
#     print(time.ctime())
#     print(interval)
#     threading.Timer(interval, hold_ws_for, [interval]).start()


def retry_connecting(func, retries=30, delay=5, *args, **kwargs) -> WebSocketApp | None:
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Retry {attempt + 1} / {retries}: {e}")
            time.sleep(delay)
    return None


def connect_to_network(url) -> WebSocketApp | None:
    try:
        ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
        ws.run_forever()  # ping_interval=2, reconnect=2
        return ws
    except Exception as e:
        print(f"Exception while connecting to url {url}: {e}")
        raise
        # return None


# def main():
#     ws = retry_connecting(connect_to_network, url=binance_ws_url)

    # def hold_ws_for(interval):
    #     print(time.ctime())
    #     print(interval)
    #     threading.Timer(interval, hold_ws_for, [interval]).start()
    #
    # hold_ws_for(SECONDS_IN_10_HOURS)

# def foo():
#     print(time.ctime())
#     threading.Timer(10, foo, ).start()
#
# foo()



# ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_close=on_close)
#
# ws.run_forever()
#
# ws.close()

if __name__ == "__main__":
    ws1 = retry_connecting(connect_to_network, url=binance_ws_url)
    # main()
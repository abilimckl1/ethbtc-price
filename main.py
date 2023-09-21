from threading import Lock
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import requests



# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

urlBTCByBit = 'https://api-testnet.bybit.com/v2/public/tickers?symbol=BTCUSDT'
urlBTCBinance = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
urlETHByBit = 'https://api-testnet.bybit.com/v2/public/tickers?symbol=ETHUSDT'
urlETHBinance = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(2)
        count += 1
		
        priceBTCByBit = ((requests.get(urlBTCByBit)).json())['result'][0]['index_price']
        priceBTCBinance = str(round(float(((requests.get(urlBTCBinance)).json())['price']),2))
        priceETHByBit = ((requests.get(urlETHByBit)).json())['result'][0]['index_price']
        priceETHBinance = str(round(float(((requests.get(urlETHBinance)).json())['price']),2))
		
        verdictETH = compare(priceETHByBit, priceETHBinance)
        socketio.emit('Response_Verdict_ETH',{'data': verdictETH, 'count': count})
        verdictBTC = compare(priceBTCByBit, priceBTCBinance)
        socketio.emit('Response_Verdict_BTC',{'data': verdictBTC, 'count': count})
		

        socketio.emit('Response_BTCUSDT_ByBit',{'data': 'ByBit (USDT): ' + priceBTCByBit, 'count': count})
        socketio.emit('Response_BTCUSDT_Binance',{'data': 'Binance (USDT): ' + priceBTCBinance, 'count': count})
        socketio.emit('Response_ETHUSDT_ByBit',{'data': 'ByBit (USDT): ' + priceETHByBit, 'count': count})
        socketio.emit('Response_ETHUSDT_Binance',{'data': 'Binance (USDT): ' + priceETHBinance, 'count': count})

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
@app.route('/eth')
def eth():
    return render_template('ethereum.html', async_mode=socketio.async_mode)
@app.route('/btc')
def btc():
    return render_template('bitcoin.html', async_mode=socketio.async_mode)

@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('Response_BTCUSDT_ByBit',
         {'data': message['data'], 'count': session['receive_count']})
    emit('Response_BTCUSDT_Binance',
         {'data': message['data'], 'count': session['receive_count']})
    emit('Response_ETHUSDT_ByBit',
         {'data': message['data'], 'count': session['receive_count']})
    emit('Response_ETHUSDT_Binance',
         {'data': message['data'], 'count': session['receive_count']})

def compare(bybit, binance):
     if(bybit < binance):
         return "It's lower on Bybit now at " + bybit
     else:
         return "It's lower on Binance now at " + binance


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
    socketio.run(app)
import time
import datetime
import os
import math
import pandas as pd
from statistics import mean, stdev
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL
from dotenv import load_dotenv

# Cargar claves desde .env
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Inicializar cliente sin llamar a ping()
client = Client(api_key, api_secret, tld="us")
client.API_URL = 'https://api.binance.us/api'

# Configuraciones
TRADING_PAIR = "DOGEUSD"
INTERVAL = Client.KLINE_INTERVAL_15MINUTE
RSI_PERIOD = 14
MAX_WEEKLY_LOSS = 0.30
CHECK_INTERVAL = 600  # 10 minutos
initial_balance_usdt = 200.0
last_trade_time = None
weekly_loss_limit_hit = False
entry_price = None
trade_history = []  # [(datetime, action, success)]

# Obtener historial de precios
def get_price_history():
    klines = client.get_klines(symbol=TRADING_PAIR, interval=INTERVAL, 
limit=RSI_PERIOD + 1)
    close_prices = [float(kline[4]) for kline in klines]
    return close_prices

def get_current_price():
    ticker = client.get_symbol_ticker(symbol=TRADING_PAIR)
    return float(ticker['price'])

def calculate_rsi(prices):
    gains = []
    losses = []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        if delta > 0:
            gains.append(delta)
        else:
            losses.append(abs(delta))
    if not gains:
        return 0
    if not losses:
        return 100
    avg_gain = mean(gains)
    avg_loss = mean(losses)
    rs = avg_gain / avg_loss if avg_loss else 0
    return 100 - (100 / (1 + rs))

def calculate_volatility(prices):
    return stdev(prices)

def get_recent_success_rate():
    recent = trade_history[-3:]
    if not recent:
        return 0.0
    return sum(1 for t in recent if t[2]) / len(recent)

def determine_trade_amount(rsi, volatility):
    success_rate = get_recent_success_rate()
    base_percent = 0.05
    if rsi < 20:
        base_percent += 0.02
    if volatility < 0.002:
        base_percent += 0.01
    if success_rate == 1:
        base_percent += 0.02
    return min(0.10, base_percent) * initial_balance_usdt

def should_buy(rsi):
    return rsi < 30

def should_sell(price, entry_price, rsi):
    return rsi > 60 and price >= entry_price * 1.03

def check_weekly_loss():
    global weekly_loss_limit_hit
    balance = float(client.get_asset_balance(asset='USD')['free'])
    if balance <= initial_balance_usdt * (1 - MAX_WEEKLY_LOSS):
        weekly_loss_limit_hit = True
        print("Weekly loss limit hit. Trading paused.")

def place_order(side, quantity):
    order = client.create_order(
        symbol=TRADING_PAIR,
        side=SIDE_BUY if side == "BUY" else SIDE_SELL,
        type='MARKET',
        quantity=quantity
    )
    print(f"Placed {side} order: {order}")
    return order

def get_quantity_to_trade(usdt_amount):
    price = get_current_price()
    quantity = usdt_amount / price
    return float(f"{quantity:.2f}")

def record_trade(action, success):
    trade_history.append((datetime.datetime.now(), action, success))

def run_bot():
    global last_trade_time, entry_price
    while True:
        if weekly_loss_limit_hit:
            time.sleep(3600)
            continue

        try:
            prices = get_price_history()
            rsi = calculate_rsi(prices)
            volatility = calculate_volatility(prices)
            current_price = get_current_price()
            now = datetime.datetime.now()
            can_trade = not last_trade_time or (now - 
last_trade_time).total_seconds() > 21600

            check_weekly_loss()

            if entry_price and should_sell(current_price, entry_price, 
rsi):
                usdt_amount = determine_trade_amount(rsi, volatility)
                quantity = get_quantity_to_trade(usdt_amount)
                place_order("SELL", quantity)
                record_trade("SELL", True)
                entry_price = None
                last_trade_time = now

            elif not entry_price and can_trade and should_buy(rsi):
                usdt_amount = determine_trade_amount(rsi, volatility)
                quantity = get_quantity_to_trade(usdt_amount)
                place_order("BUY", quantity)
                entry_price = current_price
                record_trade("BUY", True)
                last_trade_time = now

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)

run_bot()

# NOTA: Asegúrate de tener el archivo .env con BINANCE_API_KEY y 
BINANCE_API_SECRET


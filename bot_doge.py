import time
import datetime
import os
import math
import pandas as pd
from statistics import mean, stdev
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL
from ta.momentum import RSIIndicator
from dotenv import load_dotenv

# Cargar claves desde .env
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Inicializar cliente
client = Client(api_key, api_secret, tld="us")
client.API_URL = 'https://api.binance.us/api'

# Función para obtener los precios históricos de Dogecoin
def get_doge_prices():
    # Usamos el intervalo '1h' para obtener precios por hora (o puedes ajustar el intervalo a tu preferencia)
    klines = client.get_historical_klines("DOGEUSDT", Client.KLINE_INTERVAL_1HOUR, "14 days ago UTC")  
    prices = [float(kline[4]) for kline in klines]  # Usamos el precio de cierre (índice 4) de cada kline
    return prices

# Función para calcular el RSI
def calculate_rsi(prices):
    if len(prices) < 14:  # Asegúrate de que haya al menos 14 precios
        return None
    rsi_indicator = RSIIndicator(pd.Series(prices), window=14)  # Calculamos el RSI con los 14 precios
    return rsi_indicator.rsi().iloc[-1]  # Retornamos el último valor del RSI calculado

# Función para obtener el saldo de Dogecoin
def get_doge_balance():
    balance = client.get_asset_balance(asset='DOGE')
    return float(balance['free']) if balance else 0.0

# Función para comprar Dogecoin
def buy_doge(amount):
    order = client.order_market_buy(
        symbol='DOGEUSDT',
        quantity=amount
    )
    return order

# Función para vender Dogecoin
def sell_doge(amount):
    order = client.order_market_sell(
        symbol='DOGEUSDT',
        quantity=amount
    )
    return order

# Función principal del bot de trading
def run_bot():
    while True:
        try:
            prices = get_doge_prices()  # Obtén los precios históricos de Dogecoin
            rsi = calculate_rsi(prices)  # Calcula el RSI basado en los precios históricos

            if rsi is not None:
                print(f"RSI: {rsi}")
                if rsi < 30:  # Señal de compra
                    balance = get_doge_balance()  # Obtén el saldo disponible de Dogecoin
                    amount_to_buy = balance * 0.5  # Decide cuánto comprar (por ejemplo, el 50% de tu saldo)
                    buy_doge(amount_to_buy)
                elif rsi > 70:  # Señal de venta
                    balance = get_doge_balance()  # Obtén el saldo disponible de Dogecoin
                    amount_to_sell = balance * 0.5  # Decide cuánto vender (por ejemplo, el 50% de tu saldo)
                    sell_doge(amount_to_sell)
            else:
                print("No se pudo calcular el RSI.")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(3600)  # Espera 1 hora antes de la siguiente operación

if __name__ == "__main__":
    run_bot()

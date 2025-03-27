
import time
import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments as instruments
from ta.momentum import RSIIndicator
import pandas as pd
from dotenv import load_dotenv
import os

# Cargar variables del entorno
load_dotenv()
API_KEY = os.getenv("OANDA_API_KEY")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
PAIR = "EUR_USD"
UNITS = 1000
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

client = oandapyV20.API(access_token=API_KEY)

def get_candles():
    params = {
        "count": 100,
        "granularity": "M15",
        "price": "M"
    }
    r = instruments.InstrumentsCandles(instrument=PAIR, params=params)
    client.request(r)
    candles = r.response['candles']
    data = {
        "close": [float(c["mid"]["c"]) for c in candles if c["complete"]]
    }
    return pd.DataFrame(data)

def calculate_rsi(df):
    rsi = RSIIndicator(close=df["close"], window=RSI_PERIOD)
    return rsi.rsi().iloc[-1]

def place_order(units):
    data = {
        "order": {
            "instrument": PAIR,
            "units": str(units),
            "type": "market",
            "positionFill": "default"
        }
    }
    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=data)
    client.request(r)
    print("Orden ejecutada:", units)

def run_bot():
    while True:
        try:
            df = get_candles()
            rsi = calculate_rsi(df)

            print("RSI actual:", rsi)

            if rsi < RSI_OVERSOLD:
                print("RSI bajo, comprando...")
                place_order(UNITS)
            elif rsi > RSI_OVERBOUGHT:
                print("RSI alto, vendiendo...")
                place_order(-UNITS)
            else:
                print("Sin acción. Esperando nueva señal...")

        except Exception as e:
            print("Error:", e)

        time.sleep(900)  # Espera 15 minutos antes de la siguiente operación

if __name__ == "__main__":
    run_bot()


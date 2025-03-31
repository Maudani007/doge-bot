from binance.client import Client
import os
from dotenv import load_dotenv

# Cargar las claves de la API desde el archivo .env
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Inicializar el cliente de Binance
client = Client(api_key, api_secret, tld="us")
client.API_URL = 'https://api.binance.us/api'

# Obtener todos los precios actuales de los tickers
prices = client.get_all_tickers()

# Filtrar solo el ticker de Dogecoin (DOGE/USDT, por ejemplo)
doge_price = next((item for item in prices if item["symbol"] == 
"DOGEUSDT"), None)

# Mostrar el precio de Dogecoin
if doge_price:
    print(f"El precio actual de Dogecoin (DOGE/USDT) es: {doge_price['price']}")
else:
    print("No se encontró el precio de Dogecoin.")


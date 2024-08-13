import requests
from time import sleep
import tkinter  # Ensure tkinter is installed if you plan to use it
from atmiv import atm_iv  # Ensure atmiv module is correctly installed

# Initialize Tkinter (remove if not needed)


date = "090824"

# Define the symbols and URL
call_btc = "C-BTC-58200-090824"
put_btc = "P-BTC-58000-090824"
call_eth = "C-ETH-2480-090824"
put_eth = "P-ETH-2460-090824"

# Buy prices
Buy_call_btc_Price = 732
Buy_put_btc_Price = 782
Buy_call_eth_Price = 34.5  # Fixed typo here
Buy_put_eth_Price = 38.5

buy_total = Buy_call_btc_Price + Buy_put_btc_Price + Buy_call_eth_Price + Buy_put_eth_Price

def get_price(symbol):
    try:
        url = f"https://cdn.india.deltaex.org/v2/tickers/{symbol}"
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        ticker_info = response.json()
        mark_price_str = ticker_info['result']['mark_price']
        return float(mark_price_str)
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

def fetch_data():
  
        # Fetch prices
        current_btc_call_price = get_price(call_btc)
        current_btc_put_price = get_price(put_btc)
        current_eth_call_price = get_price(call_eth)
        current_eth_put_price = get_price(put_eth)  
        current_total = current_btc_call_price + current_btc_put_price + current_eth_call_price + current_eth_put_price
        per_change = ((current_total - buy_total) / buy_total) * 100
   
        print(f"Percentage Change: {per_change:.2f}%")

      

# Start fetching data continuously
while(True):
    fetch_data()
    atm_iv(date)
    sleep(60)

# Paper Trade :

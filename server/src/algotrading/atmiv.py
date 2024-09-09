import requests
import math 
from time import sleep


def atm_iv(date):
    def find_atm(symbol):
        

        response = requests.get("https://cdn.india.deltaex.org/v2/tickers" + f"/{symbol}")
        ticker_info = response.json()
        btc_price = ticker_info['result']['close']
        atm_value =  int(math.floor(btc_price / 200.0)) * 200
        return atm_value
        
 

    call_btc_atm = f"C-BTC-{find_atm("BTCUSD")}-{date}"
    put_btc_atm = f"P-BTC-{find_atm("BTCUSD")}-{date}"
    call_eth_atm = f"C-ETH-{find_atm("ETHUSD")}-{date}"
    put_eth_atm = f"P-ETH-{find_atm("ETHUSD")}-{date}"

    def get_iv(symbol):
            url = f"https://cdn.india.deltaex.org/v2/tickers/{symbol}"
            response = requests.get(url)
            ticker_info = response.json()
            mark_iv = float(ticker_info['result']['quotes']['mark_iv'])
            return mark_iv*100 


    btc_call_iv = get_iv(call_btc_atm)
    btc_put_iv = get_iv(put_btc_atm)
    btc_total_iv = (btc_put_iv + btc_call_iv)/2
    eth_call_iv = get_iv(call_eth_atm)
    eth_put_iv = get_iv(put_eth_atm)
    eth_total_iv = (eth_put_iv + eth_call_iv)/2
    print(f"BTC:ATM_IV {btc_total_iv}% Expiry Date:{date}")  
    print(f"ETH:ATM_IV {eth_total_iv}% Expiry Date:{date}")
        


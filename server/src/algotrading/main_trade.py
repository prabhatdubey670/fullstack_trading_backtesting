import customtkinter 
from tkinter import messagebox
import requests
import time
import hmac
import hashlib
import json
from time import sleep
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import math
import threading
from datetime import datetime


# Load environment variables
load_dotenv()
mongo_uri = os.getenv('MONGO_URI')
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

# Set up MongoDB connection
client = MongoClient(mongo_uri)
db = client['trading_db']
orders_collection = db['orders']

# Function to find the ATM (At-The-Money) value, call strike, and put strike
def find_atm(symbol, plus_minus):
    response = requests.get(f"https://cdn.india.deltaex.org/v2/tickers/{symbol}")
    ticker_info = response.json()
    
    price = ticker_info['result']['close']
    if symbol == 'BTCUSD':
        gap = 200
    elif symbol == 'ETHUSD':
        gap = 20
        
    atm_value = int(math.floor(price / gap)) * gap
    if plus_minus == 'Yes':        
        call_strike = atm_value + gap
        put_strike = atm_value - gap
    else:
        call_strike = atm_value
        put_strike = atm_value
    return atm_value, call_strike, put_strike

# Function to fetch the product ID
def get_product_id(option, symbol, strike, date):
    response = requests.get('https://cdn.india.deltaex.org/v2/products')
    products = response.json()

    symbol_format = f"{option}-{symbol}-{strike}-{date}"
    product_id = None

    for product in products.get('result', []):
        if product.get('symbol') == symbol_format:
            product_id = product.get('id')
            break

    if product_id:
        return product_id
    else:
        print(f"Product '{symbol_format}' not found.")
        return None

# Function to generate the HMAC signature
def generate_signature(method, endpoint, payload):
    timestamp = str(int(time.time()))
    signature_data = method + timestamp + endpoint + payload
    message = bytes(signature_data, 'utf-8')
    secret = bytes(api_secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    return hash.hexdigest(), timestamp

# Function to create an order
def create_order(product_id, size, side):
    method = 'POST'
    endpoint = '/v2/orders'
    
    order_data = {
        'product_id': product_id,
        'size': size,
        'order_type': 'market_order',
        'side': side
    }

    body = json.dumps(order_data, separators=(',', ':'))
    signature, timestamp = generate_signature(method, endpoint, body)

    headers = {
        'api-key': api_key,
        'signature': signature,
        'timestamp': timestamp,
        'Content-Type': 'application/json'
    }

    max_retries = 5
    retry_delay = 1

    for i in range(max_retries):
        response = requests.post(f'https://cdn.india.deltaex.org{endpoint}', headers=headers, data=body)
        order_response = response.json()

        order_info = {
            'timestamp': time.time(),
            'request_data': order_data,
            'response_data': order_response
        }

        print(order_response)

        if order_response.get('success'):
            print("Order placed successfully!")
            orders_collection.insert_one(order_response)
            break

        sleep(retry_delay)
        retry_delay *= 2

    if not order_response.get('success'):
        print("Failed to place the order after multiple attempts.")

# Corrected save_placed_order function
def save_placed_order(product_id, size, side, type_option, symbol, strike, expirydate):
    document = {
        "product_id": product_id,
        "current_date_time": datetime.now().strftime("%d-%m-%y %H:%M:%S"),  # Correct use of strftime
        "size": size,
        "buy_sell": side,
        "type": type_option,
        "symbol": symbol,
        "strike": strike,
        "expiry": expirydate,
    }
    # orders_collection.insert_one(document)  # Use the correct collection reference

# Function to schedule the order
def schedule_order(symbol, size, plus_minus, date, order_time):
    atm_value, call_strike, put_strike = find_atm(symbol,  plus_minus)

    # Get product IDs
    call_product_id = get_product_id("C", symbol.replace('USD', ''), call_strike, date)
    put_product_id = get_product_id("P", symbol.replace('USD', ''), put_strike, date)

    def place_orders():
        if call_product_id:
            create_order(call_product_id, size, 'buy')
            save_placed_order(call_product_id, size, 'buy', 'C', symbol, call_strike, date)
            
        if put_product_id:
            create_order(put_product_id, size, 'buy')
            save_placed_order(put_product_id, size, 'buy', 'P', symbol, put_strike, date)
        messagebox.showinfo("Order Status", "Orders placed successfully!")

    # Calculate time difference
    current_time = datetime.now()
    target_time = datetime.strptime(order_time, "%d-%m-%y %H:%M:%S")
    delay_seconds = (target_time - current_time).total_seconds()

    # If target time is in the future, schedule the orders
    if delay_seconds > 0:   
        threading.Timer(delay_seconds, place_orders).start()
        messagebox.showinfo("Scheduled", f"Order scheduled for {order_time}")
    else:
        messagebox.showerror("Error", "The scheduled time is in the past!")


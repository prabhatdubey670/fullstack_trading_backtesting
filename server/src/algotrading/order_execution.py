import requests
import time
import hmac
import hashlib
import json
from time import sleep
from dotenv import load_dotenv
import os
import pymongo
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

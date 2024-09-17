import tkinter as tk
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
def find_atm(symbol, gap):
    response = requests.get(f"https://cdn.india.deltaex.org/v2/tickers/{symbol}")
    ticker_info = response.json()
    
    btc_price = ticker_info['result']['close']
    atm_value = int(math.floor(btc_price / gap)) * gap
    
    call_strike = atm_value + gap
    put_strike = atm_value - gap
    
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
        orders_collection.insert_one(order_info)

        print(order_response)

        if order_response.get('success'):
            print("Order placed successfully!")
            break

        sleep(retry_delay)
        retry_delay *= 2

    if not order_response.get('success'):
        print("Failed to place the order after multiple attempts.")


# Function to schedule the order
def schedule_order(symbol, gap, size, date, order_time):
    atm_value, call_strike, put_strike = find_atm(symbol, gap)

    # Get product IDs
    call_product_id = get_product_id("C", "ETH", call_strike, date)
    put_product_id = get_product_id("P", "ETH", put_strike, date)

    def place_orders():
        if call_product_id:
            create_order(call_product_id, size, 'buy')
        if put_product_id:
            create_order(put_product_id, size, 'buy')
        messagebox.showinfo("Order Status", "Orders placed successfully!")

    # Calculate time difference

    current_time = datetime.now()
    # Convert the string with both date and time to a datetime object
    target_time = datetime.strptime(order_time, "%d-%m-%y %H:%M:%S")
    # Calculate the difference in seconds
    delay_seconds = (target_time - current_time).total_seconds()

    # If target time is in the future, schedule the orders
    if delay_seconds > 0:   
        threading.Timer(delay_seconds, place_orders).start()
        messagebox.showinfo("Scheduled", f"Order scheduled for {order_time}")
    else:
        messagebox.showerror("Error", "The scheduled time is in the past!")


# Tkinter setup
def submit_form():
    symbol = symbol_entry.get()
    gap = int(gap_entry.get())
    size = int(size_entry.get())
    date = date_entry.get()
    order_time = time_entry.get()

    schedule_order(symbol, gap, size, date, order_time)


# Creating the Tkinter GUI
root = tk.Tk()
root.title("Options Order Scheduler")

# Symbol input
tk.Label(root, text="Symbol:").grid(row=0, column=0)
symbol_entry = tk.Entry(root)
symbol_entry.grid(row=0, column=1)

# Gap input
tk.Label(root, text="Gap:").grid(row=1, column=0)
gap_entry = tk.Entry(root)
gap_entry.grid(row=1, column=1)

# Size input
tk.Label(root, text="Order Size:").grid(row=2, column=0)
size_entry = tk.Entry(root)
size_entry.grid(row=2, column=1)

# Date input
tk.Label(root, text="Expiration Date (DDMMYY):").grid(row=3, column=0)
date_entry = tk.Entry(root)
date_entry.grid(row=3, column=1)

# Time input for scheduling
tk.Label(root, text="Order Time (%d-%m-%y %H:%M:%S)").grid(row=4, column=0)
time_entry = tk.Entry(root)
time_entry.grid(row=4, column=1)

# Submit button
submit_button = tk.Button(root, text="Schedule Order", command=submit_form)
submit_button.grid(row=5, column=1)

# Run the Tkinter loop
root.mainloop()

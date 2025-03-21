import requests
import pandas as pd
import datetime
from datetime import timezone
import math
import mysql.connector
import openpyxl

def get_ohlc_optiondata(optiontype, index, resolution, start_time_date, hours, cursor, connection, gap):
    
    def get_historical_atm(unix_start, resolution, index):
        start = unix_start - 3600
        end = unix_start 
        params = {
            'resolution': resolution,
            'symbol': f"{index}USD",
            'start': f"{start}",
            'end': f"{end}"
        }
        response = requests.get("https://cdn.india.deltaex.org/v2/history/candles", params=params)
        data = response.json().get('result', [])
        if len(data) < 2:
            raise ValueError("Insufficient data received from the API")
        close = data[1].get('close')
        if close is None:
            raise ValueError("Close price not found in the API response")
        atm_value = int(math.floor(close / gap)) * gap
        return atm_value 
    
    def convert_to_utc_unix(dt):
        """Converts a datetime object to UTC and then to Unix timestamp."""
        utc_dt = dt.astimezone(timezone.utc)
        unix_time = int(utc_dt.timestamp())
        return unix_time

    def dates(start_time_date):
        """Parses the input string into a datetime object."""
        date_obj = datetime.datetime.strptime(start_time_date, "%d-%m-%Y %I:%M %p")
        starttime = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, date_obj.hour, date_obj.minute, date_obj.second)
        return starttime
    
    start_time = dates(start_time_date)
    end_time = start_time + datetime.timedelta(hours=hours)
    
    unix_start = convert_to_utc_unix(start_time)
    unix_end = convert_to_utc_unix(end_time)

    atm_value = get_historical_atm(unix_start, resolution, index)
    symbol = f"{optiontype}-{index}-{atm_value}-{end_time.strftime('%d%m%y')}"
    
    params = {
        'resolution': resolution,
        'symbol': symbol,
        'start': f"{unix_start}",
        'end': f"{unix_end}"
    }
    response = requests.get("https://cdn.india.deltaex.org/v2/history/candles", params=params)

    data = response.json().get('result', [])
    if not data:
        print(f"No data returned for {symbol} from {start_time_date}")
        return
    
    close_data = [{'time': entry['time'], 'close': entry['close']} for entry in data if 'time' in entry and 'close' in entry]

    if not close_data:
        print(f"No valid data found for {symbol} from {start_time_date}")
        return
    
    df = pd.DataFrame(close_data)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['time'] = df['time'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
    df['time'] = df['time'].dt.strftime('%H:%M:%S')

    date_data = {row['time']: row['close'] for _, row in df.iterrows()}
    
    # Insert into MySQL
    expiry = end_time.strftime('%d-%m-%y')
    
    # Insert main record
    insert_query = """
    INSERT INTO ohlc_data (expiry, atm_value)
    VALUES (%s, %s)
    """
    cursor.execute(insert_query, (expiry, atm_value))
    record_id = cursor.lastrowid

    # Insert time-price data
    insert_price_query = """
    INSERT INTO price_data (record_id, time_value, close_price)
    VALUES (%s, %s, %s)
    """
    for time_val, price in date_data.items():
        cursor.execute(insert_price_query, (record_id, time_val, price))
    
    connection.commit()
    print(f"Data for {start_time_date} saved to MySQL.")

# MySQL setup
connection = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="ohlc_data"
)
cursor = connection.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS ohlc_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    expiry VARCHAR(8),
    atm_value INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS price_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    record_id BIGINT,
    time_value VARCHAR(8),
    close_price FLOAT,
    FOREIGN KEY (record_id) REFERENCES ohlc_data(id)
)
""")

# Looping the function get_ohlc_optiondata for the next 30 days
start_date = '01-05-2024 12:30 PM'
end_date = '31-08-2024 12:30 PM'

current_date = datetime.datetime.strptime(start_date, "%d-%m-%Y %I:%M %p")
end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y %I:%M %p")

while current_date <= end_date:
    start_time_date = current_date.strftime("%d-%m-%Y %I:%M %p")
    try:
        get_ohlc_optiondata('P', 'BTC', '15m', start_time_date, 4, cursor, connection, 200)
    except ValueError as e:
        print(f"Error on {start_time_date}: {e}. Trying next date.")
    current_date += datetime.timedelta(days=1)

# Close the connection
cursor.close()
connection.close()

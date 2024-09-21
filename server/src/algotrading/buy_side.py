from order_execution import create_order, get_product_id
from datetime import datetime
from tkinter import messagebox


def schedule_order(symbol, size,side, plus_minus, date, order_time):
    atm_value, call_strike, put_strike = find_atm(symbol,  plus_minus)
    if(side == 'buy'):  
    # Get product IDs
        call_product_id = get_product_id("C", symbol.replace('USD', ''), call_strike, date)
        put_product_id = get_product_id("P", symbol.replace('USD', ''), put_strike, date)
    if(side == 'sell'):
        past_orders = orders_collection.findone()
        print(past_orders)
    # getting product id from mongodb for selling 
        
    def place_orders():
        if call_product_id:
            create_order(call_product_id, size, side)
           
        if put_product_id:
            create_order(put_product_id, size, side)
            
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


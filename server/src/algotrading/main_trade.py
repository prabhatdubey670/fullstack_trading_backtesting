from buy_side import schedule_order
import customtkinter as ctk
from tkinter import *
from tkinter.ttk import *

def run_gui(schedule_order):
    print("Initializing software...")

    # Set CustomTkinter appearance and theme
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("dark-blue")  

    # Create main window
    root = ctk.CTk()
    root.title("Options Order Scheduler")
    root.iconbitmap("D:/codeputs/ongoing/crypto_option_deltaexchange/frontend/Frame_1-removebg-preview.ico")

    # Create Buy button and assign the buy function
    buy_button = ctk.CTkButton(root, text="Buy", command=lambda: buy_form(root))
    buy_button.grid(row=0, column=0, padx=10, pady=10)
    sell_button = ctk.CTkButton(root, text="Sell", command=lambda: sell_form(root))
    sell_button.grid(row=0, column=1, padx=10, pady=10)
    custom_order_button = ctk.CTkButton(root, text="Custom Order", command=lambda: custom_order(root))
    custom_order_button.grid(row=0, column=2, padx=10, pady=10)
    
    
    # Start the main event loop
    root.mainloop()

def buy_form(root):
    """Displays the form for entering order details when the Buy button is clicked."""
    def submit_form():
        print("Attempting to schedule order...")
        symbol = symbol_entry.get()
        size = int(size_entry.get())
        side = str(side_entry.get())
        plus_minus = plus_minus_entry.get()
        date = date_entry.get()
        order_time = time_entry.get()
        
        try:
            schedule_order(symbol, size, side, plus_minus, date, order_time)
            print('Order successfully scheduled with the following details:')
            print(f"Symbol: {symbol}")
            print(f"Size: {size}")
            print(f"Side: {side}")
            print(f"Above & below ATM: {plus_minus}")
            print(f"Expiry Date: {date}")
            print(f"Order Time: {order_time}")
            print("Order successfully scheduled.")
        except Exception as e:
            print(f"Error: {str(e)}")
    # Clear previous widgets, if any, before displaying the form
    for widget in root.grid_slaves():
        widget.grid_forget()

    # Symbol input
    ctk.CTkLabel(root, text="Symbol:").grid(row=0, column=0, padx=10, pady=10)
    symbol_entry = ctk.CTkEntry(root)
    symbol_entry.grid(row=0, column=1, padx=10, pady=10)

    # Order Size input
    ctk.CTkLabel(root, text="Order Size:").grid(row=1, column=0, padx=10, pady=10)
    size_entry = ctk.CTkEntry(root)
    size_entry.grid(row=1, column=1, padx=10, pady=10)

    # Buy or Sell input
    ctk.CTkLabel(root, text="Buy or Sell:").grid(row=2, column=0, padx=10, pady=10)
    side_entry = ctk.CTkEntry(root)
    side_entry.grid(row=2, column=1, padx=10, pady=10)

    # Plus Minus input
    ctk.CTkLabel(root, text="Plus Minus:").grid(row=3, column=0, padx=10, pady=10)
    plus_minus_entry = ctk.CTkEntry(root)
    plus_minus_entry.grid(row=3, column=1, padx=10, pady=10)

    # Expiration Date input
    ctk.CTkLabel(root, text="Expiration Date (DDMMYY):").grid(row=4, column=0, padx=10, pady=10)
    date_entry = ctk.CTkEntry(root)
    date_entry.grid(row=4, column=1, padx=10, pady=10)

    # Order Time input
    ctk.CTkLabel(root, text="Order Time (dd-mm-yy HH:MM:SS):").grid(row=5, column=0, padx=10, pady=10)
    time_entry = ctk.CTkEntry(root)
    time_entry.grid(row=5, column=1, padx=10, pady=10)

    # Submit button to schedule the order
    submit_button = ctk.CTkButton(root, text="Schedule Order", command=submit_form)
    submit_button.grid(row=6, column=1, padx=10, pady=10)
    
    return symbol_entry, size_entry, side_entry, plus_minus_entry, date_entry, time_entry
    
def sell_form(root):
    pass


def custom_order(root):
    pass



# Run the GUI
run_gui(schedule_order)

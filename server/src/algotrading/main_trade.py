from buy_side import schedule_order
import customtkinter as ctk
# import sys

def run_gui():
    print("Initialising software...")

    # Function to redirect print statements to the GUI
    # def log_message(message):
    #     log_textbox.configure(state="normal")
    #     log_textbox.insert("end", message + "\n")
    #     log_textbox.configure(state="disabled")
    #     log_textbox.yview('end')  # Scroll to the bottom

    # Overriding the print function to redirect output to the log_message
    # class PrintLogger:
    #     def write(self, message):
    #         if message.strip() != "":
    #             log_message(message)
    #     def flush(self):
    #         pass

    # sys.stdout = PrintLogger()  # Redirect print statements to the log_message

    # ctkinter setup
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

    # Creating the ctkinter GUI
    ctk.set_appearance_mode("dark")  # Sets the appearance mode to dark
    ctk.set_default_color_theme("dark-blue")  # Sets the color theme to dark-blue

    root = ctk.CTk()  # Changed to customtkinter's CTk root window
    root.title("Options Order Scheduler")
    root.iconbitmap("D:/codeputs/ongoing/crypto_option_deltaexchange/frontend/Frame_1-removebg-preview.ico")

    # Symbol input
    ctk.CTkLabel(root, text="Symbol:").grid(row=0, column=0, padx=10, pady=10)
    symbol_entry = ctk.CTkEntry(root)
    symbol_entry.grid(row=0, column=1, padx=10, pady=10)

    # Size input
    ctk.CTkLabel(root, text="Order Size:").grid(row=1, column=0, padx=10, pady=10)
    size_entry = ctk.CTkEntry(root)
    size_entry.grid(row=1, column=1, padx=10, pady=10)

    # Side input
    ctk.CTkLabel(root, text="Buy or Sell :").grid(row=2, column=0, padx=10, pady=10)
    side_entry = ctk.CTkEntry(root)
    side_entry.grid(row=2, column=1, padx=10, pady=10)

    # Plus Minus input
    ctk.CTkLabel(root, text="Plus Minus:").grid(row=3, column=0, padx=10, pady=10)
    plus_minus_entry = ctk.CTkEntry(root)
    plus_minus_entry.grid(row=3, column=1, padx=10, pady=10)

    # Date input
    ctk.CTkLabel(root, text="Expiration Date (DDMMYY):").grid(row=4, column=0, padx=10, pady=10)
    date_entry = ctk.CTkEntry(root)
    date_entry.grid(row=4, column=1, padx=10, pady=10)

    # Time input for scheduling
    ctk.CTkLabel(root, text="Order Time (dd-mm-yy HH:MM:SS):").grid(row=5, column=0, padx=10, pady=10)
    time_entry = ctk.CTkEntry(root)
    time_entry.grid(row=5, column=1, padx=10, pady=10)

    # Submit button
    submit_button = ctk.CTkButton(root, text="Schedule Order", command=submit_form)
    submit_button.grid(row=6, column=1, padx=10, pady=10)

    # Output log - Adjusting size, span, and positioning
    log_textbox = ctk.CTkTextbox(root, height=10, width=40)  # Adjust the height and width
    log_textbox.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")  # span across columns and stick to east-west
    log_textbox.configure(state="disabled")  # Make it read-only

    # Run the ctkinter loop
    root.mainloop()
    print("Place orders . . .")

run_gui()
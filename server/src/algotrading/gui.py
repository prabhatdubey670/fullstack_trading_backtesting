from main_trade import schedule_order
import customtkinter as ctk

# ctkinter setup
def submit_form():
    symbol = symbol_entry.get()

    size = int(size_entry.get())
    plus_minus = plus_minus_entry.get()  # Corrected to fetch from plus_minus_entry
    date = date_entry.get()
    order_time = time_entry.get()
  
    schedule_order(symbol, size, plus_minus, date, order_time)

# Creating the ctkinter GUI
ctk.set_appearance_mode("dark")  # Sets the appearance mode to dark
ctk.set_default_color_theme("dark-blue")  # Sets the color theme to dark-blue

root = ctk.CTk()  # Changed to customtkinter's CTk root window
root.title("Options Order Scheduler")
root.iconbitmap("D:/codeputs/ongoing/crypto_option_deltaexchange/frontend/Frame_1-removebg-preview.ico", )


# Symbol input
ctk.CTkLabel(root, text="Symbol:").grid(row=0, column=0, padx=10, pady=10)
symbol_entry = ctk.CTkEntry(root)
symbol_entry.grid(row=0, column=1, padx=10, pady=10)

# Size input
ctk.CTkLabel(root, text="Order Size:").grid(row=1, column=0, padx=10, pady=10)
size_entry = ctk.CTkEntry(root)
size_entry.grid(row=1, column=1, padx=10, pady=10)

# Plus Minus input
ctk.CTkLabel(root, text="Plus Minus:").grid(row=2, column=0, padx=10, pady=10)
plus_minus_entry = ctk.CTkEntry(root)
plus_minus_entry.grid(row=2, column=1, padx=10, pady=10)

# Date input
ctk.CTkLabel(root, text="Expiration Date (DDMMYY):").grid(row=3, column=0, padx=10, pady=10)
date_entry = ctk.CTkEntry(root)
date_entry.grid(row=3, column=1, padx=10, pady=10)

# Time input for scheduling
ctk.CTkLabel(root, text="Order Time (dd-mm-yy HH:MM:SS):").grid(row=4, column=0, padx=10, pady=10)
time_entry = ctk.CTkEntry(root)
time_entry.grid(row=4, column=1, padx=10, pady=10)

# Submit button
submit_button = ctk.CTkButton(root, text="Schedule Order", command=submit_form)
submit_button.grid(row=5, column=1, padx=10, pady=10)

# Run the ctkinter loop
root.mainloop()

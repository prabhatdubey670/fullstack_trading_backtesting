import customtkinter as ctk 
import tkinter as tk
from order_execution import create_order, get_product_id

 
def custom_order(option, symbol, strike, date, size, side, ):
    product_id = get_product_id(option, symbol, strike, date)
    order = create_order(product_id, size, side)
    
    
    
    
    
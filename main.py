from tkinter import ttk
from ttkthemes import ThemedTk

from main_window import MainWindow

import sqlite3

#connect to the database
conn = sqlite3.connect("purchases.db")

root = ThemedTk(theme = "equilux")
MainWindow(root, conn)
root.mainloop()

from tkinter import ttk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkcalendar import DateEntry

import datetime
from datetime import datetime

import sqlite3

class InsertWindow():
    

    def __init__(self, master, conn, parent):
        #making a connection to the database
        self.conn = conn

        #creating a cursor object
        self.cur = self.conn.cursor()

        #intialising the window
        self.master = master
        self.parent = parent
        self.master.resizable(width = False, height = False)
        self.master.title("Inserting Window")

        #centering the window
        self.width = 300
        self.height = 200
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        self.xcor = (self.screen_width/2) - (self.width/2)
        self.ycor = (self.screen_height/2) - (self.height/2)
        self.master.geometry("%dx%d+%d+%d" % (self.width, self.height, self.xcor, self.ycor))

        #intialsing the frame
        self.frame = ttk.Frame(master)
        self.frame.pack(fill = tk.BOTH, expand = True)

        #configuring the rows and colums
        self.frame.rowconfigure(0, weight = 1)
        self.frame.rowconfigure(1, weight = 1)
        self.frame.rowconfigure(2, weight = 1)
        self.frame.rowconfigure(3, weight = 1)
        self.frame.rowconfigure(4, weight = 1)
        self.frame.columnconfigure(0, weight = 2, uniform = "uniform")
        self.frame.columnconfigure(1, weight = 5, uniform = "uniform")

        #styles
        self.style = ttk.Style()
        self.style.configure("4.TLabel", font = ("Open Sans", 15, "bold"), foreground = "#EDF6F9")
        self.style.configure("2.TButton", font = ("Open Sans", 14, "bold"), foreground = "#EDF6F9")
        self.style.configure("3.TButton", font = ("Open Sana", 14, "bold"), foreground = "#278EA5")

        #the components
        #all labels
        self.label1 = ttk.Label(self.frame, text = "Item: ", style = "4.TLabel")
        self.label1.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = "w")
        self.label2 = ttk.Label(self.frame, text = "Type: ", style = "4.TLabel")
        self.label2.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = "w")
        self.label3 = ttk.Label(self.frame, text = "Cost: ", style = "4.TLabel")
        self.label3.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = "w")
        self.label4 = ttk.Label(self.frame, text = "Date: ", style = "4.TLabel")
        self.label4.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = "w")

        #all entry boxes
        self.item_text = tk.StringVar()
        self.entry_item = ttk.Entry(self.frame, textvariable = self.item_text)
        self.entry_item.grid(row = 0, column = 1)
        self.combo_type =  ttk.Combobox(self.frame, state = "readonly", 
                            values=[
                                    "Household", 
                                    "Apparel",
                                    "Beauty",
                                    "Health",
                                    "Education",
                                    "Food",
                                    "Other"], width = 18)
        self.combo_type.grid(row = 1, column = 1)
        self.cost_text = tk.StringVar()
        self.entry_cost = ttk.Entry(self.frame, textvariable = self.cost_text)
        self.entry_cost.grid(row = 2, column = 1)
        self.cal = DateEntry(self.frame, width = 18, background = "darkblue",
                             foreground = "white", borderwidth = 2, year = 2020)
        self.cal.grid(row = 3, column = 1)
        self.cal._top_cal.overrideredirect(False) #allows the DateEntry widget to appear

        #the buttons
        self.insert_button = ttk.Button(self.frame, text = "Insert",style = "2.TButton",
                                       command = self.insert_data, width = 18)
        self.insert_button.grid(row = 4, column = 1, padx = 10, pady = 10)
        self.back_button = ttk.Button(self.frame, text = "⤶", style = "3.TButton",
                                     command = self.close_windows, width = 13)
        self.back_button.grid(row = 4, column = 0, padx = 10)

        #all the needed data for the insert window
        self.past_months = []
        for i in self.cur.execute("SELECT Date FROM Purchases"):
            self.past_months.append(i[-1][:7])
        
    def close_windows(self):
        self.master.destroy()

    def insert_data(self):
        self.date = self.cal.get_date()
        self.date = str(self.date)[:7]
        self.budget = 0
        for budget in self.cur.execute("SELECT Budget FROM Budget WHERE Date LIKE '" + self.date + "%'"):
            self.budget = budget[-1]
        self.leftover_money = 0
        for money in self.cur.execute("SELECT Leftover FROM Analysis WHERE Date = '" + self.date + "'"):
            self.leftover_money = money[-1]
        
        #making sure all the fields have been filled
        if not self.cost_text.get() or not self.item_text.get() or not self.combo_type.get():
            messagebox.showwarning("Error", "You have to fill in all the details")
        else:
            #insert into purhases database
            self.cur.execute("INSERT INTO purchases(Item, Type, Cost, Date) VALUES('"
                             + self.item_text.get() + "', '"
                             + self.combo_type.get() + "', '"
                             + self.cost_text.get() + "', '"
                             + str(self.cal.get_date()) + "')")

            #doing the arithmetic for insertion into the analysis table
            for i in self.past_months:
                if i == self.date:
                    self.cur.execute("UPDATE Analysis SET Leftover = ? WHERE Date = ?",
                                 (str(self.leftover_money - int(self.cost_text.get())),
                                  self.date))
                    break
                else:
                    self.cur.execute("INSERT INTO Analysis(Date, Leftover) VALUES('"
                                      + self.date + "', '"
                                      + str(self.budget - int(self.cost_text.get())) + "')")
                    break
                
            self.conn.commit()
            self.parent.refresh() #refresh the main table
            self.master.destroy() #close this window
        

    
        

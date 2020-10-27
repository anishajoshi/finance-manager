from tkinter import ttk  
import tkinter as tk
import tkinter.ttk as ttk

import matplotlib.figure
import matplotlib.patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import datetime
import calendar
from datetime import datetime
import sqlite3

class AdviceWindow:
    

    def __init__(self, master, conn):

        #making a connection to the database
        self.conn = conn

        #creating a cursor object
        self.cur = self.conn.cursor()

        #intialising the window
        self.master = master
        master.resizable(width = False, height = False)
        master.title("Debt Information Window")

        #centering the window
        self.width = 800
        self.height = 600
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        self.xcor = (self.screen_width / 2) - (self.width / 2)
        self.ycor = (self.screen_height / 2) - (self.height / 2)
        self.master.geometry("%dx%d+%d+%d" % (self.width, self.height, self.xcor, self.ycor))

        #intialsing the frame
        self.frame = ttk.Frame(master)
        self.frame.pack(fill = tk.BOTH, expand = True)

        #configuring the rows and columns
        self.frame.rowconfigure(0, weight = 1)
        self.frame.rowconfigure(1, weight = 1)
        self.frame.rowconfigure(2, weight = 2)
        self.frame.rowconfigure(3, weight = 2)
        self.frame.rowconfigure(4, weight = 2)
        self.frame.rowconfigure(5, weight = 1)
        self.frame.columnconfigure(0, weight = 2, uniform = "uniform")
        self.frame.columnconfigure(1, weight = 4, uniform = "uniform")
        self.frame.columnconfigure(2, weight = 1, uniform = "uniform")

        #styles
        self.style = ttk.Style()
        self.style.configure("1.TLabel", font = ("Open Sans", 24, "bold"), foreground = "#EDF6F9")
        self.style.configure("2.TLabel", font = ("Open Sans", 18, "bold"), foreground = "#EDF6F9")
        self.style.configure("3.TLabel", font = ("Open Sans", 12), foreground = "#EDF6F9")
        self.style.configure("2.TButton", font = ("Open Sans", 14, "bold"), foreground = "#EDF6F9")

        #components
        #heading label
        self.heading_label = ttk.Label(self.frame, text = "Debt Information", style = "1.TLabel")
        self.heading_label.grid(row = 0, column = 0, columnspan = 3, padx = 10, pady = 10)
        
        self.label_current = ttk.Label(self.frame, text = "Current Situation", style = '2.TLabel')
        self.label_current.grid(row = 1, column = 0, padx = 10, pady = 10)
    
        self.label_time = ttk.Label(self.frame, text = "Over all of time", style = '2.TLabel')
        self.label_time.grid(row = 1, column = 1, padx = 10, pady = 10)

        self.label_filters = ttk.Label(self.frame, text = "Filters", style = '2.TLabel')
        self.label_filters.grid(row = 1, column = 2, padx = 10, pady = 10)

        self.label_debt_info = ttk.Label(self.frame, text = "", style = "3.TLabel")
        self.label_debt_info.grid(row = 4, column = 0, padx = 10, pady = 10)

        self.label_predict = ttk.Label(self.frame, text = "", style = "3.TLabel")
        self.label_predict.grid(row = 4, column = 1, padx = 10, pady = 10)

        #comboboxes and their filters
        self.year_filters = []
        for date in self.cur.execute("SELECT Date FROM Purchases").fetchall():
            self.year_filters.append(date[-1][:4])
        self.year_filters = list(dict.fromkeys(self.year_filters))

        #month filters
        self.month_filters = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        self.combo_year = ttk.Combobox(self.frame, state = "readonly", 
                            values = self.year_filters, width = 11)
        self.combo_year.grid(row = 2, column = 2, padx = 10, pady = 10)
        self.combo_month = ttk.Combobox(self.frame, state = "readonly",
                                        values = self.month_filters, width = 11)
        self.combo_month.grid(row = 3, column = 2, padx = 10, pady = 10)

        #buttons
        self.reset_button = ttk.Button(self.frame, text = "Reset", style = "2.TButton", command = self.all_time)
        self.reset_button.grid(row = 4, column = 2, padx = 10)

        self.home_button = ttk.Button(self.frame, text = "Home", style = "2.TButton",
                                      command = self.close_windows)
        self.home_button.grid(row = 5, columnspan = 3, padx = 10, pady = 10, ipadx = 1000)

        #calling the respective functions
        self.debt_graph_and_info()
        self.all_time()

        self.combo_year.bind("<<ComboboxSelected>>", self.year_filter)
        self.combo_month.bind("<<ComboboxSelected>>", self.month_filter)
        
    def close_windows(self):
        self.master.destroy()

    def year_filter(self, event):
        self.year = self.combo_year.get()
        self.cur.execute("SELECT Date, Leftover FROM Analysis WHERE Date LIKE '" + self.year + "%'")
        self.dates = []
        self.leftover = []
        self.rows = self.cur.fetchall()
        for row in self.rows:
            self.dates.append(datetime.strptime(row[0], '%Y-%m'))
            self.leftover.append(row[1])
            
        self.new_data = list(zip(self.dates, self.leftover))
        self.new_data.sort()
        self.new_data = np.array(self.new_data)

        #the plotting
        self.fig = matplotlib.figure.Figure(figsize = (12, 4), dpi = 80)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(self.new_data[:,0], self.new_data[:,1])
        for label in self.ax.get_xticklabels():
            label.set_rotation(13)
            label.set_color("#EDF6F9")
        for label in self.ax.get_yticklabels():
            label.set_color("#EDF6F9")
        self.fig.patch.set_facecolor("#454545")
        self.ax.axhline(linewidth = 3, color = "r")

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 2, column = 1, rowspan = 2, padx = 10, pady = 10)
        self.canvas.draw()
        

    def month_filter(self, event):
        self.month = self.combo_month.get()
        self.month_number = datetime.strptime(self.month, "%b").month
        if (0 < self.month_number < 10):
            self.month_number = "0" + str(self.month_number)
        self.date = str(self.combo_year.get()) + "-" + str(self.month_number)
        self.budget = 0
        for i in self.cur.execute("SELECT Budget FROM Budget WHERE Date LIKE '" + self.date + "%'"):
            self.budget = i[-1]
        self.leftover = 0
        for i in self.cur.execute("SELECT Leftover FROM Analysis WHERE Date = '" + str(self.date) + "'"):
            self.leftover = round(i[-1], 2)
        self.spent = round(self.budget - self.leftover, 2)
        colors = ["#278EA5", "#1F4287"]

        #the plotting
        self.fig = matplotlib.figure.Figure(figsize = (5, 3), dpi = 80)
        self.ax = self.fig.add_subplot(111)
        self.ax.pie([self.spent, self.leftover], colors = colors) 
        self.ax.legend(["spent: " + str(self.spent),"leftover: " + str(self.leftover)])

        self.circle = matplotlib.patches.Circle((0,0), 0.7, color = "#464646")
        self.ax.add_artist(self.circle)
        self.fig.patch.set_facecolor("#464646")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 2, column = 0, rowspan = 2, padx = 10, pady = 10)
        self.canvas.draw()

    def debt_graph_and_info(self):
        self.current_month = datetime.date(datetime.now()).strftime("%Y-%m") #get the current month
        self.budget = self.cur.execute("SELECT Budget FROM Budget").fetchall()[-1][-1] #get the latest budget
        self.leftover = 0
        for i in self.cur.execute("SELECT Leftover FROM Analysis WHERE Date = '" + str(self.current_month) + "'"):
            self.leftover = round(i[-1], 2)
        self.spent = round(self.budget - self.leftover, 2)
        colors = ["#278EA5", "#1F4287"]

        #the plotting
        self.fig = matplotlib.figure.Figure(figsize = (5, 3), dpi = 80)
        self.ax = self.fig.add_subplot(111)
        self.ax.pie([self.spent, self.leftover], colors = colors) 
        self.ax.legend(["spent: " + str(self.spent),"leftover: " + str(self.leftover)])

        self.circle = matplotlib.patches.Circle((0,0), 0.7, color = "#464646")
        self.ax.add_artist(self.circle)
        self.fig.patch.set_facecolor("#464646")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 2, column = 0, rowspan = 2, padx = 10, pady = 10)
        self.canvas.draw()

        #the info part of it
        if self.spent > self.budget:
            self.text = "You're in debt! Maybe consider lowering next month's budget by around $" + str(abs(self.leftover)) + "."
        else:
            self.text = "Good Job! You're not in debt. You still have $" + str(self.leftover) +" left to spend this month."

        self.label3 = ttk.Label(self.frame, text = self.text, style = '3.TLabel')
        self.label3.grid(row = 4, column = 0, columnspan = 2, sticky = "nsew", padx = 10)

    def all_time(self):
        self.cur.execute("SELECT Date, Leftover FROM Analysis")
        self.dates = []
        self.leftover = []
        self.rows = self.cur.fetchall()
        for row in self.rows:
            self.dates.append(datetime.strptime(row[0], '%Y-%m'))
            self.leftover.append(row[1])
            
        self.new_data = list(zip(self.dates, self.leftover))
        self.new_data.sort()
        self.new_data = np.array(self.new_data)

        #the plotting
        self.fig = matplotlib.figure.Figure(figsize = (12, 4), dpi = 80)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(self.new_data[:,0], self.new_data[:,1])
        self.fig.patch.set_facecolor("#454545")
        self.ax.axhline(linewidth = 3, color = "r")

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 2, column = 1, rowspan = 2, padx = 10, pady = 10)
        self.canvas.draw()

        #clearing out all the other comboboxes
        self.combo_year.set("")
        self.combo_month.set("")

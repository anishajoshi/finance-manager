from tkinter import ttk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font
from tkinter import messagebox

import datetime
import calendar
from datetime import datetime
import sqlite3

import matplotlib.figure
import matplotlib.patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches

from overview_window import OverviewWindow
from purchases_window import PurchasesWindow
from advice_window import AdviceWindow

class MainWindow:
    

    def __init__(self, master, conn):     
        #making a connection to the database
        self.conn = conn

        #creating a cursor object
        self.cur = self.conn.cursor() 

        #intialising the window
        self.master = master
        master.resizable(width = False, height = False)
        master.title("Main Window")

        #centering the window
        self.width = 750
        self.height = 500
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        self.xcor = (self.screen_width / 2) - (self.width / 2)
        self.ycor = (self.screen_height / 2) - (self.height / 2)
        master.geometry("%dx%d+%d+%d" % (self.width, self.height, self.xcor, self.ycor))

        #intialsing the frame
        self.frame = ttk.Frame(master)
        self.frame.pack(fill = tk.BOTH, expand = True)

        #configuring the rows and columns
        self.frame.rowconfigure(0, weight = 1)
        self.frame.rowconfigure(1, weight = 1)
        self.frame.rowconfigure(2, weight = 1)
        self.frame.rowconfigure(3, weight = 1)
        self.frame.rowconfigure(4, weight = 1)
        self.frame.columnconfigure(0, weight = 1, uniform = "uniform")
        self.frame.columnconfigure(1, weight = 1, uniform = "uniform")
        self.frame.columnconfigure(2, weight = 1, uniform = "uniform")

        #styles and font for labels and buttons
        self.style = ttk.Style()
        self.style.configure("1.TButton", font = ("Open Sans", 20, "bold"), foreground = "#EDF6F9")
        self.style.configure("2.TButton", font = ("Open Sans", 14, "bold"), foreground = "#EDF6F9")
        self.style.configure("1.TLabel", font = ("Open Sans", 24, "bold"), foreground = "#EDF6F9")
        self.style.configure("2.TLabel", font = ("Open Sans", 18, "bold"), foreground = "#EDF6F9")
        self.style.configure("3.TLabel", font = ("Open Sans", 12), foreground = "#EDF6F9")
       
        #getting all the needed data for the main window mainly from the database
        self.recent_purchase = self.cur.execute("SELECT Item FROM Purchases").fetchall()[-1][-1]
        self.current_budget = self.cur.execute("SELECT Budget FROM Budget").fetchall()[-1][-1]

        #calendar information
        self.current_month = datetime.date(datetime.now()).strftime("%Y-%m")
        self.day = int(datetime.date(datetime.now()).strftime("%d"))
        self.year = int(datetime.date(datetime.now()).strftime("%Y"))
        self.month = int(datetime.date(datetime.now()).strftime("%m"))
        self.monthRange = calendar.monthrange(self.year, self.month)[1]

        #total amount of money spent for this particular month
        self.costs = self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" +\
                                      self.current_month + "%'") 
        self.total_spent = 0
        for num in self.costs:
            self.total_spent += int(num[0])

        #arithmetic calculations
        self.ten_percent = round(0.10 * self.current_budget,2)
        self.days_left = int(self.monthRange) - int(self.day)
        self.average_over_left_days = round((self.total_spent / self.days_left), 2)

        #all the main components for the page

        #labels
        self.heading_label = ttk.Label(self.frame, text = "My Money Manager!", style = "1.TLabel")
        self.heading_label.grid(row = 0, columnspan = 3, pady = (10,0))

        #buttons
        self.purchase_button = ttk.Button(self.frame, text = "Purchases", style = "1.TButton",
                                          command = self.purchases_window)
        self.purchase_button.grid(row = 1,column = 0, sticky = "nsew", padx = 10, pady = 10)

        self.overview_button = ttk.Button(self.frame, text = "Overview", style = "1.TButton",
                                         command = self.overview_window)
        self.overview_button.grid(row = 2,column = 0, sticky = "nsew", padx = 10, pady = 10)

        self.advice_button = ttk.Button(self.frame, text = "Advice", style = "1.TButton",
                                         command = self.advice_window)
        self.advice_button.grid(row = 3, column = 0, rowspan = 2, sticky = "nsew", padx = 10, pady = 10)

        self.save_button = ttk.Button(self.frame, text = "Save", style = "2.TButton",
                                     command = self.save_budget)
        self.save_button.grid(row = 4,column = 1, sticky = "nsew", padx = 10, pady = (0, 10), ipady = 15)

        #entry box for entering monthly budget
        self.budget_text = tk.StringVar()
        self.budget_entry = ttk.Entry(self.frame, textvariable = self.budget_text,
                                      font = ("Open Sans", 13), foreground = "#EDF6F9",
                                      width = 40)
        self.budget_text.set("Enter Monthly Budget...")
        self.budget_entry.bind("<Button-1>", self.erase_on_click)
        self.budget_entry.grid(row = 3, column = 1, padx = 10, ipady = 15)

        #calling all the functions
        self.graph_current_budget()
        self.graph_days_left()
        self.info_reminders()

    #the following are all the functions required to open the respective windows
        
    def purchases_window(self):   
        PurchasesWindow(tk.Toplevel(self.master), self.conn)
        
    def overview_window(self):     
        OverviewWindow(tk.Toplevel(self.master), self.conn)

    def advice_window(self):    
        AdviceWindow(tk.Toplevel(self.master), self.conn)

    def info_reminders(self):
        #text for the info and reminders label
        self.remind_text = (
            f"1) Your latest purchase was {self.recent_purchase}\n\n"
            f"2) In order to save 10% of your budget\n"
            f"     you can't spend more than ${self.ten_percent}\n\n"
            f"3) You have approximately ${self.average_over_left_days} left\n"
            f"     for each day of this month\n\n"
            f"4) Below you can see you have {self.days_left} days\n"
            f"     before your next cycle :)"
            )
        #label for the window
        self.reminders_label = ttk.Label(self.frame, text = "Info and Reminders", style = "2.TLabel")
        self.reminders_label.grid(row = 1, column = 2)

        self.info_label = ttk.Label(self.frame, text = self.remind_text, style = "3.TLabel")
        self.info_label.grid(row = 2, column = 2)
        

    def graph_current_budget(self):
        #most variables have been initialised in __init__
        self.left = self.current_budget - self.total_spent #calculates how much money is left
        colors = ["#278ea5", "#1f4287"]

        #the plotting
        self.fig = matplotlib.figure.Figure(figsize = (4, 4), dpi = 60)
        self.ax = self.fig.add_subplot(111)
        self.ax.pie([self.total_spent, self.left], colors = colors) 
        self.ax.legend(["spent: " + str(self.total_spent),"amount left: " + str(self.left)])

        self.circle = matplotlib.patches.Circle((0,0), 0.7, color = "#464646")
        self.ax.add_artist(self.circle)
        self.fig.patch.set_facecolor("#464646")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 1, rowspan = 2, column = 1, padx = 10, pady = 10)
        self.canvas.draw()

    def graph_days_left(self):
        #all the needed data
        self.start = 0
        colors = ["#278EA5", "#1F4287"]

        #the plotting
        self.fig = matplotlib.figure.Figure(figsize = (5, 2), dpi = 60)
        self.fig.patch.set_facecolor("#464646")
        self.ax = self.fig.add_subplot(111)
        self.ax.broken_barh([(self.start, self.day),(self.day, self.days_left)],
                            [10, 10], facecolors = ("#278EA5", "#1F4287"))
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.set_axisbelow(True) 
        self.ax.set_yticklabels([""])
        self.ax.grid(axis='x')
        self.leg1 = mpatches.Patch(color="#278EA5", label='Over')
        self.leg2 = mpatches.Patch(color="#1F4287", label='Left')
        self.ax.legend(handles=[self.leg1, self.leg2], ncol=2)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 3, rowspan = 2, column = 2, padx = 10, pady = 10)
        self.canvas.draw()

    def save_budget(self):
        #getting all the neccesary data 
        self.latest_month = self.cur.execute("SELECT Date FROM Budget").fetchall()[-1][-1][:7]

        #check if they inserted only integers
        try:
            int(self.budget_text.get())
        except ValueError:
            messagebox.showwarning("Error", "You can only insert numbers")
        else:
            #check if they've already inserted a budget for this month
            if self.current_month == self.latest_month:
                messagebox.showwarning("Error", "You've already insert a budget for this month")
                self.answer = messagebox.askquestion ("Budget Change","Do you wish to change your current budget?")
                if self.answer == "yes":
                    self.cur.execute("DELETE FROM Budget WHERE DATE LIKE '" + self.current_month + "%'")               
                self.budget_text.set("Enter Monthly Budget...")
            else:
                self.cur.execute("INSERT INTO Budget(Date, Budget) VALUES('"
                                 + datetime.date(datetime.now()).strftime("%Y-%m-%d")
                                 + "', '" + self.budget_text.get() + "')")
                self.conn.commit()       

        #set the enter box back to its original state
        self.budget_text.set("Enter Monthly Budget...")

    def erase_on_click(self, event):
        #erasing the text when user clicks on a widget
        event.widget.delete(0, tk.END)      

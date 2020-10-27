from tkinter import ttk  
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font
from tkcalendar import Calendar

import matplotlib.figure
import matplotlib.patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from datetime import datetime
import sqlite3

class OverviewWindow:
    

    def __init__(self, master, conn):
        #making a connection to the database
        self.conn = conn

        #creating a cursor object
        self.cur = self.conn.cursor()

        #intialising the window
        self.master = master
        master.resizable(width = False, height = False)
        master.title("Overview Window")

        #centering the window
        self.width = 1200
        self.height = 700
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        self.xcor = (self.screen_width / 2) - (self.width / 2)
        self.ycor = (self.screen_height / 2) - (self.height / 2)
        self.master.geometry("%dx%d+%d+%d" % (self.width, self.height, self.xcor, self.ycor))

        #intialsing the frame
        self.frame = ttk.Frame(master)
        self.frame.pack(fill = tk.BOTH, expand = True)

        #styles
        self.style = ttk.Style()
        self.style.configure("1.TLabel", font = ("Open Sans", 24, "bold"), foreground = "#EDF6F9")
        self.style.configure("4.TLabel", font = ("Open Sans", 15, "bold"), foreground = "#EDF6F9")
        self.style.configure("2.TButton", font = ("Open Sans", 14, "bold"), foreground = "#EDF6F9")

        #configuring the rows and columns
        self.frame.rowconfigure(0, weight = 1)
        self.frame.rowconfigure(1, weight = 1)
        self.frame.rowconfigure(2, weight = 1)
        self.frame.rowconfigure(3, weight = 1)
        self.frame.rowconfigure(4, weight = 1)
        self.frame.rowconfigure(5, weight = 1)
        self.frame.columnconfigure(0, weight = 1, uniform = "uniform")
        self.frame.columnconfigure(1, weight = 1, uniform = "uniform")
        self.frame.columnconfigure(2, weight = 3, uniform = "uniform")
        self.frame.columnconfigure(3, weight = 3, uniform = "uniform")

        #the components
        #heading label
        self.label_heading = ttk.Label(self.frame, text = "The Overview", style = "1.TLabel")
        self.label_heading.grid(row = 0, column = 0, columnspan = 7, pady = 10)

        #the differnt filters
        self.label_year = ttk.Label(self.frame, text = "Year : ", style = "2.TLabel")
        self.label_year.grid(sticky = "nswe", row = 1, column = 0, padx = (20,0), pady = 10)
        self.label_month = ttk.Label(self.frame, text = "Month : ", style = "2.TLabel")
        self.label_month.grid(sticky = "nswe", row = 2, column = 0, padx = (20,0), pady = 10)
        self.label_category = ttk.Label(self.frame, text = "Category : ", style = "2.TLabel")
        self.label_category.grid(sticky = "nswe", row = 3, column = 0, padx = (20,0), pady = 10)
        
        #the values for each of the filters
        #for the year filter, get all the years that they have inserted purchases for
        self.year_filters = []
        for date in self.cur.execute("SELECT Date FROM Purchases").fetchall():
            self.year_filters.append(date[-1][:4])
        self.year_filters = list(dict.fromkeys(self.year_filters))
        #month filters
        self.month_filters = ["None", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        #cateogry filters
        self.category_filters = ["None", "Household", "Apparel", "Beauty", "Health", "Education", "Food", "Other"]

        #the actual comboboxes
        self.combo_year = ttk.Combobox(self.frame, state = "readonly", 
                            values = self.year_filters, width = 10)
        self.combo_year.grid(row = 1, column = 1, padx = 10, pady = 10)
        self.combo_month = ttk.Combobox(self.frame, state = "readonly",
                                        values = self.month_filters, width = 10)
        self.combo_month.grid(row = 2, column = 1, padx = 10, pady = 10)
        self.combo_category = ttk.Combobox(self.frame, state = "readonly",
                                           values = self.category_filters, width = 10)
        self.combo_category.grid(row = 3, column = 1, padx = 10, pady = 10)
        
        #buttons
        self.alltime_button = ttk.Button(self.frame, text = "Of All Time", style = "2.TButton", command = self.all_time)
        self.alltime_button.grid(row = 4, column = 0, columnspan = 2, ipadx = 70, padx = 10)
        self.home_button = ttk.Button(self.frame, text = "Home", style = "2.TButton", command = self.close_windows)
        self.home_button.grid(row = 5, column = 0, columnspan = 4, ipadx = 400, padx = 10, pady = 10)


        #upon opening, the "of all time" graphs should be showing
        self.all_time()

        #makign sure that the appropriate functions are called when the combobox expriences a change
        self.combo_year.bind("<<ComboboxSelected>>", self.window_year)
        self.combo_month.bind("<<ComboboxSelected>>", self.window_month)
        self.combo_category.bind("<<ComboboxSelected>>", self.window_category)

    def window_year(self, event):
        #getting the chosen year from the combobox
        self.year = self.combo_year.get()

        #categorical spending in that year
        #initialisign all the variables
        self.household = 0
        self.apparel = 0
        self.beauty = 0
        self.health = 0
        self.education = 0
        self.food = 0
        self.other = 0

        #querying for all the different categories
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Household' AND Date LIKE '" + str(self.year) + "%'"):
            self.household += i[-1]     
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Apparel' AND Date LIKE '" + str(self.year) + "%'"):
            self.apparel += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Beauty' AND Date LIKE '" + str(self.year) + "%'"):
            self.beauty += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Health' AND Date LIKE '" + str(self.year) + "%'"):
            self.health += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Education' AND Date LIKE '" + str(self.year) + "%'"):
            self.education += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Food' AND Date LIKE '" + str(self.year) + "%'"):
            self.food += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Other' AND Date LIKE '" + str(self.year) + "%'"):
            self.other += i[-1]
     
        fig = matplotlib.figure.Figure(figsize = (5, 3), dpi = 80)
        ax = fig.add_subplot(111)
        x_labels = ['Household', 'Apparel', 'Beauty', 'Health', 'Education', 'Food', 'Others']
        y_labels = [self.household, self.apparel, self.beauty, self.health, self.education, self.food, self.other]
        colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'lightgreen', 'pink', 'orange']
        ax.pie(y_labels, labels = x_labels, startangle = 90, shadow = True,
               colors = colors, radius = 1.2)
        fig.patch.set_facecolor("#454545")

        canvas = FigureCanvasTkAgg(fig, master = self.frame)
        canvas.get_tk_widget().grid(row = 3, column = 2, rowspan = 2, padx = 10, pady = 10)
        canvas.draw()

        #money spent throughout the year
        self.cur.execute("SELECT Date, Cost FROM purchases WHERE Date LIKE '" + str(self.year) + "%'")
        self.dates = []
        self.costs = []
        self.rows = self.cur.fetchall()
        for row in self.rows:
            self.dates.append(datetime.strptime(row[0], '%Y-%m-%d'))
            self.costs.append(row[1])
            
        self.new_data = list(zip(self.dates, self.costs))
        self.new_data.sort()
        self.new_data = np.array(self.new_data)

        #the plotting
        self.fig = matplotlib.figure.Figure(figsize = (12, 4), dpi = 80)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(self.new_data[:,0], self.new_data[:,1])
        self.fig.patch.set_facecolor("#454545")

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 1, column = 2, columnspan = 2, rowspan = 2, padx = 10, pady = 10)
        self.canvas.draw()

        #monthly spendings
        self.jan = 0
        self.feb = 0
        self.mar = 0
        self.apr = 0
        self.may = 0
        self.jun = 0
        self.july = 0
        self.aug = 0
        self.sept = 0
        self.oct = 0
        self.nov = 0
        self.dec = 0
            
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_01%'"):
            self.jan += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_02%'"):
            self.feb += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_03%'"):
            self.mar += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_04%'"):
            self.apr += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_05%'"):
            self.may += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_06%'"):
            self.jun += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_07%'"):
            self.july += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_08%'"):
            self.aug += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_09%'"):
            self.sept += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_10%'"):
            self.oct += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_11%'"):
            self.nov += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.year) + "_12%'"):
            self.dec += i[-1]

        x_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "July", "Aug", "Sept", "Oct", "Nov", "Dec"]
        y_labels = [self.jan, self.feb, self.mar, self.apr, self.may, self.jun, self.july,\
                    self.aug, self.sept, self.oct, self.nov, self.dec]

        fig = matplotlib.figure.Figure(figsize = (6, 3), dpi = 65)
        ax = fig.add_subplot(111)
        ax.bar(x_labels, y_labels)
        ax.set_title('Monthly Money Spent')
        fig.patch.set_facecolor("#454545")

        canvas = FigureCanvasTkAgg(fig, master = self.frame)
        canvas.get_tk_widget().grid(row = 3, column = 3, rowspan = 2, padx = 10, pady = 10)
        canvas.draw()
        
    def window_month(self, event):
        try:
            #getting the date from the comboboxes
            self.month = self.combo_month.get()
            self.month_number = datetime.strptime(self.month, "%b").month
            if (0 < self.month_number < 10):
                self.month_number = "0" + str(self.month_number)
            self.date = str(self.combo_year.get()) + "-" + str(self.month_number)
            
            #over all of the time in that month spendings
            self.cur.execute("SELECT Date, Cost FROM purchases WHERE Date LIKE '" + str(self.date) + "%'")
            self.dates = []
            self.costs = []
            self.rows = self.cur.fetchall()
            for row in self.rows:
                self.dates.append(datetime.strptime(row[0], '%Y-%m-%d'))
                self.costs.append(row[1])
                
            self.new_data = list(zip(self.dates, self.costs))
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

            self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
            self.canvas.get_tk_widget().grid(row = 1, column = 2, columnspan = 2, rowspan = 2, padx = 10, pady = 10)
            self.canvas.draw()

            #categorical spendigns in that month
            #initialisign all the variables
            self.household = 0
            self.apparel = 0
            self.beauty = 0
            self.health = 0
            self.education = 0
            self.food = 0
            self.other = 0

            #querying for all the different categories
            for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Household' AND Date LIKE '" + str(self.date) + "%'"):
                self.household += i[-1]     
            for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Apparel' AND Date LIKE '" + str(self.date) + "%'"):
                self.apparel += i[-1]
            for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Beauty' AND Date LIKE '" + str(self.date) + "%'"):
                self.beauty += i[-1]
            for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Health' AND Date LIKE '" + str(self.date) + "%'"):
                self.health += i[-1]
            for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Education' AND Date LIKE '" + str(self.date) + "%'"):
                self.education += i[-1]
            for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Food' AND Date LIKE '" + str(self.date) + "%'"):
                self.food += i[-1]
            for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Other' AND Date LIKE '" + str(self.date) + "%'"):
                self.other += i[-1]
         
            fig = matplotlib.figure.Figure(figsize = (5, 3), dpi = 80)
            ax = fig.add_subplot(111)
            x_labels = ['Household', 'Apparel', 'Beauty', 'Health', 'Education', 'Food', 'Others']
            y_labels = [self.household, self.apparel, self.beauty, self.health, self.education, self.food, self.other]
            colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'lightgreen', 'pink', 'orange']
            ax.pie(y_labels, labels = x_labels, startangle = 90, shadow = True,
                   colors = colors, radius = 1.2)
            fig.patch.set_facecolor("#454545")

            canvas = FigureCanvasTkAgg(fig, master = self.frame)
            canvas.get_tk_widget().grid(row = 3, column = 2, rowspan = 2, padx = 10, pady = 10)
            canvas.draw()

            #monthly savings in that month
            self.budget = 0
            for i in self.cur.execute("SELECT Budget FROM Budget WHERE Date LIKE '" + str(self.date) + "%'"):
                self.budget = round(i[-1], 2)
            self.savings = 0
            for i in self.cur.execute("SELECT Leftover FROM Analysis WHERE Date LIKE '" + str(self.date) + "%'"):
                self.savings = round(i[-1], 2)
            self.spent = round(self.budget - self.savings, 2)
            colors = ["#278EA5", "#1F4287"]

            #the plotting
            self.fig = matplotlib.figure.Figure(figsize = (5, 3), dpi = 80)
            self.ax = self.fig.add_subplot(111)
            self.ax.pie([self.spent, self.savings], colors = colors) 
            self.ax.legend(["spent: " + str(self.spent),"savings: " + str(self.savings)])

            self.circle = matplotlib.patches.Circle((0,0), 0.7, color = "#464646")
            self.ax.add_artist(self.circle)
            self.fig.patch.set_facecolor("#464646")
            
            self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
            self.canvas.get_tk_widget().grid(row = 3, column = 3, rowspan = 2, padx = 10, pady = 10)
            self.canvas.draw()

        except IndexError:
            self.label1 = ttk.Label(self.frame, text = "No Data Found", width = 100)
            self.label1.grid(row = 1, column = 2, columnspan = 2, rowspan = 4, ipady = 260)

    def window_category(self, event):
        try:
            #money spent in that month of that year in that category
            self.month = self.combo_month.get()
            self.month_number = datetime.strptime(self.month, "%b").month
            if (0 < self.month_number < 10):
                self.month_number = "0" + str(self.month_number)
            self.date = str(self.combo_year.get()) + "-" + str(self.month_number)
            self.category = self.combo_category.get()

            #total spent for the category in that year
            self.cur.execute("SELECT Date, Cost FROM purchases WHERE Date LIKE '" + str(self.date) + "%'AND Type = '" + self.combo_category.get() + "'")
            self.dates = []
            self.costs = []
            self.rows = self.cur.fetchall()
            for row in self.rows:
                self.dates.append(datetime.strptime(row[0], '%Y-%m-%d'))
                self.costs.append(row[1])
                
            self.new_data = list(zip(self.dates, self.costs))
            self.new_data.sort()
            self.new_data = np.array(self.new_data)

            #the plotting
            self.fig = matplotlib.figure.Figure(figsize = (12, 4), dpi = 80)
            self.ax = self.fig.add_subplot(111)
            self.ax.plot(self.new_data[:,0], self.new_data[:,1])

            for label in self.ax.get_xticklabels():
                label.set_rotation(13)
            self.fig.patch.set_facecolor("#454545")

            self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
            self.canvas.get_tk_widget().grid(row = 1, column = 2, columnspan = 2, rowspan = 2, padx = 10, pady = 10)
            self.canvas.draw()

            #two blank labels for the bottom two graphs
            self.label1 = ttk.Label(self.frame, text = "", width = 100)
            self.label1.grid(row = 3, column = 2, rowspan = 2, padx = 10, pady = 10, ipady = 100)
            self.label2 = ttk.Label(self.frame, text = "", width = 100)
            self.label2.grid(row = 3, column = 3, rowspan = 2, padx = 10, pady = 10, ipady = 100)
        except IndexError:
            self.label1 = ttk.Label(self.frame, text = "No Data Found", width = 100)
            self.label1.grid(row = 1, column = 2, columnspan = 2, rowspan = 4, ipady = 260)

    def all_time(self):
        #graph for purchases over all of time
        #all the needed data
        self.cur.execute("SELECT Date, Cost FROM purchases")
        self.dates = []
        self.costs = []
        self.rows = self.cur.fetchall()
        for row in self.rows:
            self.dates.append(datetime.strptime(row[0], '%Y-%m-%d'))
            self.costs.append(row[1])

        self.new_data = list(zip(self.dates, self.costs))
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

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 1, column = 2, columnspan = 2, rowspan = 2, padx = 10, pady = 10)
        self.canvas.draw()

        #graph for categorical spendings over all of time
        self.household = 0
        self.apparel = 0
        self.beauty = 0
        self.health = 0
        self.education = 0
        self.food = 0
        self.other = 0

        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Household'"):
            self.household += i[-1]     
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Apparel'"):
            self.apparel += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Beauty'"):
            self.beauty += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Health'"):
            self.health += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Education'"):
            self.education += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Food'"):
            self.food += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Type = 'Other'"):
            self.other += i[-1]
     
        fig = matplotlib.figure.Figure(figsize = (5, 3), dpi = 80)
        ax = fig.add_subplot(111)
        x_labels = ['Household', 'Apparel', 'Beauty', 'Health', 'Education', 'Food', 'Others']
        y_labels = [self.household, self.apparel, self.beauty, self.health, self.education, self.food, self.other]
        colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'lightgreen', 'pink', 'orange']
        explode_list = [0.1, 0, 0, 0, 0.1, 0.1, 0]
        ax.pie(y_labels, labels = x_labels, startangle = 90, shadow = True,
               colors = colors, radius = 1.2, explode = explode_list)
        fig.patch.set_facecolor("#454545")

        canvas = FigureCanvasTkAgg(fig, master = self.frame)
        canvas.get_tk_widget().grid(row = 3, column = 2, rowspan = 2, padx = 10, pady = 10)
        canvas.draw()

        #graph for yearly spendings
        self.current_year = int(datetime.date(datetime.now()).strftime("%Y"))
        self.prev1_year = int(self.current_year) - 1
        self.prev2_year = int(self.current_year) - 2
        self.prev3_year = int(self.current_year) - 3
        self.prev4_year = int(self.current_year) - 4
        self.data_current = 0
        self.data_prev1 = 0
        self.data_prev2 = 0
        self.data_prev3 = 0
        self.data_prev4 = 0

        
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.current_year) + "%'"):
            self.data_current += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.prev1_year) + "%'"):
            self.data_prev1 += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.prev2_year) + "%'"):
            self.data_prev2 += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.prev3_year) + "%'"):
            self.data_prev3 += i[-1]
        for i in self.cur.execute("SELECT Cost FROM Purchases WHERE Date LIKE '" + str(self.prev4_year) + "%'"):
            self.data_prev4 += i[-1]

        fig = matplotlib.figure.Figure(figsize = (6, 3), dpi = 65)
        ax = fig.add_subplot(111)
        x_labels = [self.current_year, self.prev1_year, self.prev2_year, self.prev3_year, self.prev4_year]
        y_labels = [self.data_current, self.data_prev1, self.data_prev2, self.data_prev3, self.data_prev4]

        ax.bar(x_labels, y_labels)
        ax.set_title('Money Spent')
        fig.patch.set_facecolor("#454545")

        canvas = FigureCanvasTkAgg(fig, master = self.frame)
        canvas.get_tk_widget().grid(row = 3, column = 3, rowspan = 2, padx = 10, pady = 10)
        canvas.draw()

        #clearing out all the other comboboxes
        self.combo_year.set("")
        self.combo_month.set("")
        self.combo_category.set("")
           
    def close_windows(self):
        self.master.destroy()






        

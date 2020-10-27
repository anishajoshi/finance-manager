from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedTk
import tkinter as tk
import tkinter.ttk as ttk
from tkcalendar import DateEntry
import datetime
from datetime import datetime

import sqlite3

class EditWindow:


    def __init__(self, master, conn, parent):

        #making a connection to the database
        self.conn = conn
        self.cur = self.conn.cursor()

        #intialising the window
        self.master = master
        self.parent = parent
        master.resizable(width = False, height = False)
        master.title("Editing")

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

        #variables
        self.old_item = self.parent.display_tree.item(self.parent.display_tree.selection())["values"][1]
        self.old_type = self.parent.display_tree.item(self.parent.display_tree.selection())["values"][2]
        self.old_cost = self.parent.display_tree.item(self.parent.display_tree.selection())["values"][3]
        self.old_date = self.parent.display_tree.item(self.parent.display_tree.selection())["values"][4]
        self.old_date = datetime.strptime(self.old_date, "%Y-%m-%d").strftime("%d/%m/%Y")

        #the components
        #all the labels
        self.label1 = ttk.Label(self.frame, text = "Item: ", style = "4.TLabel")
        self.label1.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = "w")
        self.label2 = ttk.Label(self.frame, text = "Type: ", style = "4.TLabel")
        self.label2.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = "w")
        self.label3 = ttk.Label(self.frame, text = "Cost: ", style = "4.TLabel")
        self.label3.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = "w")
        self.label4 = ttk.Label(self.frame, text = "Date: ", style = "4.TLabel")
        self.label4.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = "w")

        #all the inputs - been populated
        self.item_text = tk.StringVar(value = self.old_item)
        self.entry_item = ttk.Entry(self.frame, textvariable = self.item_text)
        self.entry_item.grid(row = 0, column = 1)
        self.type_text = tk.StringVar(value = self.old_type)
        self.combo_type =  ttk.Combobox(self.frame, textvariable = self.type_text, state = "readonly", 
                            values=[
                                    "Household", 
                                    "Apparel",
                                    "Beauty",
                                    "Health",
                                    "Education",
                                    "Food",
                                    "Other"], width = 18)
        self.combo_type.grid(row = 1, column = 1)
        self.cost_text = tk.StringVar(value = self.old_cost)
        self.entry_cost = ttk.Entry(self.frame, textvariable = self.cost_text)
        self.entry_cost.grid(row = 2, column = 1)
        self.cal = DateEntry(self.frame, width = 18, background = "darkblue",
                             foreground = "white", borderwidth = 2, state = "readonly")
        self.cal.grid(row = 3, column = 1)
        self.cal.set_date(self.old_date)
        self.cal._top_cal.overrideredirect(False)
        self.save_button = ttk.Button(self.frame, text = "Save", style = "2.TButton",
                                      command = self.save_data, width = 18)
        self.save_button.grid(row = 4, column = 1, padx = 10, pady = 10)
        self.back_button = ttk.Button(self.frame, text = "⤶", style = "3.TButton",
                                      command = self.close_windows, width = 13)
        self.back_button.grid(row = 4, column = 0, padx = 10)

    def close_windows(self):
        self.master.destroy()

    def save_data(self):
        if not self.cost_text.get() or not self.item_text.get() or not self.combo_type.get():
            messagebox.showwarning("Error", "You have to fill in all the details")
        else:
            self.date = self.cal.get_date()
            self.date = str(self.date)[:7]
            for selected_item in self.parent.display_tree.selection():
                #update the Analysis table first
                self.leftover_money = 0
                for money in self.cur.execute("SELECT Leftover FROM Analysis WHERE Date = '" + self.date + "'"):
                    self.leftover_money = money[-1]
                self.new_leftover_money = self.leftover_money - (int(self.cost_text.get()) - self.old_cost)
                
                self.item_date = self.cal.get_date().strftime("%Y-%m")
                self.cur.execute("UPDATE Analysis SET Leftover = ? WHERE Date = ?",
                                 (self.new_leftover_money,
                                 self.item_date))

                #update the purchases table
                self.cur.execute("UPDATE purchases SET Item = ?, Type = ?, Cost = ?, Date = ? WHERE id = ?",
                                 (self.item_text.get(),
                                  self.type_text.get(),
                                  self.cost_text.get(),
                                  str(self.cal.get_date()),
                                  self.parent.display_tree.set(selected_item, '#1'),))
                self.conn.commit()
                self.parent.refresh()
                self.master.destroy()
        
        
        
        



        

        

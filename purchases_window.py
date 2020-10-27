from tkinter import ttk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

import sqlite3

from insert_window import InsertWindow
from edit_window import EditWindow
       
class PurchasesWindow:
    

    def __init__(self, master, conn):
        #making a connection to the database
        self.conn = conn

        #creating a cursor object
        self.cur = self.conn.cursor()    

        #intialising the window
        self.master = master
        self.master.resizable(width = False, height = False)
        self.master.title("Purchases Window")

        #centering the window
        self.width = 670
        self.height = 340
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        self.xcor = (self.screen_width / 2) - (self.width / 2)
        self.ycor = (self.screen_height / 2) - (self.height / 2)
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
        self.frame.rowconfigure(5, weight = 1)
        self.frame.columnconfigure(0, weight = 6, uniform = "uniform")
        self.frame.columnconfigure(1, weight = 2, uniform = "uniform")

        #styles
        self.style = ttk.Style()
        self.style.configure("1.TLabel", font = ("Open Sans", 24, "bold"), foreground = "#EDF6F9")
        self.style.configure("2.TButton", font = ("Open Sans", 14, "bold"), foreground = "#EDF6F9")
        
        #the components
        #heading label
        self.label_heading = ttk.Label(self.frame, text = "Your Purchases", style = "1.TLabel")
        self.label_heading.grid(row = 0, column = 0, columnspan = 3, pady = (10, 0))

        #making the table for the purchases
        self.display_tree = ttk.Treeview(self.frame,
                                         column = ("column1", "column2", "column3", "column4", "column5"),
                                         show = "headings")
        self.display_tree.heading("#1", text = "Id")
        self.display_tree.column("column1", minwidth = 0, width = 80, stretch = False, anchor = "c")
        self.display_tree.heading("#2", text = "Item")
        self.display_tree.column("column2", minwidth = 0, width = 100, stretch = False, anchor = "c")
        self.display_tree.heading("#3", text = "Type")
        self.display_tree.column("column3", minwidth = 0, width = 100, stretch = False, anchor = "c")
        self.display_tree.heading("#4", text = "Cost")
        self.display_tree.column("column4", minwidth = 0, width = 100, stretch = False, anchor = "c")
        self.display_tree.heading("#5", text = "Date")
        self.display_tree.column("column5", minwidth = 0, width = 100, stretch = False, anchor = "c")
        self.display_tree.grid(row = 1, rowspan = 4, column = 0, padx = (20, 0))


        #buttons
        self.insert_button = ttk.Button(self.frame, text = "Insert",
                                        command = self.insert_open, style = "2.TButton")
        self.insert_button.grid(row = 1, column = 1, pady = 5)
        self.delete_button = ttk.Button(self.frame, text = "Delete",
                                        command = self.delete, style = "2.TButton")
        self.delete_button.grid(row = 2, column = 1, pady = 5)
        self.edit_button = ttk.Button(self.frame, text = "Edit",
                                      command = self.edit_open, style = "2.TButton")
        self.edit_button.grid(row = 3, column = 1, pady = 5)
        self.home_button = ttk.Button(self.frame, text = "Home",
                                      command = self.close_windows, style = "2.TButton")
        self.home_button.grid(row = 4, column = 1, pady = (5, 0))

        #calling the needed functions
        self.refresh() 
    
    def close_windows(self):
        self.master.destroy()

    def insert_open(self):
        InsertWindow(tk.Toplevel(self.master), self.conn, self)

    def delete(self):
        if  self.display_tree.selection(): #whether an item has been selected
            for selected_item in self.display_tree.selection():

                #getting the cost to subtract from Analysis first before deleting the item
                self.item_cost = self.cur.execute("SELECT Cost FROM Purchases WHERE id = ?",
                                                  (self.display_tree.set(selected_item, "#1"),))
                for i in self.item_cost:
                    self.item_cost = i[-1]
   
                self.item_date = self.cur.execute("SELECT Date FROM Purchases WHERE id = ?",
                                                  (self.display_tree.set(selected_item, "#1"),))
                for j in self.item_date:
                    self.item_date = j[-1][:7]
                    
                self.current_leftover_money = self.cur.execute("SELECT Leftover FROM Analysis").fetchall()[-1][-1]

                self.cur.execute("UPDATE Analysis SET Leftover = ? WHERE Date = ?",
                                  (self.current_leftover_money + self.item_cost,
                                   self.item_date))

                #deleting the selected item from the database - purchases table
                self.cur.execute("DELETE FROM purchases WHERE id = ?",
                                 (self.display_tree.set(selected_item, "#1"),))

                self.conn.commit()
                self.display_tree.delete(selected_item) #deleting it from the treeview on the application
        else:
            messagebox.showwarning("Error", "You have to select an item!")

    def edit_open(self):
        if  self.display_tree.selection(): #whether an item has been selected
            EditWindow(tk.Toplevel(self.master), self.conn, self)
        else:
            messagebox.showwarning("Error", "You have to select an item!")      

    def refresh(self):
        self.records = self.display_tree.get_children()
        for i in self.records:
            self.display_tree.delete(i)
        self.cur.execute("SELECT * FROM purchases")
        self.rows = self.cur.fetchall()
        for row in self.rows:
            self.display_tree.insert("", tk.END, values = row)

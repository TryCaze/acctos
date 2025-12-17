import tkinter as tk
from tkinter import ttk
from database import Database
from kategorije.kategorijeTab import *
from racuni import createAccountsTab
from transakcije import createTransactionsTab
from zalihe.zaliheTab import createInventoryTab

db = Database("acctos.db")

root = tk.Tk()
root.title("ACCTOS")
root.geometry("1400x800")

# Menubar
menubar = tk.Menu(root)
file = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='File', menu = file)
file.add_command(label ='New File', command = None)
file.add_command(label ='Open...', command = None)
file.add_command(label ='Save', command = None)
file.add_separator()
file.add_command(label ='Exit', command = root.destroy)

edit = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='Edit', menu = edit)
edit.add_command(label ='Cut', command = None)
edit.add_command(label ='Copy', command = None)
edit.add_command(label ='Paste', command = None)
edit.add_command(label ='Select All', command = None)
edit.add_separator()
edit.add_command(label ='Find...', command = None)
edit.add_command(label ='Find again', command = None)

help_ = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='Help', menu = help_)
help_.add_command(label ='Tk Help', command = None)
help_.add_command(label ='Demo', command = None)
help_.add_separator()
help_.add_command(label ='About Tk', command = None)

root.config(menu=menubar)

# Create Notebook
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Add tabs

# RACUNI
accountsTab = createAccountsTab(notebook, db.cursor, db.conn)
notebook.add(accountsTab, text="Računi")

# TRANSAKCIJE
transactionsTab = createTransactionsTab(notebook, db.cursor, db.conn)
notebook.add(transactionsTab, text="Transakcije")

# KATEGORIJE
categoriesTab = createCategoriesTab(notebook, db.cursor, db.conn)
notebook.add(categoriesTab, text="Kategorije")

# ZALIHE
inventoryTab = createInventoryTab(notebook, db.cursor, db.conn)
notebook.add(inventoryTab, text="Zalihe")

# IZVJESTAJI
reportsTab = ttk.Frame(notebook)
notebook.add(reportsTab, text="Izvještaji")
ttk.Label(reportsTab, text="Izvještaji - U izradi", font=("Arial", 14)).pack(pady=50)

# Status bar
statusBar = ttk.Label(root, text="Spremno", relief=tk.SUNKEN, anchor=tk.W)
statusBar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
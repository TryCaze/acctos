import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from .racuni import accountsTable, refreshAccountsTable as refreshAccTable, openEditAccountForm
from .racuniForm import addAccountForm

def createAccountsTab(parent, cursor, conn):
    frame = ttk.Frame(parent)

    btnFrame = ttk.Frame(frame, padding=10)
    btnFrame.pack(fill="x")
    
    #def refreshTables():
    #    refreshAccTable(accountsTreeTable, cursor)
    #
    #def onAccountSelected(tree):
    #    selected_items = tree.selection()
    #    if not selected_items:
    #        return
    #    
    #    selected_item = selected_items[0]
    #    account_id = tree.item(selected_item)["values"][0]
    #    openEditAccountForm(frame, cursor, conn, account_id, refreshCallback=refreshTables)
    
    split = ttk.PanedWindow(frame, orient="horizontal")
    split.pack(fill="both", expand=True, padx=10, pady=10)

    leftFrame = ttk.Frame(split)
    split.add(leftFrame, weight=1)

    categoryTree = ttk.Treeview(leftFrame, columns=("Naziv", "Vrsta"), show="headings", height=20)
    categoryTree.heading("Naziv", text="Naziv")
    categoryTree.heading("Vrsta", text="Vrsta")

    categoryTree.column("Naziv", width=180)
    categoryTree.column("Vrsta", width=70, anchor="center")

    scrollLeft = ttk.Scrollbar(leftFrame, orient="vertical", command=categoryTree.yview)
    categoryTree.configure(yscrollcommand=scrollLeft.set)

    categoryTree.pack(side="left", fill="both", expand=True)
    scrollLeft.pack(side="right", fill="y")

    rightFrame = ttk.LabelFrame(split, text="Detalji kategorije", padding=10)
    split.add(rightFrame, weight=3)

    lblName = ttk.Label(rightFrame, text="Naziv: ")
    lblName.pack(anchor="w", pady=3)

    lblType = ttk.Label(rightFrame, text="Vrsta: ")
    lblType.pack(anchor="w", pady=3)

    lblType = ttk.Label(rightFrame, text="Vrsta: ")
    lblType.pack(anchor="w", pady=3)

    ttk.Label(rightFrame, text="Opis:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
    txtOpis = tk.Text(rightFrame, width=50, height=6, wrap="word", state="disabled")
    txtOpis.pack(fill="x")

    detailsBtnFrame = ttk.Frame(rightFrame)
    detailsBtnFrame.pack(anchor="w", pady=10)

    btnEdit = ttk.Button(detailsBtnFrame, text="Uredi", command=lambda: onEditAccount(selectedId.get()))
    btnEdit.grid(row=0, column=0, padx=5)

    selectedId = tk.IntVar(value=0)

    # Accounts tab content
    #accountsBtnFrame = ttk.Frame(frame, padding=10)
    #accountsBtnFrame.pack(fill="x")
    #
    #ttk.Button(accountsBtnFrame, text="Dodajte novi račun", 
    #          command=lambda: addAccountForm(frame, cursor, conn, refreshCallback=refreshTables)).pack(side="left")
    #
    #ttk.Button(accountsBtnFrame, text="Osvježi", command=refreshTables).pack(side="left", padx=5)
    #
    #accountsTreeFrame = ttk.Frame(frame)
    #accountsTreeFrame.pack(fill="both", expand=True, padx=10, pady=10)
    #
    #accountsTreeTable = accountsTable(accountsTreeFrame, cursor, onSelectCallback=onAccountSelected)
    #
    #accountsScrollbar = ttk.Scrollbar(accountsTreeFrame, orient="vertical", command=accountsTreeTable.yview)
    #accountsTreeTable.configure(yscrollcommand=accountsScrollbar.set)
    #accountsScrollbar.pack(side="right", fill="y")
    #accountsTreeTable.pack(side="left", fill="both", expand=True)
    #
    #instructionLabel = ttk.Label(frame, text="Kliknite na račun u tablici za uređivanje", font=("Arial", 10))
    #instructionLabel.pack(pady=5)
    
    #refreshTables()
    
    #return frame

    accountCache = []
    accountCounts = {}
    
    def refreshAccounts():
        from .racuni import getAllAccounts

        for item in categoryTree.get_children():
            categoryTree.delete(item)

        accounts = getAllAccounts(cursor)
        accountCache.clear()
        accountCache.extend(accounts)
        
        accountCounts.clear()
        for row in cursor.fetchall():
            accountCounts[row['id']] = row['count']

        for account in accounts:
            categoryTree.insert("", "end", values=(account['naziv'], account['vrsta'].capitalize()), iid=str(account['id']))

        clearDetails()

    def clearDetails():
        selectedId.set(0)
        lblName.config(text="Naziv:")
        lblType.config(text="Vrsta:")
        txtOpis.config(state="normal")
        txtOpis.delete("1.0", "end")
        txtOpis.config(state="disabled")

    def showDetails(catId):
        if not catId:
            return
        cat = next((c for c in accountCache if c['id'] == catId), None)
        if not cat:
            return
        
        selectedId.set(catId)

        lblName.config(text=f"Naziv: {cat['naziv']}")
        lblType.config(text=f"Vrsta: {cat['vrsta'].capitalize()}")
        
        txtOpis.config(state="normal")
        txtOpis.delete("1.0", "end")
        txtOpis.insert("1.0", cat['biljeska'] or "")
        txtOpis.config(state="disabled")

    def onAddAccount():
        addAccountForm(frame, cursor, conn, refreshCallback=refreshAccounts)

    def onEditAccount(catId=None):
        if not catId:
            messagebox.showwarning("Upozorenje", "Odaberite kategoriju!")
            return
        openEditAccountForm(frame, cursor, conn, catId, refreshCallback=refreshAccounts)

    def onDeleteAccount(catId=None):
        if not catId:
            messagebox.showwarning("Upozorenje", "Odaberite kategoriju!")
            return
        
        cat = next((c for c in accountCache if c['id'] == catId), None)
        if not cat:
            return
        
        if not messagebox.askyesno("Potvrdite", f"Obrisati kategoriju '{cat['ime']}'?"):
            return
        
        from .racuni import onDeleteAccount
        success, msg = onDeleteAccount(cursor, conn, catId)

        if success:
            messagebox.showinfo("Uspjeh", msg)
            refreshAccounts()
        else:
            messagebox.showwarning("Upozorenje", msg)

    def onSelect(event):
        item = categoryTree.selection()
        if not item:
            clearDetails()
            return
        catId = int(item[0])
        showDetails(catId)

    categoryTree.bind("<<TreeviewSelect>>", onSelect)

    ttk.Button(btnFrame, text="Nova Kategorija", command=lambda: onAddAccount()).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Osvježi", command=lambda: refreshAccounts()).pack(side="left", padx=5)

    refreshAccounts()

    return frame

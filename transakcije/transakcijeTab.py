import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from .transakcijeForm import addTransactionForm, editTransactionForm

def createTransactionsTab(parent, cursor, conn):
    frame = ttk.Frame(parent)
    
    # Store references
    current_filters = {}
    
    filterBar = ttk.LabelFrame(frame, text="Filteri", padding=10)
    filterBar.pack(fill="x", padx=10, pady=5)
    
    # Date filter
    ttk.Label(filterBar, text="Datum:").grid(row=0, column=0, padx=5)
    startDateVar = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    endDateVar = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    
    ttk.Label(filterBar, text="Od:").grid(row=0, column=1, padx=2)
    startDateEntry = ttk.Entry(filterBar, textvariable=startDateVar, width=12)
    startDateEntry.grid(row=0, column=2, padx=2)
    
    ttk.Label(filterBar, text="Do:").grid(row=0, column=3, padx=2)
    endDateEntry = ttk.Entry(filterBar, textvariable=endDateVar, width=12)
    endDateEntry.grid(row=0, column=4, padx=2)
    
    # Type filter
    ttk.Label(filterBar, text="Vrsta:").grid(row=0, column=5, padx=5)
    typeVar = tk.StringVar(value="sve")
    typeCombo = ttk.Combobox(filterBar, textvariable=typeVar, values=["sve", "prihod", "rashod"], width=10, state="readonly")
    typeCombo.grid(row=0, column=6, padx=2)
    
    # Account filter
    ttk.Label(filterBar, text="Račun:").grid(row=0, column=7, padx=5)
    accountVar = tk.StringVar(value="svi")
    accountCombo = ttk.Combobox(filterBar, textvariable=accountVar, width=15, state="readonly")
    accountCombo.grid(row=0, column=8, padx=2)
    
    # Category filter
    ttk.Label(filterBar, text="Kategorija:").grid(row=0, column=9, padx=5)
    categoryVar = tk.StringVar(value="sve")
    categoryCombo = ttk.Combobox(filterBar, textvariable=categoryVar, width=15, state="readonly")
    categoryCombo.grid(row=0, column=10, padx=2)
    
    # Reconciliation filter
    ttk.Label(filterBar, text="Uskladeno:").grid(row=0, column=11, padx=5)
    reconVar = tk.StringVar(value="sve")
    reconCombo = ttk.Combobox(filterBar, textvariable=reconVar, values=["sve", "da", "ne"], width=8, state="readonly")
    reconCombo.grid(row=0, column=12, padx=2)
    
    # Filter buttons
    ttk.Button(filterBar, text="Primijeni", command=lambda: applyFilters()).grid(row=0, column=13, padx=10)
    ttk.Button(filterBar, text="Resetiraj", command=lambda: resetFilters()).grid(row=0, column=14, padx=5)
    
    btnFrame = ttk.Frame(frame, padding=10)
    btnFrame.pack(fill="x")
    
    treeFrame = ttk.Frame(frame)
    treeFrame.pack(fill="both", expand=True, padx=10, pady=10)
    
    tree = ttk.Treeview(treeFrame, columns=("ID", "Datum", "Račun", "Opis", "Dobavljač", "Iznos", "Vrsta", "Uskladeno"), show="headings")
    
    tree.heading("ID", text="ID")
    tree.heading("Datum", text="Datum")
    tree.heading("Račun", text="Račun")
    tree.heading("Opis", text="Opis")
    tree.heading("Dobavljač", text="Dobavljač/Klijent")
    tree.heading("Iznos", text="Iznos")
    tree.heading("Vrsta", text="Vrsta")
    tree.heading("Uskladeno", text="Uskladeno")
    
    tree.column("ID", width=50)
    tree.column("Datum", width=90)
    tree.column("Račun", width=120)
    tree.column("Opis", width=200)
    tree.column("Dobavljač", width=150)
    tree.column("Iznos", width=100)
    tree.column("Vrsta", width=80)
    tree.column("Uskladeno", width=80)
    
    summaryFrame = ttk.Frame(frame, padding=10)
    summaryFrame.pack(fill="x", padx=10, pady=5)
    
    totalPrihodLabel = ttk.Label(summaryFrame, text="Ukupni Prihodi: 0.00")
    totalPrihodLabel.pack(side="left", padx=20)
    
    totalRashodLabel = ttk.Label(summaryFrame, text="Ukupni Rashodi: 0.00")
    totalRashodLabel.pack(side="left", padx=20)
    
    netoLabel = ttk.Label(summaryFrame, text="Neto: 0.00", font=("Arial", 10, "bold"))
    netoLabel.pack(side="left", padx=20)
    
    countLabel = ttk.Label(summaryFrame, text="Broj transakcija: 0")
    countLabel.pack(side="left", padx=20)
    
    def loadFilterOptions():
        # Load accounts
        cursor.execute("SELECT id, naziv FROM ACCTOSRACUNI ORDER BY naziv")
        accounts = cursor.fetchall()
        account_options = ["svi"]
        for acc in accounts:
            account_options.append(acc['naziv'])
        accountCombo['values'] = account_options
        accountCombo.set("svi")
        
        # Load categories
        cursor.execute("SELECT id, ime FROM ACCTOSKATEGORIJE ORDER BY ime")
        categories = cursor.fetchall()
        category_options = ["sve"]
        for cat in categories:
            category_options.append(cat['ime'])
        categoryCombo['values'] = category_options
        categoryCombo.set("sve")
    
    def applyFilters():
        filters = {}
        
        # Date range
        if startDateVar.get().strip():
            filters['start_date'] = startDateVar.get().strip()
        if endDateVar.get().strip():
            filters['end_date'] = endDateVar.get().strip()
        
        # Transaction type
        if typeVar.get() != "sve":
            filters['vrsta'] = typeVar.get()
        
        # Account
        if accountCombo.get() != "svi":
            cursor.execute("SELECT id FROM ACCTOSRACUNI WHERE naziv = ?", (accountCombo.get(),))
            acc = cursor.fetchone()
            if acc:
                filters['racunId'] = acc['id']
        
        # Category
        if categoryCombo.get() != "sve":
            cursor.execute("SELECT id FROM ACCTOSKATEGORIJE WHERE ime = ?", (categoryCombo.get(),))
            cat = cursor.fetchone()
            if cat:
                filters['kategorijaId'] = cat['id']
        
        # Reconciliation
        if reconVar.get() == "da":
            filters['uskladeno'] = 1
        elif reconVar.get() == "ne":
            filters['uskladeno'] = 0
        
        # Store and refresh
        current_filters.clear()
        current_filters.update(filters)
        refreshTransactions()
    
    def resetFilters():
        startDateVar.set((datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        endDateVar.set(datetime.now().strftime("%Y-%m-%d"))
        typeVar.set("sve")
        accountCombo.set("svi")
        categoryCombo.set("sve")
        reconVar.set("sve")
        
        current_filters.clear()
        refreshTransactions()
    
    def refreshTransactions():
        from .transakcije import getAllTransactions, getTransactionSummary
        
        # Clear tree
        for item in tree.get_children():
            tree.delete(item)
        
        # Get transactions
        transactions = getAllTransactions(cursor, current_filters)
        
        # Populate tree
        for trans in transactions:
            uskladeno_text = "✓" if trans['uskladeno'] else "✗"
            iznos_text = f"{trans['iznos']:.2f}"
            
            # Color code based on type
            tags = ('prihod',) if trans['vrsta'] == 'prihod' else ('rashod',)
            
            tree.insert("", "end", values=(
                trans['id'],
                trans['datum'],
                trans['racunNaziv'] or "",
                (trans['opis'] or "")[:30],
                (trans['dobavljacKlijent'] or "")[:20],
                iznos_text,
                trans['vrsta'].capitalize(),
                uskladeno_text
            ), tags=tags)
        
        # Configure tags for coloring
        tree.tag_configure('prihod', foreground='green')
        tree.tag_configure('rashod', foreground='red')
        
        # Update summary
        summary = getTransactionSummary(cursor, current_filters)
        totalPrihodLabel.config(text=f"Ukupni Prihodi: {summary['total_prihod']:.2f}")
        totalRashodLabel.config(text=f"Ukupni Rashodi: {summary['total_rashod']:.2f}")
        countLabel.config(text=f"Broj transakcija: {summary['count']}")
        
        neto_color = "green" if summary['neto'] >= 0 else "red"
        netoLabel.config(
            text=f"Neto: {summary['neto']:.2f}", 
            foreground=neto_color
        )
    
    def onAddTransaction():
        addTransactionForm(frame, cursor, conn, refreshCallback=refreshTransactions)
    
    def onEditTransaction():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Upozorenje", "Odaberite transakciju za uređivanje!")
            return
        
        selected_item = selected_items[0]
        trans_id = tree.item(selected_item)["values"][0]
        
        editTransactionForm(frame, cursor, conn, trans_id, refreshCallback=refreshTransactions)
    
    def onDeleteTransaction():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Upozorenje", "Odaberite transakciju za brisanje!")
            return
        
        if not messagebox.askyesno("Potvrdite", "Jeste li sigurni da želite izbrisati ovu transakciju?"):
            return
        
        selected_item = selected_items[0]
        trans_id = tree.item(selected_item)["values"][0]
        
        from .transakcije import deleteTransaction
        if deleteTransaction(cursor, conn, trans_id):
            messagebox.showinfo("Uspjeh", "Transakcija izbrisana!")
            refreshTransactions()
        else:
            messagebox.showerror("Greška", "Nije moguće izbrisati transakciju!")
    
    def onToggleReconciliation():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Upozorenje", "Odaberite transakciju!")
            return
        
        selected_item = selected_items[0]
        trans_id = tree.item(selected_item)["values"][0]
        
        from .transakcije import toggleReconciliation
        if toggleReconciliation(cursor, conn, trans_id):
            refreshTransactions()
        else:
            messagebox.showerror("Greška", "Nije moguće promijeniti status usklađenja!")
    
    def onExport():
        from .transakcije import getAllTransactions
        import csv
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            transactions = getAllTransactions(cursor, current_filters)
            if transactions:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['ID', 'Datum', 'Račun', 'Opis', 'Dobavljač', 'Iznos', 'Vrsta', 'Uskladeno']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for trans in transactions:
                        writer.writerow({
                            'ID': trans['id'],
                            'Datum': trans['datum'],
                            'Račun': trans['racunNaziv'] or '',
                            'Opis': trans['opis'] or '',
                            'Dobavljač': trans['dobavljačKlijent'] or '',
                            'Iznos': trans['iznos'],
                            'Vrsta': trans['vrsta'],
                            'Uskladeno': 'Da' if trans['uskladeno'] else 'Ne'
                        })
                
                messagebox.showinfo("Uspjeh", f"Transakcije izvezene u: {file_path}")
    
    ttk.Button(btnFrame, text="Nova Transakcija", command=onAddTransaction).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Uredi", command=onEditTransaction).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Izbriši", command=onDeleteTransaction).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Uskladi/Odskladi", command=onToggleReconciliation).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Izvezi CSV", command=onExport).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Osvježi", command=refreshTransactions).pack(side="left", padx=5)
    
    scrollbar = ttk.Scrollbar(treeFrame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)
    
    # Double-click to edit
    def onDoubleClick(event):
        selected_items = tree.selection()
        if selected_items:
            onEditTransaction()
    
    tree.bind('<Double-Button-1>', onDoubleClick)
    
    loadFilterOptions()
    refreshTransactions()
    
    return frame
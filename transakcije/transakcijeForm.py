import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from integration import linkTransactionToInventory

def addTransactionForm(parent, cursor, conn, refreshCallback=None):
    window = tk.Toplevel(parent)
    window.title("Nova Transakcija")
    window.geometry("500x600")
    
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill="both", expand=True)
    
    # Transaction Type
    ttk.Label(frame, text="Vrsta Transakcije:*").grid(row=0, column=0, sticky="w", pady=5)
    vrstaVar = tk.StringVar(value="rashod")
    ttk.Radiobutton(frame, text="Rashod", variable=vrstaVar, value="rashod").grid(row=0, column=1, sticky="w", padx=5)
    ttk.Radiobutton(frame, text="Prihod", variable=vrstaVar, value="prihod").grid(row=0, column=2, sticky="w", padx=5)
    
    # Date
    ttk.Label(frame, text="Datum:*").grid(row=1, column=0, sticky="w", pady=5)
    datumEntry = ttk.Entry(frame, width=30)
    datumEntry.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)
    datumEntry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    # Amount
    ttk.Label(frame, text="Iznos:*").grid(row=2, column=0, sticky="w", pady=5)
    iznosEntry = ttk.Entry(frame, width=30)
    iznosEntry.grid(row=2, column=1, columnspan=2, sticky="w", pady=5)
    
    # Account
    ttk.Label(frame, text="Račun:*").grid(row=3, column=0, sticky="w", pady=5)
    accountCombo = ttk.Combobox(frame, width=28, state="readonly")
    accountCombo.grid(row=3, column=1, columnspan=2, sticky="w", pady=5)
    
    # Load accounts
    cursor.execute("SELECT id, naziv FROM ACCTOSRACUNI ORDER BY naziv")
    accounts = cursor.fetchall()
    accountDict = {acc['naziv']: acc['id'] for acc in accounts}
    accountCombo['values'] = list(accountDict.keys())
    if accounts:
        accountCombo.set(accounts[0]['naziv'])
    
    # Category
    ttk.Label(frame, text="Kategorija:").grid(row=4, column=0, sticky="w", pady=5)
    categoryCombo = ttk.Combobox(frame, width=28, state="readonly")
    categoryCombo.grid(row=4, column=1, columnspan=2, sticky="w", pady=5)
    
    # Add inventory section (collapsible)
    inventoryFrame = ttk.LabelFrame(frame, text="Povezivanje s Inventarom (opcionalno)", padding=10)
    inventoryFrame.grid(row=11, column=0, columnspan=3, sticky="we", pady=10)
    
    # Article selection
    ttk.Label(inventoryFrame, text="Artikl iz inventara:").grid(row=0, column=0, sticky="w", pady=5)
    artiklCombo = ttk.Combobox(inventoryFrame, width=35, state="readonly")
    artiklCombo.grid(row=0, column=1, columnspan=2, sticky="w", pady=5)
    
    # Load articles
    cursor.execute("SELECT id, sku, naziv FROM ARTIKLZALIHE ORDER BY naziv")
    artikli = cursor.fetchall()
    artiklDict = {f"{a['sku']} - {a['naziv']}": a['id'] for a in artikli}
    artiklCombo['values'] = ["Nije povezano s inventarom"] + list(artiklDict.keys())
    artiklCombo.set("Nije povezano s inventarom")
    
    # Quantity
    ttk.Label(inventoryFrame, text="Količina:").grid(row=1, column=0, sticky="w", pady=5)
    kolicinaEntry = ttk.Entry(inventoryFrame, width=15)
    kolicinaEntry.grid(row=1, column=1, sticky="w", pady=5)
    
    # Unit price (auto-filled from inventory if available)
    ttk.Label(inventoryFrame, text="Jedinična cijena:").grid(row=2, column=0, sticky="w", pady=5)
    jedinicnaCijenaEntry = ttk.Entry(inventoryFrame, width=15)
    jedinicnaCijenaEntry.grid(row=2, column=1, sticky="w", pady=5)
    
    # Location
    ttk.Label(inventoryFrame, text="Lokacija:").grid(row=3, column=0, sticky="w", pady=5)
    lokacijaEntry = ttk.Entry(inventoryFrame, width=15)
    lokacijaEntry.grid(row=3, column=1, sticky="w", pady=5)
    
    # Transaction type (purchase/sale)
    ttk.Label(inventoryFrame, text="Tip inventara:").grid(row=4, column=0, sticky="w", pady=5)
    inventoryTypeVar = tk.StringVar(value="nabava")
    ttk.Radiobutton(inventoryFrame, text="Nabava", variable=inventoryTypeVar, value="nabava").grid(row=4, column=1, sticky="w")
    ttk.Radiobutton(inventoryFrame, text="Prodaja", variable=inventoryTypeVar, value="prodaja").grid(row=4, column=2, sticky="w")

    # Function to auto-fill price when article is selected
    def onArticleSelect(event):
        selected = artiklCombo.get()
        if selected in artiklDict:
            art_id = artiklDict[selected]
            cursor.execute("SELECT nabavnaCijena, prodajnaCijena FROM ARTIKLZALIHE WHERE id = ?", (art_id,))
            art = cursor.fetchone()
            if art:
                if inventoryTypeVar.get() == "nabava":
                    jedinicnaCijenaEntry.delete(0, tk.END)
                    jedinicnaCijenaEntry.insert(0, str(art['nabavnaCijena']))
                else:
                    jedinicnaCijenaEntry.delete(0, tk.END)
                    jedinicnaCijenaEntry.insert(0, str(art['prodajnaCijena']))
    
    artiklCombo.bind("<<ComboboxSelected>>", onArticleSelect)
    inventoryTypeVar.trace_add('write', lambda *args: onArticleSelect(None))

    def updateCategories(*args):
        vrsta = vrstaVar.get()
        cursor.execute("SELECT id, ime FROM ACCTOSKATEGORIJE WHERE vrsta = ? ORDER BY ime", (vrsta,))
        categories = cursor.fetchall()
        categoryDict = {cat['ime']: cat['id'] for cat in categories}
        categoryCombo['values'] = list(categoryDict.keys())
        if categories:
            categoryCombo.set(categories[0]['ime'])
    
    vrstaVar.trace_add('write', updateCategories)
    updateCategories()
    
    # Supplier/Client
    ttk.Label(frame, text="Dobavljač/Klijent:").grid(row=5, column=0, sticky="w", pady=5)
    dobavljacEntry = ttk.Entry(frame, width=30)
    dobavljacEntry.grid(row=5, column=1, columnspan=2, sticky="w", pady=5)
    
    # Description
    ttk.Label(frame, text="Opis:").grid(row=6, column=0, sticky="w", pady=5)
    opisText = tk.Text(frame, height=3, width=30)
    opisText.grid(row=6, column=1, columnspan=2, sticky="w", pady=5)
    
    # Account Number
    ttk.Label(frame, text="Broj Računa:").grid(row=7, column=0, sticky="w", pady=5)
    brojRacunaEntry = ttk.Entry(frame, width=30)
    brojRacunaEntry.grid(row=7, column=1, columnspan=2, sticky="w", pady=5)
    
    # Tax Amount
    ttk.Label(frame, text="Iznos Poreza:").grid(row=8, column=0, sticky="w", pady=5)
    porezEntry = ttk.Entry(frame, width=30)
    porezEntry.grid(row=8, column=1, columnspan=2, sticky="w", pady=5)
    porezEntry.insert(0, "0")
    
    # Notes
    ttk.Label(frame, text="Napomene:").grid(row=9, column=0, sticky="w", pady=5)
    napomeneText = tk.Text(frame, height=3, width=30)
    napomeneText.grid(row=9, column=1, columnspan=2, sticky="w", pady=5)
    
    def submit():
        from .transakcije import addTransaction
        
        # Validate
        try:
            iznos = float(iznosEntry.get().strip())
            if iznos <= 0:
                raise ValueError
        except:
            messagebox.showerror("Greška", "Unesite ispravan iznos!")
            return
        
        if not datumEntry.get().strip():
            messagebox.showerror("Greška", "Unesite datum!")
            return
        
        if not accountCombo.get():
            messagebox.showerror("Greška", "Odaberite račun!")
            return
        
        # Get account ID
        racunId = accountDict.get(accountCombo.get())
        
        # Get category ID
        kategorijaId = None
        if categoryCombo.get():
            cursor.execute("SELECT id FROM ACCTOSKATEGORIJE WHERE ime = ?", (categoryCombo.get(),))
            cat = cursor.fetchone()
            if cat:
                kategorijaId = cat['id']
        
        # Get tax amount
        try:
            iznosPoreza = float(porezEntry.get().strip() or "0")
        except:
            iznosPoreza = 0
        
        # Add transaction
        transactionId = addTransaction(
            cursor, conn,
            datum=datumEntry.get().strip(),
            iznos=iznos,
            vrsta=vrstaVar.get(),
            racunId=racunId,
            kategorijaId=kategorijaId,
            dobavljacKlijent=dobavljacEntry.get().strip() or None,
            opis=opisText.get("1.0", tk.END).strip() or None,
            brojRacuna=brojRacunaEntry.get().strip() or None,
            iznosPoreza=iznosPoreza,
            napomene=napomeneText.get("1.0", tk.END).strip() or None
        )

        if transactionId:
            # Check if inventory linking is requested
            selectedArtikl = artiklCombo.get()
            if selectedArtikl != "Nije povezano s inventarom" and selectedArtikl in artiklDict:
                try:
                    artiklId = artiklDict[selectedArtikl]
                    kolicina = int(kolicinaEntry.get().strip())
                    jedinicnaCijena = float(jedinicnaCijenaEntry.get().strip())
                    lokacija = lokacijaEntry.get().strip()
                    
                    # Link to inventory
                    success, message = linkTransactionToInventory(
                        cursor, conn,
                        transactionId,
                        artiklId,
                        kolicina,
                        jedinicnaCijena,
                        inventoryTypeVar.get(),
                        lokacija or None
                    )
                    
                    if not success:
                        messagebox.showwarning("Upozorenje", f"Transakcija dodana, ali nije povezana s inventarom: {message}")
                
                except ValueError:
                    messagebox.showwarning("Upozorenje", "Transakcija dodana, ali nije povezana s inventarom zbog neispravnih podataka")
            
            messagebox.showinfo("Uspjeh", f"Transakcija dodana pod ID: {transactionId}")
            if refreshCallback:
                refreshCallback()
            window.destroy()
        else:
            messagebox.showerror("Greška", "Transakcija nije dodana!")
        
        if transactionId:
            messagebox.showinfo("Uspjeh", f"Transakcija dodana pod ID: {transactionId}")
            if refreshCallback:
                refreshCallback()
            window.destroy()
        else:
            messagebox.showerror("Greška", "Transakcija nije dodana!")
    
    ttk.Button(frame, text="Dodaj Transakciju", command=submit).grid(row=10, column=0, columnspan=3, pady=20)
    
    return window

def editTransactionForm(parent, cursor, conn, transakcijaId, refreshCallback=None):
    from .transakcije import getTransactionById, updateTransaction
    
    # Get transaction details
    transaction = getTransactionById(cursor, transakcijaId)
    
    if not transaction:
        messagebox.showerror("Greška", "Transakcija nije pronađena!")
        return
    
    window = tk.Toplevel(parent)
    window.title(f"Uredi Transakciju #{transakcijaId}")
    window.geometry("500x600")
    
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill="both", expand=True)
    
    # Transaction Type
    ttk.Label(frame, text="Vrsta Transakcije:*").grid(row=0, column=0, sticky="w", pady=5)
    vrstaVar = tk.StringVar(value=transaction['vrsta'])
    ttk.Radiobutton(frame, text="Rashod", variable=vrstaVar, value="rashod").grid(row=0, column=1, sticky="w", padx=5)
    ttk.Radiobutton(frame, text="Prihod", variable=vrstaVar, value="prihod").grid(row=0, column=2, sticky="w", padx=5)
    
    # Date
    ttk.Label(frame, text="Datum:*").grid(row=1, column=0, sticky="w", pady=5)
    datumEntry = ttk.Entry(frame, width=30)
    datumEntry.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)
    datumEntry.insert(0, transaction['datum'])
    
    # Amount
    ttk.Label(frame, text="Iznos:*").grid(row=2, column=0, sticky="w", pady=5)
    iznosEntry = ttk.Entry(frame, width=30)
    iznosEntry.grid(row=2, column=1, columnspan=2, sticky="w", pady=5)
    iznosEntry.insert(0, str(transaction['iznos']))
    
    # Account
    ttk.Label(frame, text="Račun:*").grid(row=3, column=0, sticky="w", pady=5)
    accountCombo = ttk.Combobox(frame, width=28, state="readonly")
    accountCombo.grid(row=3, column=1, columnspan=2, sticky="w", pady=5)
    
    # Load accounts and set current
    cursor.execute("SELECT id, naziv FROM ACCTOSRACUNI ORDER BY naziv")
    accounts = cursor.fetchall()
    accountDict = {acc['naziv']: acc['id'] for acc in accounts}
    accountCombo['values'] = list(accountDict.keys())
    
    # Find and set current account
    cursor.execute("SELECT naziv FROM ACCTOSRACUNI WHERE id = ?", (transaction['racunId'],))
    current_account = cursor.fetchone()
    if current_account:
        accountCombo.set(current_account['naziv'])
    elif accounts:
        accountCombo.set(accounts[0]['naziv'])
    
    # Category
    ttk.Label(frame, text="Kategorija:").grid(row=4, column=0, sticky="w", pady=5)
    categoryCombo = ttk.Combobox(frame, width=28, state="readonly")
    categoryCombo.grid(row=4, column=1, columnspan=2, sticky="w", pady=5)
    
    def updateCategories(*args):
        vrsta = vrstaVar.get()
        cursor.execute("SELECT id, ime FROM ACCTOSKATEGORIJE WHERE vrsta = ? ORDER BY ime", (vrsta,))
        categories = cursor.fetchall()
        categoryDict = {cat['ime']: cat['id'] for cat in categories}
        categoryCombo['values'] = list(categoryDict.keys())
        
        # Try to set current category
        if transaction['kategorijaId']:
            cursor.execute("SELECT ime FROM ACCTOSKATEGORIJE WHERE id = ?", (transaction['kategorijaId'],))
            current_cat = cursor.fetchone()
            if current_cat:
                categoryCombo.set(current_cat['ime'])
        elif categories:
            categoryCombo.set(categories[0]['ime'])
    
    vrstaVar.trace('w', updateCategories)
    updateCategories()
    
    # Supplier/Client
    ttk.Label(frame, text="Dobavljač/Klijent:").grid(row=5, column=0, sticky="w", pady=5)
    dobavljacEntry = ttk.Entry(frame, width=30)
    dobavljacEntry.grid(row=5, column=1, columnspan=2, sticky="w", pady=5)
    dobavljacEntry.insert(0, transaction['dobavljacKlijent'] or "")
    
    # Description
    ttk.Label(frame, text="Opis:").grid(row=6, column=0, sticky="w", pady=5)
    opisText = tk.Text(frame, height=3, width=30)
    opisText.grid(row=6, column=1, columnspan=2, sticky="w", pady=5)
    opisText.insert("1.0", transaction['opis'] or "")
    
    # Account Number
    ttk.Label(frame, text="Broj Računa:").grid(row=7, column=0, sticky="w", pady=5)
    brojRacunaEntry = ttk.Entry(frame, width=30)
    brojRacunaEntry.grid(row=7, column=1, columnspan=2, sticky="w", pady=5)
    brojRacunaEntry.insert(0, transaction['brojRacuna'] or "")
    
    # Tax Amount
    ttk.Label(frame, text="Iznos Poreza:").grid(row=8, column=0, sticky="w", pady=5)
    porezEntry = ttk.Entry(frame, width=30)
    porezEntry.grid(row=8, column=1, columnspan=2, sticky="w", pady=5)
    porezEntry.insert(0, str(transaction['iznosPoreza'] or 0))
    
    # Reconciliation status
    ttk.Label(frame, text="Uskladeno:").grid(row=9, column=0, sticky="w", pady=5)
    uskladenoVar = tk.BooleanVar(value=bool(transaction['uskladeno']))
    ttk.Checkbutton(frame, variable=uskladenoVar, text="Da").grid(row=9, column=1, sticky="w", pady=5)
    
    # Notes
    ttk.Label(frame, text="Napomene:").grid(row=10, column=0, sticky="w", pady=5)
    napomeneText = tk.Text(frame, height=3, width=30)
    napomeneText.grid(row=10, column=1, columnspan=2, sticky="w", pady=5)
    napomeneText.insert("1.0", transaction['napomene'] or "")
    
    def submitUpdate():
        # Validate
        try:
            iznos = float(iznosEntry.get().strip())
            if iznos <= 0:
                raise ValueError
        except:
            messagebox.showerror("Greška", "Unesite ispravan iznos!")
            return
        
        if not datumEntry.get().strip():
            messagebox.showerror("Greška", "Unesite datum!")
            return
        
        if not accountCombo.get():
            messagebox.showerror("Greška", "Odaberite račun!")
            return
        
        # Get account ID
        racunId = accountDict.get(accountCombo.get())
        
        # Get category ID
        kategorijaId = None
        if categoryCombo.get():
            cursor.execute("SELECT id FROM ACCTOSKATEGORIJE WHERE ime = ?", (categoryCombo.get(),))
            cat = cursor.fetchone()
            if cat:
                kategorijaId = cat['id']
        
        # Get tax amount
        try:
            iznosPoreza = float(porezEntry.get().strip() or "0")
        except:
            iznosPoreza = 0
        
        # Update transaction
        success = updateTransaction(
            cursor, conn,
            transakcijaId=transakcijaId,
            datum=datumEntry.get().strip(),
            iznos=iznos,
            vrsta=vrstaVar.get(),
            racunId=racunId,
            kategorijaId=kategorijaId,
            dobavljacKlijent=dobavljacEntry.get().strip() or None,
            opis=opisText.get("1.0", tk.END).strip() or None,
            brojRacuna=brojRacunaEntry.get().strip() or None,
            iznosPoreza=iznosPoreza,
            uskladeno=1 if uskladenoVar.get() else 0,
            napomene=napomeneText.get("1.0", tk.END).strip() or None
        )
        
        if success:
            messagebox.showinfo("Uspjeh", "Transakcija uspješno ažurirana!")
            if refreshCallback:
                refreshCallback()
            window.destroy()
        else:
            messagebox.showerror("Greška", "Transakcija nije ažurirana!")
    
    def deleteTransaction():
        from .transakcije import deleteTransaction as deleteTrans
        if messagebox.askyesno("Potvrdite", "Jeste li sigurni da želite izbrisati ovu transakciju?"):
            if deleteTrans(cursor, conn, transakcijaId):
                messagebox.showinfo("Uspjeh", "Transakcija izbrisana!")
                if refreshCallback:
                    refreshCallback()
                window.destroy()
            else:
                messagebox.showerror("Greška", "Nije moguće izbrisati transakciju!")
    
    # Buttons frame
    buttonFrame = ttk.Frame(frame)
    buttonFrame.grid(row=11, column=0, columnspan=3, pady=20)
    
    ttk.Button(buttonFrame, text="Spremi Promjene", command=submitUpdate).pack(side="left", padx=5)
    ttk.Button(buttonFrame, text="Izbriši Transakciju", command=deleteTransaction).pack(side="left", padx=5)
    ttk.Button(buttonFrame, text="Odustani", command=window.destroy).pack(side="left", padx=5)
    
    return window
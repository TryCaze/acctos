from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from .zalihe import getSuppliers, addItem, editItem, addStockEntry, getItemById

def addItemForm(parent, cursor, conn, refreshCallback=None):
    form = tk.Toplevel(parent)
    form.title("Novi Artikl")
    form.geometry("500x500")

    fields = {}
    labels = [
        ("SKU", "sku"), ("Naziv", "naziv"), ("Opis", "opis"),
        ("Kategorija", "kategorija"), ("Jedinica", "jedinica"),
        ("Nabavna cijena", "nabavnaCijena"), ("Prodajna cijena", "prodajnaCijena"),
        ("Minimalna količina", "minimalnaKolicina"), ("Idealna količina", "idealnaKolicina"),
        ("Lokacija", "lokacija"), ("Napomene", "napomene")
    ]

    for i, (lab, key) in enumerate(labels):
        ttk.Label(form, text=lab + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
        if key == "napomene" or key == "opis":
            txt = tk.Text(form, width=40, height=4)
            txt.grid(row=i, column=1, padx=5, pady=5)
            fields[key] = txt
        else:
            ent = ttk.Entry(form)
            ent.grid(row=i, column=1, padx=5, pady=5, sticky="we")
            fields[key] = ent

    # dobavljač (odabir računa)
    ttk.Label(form, text="Dobavljač (račun):").grid(row=len(labels), column=0, padx=5, pady=5)
    accounts = getSuppliers(cursor)
    # show "nije odabran" + list of racunId
    values = ["Nije odabrano"] + [f"{s['racunId']} - {s.get('racunNaziv') or ''}" for s in accounts]
    supplierVar = tk.StringVar(value=values[0])
    supplierCombo = ttk.Combobox(form, textvariable=supplierVar, values=values, state="readonly")
    supplierCombo.grid(row=len(labels), column=1, padx=5, pady=5, sticky="we")

    def onSave():
        data = {}
        for key, widget in fields.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", "end").strip()
            else:
                data[key] = widget.get().strip()
        sel = supplierVar.get()
        if sel and sel != "Nije odabrano" and "-" in sel:
            data['dobavljacId'] = int(sel.split("-", 1)[0].strip())
        else:
            data['dobavljacId'] = None

        if not data.get('naziv'):
            messagebox.showwarning("Upozorenje", "Naziv je obavezan.")
            return

        success, msg = addItem(cursor, conn, data)
        if success:
            messagebox.showinfo("Uspjeh", msg)
            if refreshCallback:
                refreshCallback()
            form.destroy()
        else:
            messagebox.showerror("Pogreška", msg)

    ttk.Button(form, text="Spremi", command=onSave).grid(row=99, column=0, pady=10)
    ttk.Button(form, text="Odustani", command=form.destroy).grid(row=99, column=1, pady=10)

def editItemForm(parent, cursor, conn, artiklId, refreshCallback=None):
    artikl = getItemById(cursor, artiklId)
    if not artikl:
        messagebox.showerror("Pogreška", "Artikl nije pronađen.")
        return

    form = tk.Toplevel(parent)
    form.title("Uredi Artikl")
    form.geometry("500x500")

    fields = {}
    labels = [
        ("SKU", "sku"), ("Naziv", "naziv"), ("Opis", "opis"),
        ("Kategorija", "kategorija"), ("Jedinica", "jedinica"),
        ("Nabavna cijena", "nabavnaCijena"), ("Prodajna cijena", "prodajnaCijena"),
        ("Minimalna količina", "minimalnaKolicina"), ("Idealna količina", "idealnaKolicina"),
        ("Lokacija", "lokacija"), ("Napomene", "napomene")
    ]

    for i, (lab, key) in enumerate(labels):
        ttk.Label(form, text=lab + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
        if key == "napomene" or key == "opis":
            txt = tk.Text(form, width=40, height=4)
            txt.grid(row=i, column=1, padx=5, pady=5)
            txt.insert("1.0", artikl.get(key) or "")
            fields[key] = txt
        else:
            ent = ttk.Entry(form)
            ent.grid(row=i, column=1, padx=5, pady=5, sticky="we")
            ent.insert(0, str(artikl.get(key) or ""))
            fields[key] = ent

    # dobavljač selection
    from .zalihe import getSuppliers
    accounts = getSuppliers(cursor)
    values = ["Nije odabrano"] + [f"{s['racunId']} - {s.get('racunNaziv') or ''}" for s in accounts]
    supplierVar = tk.StringVar(value=values[0])
    current_did = artikl.get('dobavljacId')
    if current_did:
        found = next((f for f in values if f.startswith(str(current_did) + " -")), None)
        if found:
            supplierVar.set(found)
    supplierCombo = ttk.Combobox(form, textvariable=supplierVar, values=values, state="readonly")
    supplierCombo.grid(row=len(labels), column=1, padx=5, pady=5, sticky="we")

    def onSave():
        data = {}
        for key, widget in fields.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", "end").strip()
            else:
                data[key] = widget.get().strip()
        sel = supplierVar.get()
        if sel and sel != "Nije odabrano" and "-" in sel:
            data['dobavljacId'] = int(sel.split("-", 1)[0].strip())
        else:
            data['dobavljacId'] = None

        if not data.get('naziv'):
            messagebox.showwarning("Upozorenje", "Naziv je obavezan.")
            return

        success, msg = editItem(cursor, conn, artiklId, data)
        if success:
            messagebox.showinfo("Uspjeh", msg)
            if refreshCallback:
                refreshCallback()
            form.destroy()
        else:
            messagebox.showerror("Pogreška", msg)

    ttk.Button(form, text="Spremi promjene", command=onSave).grid(row=99, column=0, pady=10)
    ttk.Button(form, text="Odustani", command=form.destroy).grid(row=99, column=1, pady=10)


def addStockForm(parent, cursor, conn, artiklId, artiklNaziv, refreshCallback=None):
    form = tk.Toplevel(parent)
    form.title(f"Dodaj stanje - {artiklNaziv}")
    form.geometry("450x450")

    fields = {}
    labels = [
        ("Lokacija", "lokacija"),
        ("Broj serije", "brojSerije"),
        ("Količina (pozitivno/negativno)", "kolicina"),
        ("Rok trajanja (YYYY-MM-DD)", "rokTrajanja"),
        ("Nabavna cijena po jedinici", "nabavnaCijena"),
        ("Dobavljač / kupac", "dobavljacKupac"),
        ("Iz lokacije", "izLokacije"),
        ("U lokaciju", "uLokaciju"),
        ("Napomene", "napomene"),
    ]

    for i, (lab, key) in enumerate(labels):
        ttk.Label(form, text=lab + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
        if key == "napomene":
            txt = tk.Text(form, width=35, height=4)
            txt.grid(row=i, column=1, padx=5, pady=5)
            fields[key] = txt
        else:
            ent = ttk.Entry(form)
            ent.grid(row=i, column=1, padx=5, pady=5, sticky="we")
            fields[key] = ent

    # Add option to create financial transaction
    createTransactionVar = tk.BooleanVar(value=False)
    ttk.Checkbutton(form, text="Kreiraj financijsku transakciju", variable=createTransactionVar).grid(
        row=len(labels) + 1, column=0, columnspan=2, pady=10
    )
    
    # Account selection for financial transaction
    ttk.Label(form, text="Račun za transakciju:").grid(row=len(labels) + 2, column=0, sticky="e", padx=5, pady=5)
    accountCombo = ttk.Combobox(form, width=35, state="readonly")
    accountCombo.grid(row=len(labels) + 2, column=1, padx=5, pady=5, sticky="we")
    
    # Load accounts
    cursor.execute("SELECT id, naziv FROM ACCTOSRACUNI ORDER BY naziv")
    accounts = cursor.fetchall()
    accountCombo['values'] = [f"{a['id']} - {a['naziv']}" for a in accounts]
    if accounts:
        accountCombo.set(f"{accounts[0]['id']} - {accounts[0]['naziv']}")

    def onSave():
        data = {}
        for key, widget in fields.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", "end").strip()
            else:
                data[key] = widget.get().strip()
        
        # Validate količina
        try:
            kolicina = int(data.get('kolicina') or 0)
        except:
            messagebox.showwarning("Upozorenje", "Količina mora biti cijeli broj.")
            return
        
        # Check if financial transaction should be created
        if createTransactionVar.get():
            try:
                selected_account = accountCombo.get()
                account_id = int(selected_account.split("-")[0].strip())
                
                from ..transakcije import addTransaction
                
                # Create financial transaction
                total_amount = kolicina * float(data.get('nabavnaCijena') or 0)
                transaction_type = "rashod" if kolicina > 0 else "prihod"
                
                trans_id = addTransaction(
                    cursor, conn,
                    datum=datetime.now().strftime("%Y-%m-%d"),
                    iznos=total_amount,
                    vrsta=transaction_type,
                    racunId=account_id,
                    dobavljacKlijent=data.get('dobavljacKupac'),
                    opis=f"Nabava artikla: {artiklNaziv}",
                    brojRacuna=data.get('brojSerije')
                )
                
                if trans_id:
                    # Link to inventory transaction
                    from ..integration import linkTransactionToInventory
                    linkTransactionToInventory(
                        cursor, conn,
                        trans_id,
                        artiklId,
                        kolicina,
                        float(data.get('nabavnaCijena') or 0),
                        'nabava' if kolicina > 0 else 'povrat',
                        data.get('lokacija')
                    )
            except Exception as e:
                messagebox.showwarning("Upozorenje", f"Inventar ažuriran, ali financijska transakcija nije kreirana: {e}")
        
        # Always update inventory
        success, msg = addStockEntry(cursor, conn, artiklId, data)
        if success:
            messagebox.showinfo("Uspjeh", msg)
            if refreshCallback:
                refreshCallback()
            form.destroy()
        else:
            messagebox.showerror("Pogreška", msg)

    ttk.Button(form, text="Dodaj", command=onSave).grid(row=99, column=0, pady=10)
    ttk.Button(form, text="Odustani", command=form.destroy).grid(row=99, column=1, pady=10)
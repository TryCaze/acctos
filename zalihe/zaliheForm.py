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

    def onSave():
        data = {}
        for key, widget in fields.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", "end").strip()
            else:
                data[key] = widget.get().strip()
        # validate količina
        try:
            data['kolicina'] = int(data.get('kolicina') or 0)
        except:
            messagebox.showwarning("Upozorenje", "Količina mora biti cijeli broj.")
            return
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
import tkinter as tk
from tkinter import ttk, messagebox
from .zalihe import (
    getAllItems, getInventoryTransactions, getStockEntries, getInventoryStatistics,
    deleteItem
)
from .zaliheForm import addItemForm, editItemForm, addStockForm

def createInventoryTab(parent, cursor, conn):
    frame = ttk.Frame(parent)

    # FILTERI (na vrhu)
    filterBar = ttk.LabelFrame(frame, text="Filteri", padding=10)
    filterBar.pack(fill="x", padx=10, pady=5)

    ttk.Label(filterBar, text="Pretraži:").grid(row=0, column=0, padx=5)
    searchVar = tk.StringVar()
    searchEntry = ttk.Entry(filterBar, textvariable=searchVar, width=30)
    searchEntry.grid(row=0, column=1, padx=5)

    ttk.Label(filterBar, text="Kategorija:").grid(row=0, column=2, padx=5)
    catVar = tk.StringVar(value="sve")
    catCombo = ttk.Combobox(filterBar, textvariable=catVar, values=["sve"], width=20, state="normal")
    catCombo.grid(row=0, column=3, padx=5)

    ttk.Label(filterBar, text="Lokacija:").grid(row=0, column=4, padx=5)
    locVar = tk.StringVar(value="sve")
    locCombo = ttk.Combobox(filterBar, textvariable=locVar, values=["sve"], width=15, state="normal")
    locCombo.grid(row=0, column=5, padx=5)

    ttk.Button(filterBar, text="Primijeni", command=lambda: applyFilters()).grid(row=0, column=6, padx=10)
    ttk.Button(filterBar, text="Resetiraj", command=lambda: resetFilters()).grid(row=0, column=7, padx=5)

    # GUMBE ispod filtera
    btnFrame = ttk.Frame(frame, padding=10)
    btnFrame.pack(fill="x")

    treeFrame = ttk.Frame(frame)
    treeFrame.pack(fill="both", expand=True, padx=10, pady=10)

    # Treeview
    columns = ("ID", "SKU", "Naziv", "Kategorija", "Jedinica", "Stanje", "Nabavna", "Prodajna", "Lokacija", "Min", "Ideal")
    tree = ttk.Treeview(treeFrame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.column("ID", width=50, anchor="center")
    tree.column("SKU", width=100)
    tree.column("Naziv", width=220)
    tree.column("Kategorija", width=120)
    tree.column("Jedinica", width=80, anchor="center")
    tree.column("Stanje", width=80, anchor="center")
    tree.column("Nabavna", width=90, anchor="e")
    tree.column("Prodajna", width=90, anchor="e")
    tree.column("Lokacija", width=100)
    tree.column("Min", width=60, anchor="center")
    tree.column("Ideal", width=60, anchor="center")

    # Statistika
    statsFrame = ttk.LabelFrame(frame, text="Statistika", padding=10)
    statsFrame.pack(fill="x", padx=10, pady=5)
    totalLabel = ttk.Label(statsFrame, text="Ukupno artikala: 0")
    totalLabel.pack(side="left", padx=10)
    belowLabel = ttk.Label(statsFrame, text="Ispod minimalne: 0")
    belowLabel.pack(side="left", padx=10)
    valueLabel = ttk.Label(statsFrame, text="Procijenjena vrijednost: 0.00")
    valueLabel.pack(side="left", padx=10)

    current_filters = {}

    def refreshItems():
        # clear
        for item in tree.get_children():
            tree.delete(item)

        items = getAllItems(cursor)

        # populate category and location Combos with distinct values
        cats = sorted({(i.get('kategorija') or "").strip() for i in items if (i.get('kategorija') or "").strip()})
        locs = sorted({(i.get('lokacija') or "").strip() for i in items if (i.get('lokacija') or "").strip()})
        cat_items = ["sve"] + cats
        loc_items = ["sve"] + locs
        catCombo['values'] = cat_items
        locCombo['values'] = loc_items

        # apply filters
        filtered = []
        q = (current_filters.get('query') or "").lower()
        for it in items:
            if current_filters.get('kategorija') and current_filters['kategorija'] != "sve":
                if (it.get('kategorija') or "") != current_filters['kategorija']:
                    continue
            if current_filters.get('lokacija') and current_filters['lokacija'] != "sve":
                if (it.get('lokacija') or "") != current_filters['lokacija']:
                    continue
            if q:
                if q not in (it.get('naziv') or "").lower() and q not in (it.get('sku') or "").lower():
                    continue
            filtered.append(it)

        for it in filtered:
            stanje = it.get('trenutno_stanje', 0)
            min_k = it.get('minimalnaKolicina') or 0
            tags = ()
            if stanje < min_k:
                tags = ('ispod',)
            tree.insert("", "end", values=(
                it.get('id'),
                it.get('sku'),
                it.get('naziv'),
                it.get('kategorija') or "",
                it.get('jedinica') or "",
                stanje,
                f"{(it.get('nabavnaCijena') or 0):.2f}",
                f"{(it.get('prodajnaCijena') or 0):.2f}",
                it.get('lokacija') or "",
                it.get('minimalnaKolicina') or 0,
                it.get('idealnaKolicina') or 0,
            ), tags=tags)

        tree.tag_configure('ispod', background='#fff0e0')

        # update stats
        stats = getInventoryStatistics(cursor)
        totalLabel.config(text=f"Ukupno artikala: {stats['ukupno_artikala']}")
        belowLabel.config(text=f"Ispod minimalne: {stats['ispod_minimalne']}")
        valueLabel.config(text=f"Procijenjena vrijednost: {stats['procijenjena_vrijednost']:.2f}")

    def applyFilters():
        f = {}
        if searchVar.get().strip():
            f['query'] = searchVar.get().strip()
        if catVar.get() and catVar.get() != "sve":
            f['kategorija'] = catVar.get()
        if locVar.get() and locVar.get() != "sve":
            f['lokacija'] = locVar.get()
        current_filters.clear()
        current_filters.update(f)
        refreshItems()

    def resetFilters():
        searchVar.set("")
        catVar.set("sve")
        locVar.set("sve")
        current_filters.clear()
        refreshItems()

    # Actions
    def onAddItem():
        addItemForm(frame, cursor, conn, refreshCallback=refreshItems)

    def onEditItem():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite artikl za uređivanje.")
            return
        item = tree.item(sel[0])['values']
        artiklId = item[0]
        editItemForm(frame, cursor, conn, artiklId, refreshCallback=refreshItems)

    def onDeleteItem():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite artikl za brisanje.")
            return
        item = tree.item(sel[0])['values']
        artiklId = item[0]
        artiklNaziv = item[2]
        if not messagebox.askyesno("Potvrdite", f"Jeste li sigurni da želite izbrisati artikl '{artiklNaziv}'?"):
            return
        success, msg = deleteItem(cursor, conn, artiklId)
        if success:
            messagebox.showinfo("Uspjeh", msg)
            refreshItems()
        else:
            messagebox.showwarning("Upozorenje", msg)

    def onAddStock():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite artikl za dodavanje stanja.")
            return
        item = tree.item(sel[0])['values']
        artiklId = item[0]
        artiklNaziv = item[2]
        addStockForm(frame, cursor, conn, artiklId, artiklNaziv, refreshCallback=refreshItems)

    def onViewTransactions():
        sel = tree.selection()
        artiklId = None
        if sel:
            item = tree.item(sel[0])['values']
            artiklId = item[0]
        trans = getInventoryTransactions(cursor, artiklId)
        win = tk.Toplevel(frame)
        win.title("Transakcije zaliha")
        win.geometry("900x500")
        t = ttk.Treeview(win, columns=("ID", "Datum", "Tip", "Artikl", "Količina", "Jedinicna", "Ukupno", "Dobavljač/Kupac", "Napomene"), show="headings")
        for c in ("ID", "Datum", "Tip", "Artikl", "Količina", "Jedinicna", "Ukupno", "Dobavljač/Kupac", "Napomene"):
            t.heading(c, text=c)
        t.pack(fill="both", expand=True, padx=10, pady=10)
        # map artiklId -> naziv
        items_map = {i['id']: i['naziv'] for i in getAllItems(cursor)}
        for r in trans:
            t.insert("", "end", values=(
                r.get('id'),
                r.get('datum'),
                r.get('tipTransakcije'),
                items_map.get(r.get('artiklId')) or r.get('artiklId'),
                r.get('kolicina'),
                f"{(r.get('jedinicnaCijena') or 0):.2f}",
                f"{(r.get('ukupanIznos') or 0):.2f}",
                r.get('dobavljacKupac') or "",
                (r.get('napomene') or "")[:80]
            ))

    def onViewStock():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite artikl za pregled stanja.")
            return
        item = tree.item(sel[0])['values']
        artiklId = item[0]
        entries = getStockEntries(cursor, artiklId)
        win = tk.Toplevel(frame)
        win.title("Stanje artikla")
        win.geometry("800x400")
        t = ttk.Treeview(win, columns=("ID", "Lokacija", "Serija", "Količina", "Rok", "Nabavna", "Napomene", "Datum"), show="headings")
        for c in ("ID", "Lokacija", "Serija", "Količina", "Rok", "Nabavna", "Napomene", "Datum"):
            t.heading(c, text=c)
        t.pack(fill="both", expand=True, padx=10, pady=10)
        for e in entries:
            t.insert("", "end", values=(
                e.get('id'),
                e.get('lokacija') or "",
                e.get('brojSerije') or "",
                e.get('kolicina'),
                e.get('rokTrajanja') or "",
                f"{(e.get('nabavnaCijena') or 0):.2f}",
                (e.get('napomene') or "")[:80],
                e.get('datumKreiranja') or ""
            ))

    def onViewStatistics():
        stats = getInventoryStatistics(cursor)
        win = tk.Toplevel(frame)
        win.title("Statistika zaliha")
        win.geometry("400x200")
        ttk.Label(win, text=f"Ukupno artikala: {stats['ukupno_artikala']}", font=("Arial", 11)).pack(pady=8)
        ttk.Label(win, text=f"Ispod minimalne: {stats['ispod_minimalne']}", font=("Arial", 11)).pack(pady=8)
        ttk.Label(win, text=f"Procijenjena vrijednost zaliha: {stats['procijenjena_vrijednost']:.2f}", font=("Arial", 11)).pack(pady=8)

    def onDoubleClick(event):
        sel = tree.selection()
        if sel:
            onEditItem()

    # Buttons
    ttk.Button(btnFrame, text="Novi Artikl", command=onAddItem).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Uredi", command=onEditItem).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Izbriši", command=onDeleteItem).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Dodaj Stanje", command=onAddStock).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Stanje", command=onViewStock).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Transakcije", command=onViewTransactions).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Statistika", command=onViewStatistics).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Osvježi", command=refreshItems).pack(side="left", padx=5)

    # scrollbar and pack
    scrollbar = ttk.Scrollbar(treeFrame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    tree.bind('<Double-Button-1>', onDoubleClick)

    # initial load
    refreshItems()

    return frame
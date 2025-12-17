# kategorije/kategorijeTab.py
import tkinter as tk
from tkinter import ttk, messagebox
from .kategorijeForm import addCategoryForm, editCategoryForm

def createCategoriesTab(parent, cursor, conn):
    frame = ttk.Frame(parent)

    # ========= TOP BUTTON BAR =========
    btnFrame = ttk.Frame(frame, padding=10)
    btnFrame.pack(fill="x")

    # ========= FILTER BAR =========
    filterBar = ttk.LabelFrame(frame, text="Filteri", padding=10)
    filterBar.pack(fill="x", padx=10, pady=5)

    ttk.Label(filterBar, text="Vrsta:").grid(row=0, column=0, padx=5)
    typeVar = tk.StringVar(value="sve")
    typeCombo = ttk.Combobox(filterBar, textvariable=typeVar,
                             values=["sve", "prihod", "rashod"], width=12, state="readonly")
    typeCombo.grid(row=0, column=1, padx=5)

    ttk.Label(filterBar, text="Porezno:").grid(row=0, column=2, padx=5)
    taxVar = tk.StringVar(value="sve")
    taxCombo = ttk.Combobox(filterBar, textvariable=taxVar,
                             values=["sve", "da", "ne"], width=10, state="readonly")
    taxCombo.grid(row=0, column=3, padx=5)

    ttk.Button(filterBar, text="Primijeni", command=lambda: applyFilters()).grid(row=0, column=4, padx=10)
    ttk.Button(filterBar, text="Resetiraj", command=lambda: resetFilters()).grid(row=0, column=5, padx=5)

    # ========= MAIN SPLIT PANEL =========
    split = ttk.Panedwindow(frame, orient="horizontal")
    split.pack(fill="both", expand=True, padx=10, pady=10)

    # LEFT: LIST OF CATEGORIES
    leftFrame = ttk.Frame(split)
    split.add(leftFrame, weight=1)

    categoryTree = ttk.Treeview(leftFrame,
                                columns=("Naziv", "Vrsta"),
                                show="headings",
                                height=20)
    categoryTree.heading("Naziv", text="Naziv")
    categoryTree.heading("Vrsta", text="Vrsta")

    categoryTree.column("Naziv", width=180)
    categoryTree.column("Vrsta", width=70, anchor="center")

    scrollLeft = ttk.Scrollbar(leftFrame, orient="vertical", command=categoryTree.yview)
    categoryTree.configure(yscrollcommand=scrollLeft.set)

    categoryTree.pack(side="left", fill="both", expand=True)
    scrollLeft.pack(side="right", fill="y")

    # RIGHT: CATEGORY DETAILS
    rightFrame = ttk.LabelFrame(split, text="Detalji kategorije", padding=10)
    split.add(rightFrame, weight=3)

    # Detail labels
    lblName = ttk.Label(rightFrame, text="Naziv: ", font=("Arial", 12, "bold"))
    lblName.pack(anchor="w", pady=3)

    lblType = ttk.Label(rightFrame, text="Vrsta: ")
    lblType.pack(anchor="w", pady=3)

    lblTax = ttk.Label(rightFrame, text="Porezno priznata: ")
    lblTax.pack(anchor="w", pady=3)

    lblTransactions = ttk.Label(rightFrame, text="Broj transakcija: ")
    lblTransactions.pack(anchor="w", pady=3)

    ttk.Label(rightFrame, text="Opis:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
    txtOpis = tk.Text(rightFrame, width=50, height=6, wrap="word", state="disabled")
    txtOpis.pack(fill="x")

    # Action buttons on details panel
    detailsBtnFrame = ttk.Frame(rightFrame)
    detailsBtnFrame.pack(anchor="w", pady=10)

    btnEdit = ttk.Button(detailsBtnFrame, text="Uredi", command=lambda: onEditCategory(selected_id.get()))
    btnEdit.grid(row=0, column=0, padx=5)

    btnDelete = ttk.Button(detailsBtnFrame, text="Izbriši", command=lambda: onDeleteCategory(selected_id.get()))
    btnDelete.grid(row=0, column=1, padx=5)

    # Hidden variable to hold selected category ID
    selected_id = tk.IntVar(value=0)

    # ========= STATISTICS PANEL =========
    statsFrame = ttk.LabelFrame(frame, text="Statistika", padding=10)
    statsFrame.pack(fill="x", padx=10, pady=5)

    totalCategoriesLabel = ttk.Label(statsFrame, text="Ukupno kategorija: 0")
    totalCategoriesLabel.pack(side="left", padx=20)

    incomeCategoriesLabel = ttk.Label(statsFrame, text="Kategorije prihoda: 0")
    incomeCategoriesLabel.pack(side="left", padx=20)

    expenseCategoriesLabel = ttk.Label(statsFrame, text="Kategorije rashoda: 0")
    expenseCategoriesLabel.pack(side="left", padx=20)

    # ========= INTERNAL STATE =========
    current_filters = {}
    category_cache = []     # store loaded categories
    transaction_counts = {} # map category -> number of transactions

    # ========= LOGIC =========
    def refreshCategories():
        from .kategorije import getAllCategories

        # Clear left tree
        for item in categoryTree.get_children():
            categoryTree.delete(item)

        # Load categories
        categories = getAllCategories(cursor)
        category_cache.clear()
        category_cache.extend(categories)

        # Load transaction counts
        cursor.execute("""
            SELECT kategorijaId, COUNT(*) as count
            FROM ACCTOSTRANSAKCIJE
            WHERE kategorijaId IS NOT NULL
            GROUP BY kategorijaId
        """)
        transaction_counts.clear()
        for row in cursor.fetchall():
            transaction_counts[row['kategorijaId']] = row['count']

        # Apply filters
        filtered = []
        for cat in categories:
            if current_filters.get('vrsta') and cat['vrsta'] != current_filters['vrsta']:
                continue

            if current_filters.get('porezno'):
                tax_ok = 1 if current_filters['porezno'] == "da" else 0
                if cat['poreznoPriznato'] != tax_ok:
                    continue

            filtered.append(cat)

        # Fill category list
        for cat in filtered:
            categoryTree.insert("", "end",
                                values=(cat['ime'], cat['vrsta'].capitalize()),
                                iid=str(cat['id']))

        updateStatistics()

        # Clear right panel
        clearDetails()

    def clearDetails():
        selected_id.set(0)
        lblName.config(text="Naziv:")
        lblType.config(text="Vrsta:")
        lblTax.config(text="Porezno priznata:")
        lblTransactions.config(text="Broj transakcija:")
        txtOpis.config(state="normal")
        txtOpis.delete("1.0", "end")
        txtOpis.config(state="disabled")

    def showDetails(cat_id):
        if not cat_id:
            return
        cat = next((c for c in category_cache if c['id'] == cat_id), None)
        if not cat:
            return

        selected_id.set(cat_id)

        lblName.config(text=f"Naziv: {cat['ime']}")
        lblType.config(text=f"Vrsta: {cat['vrsta'].capitalize()}")
        lblTax.config(text=f"Porezno priznata: {'Da' if cat['poreznoPriznato'] else 'Ne'}")

        trans_count = transaction_counts.get(cat_id, 0)
        lblTransactions.config(text=f"Broj transakcija: {trans_count}")

        txtOpis.config(state="normal")
        txtOpis.delete("1.0", "end")
        txtOpis.insert("1.0", cat['opis'] or "")
        txtOpis.config(state="disabled")

    def applyFilters():
        filters = {}

        if typeVar.get() != "sve":
            filters['vrsta'] = typeVar.get()

        if taxVar.get() != "sve":
            filters['porezno'] = taxVar.get()

        current_filters.clear()
        current_filters.update(filters)
        refreshCategories()

    def resetFilters():
        typeVar.set("sve")
        taxVar.set("sve")
        current_filters.clear()
        refreshCategories()

    def updateStatistics():
        from .kategorije import getCategoryStatistics

        stats = getCategoryStatistics(cursor)
        # stats is a LIST of sqlite3.Row objects

        total = 0
        income = 0
        expense = 0

        for row in stats:
            r = dict(row)  # convert Row → normal dict

            if r.get("vrsta") == "prihod":
                income = r.get("count", 0)

            elif r.get("vrsta") == "rashod":
                expense = r.get("count", 0)

        total = income + expense

        totalCategoriesLabel.config(text=f"Ukupno kategorija: {total}")
        incomeCategoriesLabel.config(text=f"Kategorije prihoda: {income}")
        expenseCategoriesLabel.config(text=f"Kategorije rashoda: {expense}")


    def onAddCategory():
        addCategoryForm(frame, cursor, conn, refreshCallback=refreshCategories)

    def onEditCategory(cat_id=None):
        if not cat_id:
            messagebox.showwarning("Upozorenje", "Odaberite kategoriju!")
            return
        editCategoryForm(frame, cursor, conn, cat_id, refreshCallback=refreshCategories)

    def onDeleteCategory(cat_id=None):
        if not cat_id:
            messagebox.showwarning("Upozorenje", "Odaberite kategoriju!")
            return

        cat = next((c for c in category_cache if c['id'] == cat_id), None)
        if not cat:
            return

        if not messagebox.askyesno("Potvrdite", f"Obrisati kategoriju '{cat['ime']}'?"):
            return

        from .kategorije import deleteCategory
        success, msg = deleteCategory(cursor, conn, cat_id)

        if success:
            messagebox.showinfo("Uspjeh", msg)
            refreshCategories()
        else:
            messagebox.showwarning("Upozorenje", msg)

    def onViewStatistics():
        """Show detailed category statistics in a new window."""
        from .kategorije import getCategoryStatistics

        stats_data = getCategoryStatistics(cursor)
        # stats_data is a list of sqlite3.Row

        win = tk.Toplevel(frame)
        win.title("Statistika kategorija")
        win.geometry("600x400")

        tree = ttk.Treeview(
            win,
            columns=("Kategorija", "Vrsta", "Broj transakcija", "Ukupno"),
            show="headings"
        )
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        tree.heading("Kategorija", text="Kategorija")
        tree.heading("Vrsta", text="Vrsta")
        tree.heading("Broj transakcija", text="Broj transakcija")
        tree.heading("Ukupno", text="Ukupni iznos")

        tree.column("Kategorija", width=150)
        tree.column("Vrsta", width=80)
        tree.column("Broj transakcija", width=120)
        tree.column("Ukupno", width=120)

        total_transactions = 0
        total_amount = 0.0

        for row in stats_data:
            d = dict(row)
            tree.insert(
                "",
                "end",
                values=(
                    d.get("ime", ""),
                    d.get("vrsta", "").capitalize(),
                    d.get("transaction_count", 0),
                    f"{d.get('total_amount', 0.0):.2f}"
                )
            )
            total_transactions += d.get("transaction_count", 0)
            total_amount += d.get("total_amount", 0.0)

        # summary bar
        summary = ttk.Frame(win, padding=10)
        summary.pack(fill="x")

        ttk.Label(
            summary,
            text=f"Ukupno transakcija: {total_transactions}",
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=10)

        ttk.Label(
            summary,
            text=f"Ukupni iznos: {total_amount:.2f}",
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=10)


    # ========= BINDINGS =========
    def onSelect(event):
        item = categoryTree.selection()
        if not item:
            clearDetails()
            return
        cat_id = int(item[0])
        showDetails(cat_id)

    categoryTree.bind("<<TreeviewSelect>>", onSelect)

    # ========= BUTTONS =========
    ttk.Button(btnFrame, text="Nova Kategorija", command=onAddCategory).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Statistika", command=onViewStatistics).pack(side="left", padx=5)
    ttk.Button(btnFrame, text="Osvježi", command=refreshCategories).pack(side="left", padx=5)

    # Load initial data
    refreshCategories()

    return frame
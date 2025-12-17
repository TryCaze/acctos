# kategorije/kategorijeForm.py
import tkinter as tk
from tkinter import ttk, messagebox

def addCategoryForm(parent, cursor, conn, refreshCallback=None):
    window = tk.Toplevel(parent)
    window.title("Nova Kategorija")
    window.geometry("400x400")
    
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill="both", expand=True)
    
    # Category Name
    ttk.Label(frame, text="Naziv Kategorije:*").grid(row=0, column=0, sticky="w", pady=5)
    imeEntry = ttk.Entry(frame, width=30)
    imeEntry.grid(row=0, column=1, pady=5, padx=(0, 10))
    
    # Category Type
    ttk.Label(frame, text="Vrsta:*").grid(row=1, column=0, sticky="w", pady=5)
    vrstaVar = tk.StringVar(value="rashod")
    ttk.Radiobutton(frame, text="Rashod", variable=vrstaVar, value="rashod").grid(row=1, column=1, sticky="w", padx=5)
    ttk.Radiobutton(frame, text="Prihod", variable=vrstaVar, value="prihod").grid(row=1, column=1, sticky="w", padx=100)
    
    # Tax Deductible
    ttk.Label(frame, text="Porezno Priznato:").grid(row=2, column=0, sticky="w", pady=5)
    porezVar = tk.BooleanVar(value=True)
    ttk.Checkbutton(frame, variable=porezVar, text="Da").grid(row=2, column=1, sticky="w", pady=5)
    
    # Description
    ttk.Label(frame, text="Opis:").grid(row=3, column=0, sticky="w", pady=5)
    opisText = tk.Text(frame, height=4, width=30)
    opisText.grid(row=3, column=1, pady=5, padx=(0, 10))
    
    def submit():
        from .kategorije import addCategory
        
        ime = imeEntry.get().strip()
        if not ime:
            messagebox.showerror("Greška", "Unesite naziv kategorije!")
            return
        
        category_id = addCategory(
            cursor, conn,
            ime=ime,
            vrsta=vrstaVar.get(),
            poreznoPriznato=porezVar.get(),
            opis=opisText.get("1.0", tk.END).strip() or None
        )
        
        if category_id:
            messagebox.showinfo("Uspjeh", f"Kategorija dodana pod ID: {category_id}")
            if refreshCallback:
                refreshCallback()
            window.destroy()
        else:
            messagebox.showerror("Greška", "Kategorija nije dodana! Provjerite da li već postoji kategorija s tim nazivom.")
    
    ttk.Button(frame, text="Dodaj Kategoriju", command=submit).grid(row=4, column=0, columnspan=2, pady=20)
    
    return window

def editCategoryForm(parent, cursor, conn, category_id, refreshCallback=None):
    from .kategorije import getCategoryById, updateCategory
    
    category = getCategoryById(cursor, category_id)
    
    if not category:
        messagebox.showerror("Greška", "Kategorija nije pronađena!")
        return
    
    window = tk.Toplevel(parent)
    window.title(f"Uredi Kategoriju: {category['ime']}")
    window.geometry("400x400")
    
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill="both", expand=True)
    
    # Category Name
    ttk.Label(frame, text="Naziv Kategorije:*").grid(row=0, column=0, sticky="w", pady=5)
    imeEntry = ttk.Entry(frame, width=30)
    imeEntry.grid(row=0, column=1, pady=5, padx=(0, 10))
    imeEntry.insert(0, category['ime'])
    
    # Category Type
    ttk.Label(frame, text="Vrsta:*").grid(row=1, column=0, sticky="w", pady=5)
    vrstaVar = tk.StringVar(value=category['vrsta'])
    ttk.Radiobutton(frame, text="Rashod", variable=vrstaVar, value="rashod").grid(row=1, column=1, sticky="w", padx=5)
    ttk.Radiobutton(frame, text="Prihod", variable=vrstaVar, value="prihod").grid(row=1, column=1, sticky="w", padx=100)
    
    # Tax Deductible
    ttk.Label(frame, text="Porezno Priznato:").grid(row=2, column=0, sticky="w", pady=5)
    porezVar = tk.BooleanVar(value=bool(category['poreznoPriznato']))
    ttk.Checkbutton(frame, variable=porezVar, text="Da").grid(row=2, column=1, sticky="w", pady=5)
    
    # Description
    ttk.Label(frame, text="Opis:").grid(row=3, column=0, sticky="w", pady=5)
    opisText = tk.Text(frame, height=4, width=30)
    opisText.grid(row=3, column=1, pady=5, padx=(0, 10))
    opisText.insert("1.0", category['opis'] or "")
    
    def submit():
        ime = imeEntry.get().strip()
        if not ime:
            messagebox.showerror("Greška", "Unesite naziv kategorije!")
            return
        
        success = updateCategory(
            cursor, conn,
            category_id=category_id,
            ime=ime,
            vrsta=vrstaVar.get(),
            poreznoPriznato=porezVar.get(),
            opis=opisText.get("1.0", tk.END).strip() or None
        )
        
        if success:
            messagebox.showinfo("Uspjeh", "Kategorija uspješno ažurirana!")
            if refreshCallback:
                refreshCallback()
            window.destroy()
        else:
            messagebox.showerror("Greška", "Kategorija nije ažurirana!")
    
    def deleteCategory():
        from .kategorije import deleteCategory as deleteCat
        success, message = deleteCat(cursor, conn, category_id)
        
        if success:
            messagebox.showinfo("Uspjeh", message)
            if refreshCallback:
                refreshCallback()
            window.destroy()
        else:
            messagebox.showwarning("Upozorenje", message)
    
    # Buttons frame
    buttonFrame = ttk.Frame(frame)
    buttonFrame.grid(row=4, column=0, columnspan=2, pady=20)
    
    ttk.Button(buttonFrame, text="Spremi Promjene", command=submit).pack(side="left", padx=5)
    ttk.Button(buttonFrame, text="Izbriši", command=deleteCategory).pack(side="left", padx=5)
    ttk.Button(buttonFrame, text="Odustani", command=window.destroy).pack(side="left", padx=5)
    
    return window
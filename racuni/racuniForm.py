import tkinter as tk
from tkinter import ttk, messagebox

def addAccountForm(parent, cursor, conn, refreshCallback=None):
    
    window = tk.Toplevel(parent)
    window.title("Dodajte Novi Račun")
    window.geometry("400x600")
    
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill="both", expand=True)
    
    ttk.Label(frame, text="Naziv Računa:*").grid(row=0, column=0, sticky="w", pady=5)
    entryNaziv = ttk.Entry(frame, width=30)
    entryNaziv.grid(row=0, column=1, pady=5, padx=(0, 10))
    
    ttk.Label(frame, text="Vrsta Računa:*").grid(row=1, column=0, sticky="w", pady=5)
    comboVrsta = ttk.Combobox(frame, values=["tekući", "štedni", "kreditni"], width=27)
    comboVrsta.grid(row=1, column=1, pady=5, padx=(0, 10))
    comboVrsta.set("tekući")
    
    ttk.Label(frame, text="Broj Računa:").grid(row=2, column=0, sticky="w", pady=5)
    entryBroj = ttk.Entry(frame, width=30)
    entryBroj.grid(row=2, column=1, pady=5, padx=(0, 10))
    
    ttk.Label(frame, text="Naziv Banke:").grid(row=3, column=0, sticky="w", pady=5)
    entryBanka = ttk.Entry(frame, width=30)
    entryBanka.grid(row=3, column=1, pady=5, padx=(0, 10))
    
    ttk.Label(frame, text="Unesite Početni Iznos:").grid(row=4, column=0, sticky="w", pady=5)
    entryIznos = ttk.Entry(frame, width=30)
    entryIznos.grid(row=4, column=1, pady=5, padx=(0, 10))
    entryIznos.insert(0, "0")
    
    ttk.Label(frame, text="Bilješke:").grid(row=5, column=0, sticky="w", pady=5)
    textBiljeska = tk.Text(frame, height=3, width=30)
    textBiljeska.grid(row=5, column=1, pady=5, padx=(0, 10))
    
    def submit():
        naziv = entryNaziv.get().strip()
        if not naziv:
            messagebox.showerror("Greška!", "Unesite naziv računa")
            return
        
        try:
            iznos = float(entryIznos.get() or 0)
        except:
            messagebox.showerror("Greška!", "Neispravan iznos!")
            return
        
        from .racuni import addAccount

        accountId = addAccount(
            cursor, conn,
            naziv=naziv,
            vrsta=comboVrsta.get(),
            brojRacuna=entryBroj.get().strip() or None,
            imeBanke=entryBanka.get().strip() or None,
            pocetniIznos=iznos,
            biljeska=textBiljeska.get("1.0", tk.END).strip() or None
        )
        
        if accountId:
            messagebox.showinfo("Uspjeh!", f"Račun dodan pod ID: {accountId}")

            if refreshCallback:
                refreshCallback()

            window.destroy()
    
    ttk.Button(frame, text="Dodajte Račun", command=submit).grid(row=6, column=0, columnspan=2, pady=10)
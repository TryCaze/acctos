from database import *
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

def getAllAccounts(cursor):
    cursor.execute("SELECT * FROM ACCTOSRACUNI ORDER BY naziv")
    return cursor.fetchall()

def addAccount(db_cursor, db_conn, naziv, vrsta="tekući", brojRacuna=None, imeBanke=None, pocetniIznos=0, biljeska=None):
    try:
        db_cursor.execute("""
            INSERT INTO ACCTOSRACUNI 
            (naziv, vrsta, brojRacuna, imeBanke, pocetniIznos, trenutacniIznos, biljeska)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (naziv, vrsta, brojRacuna, imeBanke, pocetniIznos, pocetniIznos, biljeska))
        db_conn.commit()
        return db_cursor.lastrowid
    except Exception as e:
        print(f"Error: {e}")
        return None

def updateAccount(cursor, conn, racunId, naziv=None, vrsta=None, brojRacuna=None, imeBanke=None, biljeska=None):
    updates = []
    params = []
    if naziv:
        updates.append("naziv = ?")
        params.append(naziv)
    if vrsta:
        updates.append("vrsta = ?")
        params.append(vrsta)
    if brojRacuna:
        updates.append("brojRacuna = ?")
        params.append(brojRacuna)
    if imeBanke:
        updates.append("imeBanke = ?")
        params.append(imeBanke)
    if biljeska:
        updates.append("biljeska = ?")
        params.append(biljeska)

    if updates:
        query = f"UPDATE ACCTOSRACUNI SET {', '.join(updates)} WHERE id = ?"
        params.append(racunId)
        cursor.execute(query, tuple(params))
        conn.commit()
        return True
    return False

def accountsTable(parent, cursor, onSelectCallback=None):
    tree = ttk.Treeview(parent, columns=("ID", "Naziv", "Vrsta", "Banka", "Iznos"), show="headings")

    tree.heading("ID", text="ID")
    tree.heading("Naziv", text="Naziv")
    tree.heading("Vrsta", text="Vrsta")
    tree.heading("Banka", text="Banka")
    tree.heading("Iznos", text="Iznos")

    tree.column("ID", width=100)
    tree.column("Naziv", width=200)
    tree.column("Vrsta", width=100)
    tree.column("Banka", width=150)
    tree.column("Iznos", width=100)
    
    # Store cursor for later use
    tree._cursor = cursor
    
    # Bind single click event if callback provided
    if onSelectCallback:
        tree.bind('<ButtonRelease-1>', lambda event: onSelectCallback(tree))
    
    return tree

def refreshAccountsTable(tree, cursor):
    for item in tree.get_children():
        tree.delete(item)
    
    accounts = getAllAccounts(cursor)
    for account in accounts:
        tree.insert("", "end", values=(
            account["id"],
            account["naziv"],
            account["vrsta"],
            account["imeBanke"] or "",
            f"{account['trenutacniIznos']:.2f}"
        ))

def openEditAccountForm(parent, cursor, conn, account_id, refreshCallback=None):
    cursor.execute("SELECT * FROM ACCTOSRACUNI WHERE id = ?", (account_id,))
    account = cursor.fetchone()
    
    if not account:
        messagebox.showerror("Greška", "Račun nije pronađen!")
        return
    
    window = tk.Toplevel(parent)
    window.title(f"Uredi Račun: {account['naziv']}")
    window.geometry("400x500")
    
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill="both", expand=True)
    
    ttk.Label(frame, text="Naziv Računa:*").grid(row=0, column=0, sticky="w", pady=5)
    entryNaziv = ttk.Entry(frame, width=30)
    entryNaziv.grid(row=0, column=1, pady=5, padx=(0, 10))
    entryNaziv.insert(0, account["naziv"])
    
    ttk.Label(frame, text="Vrsta Računa:*").grid(row=1, column=0, sticky="w", pady=5)
    comboVrsta = ttk.Combobox(frame, values=["tekući", "štedni", "kreditni"], width=27)
    comboVrsta.grid(row=1, column=1, pady=5, padx=(0, 10))
    comboVrsta.set(account["vrsta"])
    
    ttk.Label(frame, text="Broj Računa:").grid(row=2, column=0, sticky="w", pady=5)
    entryBroj = ttk.Entry(frame, width=30)
    entryBroj.grid(row=2, column=1, pady=5, padx=(0, 10))
    entryBroj.insert(0, account["brojRacuna"] or "")
    
    ttk.Label(frame, text="Naziv Banke:").grid(row=3, column=0, sticky="w", pady=5)
    entryBanka = ttk.Entry(frame, width=30)
    entryBanka.grid(row=3, column=1, pady=5, padx=(0, 10))
    entryBanka.insert(0, account["imeBanke"] or "")
    
    ttk.Label(frame, text="Trenutni Iznos:").grid(row=4, column=0, sticky="w", pady=5)
    ttk.Label(frame, text=f"{account['trenutacniIznos']:.2f}").grid(row=4, column=1, sticky="w", pady=5)
    
    ttk.Label(frame, text="Bilješke:").grid(row=5, column=0, sticky="w", pady=5)
    textBiljeska = tk.Text(frame, height=3, width=30)
    textBiljeska.grid(row=5, column=1, pady=5, padx=(0, 10))
    textBiljeska.insert("1.0", account["biljeska"] or "")
    
    def submitUpdate():
        naziv = entryNaziv.get().strip()
        if not naziv:
            messagebox.showerror("Greška!", "Unesite naziv računa")
            return
        
        success = updateAccount(
            cursor, conn,
            racunId=account_id,
            naziv=naziv,
            vrsta=comboVrsta.get(),
            brojRacuna=entryBroj.get().strip() or None,
            imeBanke=entryBanka.get().strip() or None,
            biljeska=textBiljeska.get("1.0", tk.END).strip() or None
        )
        
        if success:
            messagebox.showinfo("Uspjeh!", "Račun uspješno ažuriran!")
            
            if refreshCallback:
                refreshCallback()
            
            window.destroy()
        else:
            messagebox.showerror("Greška", "Nije moguće ažurirati račun!")
    
    ttk.Button(frame, text="Spremi Promjene", command=submitUpdate).grid(row=6, column=0, columnspan=2, pady=10)
    
    def deleteAccount():
        if messagebox.askyesno("Potvrdite", "Jeste li sigurni da želite izbrisati ovaj račun?"):
            try:
                cursor.execute("DELETE FROM ACCTOSRACUNI WHERE id = ?", (account_id,))
                conn.commit()
                messagebox.showinfo("Uspjeh!", "Račun izbrisan!")
                
                if refreshCallback:
                    refreshCallback()
                
                window.destroy()
            except Exception as e:
                messagebox.showerror("Greška", f"Nije moguće izbrisati račun: {e}")
    
    ttk.Button(frame, text="Izbriši Račun", command=deleteAccount).grid(row=7, column=0, columnspan=2, pady=5)
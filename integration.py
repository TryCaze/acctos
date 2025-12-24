import tkinter.messagebox as messagebox
from datetime import datetime

def createInventoryTransactionFromPurchase(cursor, conn, transakcijaId, artiklId, kolicina, jedinicnaCijena, lokacija=None, dobavljacKupac=None):
    try:
        cursor.execute("""
            SELECT datum, dobavljacKlijent, brojRacuna, opis
            FROM ACCTOSTRANSAKCIJE
            WHERE id = ?
        """, (transakcijaId,))
        trans = cursor.fetchone()

        if not trans:
            return False, "Transakcija nije pronađena"

        cursor.execute("SELECT naziv FROM ARTIKLZALIHE WHERE id = ?", (artiklId,))

        artikl = cursor.fetchone()

        if not artikl:
            return False, "Artikl nije pronađen"
        
        # Create inventory transaction record
        cursor.execute("""
            INSERT INTO ZALIHATRANSAKCIJA 
            (datum, tipTransakcije, artiklId, kolicina, jedinicnaCijena, ukupanIznos,
             povezaniTransakcijaId, dobavljacKupac, uLokaciju, napomene)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trans['datum'],
            'nabava',
            artiklId,
            kolicina,
            jedinicnaCijena,
            kolicina * jedinicnaCijena,
            transakcijaId,
            dobavljacKupac or trans['dobavljacKlijent'],
            lokacija,
            f"Automatski generirano iz transakcije #{transakcijaId}: {trans['opis'] or ''}"
        ))

        # Update stock
        cursor.execute("""
            INSERT INTO StanjeZalihe (artiklId, lokacija, kolicina, nabavnaCijena, napomene)
            VALUES (?, ?, ?, ?, ?)
        """, (
            artiklId,
            lokacija,
            kolicina,
            jedinicnaCijena,
            f"Automatski dodano iz transakcije #{transakcijaId}"
        ))

        conn.commit()
        return True, "Inventura ažurirana"

    except Exception as e:
        return False, f"Pogreška: {e}"
    
def createSalesTransactionFromInventory(cursor, conn, transakcijaId, artiklId, kolicina, prodajnaCijena, lokacija=None, kupac=None):
    
    try:
        cursor.execute("""
            SELECT datum, dobavljacKlijent, brojRacuna, opis, racunId
            FROM ACCTOSTRANSAKCIJE 
            WHERE id = ?
        """, (transakcijaId,))
        trans = cursor.fetchone()

        if not trans:
            return False, "Transakcija nije pronađena"
        
        cursor.execute("SELECT naziv FROM ARTIKLZALIHE WHERE id = ?", (artiklId,))

        artikl = cursor.fetchone()

        if not artikl:
            return False, "Artikl nije pronađen"
        
         # Create inventory transaction record (negative for sales)
        cursor.execute("""
            INSERT INTO ZALIHATRANSAKCIJA 
            (datum, tipTransakcije, artiklId, kolicina, jedinicnaCijena, ukupanIznos,
             povezaniTransakcijaId, dobavljacKupac, izLokacije, napomene)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trans['datum'],
            'prodaja',
            artiklId,
            -kolicina,  # Negative for sales
            prodajnaCijena,
            kolicina * prodajnaCijena,
            transakcijaId,
            kupac or trans['dobavljacKlijent'],
            lokacija,
            f"Automatski generirano iz prodajne transakcije #{transakcijaId}"
        ))
        
        # Update stock (negative quantity)
        cursor.execute("""
            INSERT INTO StanjeZalihe (artiklId, lokacija, kolicina, napomene)
            VALUES (?, ?, ?, ?)
        """, (
            artiklId,
            lokacija,
            -kolicina,  # Negative for sales
            f"Prodaja iz transakcije #{transakcijaId}"
        ))

        conn.commit()
        return True, "Inventura ažurirana za prodaju"

    except Exception as e:
        return False, f"Pogreška: {e}"
    
def linkTransactionToInventory(cursor, conn, transakcijaId, artiklId, kolicina, cijena, tip='nabava', lokacija=None):
    try:
        if tip == 'nabava':
            return createInventoryTransactionFromPurchase(cursor, conn, transakcijaId, artiklId, kolicina, cijena, lokacija)
        elif tip == 'prodaja':
            return createSalesTransactionFromInventory(cursor, conn, transakcijaId, artiklId, kolicina, cijena, lokacija)
        else:
            return False, f"Nepodržan tip transakcije: {tip}"
    except Exception as e:
        return False, f"Pogreška pri povezivanju: {e}"

def getInventoryTransactionsForFinancialTransaction(cursor, transakcijaId):
    cursor.execute("""
        SELECT z.*, a.naziv as artiklNaziv, a.sku
        FROM ZALIHATRANSAKCIJA z
        LEFT JOIN ARTIKLZALIHE a ON z.artiklId = a.id
        WHERE z.povezaniTransakcijaId = ?
    """, (transakcijaId,))
     
    return cursor.fetchall()

def getFinancialTransactionsForInventoryItem(cursor, artiklId):
    cursor.execute("""
        SELECT t.*, z.tipTransakcije, z.kolicina as inventarKolicina
        FROM ACCTOSTRANSAKCIJE t
        INNER JOIN ZALIHATRANSAKCIJA z ON t.id = z.povezaniTransakcijaId
        WHERE z.artiklId = ?
        ORDER BY t.datum DESC
    """, (artiklId,))
    return cursor.fetchall()